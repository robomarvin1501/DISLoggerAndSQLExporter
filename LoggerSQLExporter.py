import datetime
import lzma

import json
import os
import sys
import struct
import logging
import threading
import time
import urllib.parse

import sqlalchemy

import opendis

from opendis.PduFactory import createPdu
***REMOVED***
***REMOVED***


def sql_engine(db: str):
    ***REMOVED***
    params = urllib.parse.quote_plus(conn_str)
    engine = sqlalchemy.create_engine("mssql+pyodbc:///?odbc_connect=%s" % params, pool_size=5_000, max_overflow=0)

    return engine


logging.basicConfig(filename="logger_exporter.log", encoding="utf-8", level=logging.DEBUG)


class Exporter:
    def __init__(self, table_name: str, sql_meta: sqlalchemy.MetaData, sql_engine: sqlalchemy.engine):
        self.table_name = table_name
        self.table = sqlalchemy.Table(table_name, sql_meta, autoload_with=sql_engine)
        self.sql_engine = sql_engine

        self.data = []

        self.lock = threading.Lock()
        threading.Thread(target=self.export, args=()).start()

    def add_data(self, data_to_add: list):
        self.data += data_to_add

    def export(self):
        # base_tables = ["EntityStateInts", "EntityStateLocations", "EntityStateTexts", "FirePdu", "DetonationPdu", "TransmitterPDU"]
        base_tables = ["EntityStateInts", "EntityStateLocations", "EntityStateTexts"]
        if len(self.data) == 0:
            if self.table_name in base_tables:
                print(f"No data in {self.table_name}")

            if threading.main_thread().is_alive():
                threading.Timer(1, self.export).start()

        else:
            with self.sql_engine.begin() as connection:
                with self.lock:
                    if self.table_name in base_tables:
                        uid = hash(datetime.datetime.now())
                        print(f"Exporting: {self.table_name}, pid={uid}")
                    connection.execute(self.table.insert(), self.data)
                    if self.table_name in base_tables:
                        print(f"Done: {self.table_name}, pid={uid}")
                    self.data = []

            threading.Thread(target=self.export, args=(), daemon=True).start()


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

    def interpret_logger_line(self, logger_line: bytes):
        """
        Unpacks a line received from the logger into the object
        :param logger_line: bytes : a line of bytes from the loggerfile
        These are the of the format : pdu_data, PacketTime, WorldTime
        """
        if logger_line.count(b"line_divider") == 2:
            split_line = logger_line.split(b"line_divider")
        else:
            raise ValueError(
                f"Given line of data does not contain enough seperators. Perhaps some data is missing: {logger_line}")
        try:
            self.pdu = createPdu(split_line[0])
        except struct.error as e:
            # logging.info(f"Incomplete pdu")
            # print(f"Error interpreting pdu: {e}")
            raise BytesWarning
        self.packet_time = struct.unpack("d", split_line[1])[0]  # struct.unpack always returns a tuple
        self.world_time = struct.unpack("d", split_line[2])[0]


