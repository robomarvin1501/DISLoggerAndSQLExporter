import sqlalchemy
import urllib.parse
import datetime

from sqlalchemy.orm import scoped_session, sessionmaker


def multi_test():
    play_stop = sqlalchemy.Table("PlayStopScenario", meta, autoload_with=conn.engine)

    ins = play_stop.insert().values([
        {"action": 1, "ScenarioName": "TestInsertion",
         "dateTime": datetime.datetime.fromisoformat("2022-02-09 10:53:05.000"), "SenderIdSite": 1,
         "SenderIdHost": 2, "SenderIdNum": 3, "ReceiverIdSite": 0, "ReceiverIdHost": 0, "ReceiverIdNum": 0,
         "WorldTime": datetime.datetime.fromisoformat("2022-02-09 10:53:05.000"), "PacketTime": 0.211234,
         "LoggerFile": "TestLogger.lgr",
         "ExportTime": datetime.datetime.fromisoformat("2022-02-09 10:53:15.000"), "ExerciseId": 97}])

db = "GidonLSETest"

***REMOVED***
params = urllib.parse.quote_plus(conn_str)

engine = sqlalchemy.create_engine(f"mssql+pyodbc:///?odbc_connect={params}")
meta = sqlalchemy.MetaData(schema="dis")


session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)


# conn = sqlConn("GidonLSETest")
# meta = sqlalchemy.MetaData(schema="dis")  # , reflect=True
#
# play_stop = sqlalchemy.Table("PlayStopScenario", meta, autoload_with=conn.engine)
#
# ins = play_stop.insert().values([
#     {"action": 1, "ScenarioName": "TestInsertion",
#      "dateTime": datetime.datetime.fromisoformat("2022-02-09 10:53:05.000"), "SenderIdSite": 1,
#      "SenderIdHost": 2, "SenderIdNum": 3, "ReceiverIdSite": 0, "ReceiverIdHost": 0, "ReceiverIdNum": 0,
#      "WorldTime": datetime.datetime.fromisoformat("2022-02-09 10:53:05.000"), "PacketTime": 0.211234,
#      "LoggerFile": "TestLogger.lgr",
#      "ExportTime": datetime.datetime.fromisoformat("2022-02-09 10:53:15.000"), "ExerciseId": 97}])
#
# print(ins)
# conn.execute(ins)