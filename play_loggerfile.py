import lzma
import socket

from io import BytesIO

import struct
import threading
import datetime

from opendis.PduFactory import createPdu
from opendis.DataOutputStream import DataOutputStream

UDP_PORT = 3000
DESTINATION_ADDRESS = "192.133.255.255"

udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
udpSocket.bind(('', 3000))


def send(pdu):
    memoryStream = BytesIO()
    outputStream = DataOutputStream(memoryStream)
    pdu.serialize(outputStream)
    data_altered = memoryStream.getvalue()

    udpSocket.sendto(data_altered, (DESTINATION_ADDRESS, UDP_PORT))


with lzma.open("logs/exp_0_1807_3.lzma", 'r') as f:
    raw_data = f.read().split(b"line_separator")

for i, line in enumerate(raw_data):
    starting_timestamp = datetime.datetime.now().timestamp()
    if line.count(b"line_divider") == 2:
        split_line = line.split(b"line_divider")

        data = split_line[0]

        try:
            pdu = createPdu(data)
        except:
            continue

        if pdu is None:
            continue

        pdu.exerciseID = 97


        current_timestamp = datetime.datetime.now().timestamp()
        diff = current_timestamp - starting_timestamp

        packettime = struct.unpack('d', split_line[1])[0]

        delay = packettime - diff

        threading.Timer(delay, send, args=(pdu,)).start()

    else:
        print("Broken line")