class EventReportInterpreter:
    def __init__(self, pdu: LoggerPDU, pdu_encoder: dict):
        self.logger_pdu = pdu
        self.event_num = self.logger_pdu.pdu.eventType
        self.event_name = pdu_encoder[str(self.event_num)]["event_name"]

        self.pdu_encoder = pdu_encoder

        self.variable_data = {}
        self.fixed_data = {}
        self.base_data = {}

        self.interpret_pdu()

    def __str__(self):
        return f"{self.variable_data}\n{self.fixed_data}"

    def interpret_pdu(self):
        for var_data, data_name in zip(self.logger_pdu.pdu.variableDatums,
                                       self.pdu_encoder[str(self.event_num)]["VariableData"].keys()):
            # self.variable_data.append((data_name, [''.join(map(chr, var_data.variableData))]))
            self.variable_data[data_name] = ''.join(map(chr, var_data.variableData))

        for fixed_data, data_name, data_type in zip(self.logger_pdu.pdu.fixedDatums,
                                                    self.pdu_encoder[str(self.event_num)]["FixedData"].keys(),
                                                    self.pdu_encoder[str(self.event_num)]["FixedData"].values()):
            if data_type == "Float64":
                datum_as_hex = hex(fixed_data.fixedDatumValue)[2:]
                if datum_as_hex == '0':
                    datum_as_hex = "00000000"
                datum_as_bytes = bytes.fromhex(datum_as_hex)
                datum_as_float = struct.unpack("!f", datum_as_bytes)[0]

                # self.fixed_data.append((data_name, [datum_as_float]))
                self.fixed_data[data_name] = datum_as_float

            elif data_type == "Int32":
                # self.fixed_data.append((data_name, [fixed_data.fixedDatumValue]))
                self.fixed_data[data_name] = fixed_data.fixedDatumValue

        self._get_base_data()

    def _get_base_data(self):
        self.base_data["SenderIdSite"] = self.logger_pdu.pdu.originatingEntityID.siteID
        self.base_data["SenderIdHost"] = self.logger_pdu.pdu.originatingEntityID.applicationID
        self.base_data["SenderIdNum"] = self.logger_pdu.pdu.originatingEntityID.entityID

        self.base_data["ReceiverIdSite"] = self.logger_pdu.pdu.receivingEntityID.siteID
        self.base_data["ReceiverIdHost"] = self.logger_pdu.pdu.receivingEntityID.applicationID
        self.base_data["ReceiverIdNum"] = self.logger_pdu.pdu.receivingEntityID.entityID

        self.base_data["WorldTime"] = datetime.datetime.fromtimestamp(self.logger_pdu.world_time)
        self.base_data["PacketTime"] = self.logger_pdu.packet_time
        # Loggerfile, Export time, and exercise id are dealt by the LSE


