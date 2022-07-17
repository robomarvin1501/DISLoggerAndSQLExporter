import lzma
import socket
import struct

from opendis.PduFactory import createPdu
from opendis.DataOutputStream import DataOutputStream
from io import BytesIO

import logging

logging.basicConfig(filename="logger_recorder.log", encoding="utf-8", level=logging.DEBUG)


# EXERCISE_ID = 97
# UDP_PORT = 3000
EXERCISE_ID = 97
UDP_PORT = 3000
FILENAME = "integration_0704_1.lzma"

print("Created UDP socket {}".format(UDP_PORT))


def receive_pdu(udp_port, exercise_id):
    """

    :param udp_port: int : port on which dis is transmitted
    :param exercise_id: int
    :return: bytes
    """
    udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    udpSocket.bind(("", udp_port))
    udpSocket.settimeout(3)  # exit if we get nothing in this many seconds

    try:
        data = udpSocket.recv(4096)
    except OSError as e:
        logging.warning(f"Problem receiving the data: {e}")
        return b""

    try:
        current_pdu = createPdu(data)
    except struct.error:
        logging.warning("Failed to create pdu")
        return b""
    pdu_byte_data = b""

    if current_pdu is not None:
        if current_pdu.exerciseID == exercise_id:
            memory_stream = BytesIO()
            output_stream = DataOutputStream(memory_stream)

            current_pdu.serialize(output_stream)
            pdu_byte_data = memory_stream.getvalue()

    return pdu_byte_data


def write_data(output_filename, logger_processing_dir, lzma_compressor, pdu_data):
    """
    :param output_filename: str
    :param pdu_data: bytes
    :return: None
    """
    if pdu_data == b"":
        return
    with open(f"{logger_processing_dir}/{output_filename}", 'ab') as output_file:
        output_file.write(lzma_compressor.compress(pdu_data + b", "))


lzc = lzma.LZMACompressor()
try:
    while True:
        write_data(FILENAME, "logs", lzc, receive_pdu(UDP_PORT, EXERCISE_ID))

except KeyboardInterrupt:
    with open(f"logs/{FILENAME}", 'ab') as output_file:
        output_file.write(lzc.flush())
