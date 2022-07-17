import lzma

import json
import struct

import opendis

import sqlalchemy
from ***REMOVED***.Tools import sqlConn

from opendis.PduFactory import createPdu
from utils.sql_table_creation import create_tables

conn = sqlConn("GidonLSETest")
meta = sqlalchemy.MetaData(schema="dis")

create_tables(conn, r"\\files\ExpData\TomorrowsEdge2022A\LoggerSQLExporter\BLPduEncoder.xml")


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
    for i, p in enumerate(l_data):
        try:
            pdus.append(createPdu(p))
        except struct.error:
            print(f"Possibly incomplete packet of bytes at position {i}/{len(l_data) - 1}")

    return pdus


with lzma.open("logs/integration_0704_1.lzma", 'r') as f:
    # data = f.read().decode("utf-8")[:-2] + ']'
    data = f.read().split(b', ')
    l_pdus = convert_to_pdus(data)
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
