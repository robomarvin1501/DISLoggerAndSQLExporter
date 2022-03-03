import lzma
import ast

with lzma.open(r"C:\Users\gidonr\LoggerFiles\compressed_output_lzma", 'r') as f:
    data = f.read().decode("utf-8")  # change to stream

data = ast.literal_eval(data)  # Data is now a list of dicts of all the data

