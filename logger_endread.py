import struct

from opendis.PduFactory import createPdu


def get_pdus_from_filepath(filepath):
    with open(filepath, 'rb') as f:
        byte_data = f.read().split(b', ')

    pdus = []

    for pdu_bytes in byte_data:
        if pdu_bytes != b'':
            try:
                pdu = createPdu(pdu_bytes)
                pdus.append(pdu)
            except struct.error:
                print("Struct error, skipping")
            except NameError as ne:
                print(ne)

    return pdus


# pdus = get_pdus_from_filepath(r'C:\Users\gidonr\Logger\logs\integration_0704_1.lzma')
pdus = get_pdus_from_filepath(r'C:\Users\gidonr\Logger\logs\uncompressed_test_1')
print(f"Ended. {len(pdus)} PDUs in loggerfile")
