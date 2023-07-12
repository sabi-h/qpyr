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


if __name__ == '__main__':
    data = "omegaseed.co.uk"
    mode = get_best_mode(data)
    print('Best mode:', mode)
