import lzma

import sqlalchemy
from ***REMOVED***.Tools import sqlConn

from utils.sql_table_creation import create_tables

conn = sqlConn("GidonLSETest")
meta = sqlalchemy.MetaData(schema="dis")

create_tables(conn, r"\\files\ExpData\TomorrowsEdge2022A\LoggerSQLExporter\BLPduEncoder.xml")




with lzma.open("C:/Users/gidonr/Desktop/integration_1003_2.lzma", 'r') as f:
    data = f.read().decode("utf-8")[:-2] + ']'
    print("Loaded file")

# json_data = json.loads(data)
# print("Loaded JSON")

# export_json(json_data, r"\\files\ExpData\Merkava4Barak2022\LoggerSQLExporter\BLPduEncoder.xml",
#             "integration_1003_2.lgr", conn, meta)
