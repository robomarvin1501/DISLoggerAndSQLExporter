import socket

from opendis.PduFactory import createPdu
from opendis.dis7 import EntityID
from opendis.DataOutputStream import DataOutputStream
from io import BytesIO

# EXERCISE_ID = 97
# UDP_PORT = 3000
EXERCISE_ID = 20
UDP_PORT = 3000
FILENAME = "test.lzma"

entityids = set()

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

    data = udpSocket.recv(4096)

    current_pdu = createPdu(data)

    if current_pdu is not None:
        if current_pdu.exerciseID == exercise_id:
            try:
                entityids.add(current_pdu.entityID)
            except AttributeError:
                return
            print(len(entityids))

while True:
    receive_pdu(3000, 34)