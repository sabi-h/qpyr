from typing import Dict
import re


def _get_best_mode(data):
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


def _get_segment_terimator():
    return '0000'


def _get_segment(segments: list[str]):
    return ''.join(segments)


def _get_best_version(segment: str):
    version_capacity_mapping = {
        # version: ecl_M_capacities
        "1": 16,
        "2": 28,
        "3": 44,
        "4": 64,
        "5": 86,
    }

    number_of_codewords = len(segment) // 8
    print("number of codewords:", number_of_codewords)

    for version, capacity in version_capacity_mapping.items():
            if number_of_codewords <= capacity:
                print(version)
                return version
    raise ValueError('Data too long')


def main(data: str):
    """Create a QR code from data.

    Args:
        data (str): data to encode
        error_correction_level (str, optional): can be 'L', 'M', 'Q' or 'H'. Defaults to 'L'.
    """
    mode = _get_best_mode(data)
    print('Best mode:', mode)

    mode_segment = _get_segment_mode(mode)
    chr_count_segment = _get_segment_character_count(data)
    data_segment = _get_segment_data(data)
    terimator_segment = _get_segment_terimator()
    segment = _get_segment([mode_segment, chr_count_segment, data_segment, terimator_segment])
    print('Data segment:', segment)

    version = _get_best_version(segment)
    print('Best version:', version)



if __name__ == '__main__':
    data = "Hello, world! 123"
    print('Data:', data)

    # tests
    assert _get_best_mode("Hello, world! 123") == 'byte'
    assert _get_best_version("10101010"*43) == "3"

    main(data) 
