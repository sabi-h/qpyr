import math
from typing import Callable, List

import numpy as np
from numpy.typing import NDArray


class PenaltyPoint:
    N1 = 3
    N2 = 3
    N3 = 40
    N4 = 10


def get_masks() -> List[Callable]:
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


def _calculate_adjacent_penalty_inline(array: List[int]) -> int:
    consecutive_run = 1
    score = 0
    for i, num in enumerate(array):
        if i == 0:
            continue

        previous_number = array[i - 1]

        if num == previous_number:
            consecutive_run += 1
            if consecutive_run == 5:
                score += PenaltyPoint.N1
            elif consecutive_run > 5:
                score += 1
        else:
            consecutive_run = 1

    return score


def get_adjacent_modules_penalty(grid: NDArray) -> int:
    result = 0
    for row in grid.tolist():
        result += _calculate_adjacent_penalty_inline(row)

    for col in grid.T.tolist():
        result += _calculate_adjacent_penalty_inline(col)

    return result


def _calculate_finder_penalty(array: NDArray) -> int:
    pattern = [1, 0, 1, 1, 1, 0, 1]
    light_area = [0, 0, 0, 0]

    pattern1 = light_area + pattern
    pattern2 = pattern + light_area

    total_pattern_length = len(pattern1)

    patterns_found = 0

    for i in range(len(array) - total_pattern_length + 1):
        sub_array = array[i : i + total_pattern_length]
        if np.array_equal(sub_array, pattern1):
            patterns_found += 1

        if np.array_equal(sub_array, pattern2):
            patterns_found += 1

    result = patterns_found * PenaltyPoint.N3
    return result


def _calculate_finder_penalty_2(array: NDArray) -> int:
    pattern = [1, 0, 1, 1, 1, 0, 1]
    light_area = [0, 0, 0, 0]

    pattern1 = light_area + pattern
    pattern2 = pattern + light_area

    total_pattern_length = len(pattern1)

    patterns_found = 0

    for i in range(len(array) - total_pattern_length + 1):
        sub_array = array[i : i + total_pattern_length]
        if np.array_equal(sub_array, pattern1):
            patterns_found += 1

        if np.array_equal(sub_array, pattern2):
            patterns_found += 1

    result = patterns_found * PenaltyPoint.N3
    return result


def get_finder_pattern_penalty(grid):
    result = 0
    for row in grid:
        result += _calculate_finder_penalty_2(row)

    for col in grid.T:
        result += _calculate_finder_penalty_2(col)

    return result


def get_same_color_block_penalty(grid: NDArray):
    blocks_count = 0
    grid_size = grid.shape[0]
    for row in range(grid_size - 1):
        for col in range(grid_size - 1):
            if grid[row][col] == grid[row][col + 1] == grid[row + 1][col] == grid[row + 1][col + 1]:
                blocks_count += 1
    result = blocks_count * PenaltyPoint.N2
    return result


def get_proportion_penalty(grid):
    black_proportion = (grid == 1).sum() / grid.size
    deviation = abs((black_proportion * 100) - 50)

    # Every 5% departure from 50%, rating++
    rating = int(deviation / 5)
    result = rating * PenaltyPoint.N4
    return result
