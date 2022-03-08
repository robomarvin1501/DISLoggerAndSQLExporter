import lzma
import json

with lzma.open(r"C:\Users\gidonr\LoggerFiles\log_0303_1408.lzma", 'r') as f:
    data = f.read().decode("utf-8")  # change to stream

data = data[:-2] + ']'  # Removes the trailing comma

data = json.loads(data)  # Data is now a list of OrderedDicts of all the data

print(data[0])