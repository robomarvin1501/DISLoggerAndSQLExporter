import xml.etree.ElementTree as ET

import sqlalchemy


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


def create_tables(sql_conn, event_reports_config):
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

    meta.create_all(sql_conn.engine)
