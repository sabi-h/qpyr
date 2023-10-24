from typing import Callable
import math

from qrcode.custom_types import CoordinateValueMap


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
