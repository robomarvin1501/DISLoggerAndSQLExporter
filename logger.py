import json
import lzma
import socket
import struct
import sys
import datetime
import traceback

from opendis.PduFactory import createPdu
from LoggerSQLExporter import LoggerSQLExporter, LoggerPDU

import logging

logging.basicConfig(filename="dis-logger.log", encoding="utf-8", level=logging.DEBUG)
logging.info("This file is generated in case of things going wrong. Aside from this message, I hope it to be empty.")


class DISReceiver:
    """
    This class receives DIS messages through the network.
    It should be used as an iterable, that returns 4 items:
        addr, data, packettime, and world_timestamp

    addr: str               :   The ip address of the sender of this DIS message
    data: bytes             :   The received bytes from the network
    packettime: float       :   The time of the packet since the recording started
    world_timestamp: float  :   Number of seconds since 1970.01.01 (unix timestamp)
    """

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
        """
        Builds the iterator of received pdu data
        Ensures that you shouldn't miss any pdus, even if you spend a long time processing one
        :return:
        """
        try:
            received_exercise_id = -1
            data, addr = "", ""
            world_timestamp = 0
            packettime = -1
            # Keep looping until a pdu with the correct ExerciseID is received
            while received_exercise_id != self.exercise_id and packettime < 0:
                try:
                    data, addr = self.sock.recvfrom(self.msg_len)
                    world_timestamp = datetime.datetime.now().timestamp()
                except WindowsError as e:
                    # Occurs when attempting to receive a pdu that is too large.
                    # This will be left as an error that causes an exit, any such PDUs should be caught in integrations
                    print(f"Windows error, socket size? {e}")
                    sys.exit()
                try:
                    if data[2] == 20:
                        # DataPdu, it is very broken.
                        # It claims the VariableDatum is 8x longer than it actually is, and the VariableDatum is invalid
                        # UTF-8 and ASCII both
                        continue
                    received_pdu = createPdu(data)
                except struct.error as e:
                    print(f"Struct exception (shibolet): {e}")
                    logging.error(f"Struct exception (shibolet): {traceback.format_exc()}")
                    continue

                if received_pdu is not None:
                    received_exercise_id = received_pdu.exerciseID

                packettime = world_timestamp - self.starting_timestamp

            if packettime < 0:
                print(f"PACKETTIME LESS THAN 0: {packettime}")

            assert packettime >= 0
            return addr, data, packettime, world_timestamp
        except Exception as e:
            print(f"Got exception trying to receive: {e}")
            logging.error(traceback.format_exc())
            raise StopIteration

    def __del__(self):
        # Ensures that the socket is closed when deleting the object
        print("Socket deleted")
        self.sock.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Ensures that the socket is closed when deleting the object
        print("Socket exited")
        self.sock.close()


class DataWriter:
    """
    This class writes compressed DIS PDUs to the chosen loggerfile.
    It is used with the `with` statement, to ensure the files are properly opened and closed
    """

    def __init__(self, output_file_name: str, logger_dir: str, lzma_compressor: lzma.LZMACompressor):
        """
        :param output_file_name: str : name of the output file
        :param logger_dir: str : relative path from current directory to log storage
        :param lzma_compressor: lzma.LZMAConpressor : The compressor for the file
        """
        self.output_file_name = output_file_name
        self.logger_dir = logger_dir
        self.lzc = lzma_compressor

        # These dividers are given slightly odd names. This is to ensure that they will not appear within a PDU
        # and confuse things due to a PDU being split in the middle
        # Divider between data on a single line
        self.line_divider = b"line_divider"
        # Divider between lines of data
        self.line_separator = b"line_separator"

        self.output_file = None

    def __enter__(self):
        self.output_file = open(f"{self.logger_dir}/{self.output_file_name}", 'ab')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print(f"Writer closed {exc_type} : {exc_val} : {exc_tb}")
        self.output_file.write(self.lzc.flush())
        self.output_file.close()

    def write(self, pdu_data: bytes, packettime: float, worldtime: float):
        """
        This method compresses, and writes the provided PDU, and additional data to the logger file.
        :param pdu_data: bytes
        :param packettime: float
        :param worldtime: float
        :return: None
        """
        bytes_packettime = struct.pack("d", packettime)
        bytes_worldtime = struct.pack("d", worldtime)
        self.output_file.write(
            self.lzc.compress(
                pdu_data + self.line_divider + bytes_packettime + self.line_divider + bytes_worldtime
                + self.line_separator
            )
        )

    def write_export(self, pdu_data: bytes, packettime: float, worldtime: float):
        """
        This method provides the PDU, and additional data in the format as it would be in the logger file.
        This is useful when exporting in real time, since the exporter expects the received data to be of that format.
        :param pdu_data: bytes
        :param packettime: float
        :param worldtime: float
        :return: bytes
        """
        bytes_packettime = struct.pack("d", packettime)
        bytes_worldtime = struct.pack("d", worldtime)

        return pdu_data + self.line_divider + bytes_packettime + self.line_divider + bytes_worldtime


if __name__ == "__main__":
    try:
        with open("DataExporterConfig.json", 'r') as f:
            config_data = json.load(f)
    except FileNotFoundError:
        print(r"""
            ERROR: No configuration file
            Please write a configuration file in the base folder by the name "DataExporterConfig.json"
            For examples, see \\files\docs\DataExporter\DataExporterConfig.json
        """)
        sys.exit()

    if config_data["logger_file"][-5:] != ".lzma":
        config_data["logger_file"] += ".lzma"

    logging.info(f"Log {config_data['logger_file']} started on {datetime.datetime.now()}")

    lzc = lzma.LZMACompressor()

    EXERCISE_ID = config_data["exercise_id"]
    export = config_data["export_to_sql"]
    logger_file = config_data["logger_file"]
    db_name = config_data["database_name"]
    new_db = config_data["new_database"]

    if export:
        LSE = LoggerSQLExporter(logger_file, db_name, EXERCISE_ID, new_db=new_db)

        with DataWriter(logger_file, "logs", lzc) as writer:
            with DISReceiver(3000, EXERCISE_ID, msg_len=16_384) as r:
                for (address, data, packettime, world_timestamp) in r:
                    # print(f"Got packet from {address}: {data}")
                    try:
                        LSE.export(
                            LoggerPDU(
                                writer.write_export(data, packettime, world_timestamp)
                            )
                        )
                    except ValueError as e:
                        logging.warning(f"ValueError: {e}")
                    except BytesWarning as e:
                        logging.warning(f"BytesWarning: {e}")
                    except struct.error as e:
                        logging.warning(f"struct error: {e}")

                    # NOTE floats are doubles in C, so use struct.unpack('d', packettime) on them
                    writer.write(data, packettime, world_timestamp)

    else:
        with DataWriter(logger_file, "logs", lzc) as writer:
            with DISReceiver(3000, EXERCISE_ID, msg_len=16_384) as r:
                for (address, data, packettime, world_timestamp) in r:
                    # NOTE floats are doubles in C, so use struct.unpack('d', packettime) on them
                    writer.write(data, packettime, world_timestamp)

    # receiver_thread.join()
    print("Program ended")
    print("""
    ============================================================
    PLEASE WAIT FOR THE WINDOW TO CLOSE ITSELF
    ============================================================
    """)
