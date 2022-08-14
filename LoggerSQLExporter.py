import datetime
import lzma

import json
import os
import struct
import logging

import opendis

import pandas as pd

from ***REMOVED***.Tools import sqlConn

from opendis.PduFactory import createPdu
***REMOVED***
***REMOVED***

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
            self.variable_data[data_name] = [''.join(map(chr, var_data.variableData))]

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
                self.fixed_data[data_name] = [datum_as_float]

            elif data_type == "Int32":
                # self.fixed_data.append((data_name, [fixed_data.fixedDatumValue]))
                self.fixed_data[data_name] = [fixed_data.fixedDatumValue]

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
        self.pdu_encoder = None
        self.sql_conn = sqlConn(export_db)
        self.logger_file = logger_file
        self.export_time = datetime.datetime.now()
        self.exercise_id = exercise_id

        self.max_buffer_size = max_buffer_size

        self.entity_state_buffer = []

        self.read_encoder()

        if new_db:
            # Creates the Event Report tables when it's a new db. Can be run every time, but unnecessary
            ***REMOVED***()
            ***REMOVED***(export_db)

    def export(self, logger_pdu: LoggerPDU):
        pdu_type = type(logger_pdu.pdu)
        if pdu_type == opendis.dis7.EventReportPdu:
            event_report = EventReportInterpreter(logger_pdu, self.pdu_encoder)
            self._export_event_report(event_report)
        else:
            if pdu_type == opendis.dis7.EntityStatePdu:
                self._export_entity_state(logger_pdu)
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
        consistent_base_data = {"LoggerFile": self.logger_file, "ExportTime": self.export_time,
                                "ExerciseId": self.exercise_id}

        data_to_insert = event_report.fixed_data | event_report.variable_data | event_report.base_data | \
                         consistent_base_data

        data_df = pd.DataFrame(data_to_insert)

        data_df.to_sql(event_report.event_name, self.sql_conn, schema="dis", if_exists="append", index=False)

    def _export_entity_state(self, logger_pdu: LoggerPDU):
        base_data = {
            "SenderIdSite": [logger_pdu.pdu.entityID.siteID],
            "SenderIdHost": [logger_pdu.pdu.entityID.applicationID],
            "SenderIdNum": [logger_pdu.pdu.entityID.entityID],

            "WorldTime": [datetime.datetime.fromtimestamp(logger_pdu.world_time)],
            "PacketTime": [logger_pdu.packet_time],

            "LoggerFile": [self.logger_file],
            "ExportTime": [self.export_time],
            "ExerciseId": [self.exercise_id]
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
        entity_ints_damage = base_data.copy()
        damage = int(entity_appearance[3:5], 2)
        entity_ints_damage["IntType"] = ["Damage"]
        entity_ints_damage["IntValue"] = [damage]
        damage_df = pd.DataFrame(entity_ints_damage)

        # Weapon1
        entity_ints_weapon1 = base_data.copy()
        weapon1 = logger_pdu.pdu.entityAppearance
        entity_ints_weapon1["IntType"] = ["Weapon1"]
        entity_ints_weapon1["IntValue"] = [weapon1]
        weapon_df = pd.DataFrame(entity_ints_weapon1)

        # forceId
        entity_ints_forceid = base_data.copy()
        forceid = logger_pdu.pdu.forceId
        entity_ints_forceid["IntType"] = ["forceId"]
        entity_ints_forceid["IntValue"] = [forceid]
        forceid_df = pd.DataFrame(entity_ints_forceid)

        damage_df.to_sql("EntityStateInts", self.sql_conn, schema="dis", if_exists="append", index=False)
        weapon_df.to_sql("EntityStateInts", self.sql_conn, schema="dis", if_exists="append", index=False)
        forceid_df.to_sql("EntityStateInts", self.sql_conn, schema="dis", if_exists="append", index=False)

    def _entity_state_locs(self, logger_pdu: LoggerPDU, base_data: dict):
        entity_locs = base_data.copy()
        entity_locs["GeoLocationX"] = [logger_pdu.pdu.entityLocation.x]
        entity_locs["GeoLocationY"] = [logger_pdu.pdu.entityLocation.y]
        entity_locs["GeoLocationZ"] = [logger_pdu.pdu.entityLocation.z]

        entity_locs["GeoVelocityX"] = [logger_pdu.pdu.entityLinearVelocity.x]
        entity_locs["GeoVelocityY"] = [logger_pdu.pdu.entityLinearVelocity.y]
        entity_locs["GeoVelocityZ"] = [logger_pdu.pdu.entityLinearVelocity.z]

        entity_locs["Psi"] = [logger_pdu.pdu.entityOrientation.psi]
        entity_locs["Theta"] = [logger_pdu.pdu.entityOrientation.theta]
        entity_locs["Phi"] = [logger_pdu.pdu.entityOrientation.phi]

        locs_df = pd.DataFrame(entity_locs)
        locs_df.to_sql("EntityStateLocations", self.sql_conn, schema="dis", if_exists="append", index=False)

    def _entity_state_texts(self, logger_pdu: LoggerPDU, base_data: dict):
        # TODO discuss the "Entity" field, and if it is necessary since it's just "Added" and "Removed"

        # MarkingText
        entity_texts_marking = base_data.copy()
        entity_texts_marking["TextType"] = ["MarkingText"]
        entity_texts_marking["TextValue"] = ["".join(map(chr, logger_pdu.pdu.marking.characters))]
        marking_df = pd.DataFrame(entity_texts_marking)

        # EntityType
        entity_type = logger_pdu.pdu.entityType

        entity_texts_type = base_data.copy()
        entity_texts_type["TextType"] = ["EntityType"]
        entity_texts_type[
            "TextValue"] = [f"{entity_type.entityKind}:{entity_type.domain}:{entity_type.country}:{entity_type.category}:{entity_type.subcategory}:{entity_type.specific}:{entity_type.extra}"]
        type_df = pd.DataFrame(entity_texts_type)

        marking_df.to_sql("EntityStateTexts", self.sql_conn, schema="dis", if_exists="append", index=False)
        type_df.to_sql("EntityStateTexts", self.sql_conn, schema="dis", if_exists="append", index=False)

    def _export_fire_pdu(self, logger_pdu: LoggerPDU):
        munition_type = logger_pdu.pdu.descriptor.munitionType


        firepdu = {
            "EventIdSite": [logger_pdu.pdu.eventID.simulationAddress.site],
            "EventIdHost": [logger_pdu.pdu.eventID.simulationAddress.application],
            "EventIdNum": [logger_pdu.pdu.eventID.eventNumber],

            "AttackerIdSite": [logger_pdu.pdu.firingEntityID.siteID],
            "AttackerIdHost": [logger_pdu.pdu.firingEntityID.applicationID],
            "AttackerIdNum": [logger_pdu.pdu.firingEntityID.entityID],

            "TargetIdSite": [logger_pdu.pdu.targetEntityID.siteID],
            "TargetIdHost": [logger_pdu.pdu.targetEntityID.applicationID],
            "TargetIdNum": [logger_pdu.pdu.targetEntityID.entityID],

            "MunitionIdSite": [logger_pdu.pdu.munitionExpendibleID.siteID],
            "MunitionIdHost": [logger_pdu.pdu.munitionExpendibleID.applicationID],
            "MunitionIdNum": [logger_pdu.pdu.munitionExpendibleID.entityID],

            "GeoLocationX": [logger_pdu.pdu.locationInWorldCoordinates.x],
            "GeoLocationY": [logger_pdu.pdu.locationInWorldCoordinates.y],
            "GeoLocationZ": [logger_pdu.pdu.locationInWorldCoordinates.z],

            "GeoVelocityX": [logger_pdu.pdu.velocity.x],
            "GeoVelocityY": [logger_pdu.pdu.velocity.y],
            "GeoVelocityZ": [logger_pdu.pdu.velocity.z],

            "MunitionType": [f"{munition_type.entityKind}:{munition_type.domain}:{munition_type.country}:{munition_type.category}:{munition_type.subcategory}:{munition_type.specific}:{munition_type.extra}"],

            "FuseType": [logger_pdu.pdu.descriptor.fuse],
            "Quantity": [logger_pdu.pdu.descriptor.quantity],
            "Range": [logger_pdu.pdu.range],
            "WarheadType": [logger_pdu.pdu.descriptor.warhead],

            "WorldTime": [datetime.datetime.fromtimestamp(logger_pdu.world_time)],
            "PacketTime": [logger_pdu.packet_time],

            "LoggerFile": [self.logger_file],
            "ExportTime": [self.export_time],
            "ExerciseId": [self.exercise_id]
        }
        fire_df = pd.DataFrame(firepdu)

        fire_df.to_sql("FirePdu", self.sql_conn, schema="dis", if_exists="append", index=False)

    def _export_detonation_pdu(self, logger_pdu: LoggerPDU):
        munition_type = logger_pdu.pdu.descriptor.munitionType


        detonation_pdu = {
            "EventIdSite": [logger_pdu.pdu.eventID.simulationAddress.site],
            "EventIdHost": [logger_pdu.pdu.eventID.simulationAddress.application],
            "EventIdNum": [logger_pdu.pdu.eventID.eventNumber],

            "AttackerIdSite": [logger_pdu.pdu.firingEntityID.siteID],
            "AttackerIdHost": [logger_pdu.pdu.firingEntityID.applicationID],
            "AttackerIdNum": [logger_pdu.pdu.firingEntityID.entityID],

            "TargetIdSite": [logger_pdu.pdu.targetEntityID.siteID],
            "TargetIdHost": [logger_pdu.pdu.targetEntityID.applicationID],
            "TargetIdNum": [logger_pdu.pdu.targetEntityID.entityID],

            "MunitionIdSite": [logger_pdu.pdu.explodingEntityID.siteID],
            "MunitionIdHost": [logger_pdu.pdu.explodingEntityID.applicationID],
            "MunitionIdNum": [logger_pdu.pdu.explodingEntityID.entityID],

            "GeoLocationX": [logger_pdu.pdu.locationInWorldCoordinates.x],
            "GeoLocationY": [logger_pdu.pdu.locationInWorldCoordinates.y],
            "GeoLocationZ": [logger_pdu.pdu.locationInWorldCoordinates.z],

            "GeoVelocityX": [logger_pdu.pdu.velocity.x],
            "GeoVelocityY": [logger_pdu.pdu.velocity.y],
            "GeoVelocityZ": [logger_pdu.pdu.velocity.z],

            "MunitionType": [f"{munition_type.entityKind}:{munition_type.domain}:{munition_type.country}:{munition_type.category}:{munition_type.subcategory}:{munition_type.specific}:{munition_type.extra}"],

            "FuseType": [logger_pdu.pdu.descriptor.fuse],
            "Quantity": [logger_pdu.pdu.descriptor.quantity],
            "WarheadType": [logger_pdu.pdu.descriptor.warhead],

            "WorldTime": [datetime.datetime.fromtimestamp(logger_pdu.world_time)],
            "PacketTime": [logger_pdu.packet_time],

            "LoggerFile": [self.logger_file],
            "ExportTime": [self.export_time],
            "ExerciseId": [self.exercise_id]
        }
        detonation_df = pd.DataFrame(detonation_pdu)

        detonation_df.to_sql("DetonationPdu", self.sql_conn, schema="dis", if_exists="append", index=False)

    def _export_transmitter_pdu(self, logger_pdu: LoggerPDU):
        radio_entity_type = logger_pdu.pdu.radioEntityType

        transmitter_pdu = {
            "RadioID": [logger_pdu.pdu.radioNumber],

            "RadioType": [f"{radio_entity_type.entityKind}:{radio_entity_type.domain}:{radio_entity_type.country}:{radio_entity_type.category}:{radio_entity_type.subcategory}:{radio_entity_type.specific}:{radio_entity_type.extra}"],

            "TransmitState": [logger_pdu.pdu.transmitState],

            "InputSource": [logger_pdu.pdu.inputSource],

            "AntennaLocationX": [logger_pdu.pdu.antennaLocation.x],
            "AntennaLocationY": [logger_pdu.pdu.antennaLocation.y],
            "AntennaLocationZ": [logger_pdu.pdu.antennaLocation.z],

            "RelativeAntennaLocationX": [logger_pdu.pdu.relativeAntennaLocation.x],
            "RelativeAntennaLocationY": [logger_pdu.pdu.relativeAntennaLocation.y],
            "RelativeAntennaLocationZ": [logger_pdu.pdu.relativeAntennaLocation.z],

            "AntennaPatternType": [logger_pdu.pdu.antennaPatternType],

            "Frequency": [logger_pdu.pdu.frequency],

            "TransmitFrequencyBandwidth": [logger_pdu.pdu.transmitFrequencyBandwidth],

            "Power": [logger_pdu.pdu.power],

            "SenderIdSite": [logger_pdu.pdu.radioReferenceID.siteID],
            "SenderIdHost": [logger_pdu.pdu.radioReferenceID.applicationID],
            "SenderIdNum": [logger_pdu.pdu.radioReferenceID.entityID],

            "WorldTime": [datetime.datetime.fromtimestamp(logger_pdu.world_time)],
            "PacketTime": [logger_pdu.packet_time],

            "LoggerFile": [self.logger_file],
            "ExportTime": [self.export_time],
            "ExerciseId": [self.exercise_id]
        }

        transmitter_df = pd.DataFrame(transmitter_pdu)

        transmitter_df.to_sql("TransmitterPDU", self.sql_conn, schema="dis", if_exists="append", index=False)


def load_file_data(logger_file: str, db_name: str, exercise_id: int, new_db=False, debug=False):
    if debug:
        errors = 0
        separator_errors = 0
        struct_unpack_errors = 0
        pdu_unpack_error = 0

    with lzma.open(f"logs/{logger_file}", 'r') as f:
        raw_data = f.read().split(b"line_separator")

        data = []
        logger_sql_exporter = LoggerSQLExporter(logger_file, db_name, exercise_id, new_db=new_db)

        total = len(raw_data)
        print(f"Total packets: {len(raw_data):,}")
        for i, line in enumerate(raw_data):
            if i % 100_000 == 0:
                print(f"{i:,}")
            if line.count(b"line_divider") == 2:
                try:
                    logger_pdu = LoggerPDU(line)

                    data.append(logger_pdu)
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

        # data = [LoggerPDU(logger_line) for logger_line in raw_data]
        # l_pdus = convert_to_pdus(data)
        print("Loaded file")
    if debug:
        logging.info(f"Total pdus:              {total}")
        logging.info(f"Total errors:            {errors},               {100 * errors / total}%")
        logging.info(f"Seperator errors:        {separator_errors},     {100 * separator_errors / total}%")
        logging.info(f"Unpacking time errors:   {struct_unpack_errors}, {100 * struct_unpack_errors / total}%")
        logging.info(f"Unpacking pdu errors:    {pdu_unpack_error},     {100 * pdu_unpack_error / total}%")


if __name__ == "__main__":
    load_file_data("exp_0_1807_3.lzma", "GidonLSETest", 97, new_db=True)
