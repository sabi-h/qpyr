from typing import Callable

import numpy as np

from qpyr.data_masking import (
    get_adjacent_modules_penalty,
    get_masks,
    get_proportion_penalty,
    get_same_color_block_penalty,
    get_finder_pattern_penalty,
)


def test_get_finder_pattern_penalty_row():
    excepted = 40
    grid = np.array([[0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1]])
    result = get_finder_pattern_penalty(grid)
    assert excepted == result


def test_get_proportion_penalty():
    excepted = 0
    grid = np.array([[0, 0, 0, 0, 1, 1, 1, 1]])
    result = get_proportion_penalty(grid)
    assert result == excepted


def test_get_proportion_penalty_many_points():
    excepted = 30
    grid = np.array([0] * 5 + [1] * 10)
    result = get_proportion_penalty(grid)
    assert result == excepted


def test_get_finder_pattern_penalty_col():
    excepted = 40
    grid = np.array([[0], [0], [0], [0], [1], [0], [1], [1], [1], [0], [1]])
    result = get_finder_pattern_penalty(grid)
    assert excepted == result


def test_get_finder_pattern_penalty_many_points():
    excepted = 120
    grid = np.array(
        [
            [1, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1, 1],
            [1, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1, 1],
            [1, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1, 1],
        ]
    )
    result = get_finder_pattern_penalty(grid)
    assert excepted == result


def test_get_adjacent_modules_penalty():
    test_grid = np.array([[1, 0, 0, 0, 0, 0, 0, 1]])
    result = get_adjacent_modules_penalty(test_grid)
    expected = 4
    assert result == expected


def test_get_adjacent_modules_penalty_single_oints():
    test_grid = np.array([[1], [1], [1], [1], [1], [1], [0], [1]])
    result = get_adjacent_modules_penalty(test_grid)
    expected = 4
    assert result == expected


def test_get_adjacent_modules_penalty_mixed_large_points():
    test_grid = np.array(
        [
            [1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1],
        ]
    )
    result = get_adjacent_modules_penalty(test_grid)
    expected = 48
    assert result == expected


def test_get_adjacent_modules_penalty_no_points():
    test_grid = np.array([[0, 0, 0, 0, 1, 1]])
    result = get_adjacent_modules_penalty(test_grid)
    expected = 0
    assert result == expected


def test_get_same_color_block_points_large_points():
    expected = 12
    grid = np.array(
        [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
        ]
    )
    result = get_same_color_block_penalty(grid)
    assert result == expected


def test_get_same_color_block_points_no_points():
    expected = 0
    grid = np.array(
        [
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1],
        ]
    )
    result = get_same_color_block_penalty(grid)
    assert result == expected


def test_get_same_color_block_points_mixed_points():
    expected = 3
    grid = np.array(
        [
            [0, 0, 0],
            [0, 1, 1],
            [0, 1, 1],
        ]
    )
    result = get_same_color_block_penalty(grid)
    assert result == expected


def test_get_masks():
    assert isinstance(get_masks()[0], Callable)
    assert isinstance(get_masks()[7], Callable)

    masks = get_masks()
    assert masks[7](21, 21) == True
    assert masks[3](15, 14) == False
