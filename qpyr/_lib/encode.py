import itertools
import re

from qpyr._lib.error_correction import add_ecc_and_interleave
from qpyr._lib.static import ECC_CODEWORDS_PER_BLOCK, NUM_ERROR_CORRECTION_BLOCKS
from qpyr._lib.utils import (
    bits_to_bytearray,
    bytearray_to_bits,
    get_num_raw_data_modules,
    get_segment_character_bits_length,
    get_total_data_capacity_bytes,
)


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
    data_segment = "".join([bin(x)[2:].zfill(8) for x in bytearray(data, "utf-8")])
    return data_segment


def get_segment_mode(mode):
    return {"numeric": "0001", "alphanumeric": "0010", "byte": "0100"}[mode]


def get_segment_character_count(data_segment: str, mode: str, version: int):
    result = ""
    no_of_bytes = len(data_segment) // 8
    if mode == "byte":
        if version <= 9:
            result = bin(no_of_bytes)[2:].zfill(8)
        else:
            result = bin(no_of_bytes)[2:].zfill(16)
    return result


def get_segment_terminator(data_segment: str, mode_segment: str, chr_count_segment: str) -> str:
    total_bits = len(data_segment) + len(mode_segment) + len(chr_count_segment)
    if total_bits % 8 == 4:
        return "0000"
    return ""


def combine_segments(segments: list[str]):
    return "".join(segments)


def get_best_version(data_segment: str, mode: str, ecl: str) -> int:
    total_mode_bits = 4
    bits_required = len(data_segment) + total_mode_bits

    for version in range(1, 41):
        total_capacity_bits = get_total_data_capacity_bytes(ecl, version) * 8
        segment_character_bits_length = get_segment_character_bits_length(mode, version)
        bits_required_total = bits_required + segment_character_bits_length

        if bits_required_total <= total_capacity_bits:
            return version
    raise ValueError("Data too long")


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


def encode(data: str, ecl: str):
    """Create a QR code from data.

    Args:
        data (str): data to encode
    """
    mode = get_best_mode(data)
    if mode != "byte":
        raise NotImplementedError("Only byte mode supported.")

    data_segment = get_segment_data(data)
    version = get_best_version(data_segment, mode, ecl)
    mode_segment = get_segment_mode(mode)
    chr_count_segment = get_segment_character_count(data_segment, mode, version)
    terminator_segment = get_segment_terminator(data_segment, mode_segment, chr_count_segment)
    segment = combine_segments([mode_segment, chr_count_segment, data_segment, terminator_segment])
    segment_with_padding = add_padding(segment, version, ecl)
    data_to_encode = bits_to_bytearray(segment_with_padding)
    encoded_data = add_ecc_and_interleave(version=version, ecl=ecl, data=data_to_encode)
    all_bits = bytearray_to_bits(encoded_data)

    return version, all_bits
