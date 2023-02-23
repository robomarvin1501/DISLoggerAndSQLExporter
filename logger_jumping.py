import datetime
import lzma
import socket
import threading
import struct

class PlaybackPDU:
    """
    Contains any given PDU in the PDU field, along with PacketTime, and WorldTime data
    """

    def __init__(self, logger_line):
        """
        :param logger_line: bytes : a line of bytes from the loggerfile
        These are the of the format : pdu_data, PacketTime, WorldTime
        """
        self.pdu = None
        self.packet_time = 0.0
        self.world_time = 0.0

        self.interpret_logger_line(logger_line)

    def interpret_logger_line(self, logger_line: bytes):
        """
        Unpacks a line received from the logger into the object
        :param logger_line: bytes : a line of bytes from the loggerfile
        These are the of the format : pdu_data, PacketTime, WorldTime
        """
        if logger_line.count(b"line_divider") == 2:
            split_line = logger_line.split(b"line_divider")
        else:
            raise ValueError(
                f"Given line of data does not contain enough seperators. Perhaps some data is missing: {logger_line}")
        self.pdu = split_line[0]
        self.packet_time = struct.unpack("d", split_line[1])[0]  # struct.unpack always returns a tuple
        self.world_time = struct.unpack("d", split_line[2])[0]


class PlaybackLoggerFile:
    def __init__(self, loggername: str, exercise_id: int = 20):
        self.logger_pdus: list[PlaybackPDU] = []
        self.unprocessed_pdus: list[bytes] = []
        self.position_pointer = 0
        self.starting_timestamp = 0

        self.finished_loading = False
        self.restarted = False

        self.exercise_id = exercise_id

        self._UDP_PORT = 3000
        self._DESTINATION_ADDRESS = "192.133.255.255"

        self._udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self._udp_socket.bind(('', self._UDP_PORT))

        self.playback_thread = threading.Thread()

        self._message_stop_playback = False
        self._messages_awaiting = []

        self.load_logger(loggername)

    def _closer_time_then_neighbours(self, n, target_time):
        # 0: n is the closest
        # 1: n - 1 is closer
        # 2: n + 1 is closer
        if self.finished_loading:
            mid_time = self.logger_pdus[n].packet_time
            upper_time = self.logger_pdus[n + 1].packet_time
            lower_time = self.logger_pdus[n - 1].packet_time
        else:
            mid_time = PlaybackPDU(self.unprocessed_pdus[n]).packet_time
            upper_time = PlaybackPDU(self.unprocessed_pdus[n + 1]).packet_time
            lower_time = PlaybackPDU(self.unprocessed_pdus[n - 1]).packet_time

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
            high = len(self.unprocessed_pdus)
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

    def _send(self, pdu):
        def send_pdu(pdu: PlaybackPDU):
            pdu_to_send = bytearray(pdu.pdu)

            pdu_to_send[1] = self.exercise_id

            self._udp_socket.sendto(pdu_to_send, (self._DESTINATION_ADDRESS, self._UDP_PORT))

        current_timestamp = datetime.datetime.now().timestamp()

        diff = current_timestamp - self.starting_timestamp

        delay = pdu.packet_time - diff

        t = threading.Timer(delay, send_pdu, args=(pdu,))
        t.start()
        self._messages_awaiting.append(t)

    def load_logger(self, loggername: str):
        with lzma.open(f"logs/{loggername}") as f:
            print(f"Reading loggerfile: {loggername}")
            raw_data = f.read().split(b"line_separator")[:-1]
            print(f"Finished reading loggerfile: {loggername}")

        total_pdus = len(raw_data)
        self.unprocessed_pdus = raw_data
        self.logger_pdus = []
        for i, custom_pdu_bytes in enumerate(raw_data):
            if i % 10_000 == 0:
                print("{:,}/{:,}".format(i, total_pdus))
            if custom_pdu_bytes == b'':
                continue
            try:
                self.logger_pdus.append(PlaybackPDU(custom_pdu_bytes))
            except BytesWarning:
                print("struct error")
                continue
            except ValueError:
                print("seperator error")

    def move_position_to_time(self, requested_time: float):
        if self.finished_loading:
            maximum_time = self.logger_pdus[-1].packet_time
        else:
            maximum_time = PlaybackPDU(self.unprocessed_pdus[-1]).packet_time
        if 0 <= requested_time <= maximum_time:
            self.starting_timestamp = requested_time
        elif requested_time < 0:
            self.starting_timestamp = 0
        elif requested_time > maximum_time:
            self.starting_timestamp = maximum_time

        if requested_time > maximum_time:
            self.position_pointer = len(self.unprocessed_pdus) - 1
            return None
        wanted_index = self._binary_search_for_time(requested_time, len(self.unprocessed_pdus), 0)
        self.position_pointer = wanted_index

    def start_playback(self):
        def playback():
            if self.finished_loading:
                pdus = self.logger_pdus[self.position_pointer:]
            else:
                pdus = self.unprocessed_pdus[self.position_pointer:]

            for pdu in pdus:
                if not self._message_stop_playback:
                    if self.finished_loading and not self.restarted:
                        self.restarted = True
                        # restarts playback using the loaded pdus instead
                        self.stop_playback()
                        self.start_playback()
                    if not self.finished_loading:
                        pdu = PlaybackPDU(pdu)
                    self._send(pdu)
                else:
                    self.move_position_to_time(PlaybackPDU(pdu).packet_time)
                    self._message_stop_playback = False
                    for message in self._messages_awaiting:
                        message.cancel()
                    self._messages_awaiting = []
                    print(f"Current pdu: {self.position_pointer}, current time: {PlaybackPDU(self.unprocessed_pdus[self.position_pointer]).packet_time}")
                    return None
            # finally:
            #     self.move_position_to_time(0)

        # Idiotproof check
        if not self.playback_thread.is_alive():
            self.playback_thread = threading.Thread(target=playback, daemon=True)
            self.playback_thread.start()

    def stop_playback(self):
        if self.playback_thread.is_alive():
            self._message_stop_playback = True