class LoggerSQLExporter:
    """
    Exporter:
        A class with a buffer of data to export, which it does every time the buffer fills (say, 400 pieces?)
        Stores some things persistently, (eg SenderId -> MarkingText)

    """

    def __init__(self, logger_file: str, export_db: str, exercise_id: int, new_db: bool = False,
                 max_buffer_size: int = 400):
        if new_db:
            # Creates the Event Report tables when it's a new db. Can be run every time, but unnecessary
            ***REMOVED***()
            ***REMOVED***(export_db)

        self.pdu_encoder = None

        self.sql_engine = sql_engine(export_db)
        self.sql_meta = sqlalchemy.MetaData(schema="dis")

        self.logger_file = logger_file
        self.export_time = datetime.datetime.now()
        self.exercise_id = exercise_id

        self.sql_tables: dict[str, sqlalchemy.Table] = {
            "EntityStateInts": sqlalchemy.Table("EntityStateInts", self.sql_meta, autoload_with=self.sql_engine),
            "EntityStateLocations": sqlalchemy.Table("EntityStateLocations", self.sql_meta,
                                                     autoload_with=self.sql_engine),
            "EntityStateTexts": sqlalchemy.Table("EntityStateTexts", self.sql_meta, autoload_with=self.sql_engine),
            "FirePdu": sqlalchemy.Table("FirePdu", self.sql_meta, autoload_with=self.sql_engine),
            "DetonationPdu": sqlalchemy.Table("DetonationPdu", self.sql_meta, autoload_with=self.sql_engine),
            "TransmitterPDU": sqlalchemy.Table("TransmitterPDU", self.sql_meta, autoload_with=self.sql_engine),
        }

        self.exporters = {name: Exporter(name, self.sql_meta, self.sql_engine) for name in self.sql_tables.keys()}

        self.max_buffer_size = max_buffer_size

        self.entity_state_buffer = []

        self.read_encoder()

    def export(self, logger_pdu: LoggerPDU):
        pdu_type = type(logger_pdu.pdu)
        if pdu_type == opendis.dis7.EventReportPdu:
            if str(logger_pdu.pdu.eventType) not in self.pdu_encoder:
                return
            event_report = EventReportInterpreter(logger_pdu, self.pdu_encoder)
            self._export_event_report(event_report)
        else:
            if pdu_type == opendis.dis7.EntityStatePdu:
                # ent_state_start = time.perf_counter()
                self._export_entity_state(logger_pdu)
                # print(f"entity state: {time.perf_counter() - ent_state_start}")
            elif pdu_type == opendis.dis7.FirePdu:
                self._export_fire_pdu(logger_pdu)
            elif pdu_type == opendis.dis7.DetonationPdu:
                self._export_detonation_pdu(logger_pdu)
            elif pdu_type == opendis.dis7.TransmitterPdu:
                self._export_transmitter_pdu(logger_pdu)

    def read_encoder(self):
        encoder_subdir = max(os.listdir("encoders/"))
        with open(f"encoders/{encoder_subdir}/PduEncoder.json", 'r') as f:
            encoder = json.load(f)

        self.pdu_encoder = encoder

    def _export_event_report(self, event_report: EventReportInterpreter):
        # print(f"Exported event report: {event_report}")
        consistent_base_data = {
            "LoggerFile": self.logger_file,
            "ExportTime": self.export_time,
            "ExerciseId": self.exercise_id
        }

        data_to_insert = event_report.fixed_data | event_report.variable_data | event_report.base_data | \
                         consistent_base_data

        self._batch_dicts(event_report.event_name, [data_to_insert])

    def _export_entity_state(self, logger_pdu: LoggerPDU):
        base_data = {
            "SenderIdSite": logger_pdu.pdu.entityID.siteID,
            "SenderIdHost": logger_pdu.pdu.entityID.applicationID,
            "SenderIdNum": logger_pdu.pdu.entityID.entityID,

            "WorldTime": datetime.datetime.fromtimestamp(logger_pdu.world_time),
            "PacketTime": logger_pdu.packet_time,

            "LoggerFile": self.logger_file,
            "ExportTime": self.export_time,
            "ExerciseId": self.exercise_id
        }

        # Ints
        self._entity_state_ints(logger_pdu, base_data)
        # Locations
        self._entity_state_locs(logger_pdu, base_data)
        # Texts
        self._entity_state_texts(logger_pdu, base_data)

    def _entity_state_ints(self, logger_pdu: LoggerPDU, base_data: dict):
        # TODO discuss the removal of LifeformState, and Weapon2, along with potential adjustement of exported values to be inline with the DIS spec

        # Reversed for ease of indexing, since the documentation talks of bit 0, and that is the rightmost digit
        # in the non reversed number
        entity_appearance = bin(logger_pdu.pdu.entityAppearance)[2:][::-1]

        # Damage
        damage = int(entity_appearance[3:5], 2)
        entity_ints_damage = base_data | {
            "IntType": "Damage",
            "IntValue": damage
        }

        # Weapon1
        entity_ints_weapon1 = base_data | {
            "IntType": "Weapon1",
            "IntValue": logger_pdu.pdu.entityAppearance
        }

        # forceId
        entity_ints_forceid = base_data | {
            "IntType": "forceId",
            "IntValue": logger_pdu.pdu.forceId
        }

        overall_dicts = [entity_ints_damage, entity_ints_weapon1, entity_ints_forceid]

        self._batch_dicts("EntityStateInts", overall_dicts)

    def _entity_state_locs(self, logger_pdu: LoggerPDU, base_data: dict):
        entity_locs = base_data | {
            "GeoLocationX": logger_pdu.pdu.entityLocation.x,
            "GeoLocationY": logger_pdu.pdu.entityLocation.y,
            "GeoLocationZ": logger_pdu.pdu.entityLocation.z,

            "GeoVelocityX": logger_pdu.pdu.entityLinearVelocity.x,
            "GeoVelocityY": logger_pdu.pdu.entityLinearVelocity.y,
            "GeoVelocityZ": logger_pdu.pdu.entityLinearVelocity.z,

            "Psi": logger_pdu.pdu.entityOrientation.psi,
            "Theta": logger_pdu.pdu.entityOrientation.theta,
            "Phi": logger_pdu.pdu.entityOrientation.phi
        }

        self._batch_dicts("EntityStateLocations", [entity_locs])

    def _entity_state_texts(self, logger_pdu: LoggerPDU, base_data: dict):
        # MarkingText
        entity_texts_marking = base_data | {
            "TextType": "MarkingText",
            "TextValue": "".join(map(chr, logger_pdu.pdu.marking.characters))
        }

        # EntityType
        entity_type = logger_pdu.pdu.entityType
        entity_texts_type = base_data | {
            "TextType": "EntityType",
            "TextValue": f"{entity_type.entityKind}:{entity_type.domain}:{entity_type.country}:{entity_type.category}:{entity_type.subcategory}:{entity_type.specific}:{entity_type.extra}"
        }

        self._batch_dicts("EntityStateTexts", [entity_texts_marking, entity_texts_type])

    def _export_fire_pdu(self, logger_pdu: LoggerPDU):
        munition_type = logger_pdu.pdu.descriptor.munitionType

        firepdu = {
            "EventIdSite": logger_pdu.pdu.eventID.simulationAddress.site,
            "EventIdHost": logger_pdu.pdu.eventID.simulationAddress.application,
            "EventIdNum": logger_pdu.pdu.eventID.eventNumber,

            "AttackerIdSite": logger_pdu.pdu.firingEntityID.siteID,
            "AttackerIdHost": logger_pdu.pdu.firingEntityID.applicationID,
            "AttackerIdNum": logger_pdu.pdu.firingEntityID.entityID,

            "TargetIdSite": logger_pdu.pdu.targetEntityID.siteID,
            "TargetIdHost": logger_pdu.pdu.targetEntityID.applicationID,
            "TargetIdNum": logger_pdu.pdu.targetEntityID.entityID,

            "MunitionIdSite": logger_pdu.pdu.munitionExpendibleID.siteID,
            "MunitionIdHost": logger_pdu.pdu.munitionExpendibleID.applicationID,
            "MunitionIdNum": logger_pdu.pdu.munitionExpendibleID.entityID,

            "GeoLocationX": logger_pdu.pdu.locationInWorldCoordinates.x,
            "GeoLocationY": logger_pdu.pdu.locationInWorldCoordinates.y,
            "GeoLocationZ": logger_pdu.pdu.locationInWorldCoordinates.z,

            "GeoVelocityX": logger_pdu.pdu.velocity.x,
            "GeoVelocityY": logger_pdu.pdu.velocity.y,
            "GeoVelocityZ": logger_pdu.pdu.velocity.z,

            "MunitionType":
                f"{munition_type.entityKind}:{munition_type.domain}:{munition_type.country}:{munition_type.category}:{munition_type.subcategory}:{munition_type.specific}:{munition_type.extra}",

            "FuseType": logger_pdu.pdu.descriptor.fuse,
            "Quantity": logger_pdu.pdu.descriptor.quantity,
            "Range": logger_pdu.pdu.range,
            "WarheadType": logger_pdu.pdu.descriptor.warhead,

            "WorldTime": datetime.datetime.fromtimestamp(logger_pdu.world_time),
            "PacketTime": logger_pdu.packet_time,

            "LoggerFile": self.logger_file,
            "ExportTime": self.export_time,
            "ExerciseId": self.exercise_id
        }

        self._batch_dicts("FirePdu", [firepdu])

    def _export_detonation_pdu(self, logger_pdu: LoggerPDU):
        munition_type = logger_pdu.pdu.descriptor.munitionType

        detonation_pdu = {
            "EventIdSite": logger_pdu.pdu.eventID.simulationAddress.site,
            "EventIdHost": logger_pdu.pdu.eventID.simulationAddress.application,
            "EventIdNum": logger_pdu.pdu.eventID.eventNumber,

            "AttackerIdSite": logger_pdu.pdu.firingEntityID.siteID,
            "AttackerIdHost": logger_pdu.pdu.firingEntityID.applicationID,
            "AttackerIdNum": logger_pdu.pdu.firingEntityID.entityID,

            "TargetIdSite": logger_pdu.pdu.targetEntityID.siteID,
            "TargetIdHost": logger_pdu.pdu.targetEntityID.applicationID,
            "TargetIdNum": logger_pdu.pdu.targetEntityID.entityID,

            "MunitionIdSite": logger_pdu.pdu.explodingEntityID.siteID,
            "MunitionIdHost": logger_pdu.pdu.explodingEntityID.applicationID,
            "MunitionIdNum": logger_pdu.pdu.explodingEntityID.entityID,

            "GeoLocationX": logger_pdu.pdu.locationInWorldCoordinates.x,
            "GeoLocationY": logger_pdu.pdu.locationInWorldCoordinates.y,
            "GeoLocationZ": logger_pdu.pdu.locationInWorldCoordinates.z,

            "GeoVelocityX": logger_pdu.pdu.velocity.x,
            "GeoVelocityY": logger_pdu.pdu.velocity.y,
            "GeoVelocityZ": logger_pdu.pdu.velocity.z,

            "MunitionType":
                f"{munition_type.entityKind}:{munition_type.domain}:{munition_type.country}:{munition_type.category}:{munition_type.subcategory}:{munition_type.specific}:{munition_type.extra}",

            "FuseType": logger_pdu.pdu.descriptor.fuse,
            "Quantity": logger_pdu.pdu.descriptor.quantity,
            "WarheadType": logger_pdu.pdu.descriptor.warhead,

            "WorldTime": datetime.datetime.fromtimestamp(logger_pdu.world_time),
            "PacketTime": logger_pdu.packet_time,

            "LoggerFile": self.logger_file,
            "ExportTime": self.export_time,
            "ExerciseId": self.exercise_id
        }

        self._batch_dicts("DetonationPdu", [detonation_pdu])

    def _export_transmitter_pdu(self, logger_pdu: LoggerPDU):
        radio_entity_type = logger_pdu.pdu.radioEntityType

        transmitter_pdu = {
            "RadioID": logger_pdu.pdu.radioNumber,

            "RadioType":
                f"{radio_entity_type.entityKind}:{radio_entity_type.domain}:{radio_entity_type.country}:{radio_entity_type.category}:{radio_entity_type.subcategory}:{radio_entity_type.specific}:{radio_entity_type.extra}",

            "TransmitState": logger_pdu.pdu.transmitState,

            "InputSource": logger_pdu.pdu.inputSource,

            "AntennaLocationX": logger_pdu.pdu.antennaLocation.x,
            "AntennaLocationY": logger_pdu.pdu.antennaLocation.y,
            "AntennaLocationZ": logger_pdu.pdu.antennaLocation.z,

            "RelativeAntennaLocationX": logger_pdu.pdu.relativeAntennaLocation.x,
            "RelativeAntennaLocationY": logger_pdu.pdu.relativeAntennaLocation.y,
            "RelativeAntennaLocationZ": logger_pdu.pdu.relativeAntennaLocation.z,

            "AntennaPatternType": logger_pdu.pdu.antennaPatternType,

            "Frequency": logger_pdu.pdu.frequency,

            "TransmitFrequencyBandwidth": logger_pdu.pdu.transmitFrequencyBandwidth,

            "Power": logger_pdu.pdu.power,

            "SenderIdSite": logger_pdu.pdu.radioReferenceID.siteID,
            "SenderIdHost": logger_pdu.pdu.radioReferenceID.applicationID,
            "SenderIdNum": logger_pdu.pdu.radioReferenceID.entityID,

            "WorldTime": datetime.datetime.fromtimestamp(logger_pdu.world_time),
            "PacketTime": logger_pdu.packet_time,

            "LoggerFile": self.logger_file,
            "ExportTime": self.export_time,
            "ExerciseId": self.exercise_id
        }

        self._batch_dicts("TransmitterPDU", [transmitter_pdu])

    def _batch_dicts(self, table, d: list):
        try:
            self.exporters[table].add_data(d)
        except KeyError:
            self.exporters[table] = Exporter(table, self.sql_meta, self.sql_engine)
            self.exporters[table].add_data(d)

    def _thread_export(self, table: sqlalchemy.Table, data: list[dict], *args):
        with self.sql_engine.begin() as connection:
            connection.execute(table.insert(), data)


