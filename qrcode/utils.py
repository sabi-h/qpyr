from typing import Callable
import math


def convert_to_version(grid_size):
    return int((grid_size - 17) / 4)


def convert_to_grid_size(version):
    return int(version * 4 + 17)


def get_mask_func(pattern_reference: int) -> Callable:
    """
    Return the mask function for the given mask pattern_reference.
    """
    pattern_reference_map = {
        0: lambda i, j: (i + j) % 2 == 0,  # 000
        1: lambda i, j: i % 2 == 0,  # 001
        2: lambda i, j: j % 3 == 0,  # 010
        3: lambda i, j: (i + j) % 3 == 0,  # 011
        4: lambda i, j: (math.floor(i / 2) + math.floor(j / 3)) % 2 == 0,  # 100
        5: lambda i, j: (i * j) % 2 + (i * j) % 3 == 0,  # 101
        6: lambda i, j: ((i * j) % 2 + (i * j) % 3) % 2 == 0,  # 110
        7: lambda i, j: ((i * j) % 3 + (i + j) % 2) % 2 == 0,  # 111
    }
    try:
        return pattern_reference_map[pattern_reference]
    except KeyError:
        raise ValueError(f"Invalid mask pattern_reference: {pattern_reference}")


if __name__ == "__main__":
    assert isinstance(get_mask_func(0), Callable)
    assert isinstance(get_mask_func(7), Callable)
    assert get_mask_func(7)(21, 21) == True
    assert get_mask_func(3)(15, 14) == False
