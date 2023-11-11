from typing import Callable
import numpy as np

from qrcode.data_masking import get_adjacent_modules_points, get_masks


def test_get_adjacent_modules_points():
    test_grid = np.array([[1, 0, 0, 0, 0, 0, 0, 1]])
    points = get_adjacent_modules_points(test_grid)
    expected_points = 4
    assert points == expected_points


def test_get_adjacent_modules_penalty_single_oints():
    test_grid = np.array([[1], [1], [1], [1], [1], [1], [0], [1]])
    points = get_adjacent_modules_points(test_grid)
    expected_points = 4
    assert points == expected_points


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
    points = get_adjacent_modules_points(test_grid)
    expected_points = 48
    assert points == expected_points


def test_get_adjacent_modules_penalty_no_points():
    test_grid = np.array([[0, 0, 0, 0, 1, 1]])
    points = get_adjacent_modules_points(test_grid)
    expected_points = 0
    assert points == expected_points


def test_get_masks():
    assert isinstance(get_masks()[0], Callable)
    assert isinstance(get_masks()[7], Callable)

    masks = get_masks()
    assert masks[7](21, 21) == True
    assert masks[3](15, 14) == False
