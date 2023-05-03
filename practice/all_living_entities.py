import socket

from io import BytesIO

from opendis.DataOutputStream import DataOutputStream
from opendis.dis7 import EventReportPdu, FixedDatum, VariableDatum
from opendis.PduFactory import createPdu

# EXERCISE_ID = 97
# UDP_PORT = 3000
EXERCISE_ID = 99
UDP_PORT = 3000
FILENAME = "test.lzma"

DESTINATION_ADDRESS = "255.255.255.255"
entityids = set()

print("Created UDP socket {}".format(UDP_PORT))


def send(udpSocket, site=0, host=0, num=0):
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
    pdu.exerciseID = EXERCISE_ID

    memoryStream = BytesIO()
    outputStream = DataOutputStream(memoryStream)
    pdu.serialize(outputStream)
    data = memoryStream.getvalue()
    # while True:
    udpSocket.sendto(data, (DESTINATION_ADDRESS, UDP_PORT))
    # print(f"Killed {site} {host} {num}")
    # print("Sent {}. {} bytes".format(pdu.__class__.__name__, len(data)))
    # time.sleep(1)


def receive_pdu(udpSocket, exercise_id):
    """

    :param udp_port: int : port on which dis is transmitted
    :param exercise_id: int
    :return: bytes
    """

    data = udpSocket.recv(4096)

    try:
        current_pdu = createPdu(data)
    except:
        return

    if current_pdu is not None:
        if current_pdu.exerciseID == exercise_id:
            try:
                # entityids.add(current_pdu.entityID)
                if current_pdu.pduType != 1:
                    return
                send(udpSocket, current_pdu.entityID.siteID, current_pdu.entityID.applicationID,
                     current_pdu.entityID.entityID)
                print(f"Killed: {current_pdu.entityID.siteID}, {current_pdu.entityID.applicationID}, {current_pdu.entityID.entityID}, {current_pdu.marking}")
            except AttributeError:
                return


udp_port = 3000
udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
udpSocket.bind(("", udp_port))
udpSocket.settimeout(3)  # exit if we get nothing in this many seconds

while True:
    receive_pdu(udpSocket, EXERCISE_ID)
