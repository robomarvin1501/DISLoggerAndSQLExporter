import datetime
import lzma
import socket
import threading
import copy

from io import BytesIO
from opendis.DataOutputStream import DataOutputStream

from LoggerSQLExporter import LoggerPDU


class PlaybackLoggerFile:
    def __init__(self, loggername: str, exercise_id: int = 20):
        self.logger_pdus = []
        self.position_pointer = 0
        self.starting_timestamp = 0

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
        mid_time = self.logger_pdus[n].packet_time
        upper_time = self.logger_pdus[n + 1].packet_time
        lower_time = self.logger_pdus[n - 1].packet_time

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

    def _send(self, pdu: LoggerPDU):
        def send_pdu(pdu: LoggerPDU):
            self.move_position_to_time(pdu.packet_time)
            pdu_to_send = copy.deepcopy(pdu)

            pdu_to_send.pdu.exerciseID = self.exercise_id
            memory_stream = BytesIO()
            output_stream = DataOutputStream(memory_stream)
            pdu_to_send.pdu.serialize(output_stream)
            data_altered = memory_stream.getvalue()

            self._udp_socket.sendto(data_altered, (self._DESTINATION_ADDRESS, self._UDP_PORT))

        current_timestamp = datetime.datetime.now().timestamp()

        diff = current_timestamp - self.starting_timestamp

        delay = pdu.packet_time - diff

        t = threading.Timer(delay, send_pdu, args=(pdu,))
        t.start()
        self._messages_awaiting.append(t)

    def load_logger(self, loggername: str):
        with lzma.open(f"logs/{loggername}") as f:
            print(f"Reading loggerfile: {loggername}")
            raw_data = f.read().split(b"line_separator")
            print(f"Finished reading loggerfile: {loggername}")

        total_pdus = len(raw_data)
        self.logger_pdus = []
        for i, custom_pdu_bytes in enumerate(raw_data):
            if i % 10_000 == 0:
                print("{:,}/{:,}".format(i, total_pdus))
            if custom_pdu_bytes == b'':
                continue
            try:
                self.logger_pdus.append(LoggerPDU(custom_pdu_bytes))
            except BytesWarning:
                print("struct error")
                continue
            except ValueError:
                print("seperator error")

    def move_position_to_time(self, requested_time: float):
        if 0 <= requested_time <= self.logger_pdus[-1].packet_time:
            self.starting_timestamp = requested_time
        elif requested_time < 0:
            self.starting_timestamp = 0
        elif requested_time > self.logger_pdus[-1].packet_time:
            self.starting_timestamp = self.logger_pdus[-1].packet_time

        if requested_time > self.logger_pdus[-1].packet_time:
            self.position_pointer = len(self.logger_pdus) - 1
            return None
        wanted_index = self._binary_search_for_time(requested_time, len(self.logger_pdus), 0)
        self.position_pointer = wanted_index

    def start_playback(self):
        def playback():
            for pdu in self.logger_pdus[self.position_pointer:]:
                if not self._message_stop_playback:
                    self._send(pdu)
                else:
                    self._message_stop_playback = False
                    for message in self._messages_awaiting:
                        message.cancel()
                    self._messages_awaiting = []
                    return None

        # Idiotproof check
        if not self.playback_thread.is_alive():
            self.playback_thread = threading.Thread(target=playback, daemon=True)
            self.playback_thread.start()

    def stop_playback(self):
        if self.playback_thread.is_alive():
            self._message_stop_playback = True


if __name__ == "__main__":
    plg = PlaybackLoggerFile("all_the_play_stops_1.lzma", 97)
    # plg = PlaybackLoggerFile("exp_0_1807_3.lzma", 97)
    command = ""
    print(f"Total pdus: {len(plg.logger_pdus)}. Running time: {plg.logger_pdus[-1].packet_time}")
    while command != "q":
        command = input("$ ")
        split_commands = command.split(' ')
        if split_commands[0] == "move":
            plg.move_position_to_time(float(split_commands[1]))
            print(f"Total pdus: {len(plg.logger_pdus)}. Running time: {plg.logger_pdus[-1].packet_time}")
            print(
                f"Current pdu: {plg.position_pointer}, current time: {plg.logger_pdus[plg.position_pointer].packet_time}")
        elif split_commands[0] == "play":
            print(
                f"Current pdu: {plg.position_pointer}, current time: {plg.logger_pdus[plg.position_pointer].packet_time}")
            plg.start_playback()
        elif split_commands[0] == "stop":
            plg.stop_playback()
            print(
                f"Current pdu: {plg.position_pointer}, current time: {plg.logger_pdus[plg.position_pointer].packet_time}")
        elif split_commands[0] == "show" or split_commands[0] == "status":
            print(f"Total pdus: {len(plg.logger_pdus)}. Running time: {plg.logger_pdus[-1].packet_time}")
            print(
                f"Current pdu: {plg.position_pointer}, current time: {plg.logger_pdus[plg.position_pointer].packet_time}")
    print("+++ PROGRAM ENDED +++")
