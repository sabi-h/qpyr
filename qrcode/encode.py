import itertools
import re
from typing import Dict, List, NewType

from qrcode.custom_types import ECL
from qrcode.reedsolomon import _add_ecc_and_interleave
from qrcode.utils import bits_to_bytearray, bytearray_to_bits

VERSION_CAPACITIES_BY_ECC_MAPPING = {
    ECL.L: {
        # verion: (total capacity, data capacity, error correction capacity)
        "1": (26, 19, 7),
        "2": (44, 34, 10),
        "3": (70, 55, 15),
        "4": (100, 80, 20),
        "5": (134, 108, 26),
    },
    ECL.M: {
        "1": (26, 16, 10),
    },
    ECL.Q: {
        "1": (26, 13, 13),
    },
    ECL.H: {
        "1": (26, 9, 17),
    },
}


BinaryString = NewType("BinaryString", str)


def get_best_mode(data: str) -> str:
    numeric_regex: re.Pattern = re.compile(r"[0-9]*")
    alphanumeric_regex: re.Pattern = re.compile(r"[A-Z0-9 $%*+./:-]*")
    is_byte = lambda data: all(ord(char) < 256 for char in data)  # ISO-8859-1 characters

    if numeric_regex.fullmatch(data):
        return "numeric"
    elif alphanumeric_regex.fullmatch(data):
        return "alphanumeric"
    elif is_byte(data):
        return "byte"
    else:
        raise ValueError("Mode not supported")


def get_segment_data(data):
    data_segment = ""
    for char in data:
        char_bits = bin(ord(char))[2:].zfill(8)
        data_segment += char_bits
    return data_segment


def get_segment_mode(mode):
    return {"numeric": "0001", "alphanumeric": "0010", "byte": "0100"}[mode]


def get_segment_character_count(data):
    return bin(len(data))[2:].zfill(8)


def get_segment_terminator() -> str:
    return "0000"


def get_segment(segments: list[str]):
    return "".join(segments)


def get_best_version(data_segment: str, ecl: ECL) -> str:
    data_codewords = len(data_segment) // 8
    for version, capacities in VERSION_CAPACITIES_BY_ECC_MAPPING[ecl].items():
        data_capacity = capacities[1]
        if data_codewords <= data_capacity:
            return version
    raise ValueError("Data too long")


def get_number_of_ecc_codewords(version: str, ecl: ECL) -> int:
    return VERSION_CAPACITIES_BY_ECC_MAPPING[ecl][version][2]


def _binary_str_to_hex(binary_str: str) -> str:
    """Splits binary string into 8-bit chunks and converts each chunk to hex."""
    binary_str_split: List[str] = [binary_str[i : i + 8] for i in range(0, len(binary_str), 8)]
    hex_str = [hex(int(s, 2))[2:] for s in binary_str_split]
    return " ".join(hex_str)


def bytearray_to_binary(value: bytearray) -> str:
    return "".join(format(x, "08b") for x in value)


def message_to_decimals(msg: str) -> List[int]:
    data = []
    if all(map(lambda x: isinstance(x, str), msg)):
        function = ord
    elif all(map(lambda x: isinstance(x, int), msg)):
        function = int
    else:
        raise ValueError("Message must be an integer or strings, not mixed.")

    data = list(map(function, str(msg)))
    return data


def numbers_to_hex(data: List[int]) -> str:
    return " ".join(map(lambda x: hex(x)[2:], data))


def str_to_hex(data: str) -> str:
    return " ".join(map(lambda x: hex(ord(x))[2:], data))


def add_padding(data: str, version: str, ecl: ECL) -> str:
    """Add padding to data segment.

    Args:
        data (str): data segment
        version (str): QR code version
        ecl (str): error correction level

    Returns:
        str: padded data segment
    """
    data_length = len(data)
    bit_padding_required = (lambda x: (8 - (x % 8)) % 8)(data_length)
    data = data + "0" * bit_padding_required

    data_capacity = VERSION_CAPACITIES_BY_ECC_MAPPING[ecl][version][1]

    redundant_bytes_required = ((data_capacity * 8) - len(data)) // 8
    padding_bytes = itertools.cycle(["11101100", "00010001"])
    for _ in range(redundant_bytes_required):
        data += next(padding_bytes)
    return data


def str_to_decimals(data: str) -> str:
    return " ".join(map(lambda x: str(ord(x)), data))


def dec_to_binary(dec_value: int) -> str:
    return bin(dec_value)[2:].zfill(8)


def hex_to_binary(hex_value: str) -> str:
    return bin(int(hex_value, 16))[2:].zfill(8)


def binary_to_dec(binary_value: str) -> int:
    return int(binary_value, 2)


def binary_to_hex(binary_value: str) -> str:
    return hex(int(binary_value, 2))[2:]


def dec_to_hex(dec_value: int) -> str:
    return hex(dec_value)[2:]


def split_str_for_display(value: str, split_value: int) -> str:
    indices = [i * split_value for i in range(len(value) // split_value)]
    parts = [value[i:j] for i, j in zip(indices, indices[1:] + [None])]
    return " ".join(parts)


def split_binary_str(value: str, split_value: int = 8) -> list:
    indices = [i * split_value for i in range(len(value) // split_value)]
    parts = [value[i:j] for i, j in zip(indices, indices[1:] + [None])]
    return parts


def encode(data: str, ecl: ECL):
    """Create a QR code from data.

    Args:
        data (str): data to encode
    """
    data = str(data)
    print(f"data: {data}", f"decimal: {str_to_decimals(data)}", f"hex: {str_to_hex(data)}", sep="\n")

    mode = get_best_mode(data)
    print(f"Best mode: {mode}")

    mode_segment = get_segment_mode(mode)
    chr_count_segment = get_segment_character_count(data)
    data_segment = get_segment_data(data)
    version = get_best_version(data_segment, ecl)
    print(f"Best version:", version)

    terminator_segment = get_segment_terminator()
    segment = get_segment([mode_segment, chr_count_segment, data_segment, terminator_segment])
    segment = add_padding(segment, version, ecl)

    print(f"segment: {segment}")
    print(f"segment pretty: {split_str_for_display(segment, 8)}")
    print(f"segment in hex: {split_str_for_display(binary_to_hex(segment), 2)}")

    number_of_ecc_codewords = get_number_of_ecc_codewords(version, ecl)
    print(f"Number of ECC codewords: {number_of_ecc_codewords}")

    data_to_encode = bits_to_bytearray(segment)
    print(f"{data_to_encode=}")

    encoded_data = _add_ecc_and_interleave(version=int(version), ecl=ecl.name, data=data_to_encode)
    print(f"{bytearray_to_binary(encoded_data)=}")

    all_bits = bytearray_to_bits(encoded_data)
    return all_bits


if __name__ == "__main__":
    data = "hello"

    # tests
    assert get_best_mode("Hello, world! 123") == "byte"
    assert get_best_version("10101010" * 43, ECL.L) == "3"

    encode(data, ecl=ECL.M)
