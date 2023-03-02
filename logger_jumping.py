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
    udp_socket.bind(('', UDP_PORT))

    waiting_pdus: list[threading.Timer] = []
    starting_timestamp = 0

    playback_modifier = 1

    def send(pdu: bytes):
        pdu_to_send = bytearray(pdu)

        pdu_to_send[1] = exercise_id

        udp_socket.sendto(pdu_to_send, (DESTINATION_ADDRESS, UDP_PORT))

    while True:
        usages = 0
        if message_queue.poll():
            usages += 1
            message = message_queue.recv()
            if message[0] == "stop":
                executed_pdus = sum([not x.is_alive() for x in waiting_pdus])
                for pdu in waiting_pdus:
                    pdu.cancel()
                while pdu_queue.poll():
                    pdu_queue.recv()
                returning_information_queue.put(executed_pdus)
            elif message[0] == "starting_timestamp":
                starting_timestamp = datetime.datetime.now().timestamp()
            elif message[0] == "playback":
                playback_modifier = message[1]
            elif message[0] == "exit":
                break
        if pdu_queue.poll():
            usages += 1
            pdu = pdu_queue.recv()

            current_timestamp = datetime.datetime.now().timestamp()
            diff = current_timestamp - starting_timestamp
            delay = pdu[1] - diff

            delay /= playback_modifier
            logging.debug(delay)

            if delay <= 0:
                delay = 0

            t = threading.Timer(delay, send, args=(pdu[0],))
            waiting_pdus.append(t)
            t.start()
        if usages == 0:
            time.sleep(1)


class PlaybackLoggerFile:
    def __init__(self, loggername: str, pdu_queue: multiprocessing.connection.PipeConnection,
                 message_queue: multiprocessing.connection.PipeConnection,
                 returning_information_queue: multiprocessing.SimpleQueue,
                 exercise_id: int = 20):
        self.unprocessed_pdus: list[bytes] = []  # TODO maybe preload by splitting on line_divider?
        self.logger_pdus: list[tuple[bytes, float]] = []
        self.position_pointer = 0
        self.starting_timestamp = 0

        self.finished_loading = False
        self.restarted = False

        self.exercise_id = exercise_id

        # self._UDP_PORT = 3000
        # self._DESTINATION_ADDRESS = "192.133.255.255"
        #
        # self._udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # self._udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        # self._udp_socket.bind(('', self._UDP_PORT))

        self.playback_thread = threading.Thread()

        self._message_stop_playback = False
        self._messages_awaiting = []

        self._maximum_time = 0

        self.pdu_queue: multiprocessing.connection.PipeConnection = pdu_queue
        self.message_queue: multiprocessing.connection.PipeConnection = message_queue
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
        # def send_pdu(pdu: bytes):
        #     pdu_to_send = bytearray(pdu)
        #
        #     pdu_to_send[1] = self.exercise_id
        #
        #     self._udp_socket.sendto(pdu_to_send, (self._DESTINATION_ADDRESS, self._UDP_PORT))
        #     self.position_pointer += 1

        if pdu[0][2] == 21:
            return

        self.pdu_queue.send(pdu)

    def load_logger(self, loggername: str):
        with lzma.open(f"logs/{loggername}") as f:
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
        # if 0 <= requested_time <= self._maximum_time:
        #     self.starting_timestamp = requested_time
        # elif requested_time < 0:
        #     self.starting_timestamp = 0
        # elif requested_time > self._maximum_time:
        #     self.starting_timestamp = self._maximum_time

        if requested_time > self._maximum_time:
            self.position_pointer = len(self.logger_pdus) - 1
            return None
        wanted_index = self._binary_search_for_time(requested_time, len(self.logger_pdus), 0)
        self.position_pointer = wanted_index

    def start_playback(self):
        def playback():
            pdus = self.logger_pdus[self.position_pointer:]

            for pdu in pdus:
                if not self._message_stop_playback:
                    self._send(pdu)
                else:
                    # while not self.pdu_queue.empty():
                    #     self.pdu_queue.get()

                    n_sent_pdus = self.returning_information_queue.get()
                    self.position_pointer += n_sent_pdus
                    self.move_position_to_time(self.logger_pdus[self.position_pointer][1])

                    self._message_stop_playback = False
                    for message in self._messages_awaiting:
                        message.cancel()
                    self._messages_awaiting = []
                    return None
            # finally:
            #     self.move_position_to_time(0)

        self.starting_timestamp = datetime.datetime.now().timestamp()
        self.message_queue.send(("starting_timestamp", self.starting_timestamp))
        # Idiotproof check
        if not self.playback_thread.is_alive():
            self.playback_thread = threading.Thread(target=playback, daemon=True)
            self.playback_thread.start()

    def stop_playback(self):
        if self.playback_thread.is_alive():
            self._message_stop_playback = True
            self.message_queue.send(("stop",))


if __name__ == "__main__":
    pdu_receiver, pdu_sender = multiprocessing.Pipe()
    message_receiver, message_sender = multiprocessing.Pipe()
    returning_information_queue = multiprocessing.SimpleQueue()
    playback = 1

    plg = PlaybackLoggerFile("exp_1_2102_2.lzma", pdu_sender, message_sender, returning_information_queue, 97)
    # plg = PlaybackLoggerFile("exp_0_1807_3.lzma", 97)
    command = ""
    # # print(f"Total pdus: {len(plg.logger_pdus)}. Running time: {plg.logger_pdus[-1].packet_time}")
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
        elif split_commands[0] == "show" or split_commands[0] == "status":
            print(f"Total pdus: {len(plg.logger_pdus)}. Running time: {plg._maximum_time}")
            print(
                f"Current pdu: {plg.position_pointer}, current time: {plg.logger_pdus[plg.position_pointer][1]}, playback speed: {playback}")
            # print(f"Current pdu: {plg.position_pointer}, current time: {plg.logger_pdus[plg.position_pointer].packet_time}")
        elif split_commands[0] == "playback":
            # Anything that is not a number (1, 23, 1.3, 0.3, .4) returns None
            # Altering this requires a decent understanding of regex. I'm sorry.
            if re.match(r"^(?=.)([+-]?([0-9]*)(\.([0-9]+))?)$", split_commands[1]) is not None:
                playback = float(split_commands[1])
                message_sender.send(("playback", playback))

        elif split_commands[0] == "exit":
            message_sender.send(("exit",))
            break
    sender_process.start()
    print("+++ PROGRAM ENDED +++")
