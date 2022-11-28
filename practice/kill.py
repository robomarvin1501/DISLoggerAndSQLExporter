__author__ = "DMcG"
__date__ = "$Jun 23, 2015 10:27:29 AM$"

import socket
import time

from io import BytesIO

from opendis.DataInputStream import DataInputStream
from opendis.DataOutputStream import DataOutputStream
from opendis.dis7 import EntityStatePdu, EntityType, EventReportPdu, FixedDatum, VariableDatum
from opendis.RangeCoordinates import GPS

UDP_PORT = 3000
DESTINATION_ADDRESS = "192.133.255.255"

udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
udpSocket.bind(('', 3000))

gps = GPS()  # conversion helper


def send(site=0, host=0, num=0):
    if site == 4 and host == 800 and num == 5:
        return None

    pdu = EventReportPdu()  # 1 9681 12
    pdu.receivingEntityID.entityID = num
    pdu.receivingEntityID.applicationID = host
    pdu.receivingEntityID.siteID = site

    fixed_one = FixedDatum()
    fixed_two = FixedDatum()
    fixed_three = FixedDatum()

    fixed_one.fixedDatumID = 15100
    fixed_one.fixedDatumValue = site
    fixed_two.fixedDatumID = 15200
    fixed_two.fixedDatumValue = host
    fixed_three.fixedDatumID = 15300
    fixed_three.fixedDatumValue = num

    variable_one = VariableDatum()
    variable_one.variableDatumID = 0

    pdu.numberOfFixedDatumRecords = 3
    pdu.numberOfVariableDatumRecords = 1

    pdu.fixedDatums = [fixed_one, fixed_two, fixed_three]
    pdu.variableDatums = [variable_one]

    pdu.eventType = 803

    pdu.protocolVersion = 5

    pdu.length = 72
    pdu.exerciseID = 20

    memoryStream = BytesIO()
    outputStream = DataOutputStream(memoryStream)
    pdu.serialize(outputStream)
    data = memoryStream.getvalue()
    # while True:
    udpSocket.sendto(data, (DESTINATION_ADDRESS, UDP_PORT))
    # print(f"Killed {site} {host} {num}")
    # print("Sent {}. {} bytes".format(pdu.__class__.__name__, len(data)))
    # time.sleep(1)


send(1, 5355, 193)

# '1-5355-193'
# for site in range(1, 10_000):
#     for num in range(1, 10_000):
#         for host in range(1, 10_000):
#             if host % 100 == 0:
#                 print(site, host, num)
#             send(site, host, num)
