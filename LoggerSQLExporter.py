import datetime
import lzma
import xml.etree.ElementTree as ET

import sqlalchemy
from ***REMOVED***.Tools import sqlConn

import json


def translate_types(type_name):
    if type_name == "Int32":
        return sqlalchemy.Integer
    elif type_name == "Float64":
        return sqlalchemy.Float
    elif type_name == "ArrayByte":
        return sqlalchemy.NVARCHAR(400)
    elif type_name == "DateTime":
        return sqlalchemy.DateTime
    else:
        raise Exception(f"INVALID TYPE {type_name}")


def translate_data_from_hex_bytes(data, type_name):
    if type_name == "Int32":
        return int(data, base=16)
    elif type_name == "Float64":
        return float.fromhex(data)
    elif type_name == "ArrayByte":
        return bytes.fromhex(data).decode("utf-8").rstrip("\x00")
    else:
        raise Exception(f"Unrecognised type: {type_name}")


def get_table_data(event_reports_config):
    tree = ET.parse(event_reports_config)
    root = tree.getroot()

    tables = {"names": {}, "numbers": {}, "translations": {}}

    for report in root:
        # attrib["eventName"] is the name of the table
        # Every report has two children: DtFixed, and DtVAR, fixed is ints, var is strs
        table_name = report.attrib["eventName"]
        table_event_type = report.attrib["eventType"]
        tables["names"][table_name] = []
        tables["numbers"][table_event_type] = []
        tables["translations"][f"{table_event_type}"] = table_name

        for dt in report:
            for field in dt:
                tables["names"][table_name].append((field.tag, field.attrib["type"]))
                tables["numbers"][table_event_type].append((field.tag, field.attrib["type"]))

        # Constants that are in every table
        tables["names"][table_name].append(("SenderIdSite", "Int32"))
        tables["names"][table_name].append(("SenderIdHost", "Int32"))
        tables["names"][table_name].append(("SenderIdNum", "Int32"))
        tables["names"][table_name].append(("ReceiverIdSite", "Int32"))
        tables["names"][table_name].append(("ReceiverIdHost", "Int32"))
        tables["names"][table_name].append(("ReceiverIdNum", "Int32"))

        tables["names"][table_name].append(("WorldTime", "DateTime"))
        tables["names"][table_name].append(("PacketTime", "Float64"))
        tables["names"][table_name].append(("LoggerFile", "ArrayByte"))
        tables["names"][table_name].append(("ExportTime", "DateTime"))
        tables["names"][table_name].append(("ExerciseId", "Int32"))

        tables["numbers"][table_event_type].append(("SenderIdSite", "Int32"))
        tables["numbers"][table_event_type].append(("SenderIdHost", "Int32"))
        tables["numbers"][table_event_type].append(("SenderIdNum", "Int32"))
        tables["numbers"][table_event_type].append(("ReceiverIdSite", "Int32"))
        tables["numbers"][table_event_type].append(("ReceiverIdHost", "Int32"))
        tables["numbers"][table_event_type].append(("ReceiverIdNum", "Int32"))

        tables["numbers"][table_event_type].append(("WorldTime", "DateTime"))
        tables["numbers"][table_event_type].append(("PacketTime", "Float64"))
        tables["numbers"][table_event_type].append(("LoggerFile", "ArrayByte"))
        tables["numbers"][table_event_type].append(("ExportTime", "DateTime"))
        tables["numbers"][table_event_type].append(("ExerciseId", "Int32"))

    return tables


def create_tables(db, event_reports_config):
    conn = sqlConn(db)
    tables = get_table_data(event_reports_config)["names"]
    meta = sqlalchemy.MetaData(schema="dis")

    # "\\files\ExpData\Merkava4Barak2022\LoggerSQLExporter\BLPduEncoder.xml"
    for table in tables:
        current_table = sqlalchemy.Table(table, meta)

        for column in tables[table]:
            if column[0] == "ExportTime":
                current_table.append_column(sqlalchemy.Column(column[0], translate_types(column[1]), nullable=False))
            else:
                current_table.append_column(sqlalchemy.Column(column[0], translate_types(column[1])))

    meta.create_all(conn.engine)


