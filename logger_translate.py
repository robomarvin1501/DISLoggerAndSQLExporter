import lzma
import pickle
from LoggerSQLExporter import LoggerPDU

# loggername = "exp_1_2102_2.lzma"
# with lzma.open(f"logs/{loggername}") as f:
#     print(f"Reading loggerfile: {loggername}")
#     raw_data = f.read().split(b"line_separator")[:-1]
#     print(f"Finished reading loggerfile: {loggername}")
#
# logger_pdus = []
# total_pdus = len(raw_data)
# with lzma.open(f"logs/{loggername}_pickle.lzma", "wb") as f:
#     for i, custom_pdu_bytes in enumerate(raw_data):
#         if i % 10_000 == 0:
#             print("{:,}/{:,}".format(i, total_pdus))
#         if custom_pdu_bytes == b'':
#             continue
#         try:
#             pdu = LoggerPDU(custom_pdu_bytes)
#             f.write(pickle.dumps(pdu) + b"line_separator")
#         except BytesWarning:
#             print("struct error")
#             continue
#         except ValueError:
#             print("seperator error")
#
# print("Dumped, exiting")

loggername = "exp_1_2102_2.lzma_pickle.lzma"
with lzma.open(f"logs/{loggername}") as f:
    print(f"Reading loggerfile: {loggername}")
    raw_data = f.read().split(b"line_separator")
    print(f"Finished reading loggerfile: {loggername}")

total_pdus = len(raw_data)
logger_pdus = []
for i, custom_pdu_bytes in enumerate(raw_data):

    for i, custom_pdu_bytes in enumerate(raw_data):
        if i % 10_000 == 0:
            print("{:,}/{:,}".format(i, total_pdus))
        if custom_pdu_bytes == b'':
            continue
        logger_pdus.append(pickle.loads(custom_pdu_bytes))
