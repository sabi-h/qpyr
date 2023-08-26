import numpy as np
from numpy.typing import NDArray


def get_empty_grid(size: int = 21):
    grid = np.zeros((size, size))
    return grid


def get_timing_pattern(grid_size: int = 21) -> list:
    grid = np.zeros((grid_size, grid_size))
    fixed_row, fixed_col = 6, 6  # TODO: calculate based on grid instead of a contant.
    timing_pattern_row = [(fixed_row, x) for x in range(0, grid_size, 2)]
    timing_pattern_col = [(x, fixed_col) for x in range(0, grid_size, 2)]
    timing_pattern = timing_pattern_row + timing_pattern_col
    for x, y in timing_pattern:
        grid[x, y] = 1
    print(grid)
    return timing_pattern


def get_finder_pattern(grid):
    pass


def draw(binary_string: str, grid_size: int = 21):
    grid = get_empty_grid(grid_size)
    timing_pattern = get_timing_pattern(grid_size)
    print(timing_pattern)


if __name__ == "__main__":
    # import random

    # random_binary_string = "".join(random.choices(["0", "1"], k=21 * 21))
    # draw(random_binary_string)

    draw("011")
