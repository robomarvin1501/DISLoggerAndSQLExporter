import json
from collections import OrderedDict


def make_unique(key, dct):
    counter = 0
    unique_key = key
    while unique_key in dct:
        counter += 1
        unique_key = f"{key}_{counter}"
    return unique_key


def parse_object_pairs(pairs):
    dct = OrderedDict()
    for key, value in pairs:
        if key in dct:
            key = make_unique(key, dct)
        dct[key] = value
    return dct


JSON_decoder = json.JSONDecoder(object_pairs_hook=parse_object_pairs)

