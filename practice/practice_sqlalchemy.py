import sqlalchemy
import urllib.parse
import datetime

from collections import namedtuple
from sqlalchemy.orm import scoped_session, sessionmaker


def sql_engine(db: str):
    ***REMOVED***
    params = urllib.parse.quote_plus(conn_str)
    engine = sqlalchemy.create_engine("mssql+pyodbc:///?odbc_connect=%s" % params, pool_size=5_000, max_overflow=0)

    return engine



db = "GidonLSETest"

sql_engine = sql_engine(db)
sql_meta = sqlalchemy.MetaData(schema="dis")
session_factory = sessionmaker(bind=sql_engine)
Session = scoped_session(session_factory)

# play_stop = sqlalchemy.Table("PlayStopScenario", sql_meta, autoload_with=sql_engine)

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

play_stop = namedtuple("PlayStop", a[0].keys())

with Session() as session, session.begin():
    to_insert = [object(**x) for x in a]
    try:
        session.add_all(to_insert)
    except:
        session.rollback()
        raise
    else:
        session.commit()

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
