import binascii
import re
from typing import Dict, List

from reedsolo import ReedSolomonError, RSCodec
import reedsolomon as rs


VERSION_CAPACITIES_BY_ECC_MAPPING = {
    "LOW": {
        # verion: (total_capacity, data_capacity, ecc_capacity)
        "1": (26, 19, 7),
        "2": (44, 34, 10),
        "3": (70, 55, 15),
        "4": (100, 80, 20),
        "5": (134, 108, 26),
    },
    "HIGH": {
        # verion: (total_capacity, data_capacity, ecc_capacity)
        "1": (26, 7, 19),
    }
}

def validate_ecc_level(ecc_level: str) -> str:
    supported_ecc_levels = VERSION_CAPACITIES_BY_ECC_MAPPING.keys()
    if ecc_level not in supported_ecc_levels:
        raise ValueError(f'Invalid ECC level. Must be one of {supported_ecc_levels}')
    return ecc_level
    

def get_best_mode(data: str) -> str:
    numeric_regex: re.Pattern = re.compile(r"[0-9]*")
    alphanumeric_regex: re.Pattern = re.compile(r"[A-Z0-9 $%*+./:-]*")
    is_byte = lambda data: all(ord(char) < 256 for char in data) # ISO-8859-1 characters

    if numeric_regex.fullmatch(data):
        return 'numeric'
    elif alphanumeric_regex.fullmatch(data):
        return 'alphanumeric'
    elif is_byte(data):
        return 'byte'
    else:
        raise ValueError('Mode not supported')


def get_segment_data(data):
    data_segment = ''
    for char in data:
        char_bits = bin(ord(char))[2:].zfill(8)
        data_segment += char_bits
    return data_segment


def get_segment_mode(mode):
    return {"numeric": "0001", "alphanumeric": "0010", "byte": "0100"}[mode]


def get_segment_character_count(data):
    return bin(len(data))[2:].zfill(8)


def get_segment_terminator() -> str:
    return '0000'


def get_segment(segments: list[str]):
    return ''.join(segments)


def get_best_version(data_segment: str, ecc_level: str) -> str:
    data_codewords = len(data_segment) // 8
    for version, capacities in VERSION_CAPACITIES_BY_ECC_MAPPING[ecc_level].items():
        data_capacity = capacities[1]
        if data_codewords <= data_capacity:
            return version
    raise ValueError('Data too long')


def get_number_of_ecc_codewords(version: str, ecc_level: str):
    return VERSION_CAPACITIES_BY_ECC_MAPPING[ecc_level][version][2]


def _binary_str_to_hex(binary_str: str) -> str:
    """Splits binary string into 8-bit chunks and converts each chunk to hex."""
    binary_str_split: List[str] = [binary_str[i:i+8] for i in range(0, len(binary_str), 8)]
    hex_str = [hex(int(s, 2))[2:] for s in binary_str_split]
    return ' '.join(hex_str)


def bytearray_to_binary(value: bytearray) -> str:
    return ''.join(format(x, '08b') for x in value)


def message_to_decimals(msg: str) -> List[int]:
	data = []
	if all(map(lambda x: isinstance(x, str), msg)):
		function = ord
	elif all(map(lambda x: isinstance(x, int), msg)):
		function = int
	else:
		raise ValueError("Message must be a list of integers or a list of strings")
	
	data = list(map(function, str(msg)))
	return data


def numbers_to_hex(data: List[int]) -> str:
    return " ".join(map(lambda x: hex(x)[2:], data))


def str_to_hex(data: str) -> str:
    return " ".join(map(lambda x: hex(ord(x))[2:], data))


def str_to_decimals(data: str) -> str:
    return " ".join(map(lambda x: str(ord(x)), data))


def main(data: str, ecc_level: str = 'LOW'):
    """Create a QR code from data.

    Args:
        data (str): data to encode
    """
    data = str(data)
    print(
        f'data: {data}',
        f'decimal: {str_to_decimals(data)}',
        f'hex: {str_to_hex(data)}',
        sep='\n'
    )
    ecc_level = validate_ecc_level(ecc_level)

    mode = get_best_mode(data)
    print('Best mode:', mode)

    mode_segment = get_segment_mode(mode)
    chr_count_segment = get_segment_character_count(data)
    data_segment = get_segment_data(data)
    terminator_segment = get_segment_terminator()
    segment = get_segment([mode_segment, chr_count_segment, data_segment, terminator_segment])
    print('Data segment:', segment)

    version = get_best_version(data_segment, ecc_level)
    print('Best version:', version)

    data_in_numeric = message_to_decimals(data)
    number_of_ecc_codewords = get_number_of_ecc_codewords(version, ecc_level)
    all_codewords = rs.encode(data_in_numeric, number_of_ecc_codewords)
    print(f'data in numeric: {data_in_numeric}, ECC codewords: {all_codewords}')


if __name__ == '__main__':
    data = "wpp.com"

    # tests
    assert validate_ecc_level('LOW') == 'LOW'
    assert get_best_mode("Hello, world! 123") == 'byte'
    assert get_best_version("10101010"*43, "LOW") == "3"

    main(data, ecc_level='HIGH')
