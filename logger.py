import lzma
import socket
import struct
import sys
import datetime

from opendis.PduFactory import createPdu
from LoggerSQLExporter import LoggerSQLExporter, LoggerPDU


class DISReceiver:
    def __init__(self, port: int, exercise_id: int, msg_len: int = 8192, timeout: int = 15):
        """
        :param port: int : port on which dis is transmitted (usually 3000)
        :param exercise_id: int : The exercise id (experiments are usually 20, check wiki for further details)
        :param msg_len: int : The length of the message
        :param timeout: int : Amount of time to wait before giving up
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.settimeout(timeout)
        self.sock.bind(("", port))

        self.msg_len = msg_len

        self.exercise_id = exercise_id

        self.starting_timestamp = datetime.datetime.now().timestamp()

    def __iter__(self):
        return self

    def __next__(self):
        try:
            received_exercise_id = -1
            data, addr = "", ""
            world_timestamp = 0
            while received_exercise_id != self.exercise_id:
                try:
                    data, addr = self.sock.recvfrom(self.msg_len)
                    world_timestamp = datetime.datetime.now().timestamp()
                except WindowsError as e:
                    print(f"Windows error, socket size? {e}")
                    sys.exit()
                try:
                    received_pdu = createPdu(data)
                except struct.error as e:
                    print(f"Struct exception (shibolet): {e}")
                    sys.exit()

                if received_pdu is not None:
                    received_exercise_id = received_pdu.exerciseID

            packettime = world_timestamp - self.starting_timestamp
            assert packettime > 0
            return addr, data, packettime, world_timestamp
        except Exception as e:
            print(f"Got exception trying to receive {e}")
            raise StopIteration

    def __del__(self):
        print("Socket deleted")
        self.sock.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Socket exited")
        self.sock.close()


class DataWriter:
    def __init__(self, output_file_name, logger_dir, lzma_compressor):
        self.output_file_name = output_file_name
        self.logger_dir = logger_dir
        self.lzc = lzma_compressor

        self.line_divider = b"line_divider"
        self.line_separator = b"line_separator"

        self.output_file = None

    def __enter__(self):
        self.output_file = open(f"{self.logger_dir}/{self.output_file_name}", 'ab')
        return self

    # def __del__(self):
    #     print("Writer deleted")
    #     self.output_file.write(self.lzc.flush())
    #     self.output_file.close()

    def __exit__(self, exc_type, exc_val, exc_tb):
        print(f"Writer closed {exc_type} : {exc_val} : {exc_tb}")
        self.output_file.write(self.lzc.flush())
        self.output_file.close()

    def write(self, pdu_data, packettime: float, worldtime: float):
        bytes_packettime = struct.pack("d", packettime)
        bytes_worldtime = struct.pack("d", worldtime)
        self.output_file.write(
            self.lzc.compress(
                pdu_data + self.line_divider + bytes_packettime + self.line_divider + bytes_worldtime
                + self.line_separator
            )
        )

    def write_export(self, pdu_data, packettime: float, worldtime: float):
        bytes_packettime = struct.pack("d", packettime)
        bytes_worldtime = struct.pack("d", worldtime)

        return pdu_data + self.line_divider + bytes_packettime + self.line_divider + bytes_worldtime


lzc = lzma.LZMACompressor()

EXERCISE_ID = 97
export = True  # TODO move to config file
logger_file = "live_export_test.lzma"  # TODO move to config file
db_name = "GidonLSETest"

if export:
    LSE = LoggerSQLExporter(logger_file, db_name, EXERCISE_ID)

    with DataWriter(logger_file, "logs", lzc) as writer:
        with DISReceiver(3000, EXERCISE_ID, msg_len=16_384) as r:
            for (address, data, packettime, world_timestamp) in r:
                # print(f"Got packet from {address}: {data}")
                LSE.export(
                    LoggerPDU(
                        writer.write_export(data, packettime, world_timestamp)
                    )
                )
                # NOTE floats are doubles in C, so use struct.unpack('d', packettime) on them
                writer.write(data, packettime, world_timestamp)


else:
    with DataWriter(logger_file, "logs", lzc) as writer:
        with DISReceiver(3000, EXERCISE_ID, msg_len=16_384) as r:
            for (address, data, packettime, world_timestamp) in r:
                print(f"Got packet from {address}: {data}")
                # NOTE floats are doubles in C, so use struct.unpack('d', packettime) on them
                writer.write(data, packettime, world_timestamp)

# receiver_thread.join()
print("Program ended")