def export_json(json_to_export, event_reports_config, logger_file_name, conn, meta):
    export_time = datetime.datetime.now()

    # Any EventReport not in the event_reports_config is irrelevant
    event_reports = get_table_data(event_reports_config)
    universal_fields = ["SenderIdSite", "SenderIdHost", "SenderIdNum", "ReceiverIdSite", "ReceiverIdHost",
                        "ReceiverIdNum", "WorldTime", "PacketTime", "LoggerFile", "ExportTime", "ExerciseId"]
    for packet in json_to_export:
        if "Event Report PDU" in packet.keys():
            current_event_report = packet["Event Report PDU"]["dis.event_type"]
            if current_event_report in event_reports["numbers"].keys():
                table_title = event_reports["translations"][f"{current_event_report}"]
                table_columns = event_reports["numbers"][f"{current_event_report}"]
                event_report_data = packet["Event Report PDU"]

                event_report_fields = [packet_field_name for packet_field_name in event_report_data if
                                       "Fixed" in packet_field_name or "Variable" in packet_field_name]

                data_to_insert = {}
                for i, column in enumerate(table_columns):
                    if column[0] not in universal_fields:
                        # Add the fields that are local to this event report to the dict
                        try:
                            if "Fixed" in event_report_fields[i]:
                                data_as_hex_bytes = event_report_data[event_report_fields[i]][
                                    "dis.fixed_datum_value"].replace(
                                    ':', '')
                            elif "Variable" in event_report_fields[i]:
                                data_as_hex_bytes = event_report_data[event_report_fields[i]][
                                    "dis.variable_datum_value"].replace(":", "")
                            else:
                                raise Exception(
                                    f"Event report field {event_report_fields[i]} does not match approved design!")
                            data_you_want = translate_data_from_hex_bytes(data_as_hex_bytes, column[1])
                            data_to_insert[column[0]] = data_you_want
                        except (IndexError, UnicodeDecodeError) as e:
                            print(e)
                            print("Event report fields: ", event_report_fields)
                            print("table columns: ", table_columns)
                            print(i, column)
                            # sys.exit()
                    else:
                        # Add the universal fields (SenderId, WorldTime, PacketTime, etc)
                        data_to_insert["SenderIdSite"] = event_report_data["Originating Entity ID"][
                            "dis.entity_id_site"]
                        data_to_insert["SenderIdHost"] = event_report_data["Originating Entity ID"][
                            "dis.entity_id_application"]
                        data_to_insert["SenderIdNum"] = event_report_data["Originating Entity ID"][
                            "dis.entity_id_entity"]

                        data_to_insert["ReceiverIdSite"] = event_report_data["Receiving Entity ID"][
                            "dis.entity_id_entity"]
                        data_to_insert["ReceiverIdHost"] = event_report_data["Receiving Entity ID"][
                            "dis.entity_id_application"]
                        data_to_insert["ReceiverIdNum"] = event_report_data["Receiving Entity ID"][
                            "dis.entity_id_entity"]

                        data_to_insert["ExerciseId"] = packet["Header"]["dis.exer_id"]
                        data_to_insert["ExportTime"] = export_time

                        data_to_insert["WorldTime"] = datetime.datetime.fromtimestamp(
                            float(packet["frame"]["WorldTime"]))
                        data_to_insert["PacketTime"] = packet["frame"]["PacketTime"]

                        data_to_insert["LoggerFile"] = logger_file_name

                sql_table = sqlalchemy.Table(table_title, meta, autoload_with=conn.engine)

                ins = sql_table.insert().values([data_to_insert])
                conn.execute(ins)

        elif "Entity State PDU" in packet.keys():
            pass
        elif list(packet.keys())[1] in ["Transmitter PDU", "Receiver PDU", "Data PDU", "Aggregate State PDU",
                                        "Signal PDU", 'Environmental Process PDU', 'Comment PDU', 'Detonation PDU',
                                        'Fire PDU']:
            pass
        else:
            print(f"Something weird here: {packet.keys()}")


create_tables("GidonLSETest", r"\\files\ExpData\Merkava4Barak2022\LoggerSQLExporter\BLPduEncoder.xml")

meta = sqlalchemy.MetaData(schema="dis")
conn = sqlConn("GidonLSETest")

with lzma.open("C:/Users/gidonr/Desktop/integration_1003_2.lzma", 'r') as f:
    data = f.read().decode("utf-8")[:-2] + ']'
    print("Loaded file")

json_data = json.loads(data)
print("Loaded JSON")
export_json(json_data, r"\\files\ExpData\Merkava4Barak2022\LoggerSQLExporter\BLPduEncoder.xml",
            "integration_1003_2.lgr", conn, meta)
