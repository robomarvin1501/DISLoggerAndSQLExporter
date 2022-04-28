import lzma
import struct

from opendis.PduFactory import createPdu


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
    print(f"Ended. {len(pdus)} PDUs in loggerfile")
