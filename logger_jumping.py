import datetime
import lzma
import multiprocessing
import multiprocessing.connection
import re
import socket
import threading
import struct
import time

import logging

logging.basicConfig(filename="jumping.log", encoding="utf8", filemode="w", level=logging.DEBUG)


def sender(pdu_queue: multiprocessing.connection.PipeConnection,
           message_queue: multiprocessing.connection.PipeConnection,
           returning_information_queue: multiprocessing.SimpleQueue, exercise_id: int):
    UDP_PORT = 3000
    DESTINATION_ADDRESS = "192.133.255.255"

    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    # udp_socket.bind(('', UDP_PORT))

    starting_timestamp = 0
    starting_message_packettime = 0
    skip_sleep = False

    playback_modifier = 1

    def send(pdu: bytes):
        pdu_to_send = bytearray(pdu)

        pdu_to_send[1] = exercise_id

        udp_socket.sendto(pdu_to_send, (DESTINATION_ADDRESS, UDP_PORT))

    last_executed_time = 0
    messages_not_slept = 0
    while True:
        usages = 0
        if message_queue.poll():
            usages += 1
            message = message_queue.recv()
            if message[0] == "stop":
                while pdu_queue.poll():
                    pdu_queue.recv()
                logging.debug(f"{messages_not_slept} messages not slept")
                messages_not_slept = 0
                returning_information_queue.put(last_executed_time)
                last_executed_time = 0
            elif message[0] == "starting_timestamp":
                starting_timestamp = message[1]
                starting_message_packettime = message[2]
            elif message[0] == "playback":
                playback_modifier = message[1]
            elif message[0] == "skip_sleep":
                skip_sleep = message[1]
            elif message[0] == "exit":
                break
        if pdu_queue.poll():
            usages += 1
            pdu = pdu_queue.recv()

            current_timestamp = datetime.datetime.now().timestamp()
            play_time = current_timestamp - starting_timestamp
            in_world_play_time = starting_message_packettime + play_time
            delay = (pdu[1] / playback_modifier) - in_world_play_time

            if delay >= 0.1 and not skip_sleep:
                time.sleep(delay)
                logging.debug(f"{messages_not_slept} messages not slept")
                messages_not_slept = 0
                logging.debug(delay)
            else:
                messages_not_slept += 1

            send(pdu[0])
            # Ensure that when the playback is paused, and the timestamp is therefore 0,
            # last_executed_time is not set to this.
            # Especially useful since a pause is sent when playback is stopped
            if pdu[1] > 1:
                last_executed_time = pdu[1]
        if usages == 0:
            time.sleep(1)


