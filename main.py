from typing import Dict
import re


def get_best_mode(data):
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


def get_segment(data, mode):
    mode_segment = {"numeric": "0001", "alphanumeric": "0010", "byte": "0100"}[mode]

    data_segment = ''
    for char in data:
        char_bits = bin(ord(char))[2:].zfill(8)
        data_segment += char_bits

    char_count_segment = bin(len(data))[2:].zfill(8)
    terimator_segment = '0000'

    return mode_segment + char_count_segment + data_segment + terimator_segment


def main(data: str):
    mode = get_best_mode(data)
    segment = get_segment(data, mode)


if __name__ == '__main__':
    data = "Hello, world! 123"

    mode = get_best_mode(data)
    print('Best mode:', mode)

    segment = get_segment(data, mode)
    print('Data segment:', segment)
