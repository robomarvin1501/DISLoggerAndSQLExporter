import datetime
import lzma
import multiprocessing
import multiprocessing.connection
import re
import socket
import threading
import struct
import time
import os

import logging

if "DataPlayer" not in os.listdir("C:/"):
    os.mkdir("C:/DataPlayer")
logging.basicConfig(filename="C:/DataPlayer/jumping.log", encoding="utf8", filemode="w", level=logging.DEBUG)


def sender(pdu_queue: multiprocessing.connection.PipeConnection,
           message_queue: multiprocessing.connection.PipeConnection,
           returning_information_queue: multiprocessing.SimpleQueue, exercise_id: int):
    """
    This function is run in a separate thread or process, and handles the sending of the PDUs to the network.
    :param pdu_queue:                   multiprocessing.connection.PipeConnection   : Pipe through which PDUs arrive
    :param message_queue:               multiprocessing.connection.PipeConnection   : Pipe through which messages arrive
    :param returning_information_queue: multiprocessing.SimpleQueue                 : SimpleQueue for returning messages
    :param exercise_id: int
    :return: None
    """
    UDP_PORT = 3000
    DESTINATION_ADDRESS = "255.255.255.255"

    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    # udp_socket.bind(('', UDP_PORT))

    starting_timestamp = 0
    starting_message_packettime = 0
    skip_sleep = False

    playback_modifier = 1

    def send(pdu: bytes) -> None:
        """
        Sends PDU bytes over broadcast across the network
        :param pdu: bytes
        :return: None
        """
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
                # Get the last PDUs from the queue, send back the PacketTime of the last message
                while pdu_queue.poll():
                    pdu_queue.recv()
                logging.debug(f"{messages_not_slept} messages not slept")
                messages_not_slept = 0
                returning_information_queue.put(last_executed_time)
                if not message[1]:
                    last_executed_time = 0
            elif message[0] == "starting_timestamp":
                # Get the PacketTime of the first message to be sent, and modify according to the playback speed
                starting_timestamp = message[1]
                starting_message_packettime = message[2] / playback_modifier
            elif message[0] == "playback":
                playback_modifier = message[1]
            elif message[0] == "skip_sleep":
                skip_sleep = message[1]
            elif message[0] == "exit":
                break
        if pdu_queue.poll():
            usages += 1
            pdu = pdu_queue.recv()

            # Figure out how long the thread should wait before sending this PDU to the network, so it is sent at
            # the right time according to its PacketTime, and the playback speed
            current_timestamp = datetime.datetime.now().timestamp()
            play_time = current_timestamp - starting_timestamp
            in_world_play_time = starting_message_packettime + play_time
            delay = (pdu[1] / playback_modifier) - in_world_play_time

            # Honestly, a delay of < 0.1s is small enough to not be worried about.
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
    """
    This class handles playing back the logger file.
    It holds the sender function, and sends it information to be transmitted to the network, handles moving the location
    in the loggerfile, and everything required to make these things work.
    It isn't really handled directly by you, but more interfaced through other provided classes.
    """

    def __init__(self, loggername: str, pdu_queue: multiprocessing.connection.Connection,
                 message_queue: multiprocessing.connection.Connection,
                 returning_information_queue: multiprocessing.SimpleQueue,
                 exercise_id: int = 20):
        """
        :param loggername:                  str                                     : Absolute path to the logger file
        :param pdu_queue:                   multiprocessing.connection.Connection   : Pipe that holds the PDUs that are
                                                                                        to be sent
        :param message_queue:               multiprocessing.connection.Connection   : Pipe that holds messages that are
                                                                                        to be sent
        :param returning_information_queue: multiprocessing.SimpleQueue             : SimpleQueue through which
                                                                                        information returns from the
                                                                                        sender thread
        :param exercise_id:                 int
        """
        self.unprocessed_pdus: list[bytes] = []
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

        # A cache of the positions of all entities, so that when paused, they can still be seen.
        self.state_cache: dict[bytes, bytes] = dict()
        self.paused = False

        self.playback_speed = 1
        self.message_reduction_factor = 1

        self.pdu_queue: multiprocessing.connection.Connection = pdu_queue
        self.message_queue: multiprocessing.connection.Connection = message_queue
        self.returning_information_queue: multiprocessing.SimpleQueue = returning_information_queue

        self.load_logger(loggername)

    def _closer_time_then_neighbours(self, n: int, target_time: float) -> int:
        """
        For a pdu of position n in self.logger_pdus, this checks if the target time is closer to pdu n - 1, n, or n + 1
        :param n:               int     : Position in self.logger_pdus
        :param target_time:     float   : Target time in seconds from the start of the logger file
        :return: int
        """
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
        """
        Executes a binary search over self.logger_pdus to search for the pdu that is closest to the desired time.
        Returns the position of the closest pdu
        :param time: float  : Time in seconds since the start of the logger file
        :param high: int    : Upper bound of self.logger_pdus to be searched
        :param low:  int    : Lower bound of self.logger_pdus to be searched
        :return: int
        """
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

    def _send(self, pdu: tuple[bytes, float]) -> None:
        """
        Puts a PDU into the pipe to be sent to the sender thread
        :param pdu: tuple[bytes, float]     : A tuple of the pdu bytes, and its PacketTime
        :return: None
        """
        self.pdu_queue.send(pdu)

    def load_logger(self, loggername: str) -> None:
        """
        Loads a logger file from disk into memory of the program. Also translates it into a format that is useful to the
        sender, so that PDUs may be sent.
        :param loggername: str : Path to the logger file on disk
        :return: None
        """
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

    def move_position_to_time(self, requested_time: float) -> None:
        """
        Moves the playback position to the requested time.
        Can be used during active playback.
        If called during playback, playback is paused for the duration of the function
        :param requested_time: float : Seconds since the start of the exercise (PacketTime)
        :return: None
        """
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

    def start_playback(self) -> None:
        """
        Starts/unpauses the playback.
        This is achieved through sending the PDU bytes, along with the PacketTime to the sender thread
        This method pretty much solely manages the playback function, which runs in a separate thread, defined within.
        :return: None
        """
        if self.paused:
            self.unpause_playback()
            return
        self._message_stop_playback = False

        def playback():
            """
            Runs in a separate thread.
            Iterates over the PDUs, from the current position, and sends the PDUs to the sender thread.
            """
            pdus = self.logger_pdus[self.position_pointer:]
            # Emptied on start of playback to ensure that entities from the future aren't displayed early.
            self.state_cache.clear()

            for n, pdu in enumerate(pdus):
                if not self._message_stop_playback:
                    # There is such a thing as too many messages, so the number sent is reduced by the
                    # message_reduction_factor, and the playback speed, so as not to overwhelm the network connection
                    # and cause further slowdowns.
                    if n % (self.playback_speed * self.message_reduction_factor) == 0 or self.playback_speed < 1:
                        if pdu[0][2] == 1:
                            # Removes the interpolation when paused by setting the velocity to (0,0,0)
                            adjusted_velocity_pdu = bytearray(pdu[0])
                            adjusted_velocity_pdu[36:48] = b"\x00" * 12
                            self.state_cache[pdu[0][12:18]] = adjusted_velocity_pdu

                        self._send(pdu)
                    if n == len(pdus) - 5:
                        self.stop_playback()
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

                    if not self.paused:
                        self.remove_all_entities()

                    self._messages_awaiting = []
                    return None

        # Make sure that the pdu_queue has been emptied before beginning
        while self.pdu_queue.poll():
            self.pdu_queue.recv()
        self.starting_timestamp = datetime.datetime.now().timestamp()
        self.message_queue.send(
            ("starting_timestamp", self.starting_timestamp, self.logger_pdus[self.position_pointer][1]))
        # Idiotproof check, ensure the playback thread is not running right now
        if not self.playback_thread.is_alive():
            self.playback_thread = threading.Thread(target=playback, daemon=True)
            self.playback_thread.start()

    def stop_playback(self, pause=False) -> None:
        """
        Stops the playback by removing all entities, and sending a kill message to the playback thread.
        :param pause: bool : Whether this is being called from the pause method.
        :return: None
        """
        self._message_stop_playback = True

        if not pause:
            self.remove_all_entities()
        if self.playback_thread.is_alive():
            self.message_queue.send(("stop", pause))
        else:
            self.stop_time = datetime.datetime.now().timestamp()

    def remove_all_entities(self) -> None:
        """
        Iterates over all active entities, and makes them invisible so that they will no longer be seen in VRForces.
        :return: None
        """
        for e in self.state_cache:
            data = bytearray(self.state_cache[e])
            # appearance is 84-87 inclusive
            appearance = bin(struct.unpack('>I', data[84:88])[0])[2:].zfill(32)  # 8th needs changing to 1
            appearance_l = list(appearance)
            appearance_l[8] = '1'
            appearance = ''.join(appearance_l)
            appearance_bytes = struct.pack(">I", int(appearance, 2))

            data[84:88] = appearance_bytes

            self._send((data, 0))

    def _send_paused_locations(self) -> None:
        """
        Send the data from the state cache, with a PacketTime of 0, so it is sent instantly.
        :return: None
        """
        for pdu in self.state_cache:
            self._send((self.state_cache[pdu], 0))

    def pause_playback(self) -> None:
        """
        Pauses playback.
        Written in similar style of start_playback(), just the function that is run in a separate thread sends the
        PDUs with (0,0,0) in the velocity instead
        :return: None
        """
        self.stop_playback(pause=True)
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

    def unpause_playback(self) -> None:
        """
        Restarts playback from paused.
        Kinda deprecated since play() can also handle this
        :return: None
        """
        self.stop_playback(pause=True)
        self.paused = False
        while self.playback_thread.is_alive():
            time.sleep(0.1)
        self._message_stop_playback = False
        self.start_playback()
        while not self.returning_information_queue.empty():
            self.returning_information_queue.get()

    def set_playback_speed(self, playback_speed: float) -> None:
        """
        Sets the playback speed to the provided float.
        Faster the 10x doesn't really go any faster, 10x is probably the limit, but it should be sufficient so I'm
        not going to do anything about it right now.
        :param playback_speed: float
        :return: None
        """
        self.playback_speed = playback_speed
        self.message_queue.send(("playback", playback_speed))

    def disable_sleep(self, should_sleep: bool):
        """
        Will set the sender thread to either deliver packets at the required time, or to just run as fast as it can
        without sleeping.
        :param should_sleep: bool : True means do sleep, False means no sleep
        :return: None
        """
        self.message_queue.send(("skip_sleep", should_sleep))


