import lzma
import struct
import socket

from opendis.PduFactory import createPdu
from opendis.DataOutputStream import DataOutputStream
from io import BytesIO

EXERCISE_ID = 97
UDP_PORT = 3000
# EXERCISE_ID = 20
# UDP_PORT = 3000
FILENAME = "test.lzma"

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

    data = udpSocket.recv(16_384)

    current_pdu = createPdu(data)
    pdu_byte_data = b""

    if current_pdu is not None:
        if current_pdu.exerciseID == exercise_id:
            memory_stream = BytesIO()
            output_stream = DataOutputStream(memory_stream)

            current_pdu.serialize(output_stream)
            pdu_byte_data = memory_stream.getvalue()
            try:
                _ = createPdu(pdu_byte_data)
            except struct.error as e:
                print(e)
                print(f"Struct error, PDU bytes: {pdu_byte_data}")

    # print(type(current_pdu), len(pdu_byte_data))
            return [pdu_byte_data, current_pdu]
    return [None, None]


data = b''
pdus = []
pdu_bytes = b''
try:
    while True:
        try:
            pdu_info = receive_pdu(UDP_PORT, EXERCISE_ID)
            pdu_bytes = pdu_info[0]
            if pdu_bytes is not None:
                data += pdu_bytes
                data += b", "
                pdus.append(createPdu(pdu_bytes))
        except struct.error as e:
            print(e)
            print(f"Struct error, PDU bytes: {pdu_bytes}")

    # with open("logs/integration_0704_1.lzma", 'ab') as output_file:
    #     output_file.write(lzc.flush())
except KeyboardInterrupt as e:
    with open("logs/uncompressed_test", 'wb') as f:
        f.write(data)
