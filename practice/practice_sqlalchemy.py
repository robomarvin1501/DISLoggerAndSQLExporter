import sqlalchemy
import urllib.parse
import datetime

from sqlalchemy.orm import scoped_session, sessionmaker

from ***REMOVED***.Tools import sqlConn

db = "GidonLSETest"

# ***REMOVED***
# params = urllib.parse.quote_plus(conn_str)

# engine = sqlalchemy.create_engine(f"mssql+pyodbc:///?odbc_connect={params}")
conn = sqlConn(db)
meta = sqlalchemy.MetaData(schema="dis")

play_stop = sqlalchemy.Table("PlayStopScenario", meta, autoload_with=conn.engine)


a = [
    {
        "action": 1,
        "ScenarioName": "TestInsertion",
        "dateTime": datetime.datetime.fromisoformat("2022-02-09 10:53:05.000"),
        "SenderIdSite": 1,
        "SenderIdHost": 2,
        "SenderIdNum": 3,
        "ReceiverIdSite": 0,
        "ReceiverIdHost": 0,
        "ReceiverIdNum": 0,
        "WorldTime": datetime.datetime.fromisoformat("2022-02-09 10:53:05.000"),
        "PacketTime": 0.211234,
        "LoggerFile": "TestLogger.lgr",
        "ExportTime": datetime.datetime.fromisoformat("2022-02-09 10:53:15.000"),
        "ExerciseId": 97
    }, {
        "action": 0,
        "ScenarioName": "TestInsertion",
        "dateTime": datetime.datetime.fromisoformat("2022-02-09 10:53:10.000"),
        "SenderIdSite": 1,
        "SenderIdHost": 2,
        "SenderIdNum": 3,
        "ReceiverIdSite": 0,
        "ReceiverIdHost": 0,
        "ReceiverIdNum": 0,
        "WorldTime": datetime.datetime.fromisoformat("2022-02-09 10:53:10.000"),
        "PacketTime": 10.211234,
        "LoggerFile": "TestLogger.lgr",
        "ExportTime": datetime.datetime.fromisoformat("2022-02-09 10:53:15.000"),
        "ExerciseId": 97
    }
]

b = {"action": [1, 0], "ScenarioName": ["TestInsertion", "TestInsertion"],
     "dateTime": [datetime.datetime.fromisoformat("2022-02-09 10:53:05.000"),
                  datetime.datetime.fromisoformat("2022-02-09 10:53:10.000")], "SenderIdSite": [1, 1],
     "SenderIdHost": [2, 2], "SenderIdNum": [3, 3], "ReceiverIdSite": [0, 0], "ReceiverIdHost": [0, 0],
     "ReceiverIdNum": [0, 0],
     "WorldTime": [datetime.datetime.fromisoformat("2022-02-09 10:53:05.000"),
                   datetime.datetime.fromisoformat("2022-02-09 10:53:10.000")], "PacketTime": [0.211234, 0.211234],
     "LoggerFile": ["TestLogger.lgr", "TestLogger.lgr"],
     "ExportTime": [datetime.datetime.fromisoformat("2022-02-09 10:53:15.000"),
                    datetime.datetime.fromisoformat("2022-02-09 10:53:15.000")], "ExerciseId": [97, 97]}

ins = play_stop.insert().values(a)


print(ins)
conn.execute(ins)

# session_factory = sessionmaker(bind=engine)
# Session = scoped_session(session_factory)
#

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