class PlaybackLoggerFileManager:
    def __init__(self, loggername: str, pdu_queue: multiprocessing.connection.Connection,
                 message_queue: multiprocessing.connection.Connection,
                 returning_information_queue: multiprocessing.SimpleQueue,
                 exercise_id: int = 20):
        self.unprocessed_pdus: list[bytes] = []  # TODO maybe preload by splitting on line_divider?
        self.logger_pdus: list[tuple[bytes, float]] = []
        self.position_pointer = 0
        self.starting_timestamp = 0

        self.finished_loading = False
        self.restarted = False

        self.exercise_id = exercise_id

        self.playback_thread = threading.Thread()

        self._message_stop_playback = False
        self._messages_awaiting = []

        self._maximum_time = 0
        self.stop_time = datetime.datetime.now().timestamp()

        self.state_cache: dict[bytes, bytes] = dict()
        self.paused = False

        self.playback_speed = 1
        self.message_reduction_factor = 1

        self.pdu_queue: multiprocessing.connection.Connection = pdu_queue
        self.message_queue: multiprocessing.connection.Connection = message_queue
        self.returning_information_queue: multiprocessing.SimpleQueue = returning_information_queue

        self.load_logger(loggername)

    def _closer_time_then_neighbours(self, n, target_time):
        # 0: n is the closest
        # 1: n - 1 is closer
        # 2: n + 1 is closer

        mid_time = self.logger_pdus[n][1]
        upper_time = self.logger_pdus[n + 1][1]
        lower_time = self.logger_pdus[n - 1][1]

        if target_time > mid_time:
            if target_time - upper_time <= target_time - mid_time:
                # n + 1 is the closest
                return 2
            else:
                return 0

        elif target_time < mid_time:
            if lower_time - target_time <= mid_time - target_time:
                # n - 1 is the closest
                return 1
            else:
                return 0
        else:
            return 0

    def _binary_search_for_time(self, time: float, high: int = 0, low: int = 0) -> int:
        if high == 0:
            high = len(self.logger_pdus)
        if high == low:
            return high
        elif high > low:
            mid = (high + low) // 2

            closer_than_neighbours = self._closer_time_then_neighbours(mid, time)

            if closer_than_neighbours == 0:
                return mid

            elif closer_than_neighbours == 1:
                return self._binary_search_for_time(time, high=mid - 1, low=low)

            elif closer_than_neighbours == 2:
                return self._binary_search_for_time(time, high=high, low=mid + 1)

            else:
                raise ValueError(
                    f"Unexpected response ```{closer_than_neighbours}``` from self._closer_time_then_neighbours")
        else:
            return low

    def _send(self, pdu: tuple[bytes, float]):
        self.pdu_queue.send(pdu)

    def load_logger(self, loggername: str):
        with lzma.open(f"{loggername}") as f:
            print(f"Reading loggerfile: {loggername}")
            raw_data = f.read().split(b"line_separator")[:-1]
            print(f"Finished reading loggerfile: {loggername}")

        total_pdus = len(raw_data)
        self.unprocessed_pdus = raw_data
        self._maximum_time = struct.unpack("d", self.unprocessed_pdus[-1].split(b"line_divider")[1])[0]
        self.logger_pdus = []
        for i, custom_pdu_bytes in enumerate(raw_data):
            if i % 100_000 == 0:
                print("{:,}/{:,}".format(i, total_pdus))
            if custom_pdu_bytes == b'':
                continue
            try:
                pdu = custom_pdu_bytes.split(b"line_divider")
                self.logger_pdus.append((pdu[0], struct.unpack("d", pdu[1])[0]))
            except BytesWarning:
                print("struct error")
                continue
            except ValueError:
                print("seperator error")

    def move_position_to_time(self, requested_time: float):
        need_to_unpause = False
        if not self.paused and not self._message_stop_playback:
            self.pause_playback()
            need_to_unpause = True
        if requested_time > self._maximum_time:
            self.position_pointer = len(self.logger_pdus) - 1
            return None
        wanted_index = self._binary_search_for_time(requested_time, len(self.logger_pdus), 0)
        self.position_pointer = wanted_index
        if need_to_unpause:
            self.unpause_playback()

    def start_playback(self):
        if self.paused:
            self.unpause_playback()
            return
        self._message_stop_playback = False

        def playback():
            pdus = self.logger_pdus[self.position_pointer:]

            for n, pdu in enumerate(pdus):
                if not self._message_stop_playback:
                    if n % (self.playback_speed * self.message_reduction_factor) == 0 or self.playback_speed < 1:
                        if pdu[0][2] == 1:
                            # Removes the interpolation when paused by setting the velocity to (0,0,0)
                            adjusted_velocity_pdu = bytearray(pdu[0])
                            adjusted_velocity_pdu[36:48] = b"\x00" * 12
                            self.state_cache[pdu[0][12:18]] = adjusted_velocity_pdu

                        self._send(pdu)
                else:
                    # Waits to receive the end time because
                    # multiprocesssing.SimpleQueue blocks until it receives from a get()
                    end_time = self.returning_information_queue.get()
                    # if not self.paused:
                    # When paused, the current pointer logger does not get moved
                    self.move_position_to_time(end_time)

                    self.stop_time = datetime.datetime.now().timestamp()
                    # Make sure that the information queue is in fact empty
                    while not self.returning_information_queue.empty():
                        self.returning_information_queue.get()

                    # self._message_stop_playback = False
                    for message in self._messages_awaiting:
                        message.cancel()
                    self._messages_awaiting = []
                    return None

        self.starting_timestamp = datetime.datetime.now().timestamp()
        self.message_queue.send(
            ("starting_timestamp", self.starting_timestamp, self.logger_pdus[self.position_pointer][1]))
        # Idiotproof check
        if not self.playback_thread.is_alive():
            self.playback_thread = threading.Thread(target=playback, daemon=True)
            self.playback_thread.start()

    def stop_playback(self):
        self._message_stop_playback = True
        self._send_paused_locations()
        if self.playback_thread.is_alive():
            self.message_queue.send(("stop",))

    def _send_paused_locations(self):
        for pdu in self.state_cache:
            self._send((self.state_cache[pdu], 0))

    def pause_playback(self):
        self.stop_playback()
        self.paused = True

        def paused_messages():
            self._message_stop_playback = False
            while not self._message_stop_playback:
                self._send_paused_locations()
                time.sleep(0.5)

        time.sleep(0.5)
        # Idiotproof check
        if not self.playback_thread.is_alive():
            self.playback_thread = threading.Thread(target=paused_messages, daemon=True)
            self.playback_thread.start()

    def unpause_playback(self):
        self.stop_playback()
        self.paused = False
        while self.playback_thread.is_alive():
            time.sleep(0.1)
        self._message_stop_playback = False
        self.start_playback()
        while not self.returning_information_queue.empty():
            self.returning_information_queue.get()

    def set_playback_speed(self, playback_speed: float):
        self.playback_speed = playback_speed
        self.message_queue.send(("playback", playback_speed))

    def disable_sleep(self, should_sleep: bool):
        self.message_queue.send(("skip_sleep", should_sleep))


