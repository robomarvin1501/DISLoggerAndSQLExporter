__author__ = "DMcG"
__date__ = "$Jun 23, 2015 10:27:29 AM$"

import socket
import time

from io import BytesIO

from opendis.DataInputStream import DataInputStream
from opendis.DataOutputStream import DataOutputStream
from opendis.dis7 import EntityStatePdu, EntityType
from opendis.RangeCoordinates import GPS

UDP_PORT = 3000
DESTINATION_ADDRESS = "192.133.255.255"

udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
udpSocket.bind(('', 3000))

gps = GPS()  # conversion helper


def send():
    pdu = EntityStatePdu()
    pdu.entityID.entityID = 666
    pdu.entityID.siteID = 1
    pdu.entityID.applicationID = 666
    pdu.marking.setString('GidonPython')
    pdu.marking.characterSet = 1

    pdu.forceId = 1
    pdu.protocolVersion = 5


    aet = EntityType(entityKind=3, domain=1, country=105, category=1, subcategory=17, specific=1, extra=0)
    pdu.entityType = aet
    pdu.alternativeEntityType = aet

    pdu.entityLocation.x = 4350866.61702344
    pdu.entityLocation.y = 3097656.22603807
    pdu.entityLocation.z = 3475595.20593483

    pdu.entityAppearance = 33619968

    pdu.exerciseID = 34

    pdu.deadReckoningParameters.deadReckoningAlgorithm = 4

    # Out of ideas, perhaps also timestamp?
    pdu.length = 144

    memoryStream = BytesIO()
    outputStream = DataOutputStream(memoryStream)
    pdu.serialize(outputStream)
    data = memoryStream.getvalue()

    while True:
        udpSocket.sendto(data, (DESTINATION_ADDRESS, UDP_PORT))
        print("Sent {}. {} bytes".format(pdu.__class__.__name__, len(data)))
        time.sleep(1)


send()
