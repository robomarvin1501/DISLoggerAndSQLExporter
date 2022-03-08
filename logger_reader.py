import lzma
from utils.json_decoder import JSON_decoder

with lzma.open(r"C:\Users\gidonr\LoggerFiles\log_0303_1408.lzma", 'r') as f:
    data = f.read().decode("utf-8")  # change to stream

data = data[:-2] + ']'  # Removes the trailing comma
data = data.replace("'", '"')

data = JSON_decoder.decode(data)  # Data is now a list of OrderedDicts of all the data

print(data[0])