import sqlalchemy
from ***REMOVED***.Tools import sqlConn
import datetime

conn = sqlConn("GidonLSETest")
meta = sqlalchemy.MetaData(schema="dis")  # , reflect=True

play_stop = sqlalchemy.Table("PlayStopScenario", meta, autoload_with=conn.engine)

ins = play_stop.insert().values([
    {"action": 1, "ScenarioName": "TestInsertion",
     "dateTime": datetime.datetime.fromisoformat("2022-02-09 10:53:05.000"), "SenderIdSite": 1,
     "SenderIdHost": 2, "SenderIdNum": 3, "ReceiverIdSite": 0, "ReceiverIdHost": 0, "ReceiverIdNum": 0,
     "WorldTime": datetime.datetime.fromisoformat("2022-02-09 10:53:05.000"), "PacketTime": 0.211234,
     "LoggerFile": "TestLogger.lgr",
     "ExportTime": datetime.datetime.fromisoformat("2022-02-09 10:53:15.000"), "ExerciseId": 97}])


print(ins)
conn.execute(ins)


# import sqlalchemy
# from ***REMOVED***.Tools import sqlConn
#
# conn = sqlConn("GidonLSETest")
#
# meta = sqlalchemy.MetaData(schema="dis")
#
# BarakScan = sqlalchemy.Table(
#     "BarakScan", meta,
#     sqlalchemy.Column("ScanSizeX", sqlalchemy.Float),
#     sqlalchemy.Column("ScanSizeY", sqlalchemy.Float),
#     sqlalchemy.Column("iteration", sqlalchemy.Integer),
#     sqlalchemy.Column("ScanID", sqlalchemy.Integer),
#     sqlalchemy.Column("RoleID", sqlalchemy.NVARCHAR(400))
# )
#
# meta.create_all(conn.engine)


# import lzma
# from utils.json_decoder import JSON_decoder
# import json
#
# with open("C:/Users/gidonr/Desktop/integration_2402_processed.json", 'wb') as fout:
#     lzc = lzma.LZMACompressor()
#
#     with open("C:/Users/gidonr/Desktop/integration_2402.json", 'r') as f:
#         current_file_contents = []
#
#         for packet in JSON_decoder.decode(f.read()):
#             try:
#                 current_file_contents.append(packet["_source"]["layers"]["dis"])
#             except KeyError:
#                 pass
#         file_as_string = json.dumps(current_file_contents)
#         file_as_string = file_as_string.replace("'", '"')
#         file_as_bytes = file_as_string.encode("utf-8")
#     fout.write(lzc.compress(file_as_bytes))
#     fout.write(lzc.flush())