class PlaybackLoggerFile:
    def __init__(self, logger_name: str, exercise_id: int):
        self.logger_path = logger_name
        self.pdu_receiver, self.pdu_sender = multiprocessing.Pipe()
        self.message_receiver, self.message_sender = multiprocessing.Pipe()
        self.returning_information_queue = multiprocessing.SimpleQueue()
        self.playback_speed = 1

        self.playback_manager = PlaybackLoggerFileManager(logger_name, self.pdu_sender, self.message_sender,
                                                          self.returning_information_queue, exercise_id)

        self.sender_process = threading.Thread(target=sender, args=(
            self.pdu_receiver, self.message_receiver, self.returning_information_queue, 97), daemon=True)
        self.sender_process.start()

    def move(self, requested_time: float):
        self.playback_manager.move_position_to_time(requested_time)

    def play(self):
        self.playback_manager.start_playback()

    def stop(self):
        self.playback_manager.stop_playback()

    def pause(self):
        self.playback_manager.pause_playback()

    def unpause(self):
        self.playback_manager.unpause_playback()

    def status(self):
        return self.playback_manager.logger_pdus[self.playback_manager.position_pointer][1]

    def set_playback_speed(self, playback_speed: float):
        self.playback_manager.set_playback_speed(playback_speed)


if __name__ == "__main__":
    pdu_receiver, pdu_sender = multiprocessing.Pipe()
    message_receiver, message_sender = multiprocessing.Pipe()
    returning_information_queue = multiprocessing.SimpleQueue()
    playback = 1

    plg = PlaybackLoggerFileManager("exp_1_2102_2.lzma", pdu_sender, message_sender, returning_information_queue, 97)
    command = ""
    running_time = 0
    sender_process = multiprocessing.Process(target=sender,
                                             args=(pdu_receiver, message_receiver, returning_information_queue, 97),
                                             daemon=True, name="ByteSender")
    sender_process.start()
    while command != "q":
        command = input("$ ")
        split_commands = command.split(' ')
        if split_commands[0] == "move":
            plg.move_position_to_time(float(split_commands[1]))
            print(
                f"Total pdus: {len(plg.logger_pdus)}. Running time: {plg._maximum_time}")
            print(
                f"Current pdu: {plg.position_pointer}, current time: {plg.logger_pdus[plg.position_pointer][1]}")
        elif split_commands[0] == "play":
            print(
                f"Current pdu: {plg.position_pointer}, current time: {plg.logger_pdus[plg.position_pointer][1]}")
            running_time = time.perf_counter()
            plg.start_playback()
        elif split_commands[0] == "stop":
            plg.stop_playback()
            running_time = time.perf_counter() - running_time
            time.sleep(0.2)
            print(
                f"Current pdu: {plg.position_pointer}, current time: {plg.logger_pdus[plg.position_pointer][1]}")
            print(f"Real running time: {running_time}")
        elif split_commands[0] == "pause":
            plg.pause_playback()
        elif split_commands[0] == "unpause":
            plg.unpause_playback()
        elif split_commands[0] == "show" or split_commands[0] == "status":
            print(f"Total pdus: {len(plg.logger_pdus)}. Running time: {plg._maximum_time}")
            print(
                f"Current pdu: {plg.position_pointer}, current time: {plg.logger_pdus[plg.position_pointer][1]}, playback speed: {playback}")
            print(f"Message reduction factor: {plg.playback_speed * plg.message_reduction_factor}")
        elif split_commands[0] == "playback":
            # Anything that is not a number (1, 23, 1.3, 0.3, .4) returns None
            # Altering this requires a decent understanding of regex. I'm sorry.
            if re.match(r"^(?=.)([+-]?([0-9]*)(\.([0-9]+))?)$", split_commands[1]) is not None:
                playback = float(split_commands[1])
                plg.set_playback_speed(playback)
        elif split_commands[0] == "skip_sleep" and len(split_commands) > 1:
            should_skip = False
            if split_commands[1] == "1" or split_commands[1] == "True" or split_commands[1] == "true":
                should_skip = True
            plg.disable_sleep(should_skip)
        elif split_commands[0] == "reduction" and len(split_commands) > 1:
            plg.message_reduction_factor = int(split_commands[1])
        elif split_commands[0] == "exit":
            message_sender.send(("exit",))
            break
    sender_process.terminate()
    print("+++ PROGRAM ENDED +++")
