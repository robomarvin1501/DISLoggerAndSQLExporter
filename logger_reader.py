import lzma
import xml.etree.ElementTree as ET

with lzma.open(r"C:\Users\gidonr\LoggerFiles\compressed_output_lzma", 'r') as f:
    data = f.read().decode("utf-8")  # change to stream

data = ET.ElementTree(ET.fromstring(data))
