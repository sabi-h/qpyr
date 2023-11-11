from typing import List, Callable
from numpy.typing import NDArray
import math


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


def _calculate_adjacent_penalty_points(array: List[int]) -> int:
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


def get_adjacent_modules_points(grid: NDArray) -> int:
    result = 0
    for row in grid.tolist():
        row_score = _calculate_adjacent_penalty_points(row)
        result += row_score

    for col in grid.T.tolist():
        col_score = _calculate_adjacent_penalty_points(col)
        result += col_score

    return result


def get_mask_penalty_points(grid) -> int:
    adjacent_modules_points = get_adjacent_modules_points(grid)

    total = sum(
        [
            adjacent_modules_points,
        ]
    )
    return total


if __name__ == "__main__":
    import numpy as np

    grid = np.array([[1, 0, 0, 0, 0, 0, 0, 0]])

    points = get_adjacent_modules_points(grid)

    print(f"grid: \n {grid}")
    print(f"{points=}")
