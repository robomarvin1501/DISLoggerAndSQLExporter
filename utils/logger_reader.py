import datetime
import lzma
import struct

import pytz
import sqlalchemy

import opendis

from opendis.PduFactory import createPdu


def get_int_value(pdu, int_type: str):
    if int_type == "forceId":
        return pdu.forceId
    elif int_type == "LifeFormState":
        return 0
    elif int_type == "Damage":
        return 0
    elif int_type == "Weapon1":
        return pdu.entityAppearance
    elif int_type == "Weapon1":
        return 0
    else:
        raise Exception(f"{int_type} is not a valid IntType!")



def export_pdu(pdu):
    meta = sqlalchemy.MetaData(schema="dis")  # , reflect=True
    if type(pdu) == opendis.dis7.EntityStatePdu:
        state_ints = sqlalchemy.Table("EntityStateInts", meta)
        state_locs = sqlalchemy.Table("EntityStateLocations", meta)
        state_texts = sqlalchemy.Table("EntityStateTexts", meta)

        # Remove to its own function for entity state

        # ints
        int_types = ["forceId", "LifeFormState", "Damage", "Weapon1", "Weapon2"]
        for int_type in int_types:
            ints_ins = state_ints.insert().values([
                {
                    "SenderIdSite": pdu.entityID.siteID,
                    "SenderIdHost": pdu.entityID.applicationID,
                    "SenderIdNum": pdu.entityID.entityID,

                    "IntType": int_type,
                    "IntValue": get_int_value(pdu, int_type),
                    "WorldTime": datetime.datetime.fromtimestamp(pdu.timestamp, tz=pytz.timezone("Asia/Jerusalem")),
                    # "PacketTime":

                }
            ])

        print("Entity State")


def get_pdus_from_filepath(filepath):
    with lzma.open(filepath, 'rb') as f:
        byte_data = f.read().split(b', ')

    pdus = []
    struct_errors = 0
    name_errors = 0

    for pdu_bytes in byte_data:
        if pdu_bytes != b'':
            try:
                pdu = createPdu(pdu_bytes)
                pdus.append(pdu)
            except struct.error:
                struct_errors += 1
            except NameError:
                name_errors += 1

    total_errors = struct_errors + name_errors
    total_data = len(pdus) + name_errors + struct_errors
    percent_error = (total_errors / total_data) * 100

    print(f"Error: {round(percent_error, 2)}%")

    return pdus


if __name__ == "__main__":
    pdus = get_pdus_from_filepath(r'C:\Users\gidonr\Logger\logs\integration_0704_1.lzma')
    for pdu in pdus:
        export_pdu(pdu)
    print(f"Ended. {len(pdus)} PDUs in loggerfile")
