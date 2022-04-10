import lzma

from opendis.PduFactory import createPdu

with lzma.open("logs/data_out.lzma", 'rb') as f:
    byte_data = f.read().split(b', ')

pdus = []

for pdu_bytes in byte_data:
    if pdu_bytes != b'':
        pdu = createPdu(pdu_bytes)
        pdus.append(pdu)

print(f"Ended. {len(pdus)} PDUs in loggerfile")
