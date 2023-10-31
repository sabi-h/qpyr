from typing import Callable
import math

from qrcode.custom_types import CoordinateValueMap


def bits_to_bytearray(bit_string):
    byte_array = bytearray()

    # Split the string into 8-bit chunks and convert to bytes
    for i in range(0, len(bit_string), 8):
        byte_chunk = bit_string[i : i + 8]
        byte = int(byte_chunk, 2)
        byte_array.append(byte)

    return byte_array


def bytearray_to_bits(byte_array):
    bit_string = ""
    for byte in byte_array:
        binary_representation = bin(byte)[2:]  # Remove the '0b' prefix
        padded_binary = binary_representation.zfill(8)  # Pad with zeros to make it 8 bits long
        bit_string += padded_binary
    return bit_string


def convert_to_version(grid_size):
    return int((grid_size - 17) / 4)


def convert_to_grid_size(version):
    return int(version * 4 + 17)


def get_masks():
    """
    Return the mask function for the given mask pattern_reference.
    """
    pattern_reference_map = [
        lambda i, j: (i + j) % 2 == 0,
        lambda i, j: i % 2 == 0,
        lambda i, j: j % 3 == 0,
        lambda i, j: (i + j) % 3 == 0,
        lambda i, j: (math.floor(i / 2) + math.floor(j / 3)) % 2 == 0,
        lambda i, j: (i * j) % 2 + (i * j) % 3 == 0,
        lambda i, j: ((i * j) % 2 + (i * j) % 3) % 2 == 0,
        lambda i, j: ((i * j) % 3 + (i + j) % 2) % 2 == 0,
    ]
    return pattern_reference_map


def adjacent_modules_penalty(grid_list):
    for row in grid_list:
        adjacent_tracker = []
        score = 0
        for value in row:
            pass


def get_mask_penalty_points(grid) -> int:
    grid_list = grid.tolist()
    adjacent_modules_penalty(grid_list)
    return 999999999


if __name__ == "__main__":
    assert isinstance(get_masks()[0], Callable)
    assert isinstance(get_masks()[7], Callable)

    masks = get_masks()
    assert masks[7](21, 21) == True
    assert masks[3](15, 14) == False