def load_file_data(logger_file: str, db_name: str, exercise_id: int, new_db=False, debug=False):
    if debug:
        errors = 0
        separator_errors = 0
        struct_unpack_errors = 0
        pdu_unpack_error = 0

    with lzma.open(f"logs/{logger_file}", 'r') as f:
        raw_data = f.read().split(b"line_separator")

        data = []
        logger_sql_exporter = LoggerSQLExporter(logger_file, db_name, exercise_id, new_db=new_db, max_buffer_size=400)

        total = len(raw_data)
        print(f"Start time: {datetime.datetime.now()}")
        print(f"Total packets: {len(raw_data):,}")
        for i, line in enumerate(raw_data):
            if i % 100_000 == 0:
                print(f"{i:,}")

            if line.count(b"line_divider") == 2:
                try:
                    logger_pdu = LoggerPDU(line)

                    # data.append(logger_pdu)

                    logger_sql_exporter.export(logger_pdu)

                except ValueError:
                    if debug:
                        errors += 1
                        separator_errors += 1
                    continue
                except BytesWarning:
                    if debug:
                        errors += 1
                        pdu_unpack_error += 1
                    continue
                except struct.error:
                    if debug:
                        errors += 1
                        struct_unpack_errors += 1
                    continue
                except KeyError:  # TODO Bad fix, there are event reports that are not wanted, so find a way to deal with them
                    continue
            else:
                if debug:
                    errors += 1
                    separator_errors += 1
                continue

        print("Loaded file")
    if debug:
        logging.info(f"Total pdus:              {total}")
        logging.info(f"Total errors:            {errors},               {100 * errors / total}%")
        logging.info(f"Seperator errors:        {separator_errors},     {100 * separator_errors / total}%")
        logging.info(f"Unpacking time errors:   {struct_unpack_errors}, {100 * struct_unpack_errors / total}%")
        logging.info(f"Unpacking pdu errors:    {pdu_unpack_error},     {100 * pdu_unpack_error / total}%")


if __name__ == "__main__":
    try:
        with open("DataExporterConfig.json", 'r') as f:
            config_data = json.load(f)
    except FileNotFoundError:
        print(r"""
            ERROR: No configuration file
            Please write a configuration file in the base folder by the name "DataExporterConfig.json"
            For examples, see \\files\docs\DataExporter\DataExporterConfig.json
        """)
        sys.exit()

    if config_data["logger_file"][-5:] != ".lzma":
        config_data["logger_file"] += ".lzma"

    exercise_id = config_data["exercise_id"]
    logger_file = config_data["logger_file"]
    db_name = config_data["database_name"]
    new_db = config_data["new_database"]

    start_time = time.perf_counter()
    load_file_data(logger_file, db_name, exercise_id, new_db=new_db)
    end_time = time.perf_counter()
    print(f"Execution time: {datetime.timedelta(seconds=(end_time - start_time))}")