if __name__ == "__main__":
    plg = PlaybackLoggerFile("exp_1_2102_2.lzma", 97)
    # plg = PlaybackLoggerFile("exp_0_1807_3.lzma", 97)
    command = ""
    # # print(f"Total pdus: {len(plg.logger_pdus)}. Running time: {plg.logger_pdus[-1].packet_time}")
    while command != "q":
        command = input("$ ")
        split_commands = command.split(' ')
        if split_commands[0] == "move":
            plg.move_position_to_time(float(split_commands[1]))
            print(
                f"Total pdus: {len(plg.unprocessed_pdus)}. Running time: {PlaybackPDU(plg.unprocessed_pdus[-1]).packet_time}")
            print(
                f"Current pdu: {plg.position_pointer}, current time: {PlaybackPDU(plg.unprocessed_pdus[plg.position_pointer]).packet_time}")
        elif split_commands[0] == "play":
            print(
                f"Current pdu: {plg.position_pointer}, current time: {PlaybackPDU(plg.unprocessed_pdus[plg.position_pointer]).packet_time}")
            plg.start_playback()
        elif split_commands[0] == "stop":
            plg.stop_playback()
            print(f"Current pdu: {plg.position_pointer}, current time: {PlaybackPDU(plg.unprocessed_pdus[plg.position_pointer]).packet_time}")
        elif split_commands[0] == "show" or split_commands[0] == "status":
            print(f"Total pdus: {len(plg.unprocessed_pdus)}. Running time: {PlaybackPDU(plg.unprocessed_pdus[-1]).packet_time}")
            # print(f"Current pdu: {plg.position_pointer}, current time: {plg.logger_pdus[plg.position_pointer].packet_time}")
    print("+++ PROGRAM ENDED +++")
