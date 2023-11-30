import itertools
import re
from typing import Dict, List, NewType

from qrcode.custom_types import ECL
from qrcode.reedsolomon import _add_ecc_and_interleave, get_num_raw_data_modules
from qrcode.utils import bits_to_bytearray, bytearray_to_bits, get_data_codewords_per_short_block
from qrcode.static import ECC_CODEWORDS_PER_BLOCK, NUM_ERROR_CORRECTION_BLOCKS


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


def get_best_version(data_segment: str, ecl: str) -> int:
    bytes_required = len(data_segment) // 8
    for version in range(1, 41):
        capacity_per_block = get_data_codewords_per_short_block(ecl, version)
        num_blocks = NUM_ERROR_CORRECTION_BLOCKS[ecl][version]
        max_capacity = capacity_per_block * num_blocks
        if bytes_required <= max_capacity:
            return version
    raise ValueError("Data too long")


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


def add_padding(data: str, version: int, ecl: str) -> str:
    """Add padding to data segment.

    Args:
        data (str): data segment

    Returns:
        str: padded data segment
    """
    data_length = len(data)
    bit_padding_required = (8 - (data_length % 8)) % 8
    data = data + "0" * bit_padding_required

    total_num_of_codewords: int = get_num_raw_data_modules(version) // 8
    num_of_blocks = NUM_ERROR_CORRECTION_BLOCKS[ecl][version]
    blockecclen: int = ECC_CODEWORDS_PER_BLOCK[ecl][version]

    total_data_capacity = total_num_of_codewords - (blockecclen * num_of_blocks)
    redundant_bytes_required = ((total_data_capacity * 8) - len(data)) // 8

    padding_bytes = itertools.cycle(["11101100", "00010001"])
    for _ in range(redundant_bytes_required):
        data += next(padding_bytes)
    return data


def str_to_decimals(data: str) -> str:
    return " ".join(map(lambda x: str(ord(x)), data))


def binary_to_hex(binary_value: str) -> str:
    return hex(int(binary_value, 2))[2:]


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
    print(f"ECL: {ecl.value}")
    print(f"data: {data}", f"decimal: {str_to_decimals(data)}", f"hex: {str_to_hex(data)}", sep="\n")

    mode = get_best_mode(data)
    print(f"Best mode: {mode}")

    mode_segment = get_segment_mode(mode)
    chr_count_segment = get_segment_character_count(data)
    data_segment = get_segment_data(data)
    terminator_segment = get_segment_terminator()
    segment = get_segment([mode_segment, chr_count_segment, data_segment, terminator_segment])
    print(f"{segment=}")

    version = get_best_version(segment, ecl.value)
    print(f"Best version:", version)

    segment_with_padding = add_padding(segment, version, ecl.value)

    print(f"segment with padding: {segment_with_padding}")
    print(f"\nsegment pretty: {split_str_for_display(segment_with_padding, 8)}")
    print(f"\nsegment in hex: {split_str_for_display(binary_to_hex(segment_with_padding), 2)}")

    data_to_encode = bits_to_bytearray(segment_with_padding)
    print(f"\n{data_to_encode=}")

    encoded_data = _add_ecc_and_interleave(version=version, ecl=ecl.name, data=data_to_encode)
    print(f"\nDATA+ECC: {bytearray_to_binary(encoded_data)}")

    all_bits = bytearray_to_bits(encoded_data)
    return version, all_bits


if __name__ == "__main__":
    data = "Hello, world! 123Hello, world! 123Hello, world! 123Hello83nde"
    encode(data=data, ecl=ECL.H)
