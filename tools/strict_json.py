"""Load finite JSON without silently discarding duplicate object members."""
import json
import math


def _constant(value):
    raise ValueError(f'Non-JSON numeric constant: {value}')


def _float(value):
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f'JSON number exceeds finite range: {value}')
    return result


def _object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'Duplicate JSON object member: {key}')
        result[key] = value
    return result


def loads(text):
    return json.loads(text, parse_constant=_constant, parse_float=_float,
                      object_pairs_hook=_object)


def load(path):
    return loads(path.read_text(encoding='utf-8'))
