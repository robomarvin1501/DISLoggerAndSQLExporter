import lzma

import json
import struct
import logging

import opendis

import sqlalchemy
from ***REMOVED***.Tools import sqlConn

from opendis.PduFactory import createPdu
from utils.sql_table_creation import create_tables

conn = sqlConn("GidonLSETest")
meta = sqlalchemy.MetaData(schema="dis")

# create_tables(conn, r"\\files\ExpData\TomorrowsEdge2022A\LoggerSQLExporter\BLPduEncoder.xml")

logging.basicConfig(filename="logger_exporter.log", encoding="utf-8", level=logging.DEBUG)


def check_for(data, host: str, num: str, site: str = '1'):
    out = set()
    for i, p in enumerate(data):
        if type(p) == opendis.dis7.EntityStatePdu:
            if p.entityID.applicationID == host and \
                    p.entityID.entityID == num:
                out.add((i, p.entityID))
    return out


def get_names(data):
    out = set()
    for p in data:
        if type(p) == opendis.dis7.EntityStatePdu:
            out.add((''.join(map(chr, p.marking.characters)),
                     str(p.entityID)))
    return out


def convert_to_pdus(l_data: list[bytes]):
    pdus = []
    n_failures = 0
    for i, p in enumerate(l_data):
        try:
            pdus.append(createPdu(p))
        except struct.error:
            # print(f"Possibly incomplete packet of bytes at position {i}/{len(l_data) - 1}")
            logging.info(f"Possibly incomplete packet of bytes at position {i}/{len(l_data) - 1}")
            n_failures += 1
    logging.warning(f"Total number of failed packages: {n_failures}/{len(l_data)} : {100 * n_failures / len(l_data)}%")

    return pdus


class LoggerPDU:
    """
    Contains any given PDU in the PDU field, along with PacketTime, and WorldTime data
    """

    def __init__(self, logger_line):
        """
        :param logger_line: bytes : a line of bytes from the loggerfile
        These are the of the format : pdu_data, PacketTime, WorldTime
        """
        self.pdu = None
        self.packet_time = 0.0
        self.world_time = 0.0

        self.interpret_logger_line(logger_line)

    def interpret_logger_line(self, logger_line):
        """
        Unpacks a line received from the logger into the object
        :param logger_line: bytes : a line of bytes from the loggerfile
        These are the of the format : pdu_data, PacketTime, WorldTime
        """
        split_line = logger_line.split(b", ")
        self.pdu = createPdu(split_line[0])
        self.packet_time = struct.unpack("d", split_line[1])[0]  # struct.unpack always returns a tuple
        self.world_time = struct.unpack("d", split_line[2])[0]


with lzma.open("logs/test.lzma", 'r') as f:
    # data = f.read().decode("utf-8")[:-2] + ']'
    # data = f.read().split(b', ')
    raw_data = f.read()
    data = [LoggerPDU(logger_line) for logger_line in f.read().split(b"\n")]
    # l_pdus = convert_to_pdus(data)
    print("Loaded file")

# with lzma.open("C:/Users/gidonr/Desktop/integration_1003_2.lzma", 'r') as f:
#     data = f.read().decode("utf-8")[:-2] + ']'
#     print("Loaded file")
#     j_data = json.loads(data)
#     check_for(j_data, '8643', '208')
# json_data = json.loads(data)
# print("Loaded JSON")

# export_json(json_data, r"\\files\ExpData\Merkava4Barak2022\LoggerSQLExporter\BLPduEncoder.xml",
#             "integration_1003_2.lgr", conn, meta)
