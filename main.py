from typing import Dict, List
import re

from reedsolo import RSCodec, ReedSolomonError


VERSION_CAPACITIES_BY_ECC_MAPPING = {
    "LOW": {
        # verion: (total_capacity, data_capacity, ecc_capacity)
        "1": (26, 19, 7),
        "2": (44, 34, 10),
        "3": (70, 55, 15),
        "4": (100, 80, 20),
        "5": (134, 108, 26),
    }
}

def _validate_ecc_level(ecc_level: str) -> str:
    supported_ecc_levels = VERSION_CAPACITIES_BY_ECC_MAPPING.keys()
    if ecc_level not in supported_ecc_levels:
        raise ValueError(f'Invalid ECC level. Must be one of {supported_ecc_levels}')
    return ecc_level
    

def _get_best_mode(data: str) -> str:
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


def _get_segment_data(data):
    data_segment = ''
    for char in data:
        char_bits = bin(ord(char))[2:].zfill(8)
        data_segment += char_bits
    return data_segment


def _get_segment_mode(mode):
    return {"numeric": "0001", "alphanumeric": "0010", "byte": "0100"}[mode]


def _get_segment_character_count(data):
    return bin(len(data))[2:].zfill(8)


def _get_segment_terminator() -> str:
    return '0000'


def _get_segment(segments: list[str]):
    return ''.join(segments)


def _get_best_version(segment: str, ecc_level: str) -> str:
    data_codewords = len(segment) // 8
    for version, capacities in VERSION_CAPACITIES_BY_ECC_MAPPING[ecc_level].items():
        data_capacity = capacities[1]
        if data_codewords <= data_capacity:
            return version
    raise ValueError('Data too long')


def _get_data_with_ecc_codewords(data: str, version: str, ecc_level: str):
    number_of_ecc_codewords = VERSION_CAPACITIES_BY_ECC_MAPPING[ecc_level][version][2]
    data_bytes = bytearray(data, encoding="utf-8")
    rsc = RSCodec(nsym=number_of_ecc_codewords)
    encoded_message = rsc.encode(data_bytes)
    return encoded_message


def _binary_str_to_hex(binary_str: str) -> str:
    """Splits binary string into 8-bit chunks and converts each chunk to hex."""
    result = []
    binary_str_split: List[str] = [binary_str[i:i+8] for i in range(0, len(binary_str), 8)]
    for binary_str in binary_str_split:
        first_4_bits = hex(int(binary_str[:4], 2))[2:]
        last_4_bits = hex(int(binary_str[4:], 2))[2:]
        result.append(first_4_bits + last_4_bits)
    return ' '.join(result)


def _get_ecc_codewords(data: str, version: str, ecc_level: str):
    pass


def main(data: str, ecc_level: str = 'LOW'):
    """Create a QR code from data.

    Args:
        data (str): data to encode
    """
    ecc_level = _validate_ecc_level(ecc_level)

    mode = _get_best_mode(data)
    print('Best mode:', mode)

    mode_segment = _get_segment_mode(mode)
    chr_count_segment = _get_segment_character_count(data)
    data_segment = _get_segment_data(data)
    terminator_segment = _get_segment_terminator()
    segment = _get_segment([mode_segment, chr_count_segment, data_segment, terminator_segment])
    print('Data segment:', segment, "\nhex:", _binary_str_to_hex(segment))

    version = _get_best_version(segment, ecc_level)
    print('Best version:', version)

    all_codewords = _get_data_with_ecc_codewords(data, version, ecc_level)
    print('ECC codewords:', all_codewords) # "\nhex:", _binary_str_to_hex(all_codewords)

    # segment_bytes = _to_bytes(segment)
    # print('Segment bytes:', segment_bytes)

    # hex_segment = _binary_to_hex(segment_bytes)
    # print('Hex segment:', hex_segment)


    # all_codewords_split = [all_codewords[i:i+8] for i in range(0, len(all_codewords), 8)]
    # print('Codewords split:', all_codewords_split)

    # for codeword in all_codewords_split:
    #     hex_data = _binary_to_hex(all_codewords_split)
    #     print('Hex data:', hex_data)


if __name__ == '__main__':
    data = "Hello, world! 123"
    # data = "Helloooo09daay"
    print('Data:', data)

    # tests
    assert _validate_ecc_level('LOW') == 'LOW'
    assert _get_best_mode("Hello, world! 123") == 'byte'
    assert _get_best_version("10101010"*43, "LOW") == "3"

    main(data, ecc_level='LOW') 