class PlaybackLoggerFile:
    """
    This class provides easy control of the PlaybackLoggerFileManager
    It exists for connecting to the API, and for the GUI
    """

    def __init__(self, logger_name: str, exercise_id: int):
        """
        :param logger_name: str : absolute path to the lzma logger file that you want to load
        :param exercise_id: int : exercise id upon which you wish to play back
        """
        self.logger_path = logger_name
        self.pdu_receiver, self.pdu_sender = multiprocessing.Pipe()
        self.message_receiver, self.message_sender = multiprocessing.Pipe()
        self.returning_information_queue = multiprocessing.SimpleQueue()

        self.playback_manager = PlaybackLoggerFileManager(logger_name, self.pdu_sender, self.message_sender,
                                                          self.returning_information_queue, exercise_id)

        self.sender_process = threading.Thread(target=sender, args=(
            self.pdu_receiver, self.message_receiver, self.returning_information_queue, exercise_id), daemon=True)
        self.sender_process.start()

    def move(self, requested_time: float) -> None:
        """
        Moves the logger to the requested time. Can be used during playback
        :param requested_time: float
        :return: None
        """
        self.playback_manager.move_position_to_time(requested_time)

    def play(self) -> None:
        """
        Starts the playback of the loggerfile, or unpauses playback
        :return: None
        """
        self.playback_manager.start_playback()

    def stop(self) -> None:
        """
        Stops playback, and deletes entities from the game world
        :return: None
        """
        self.playback_manager.stop_playback()

    def pause(self) -> None:
        """
        Pauses playback. This means that the entities are still visible in the game world, they're just not moving
        :return: None
        """
        self.playback_manager.pause_playback()

    def unpause(self) -> None:
        """
        Restarts playback when paused. A Little deprecated since play can also do this now.
        :return: None
        """
        self.playback_manager.unpause_playback()

    def status(self) -> float:
        """
        Returns the PacketTime of the current pdu
        :return: float
        """
        return self.playback_manager.logger_pdus[self.playback_manager.position_pointer][1]

    def set_playback_speed(self, playback_speed: float) -> None:
        """
        Sets the playback speed, faster than 10 doesn't really world too well, but I see very little reason to try
        and optimise that.
        :param playback_speed: float
        :return: None
        """
        self.playback_manager.set_playback_speed(playback_speed)

    def set_exercise_id(self, exercise_id: int) -> None:
        """
        Sets the exercise ID. CANNOT be set while playing back.
        :param exercise_id: int
        :return: None
        """
        self.playback_manager.message_queue.send(("exit",))
        while self.sender_process.is_alive():
            time.sleep(0.05)
        self.sender_process = threading.Thread(target=sender, args=(
            self.pdu_receiver, self.message_receiver, self.returning_information_queue, exercise_id), daemon=True)
        self.sender_process.start()


if __name__ == "__main__":
    pdu_receiver, pdu_sender = multiprocessing.Pipe()
    message_receiver, message_sender = multiprocessing.Pipe()
    returning_information_queue = multiprocessing.SimpleQueue()
    playback = 1

    plg = PlaybackLoggerFileManager("logs/check_wildgoose_0305_1.lzma", pdu_sender, message_sender, returning_information_queue,
                                    99)
    command = ""
    running_time = 0
    sender_process = multiprocessing.Process(target=sender,
                                             args=(pdu_receiver, message_receiver, returning_information_queue, 99),
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
            running_time = time.perf_counter() - running_time
            print(
                f"Current pdu: {plg.position_pointer}, current time: {plg.logger_pdus[plg.position_pointer][1]}")
            print(f"Real running time: {running_time}")
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
