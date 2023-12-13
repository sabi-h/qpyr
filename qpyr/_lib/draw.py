from typing import Callable, Dict, List, Optional, Tuple

import numpy as np
from numpy.typing import NDArray
from PIL import Image, ImageDraw

from qpyr._lib.data_masking import (
    get_adjacent_modules_penalty,
    get_finder_pattern_penalty,
    get_masks,
    get_proportion_penalty,
    get_same_color_block_penalty,
)
from qpyr._lib.utils import get_grid_size


CoordinateValueMap = Dict[Tuple[int, int], int]

WHITE = 0
BLACK = 1
DEFAULT_VALUE = -1
DUMMY_VALUE = -2


def get_timing_pattern(grid_size: int = 21) -> CoordinateValueMap:
    fixed_row, fixed_col = 6, 6
    timing_pattern_row_black = {(fixed_row, x): BLACK for x in range(0, grid_size, 2)}
    timing_pattern_row_white = {(fixed_row, x): WHITE for x in range(1, grid_size, 2)}
    timing_pattern_col_black = {(x, fixed_col): BLACK for x in range(0, grid_size, 2)}
    timing_pattern_col_white = {(x, fixed_col): WHITE for x in range(1, grid_size, 2)}
    result: CoordinateValueMap = {
        **timing_pattern_row_black,
        **timing_pattern_row_white,
        **timing_pattern_col_black,
        **timing_pattern_col_white,
    }
    return result


def _finder_and_seperator_pattern_generator(row, col, grid_size) -> CoordinateValueMap:
    result = {}
    for r in range(-1, 8):
        if row + r <= -1 or grid_size <= row + r:
            continue

        for c in range(-1, 8):
            if col + c <= -1 or grid_size <= col + c:
                continue

            if (0 <= r <= 6 and c in (0, 6)) or (0 <= c <= 6 and r in (0, 6)) or (2 <= r <= 4 and 2 <= c <= 4):
                result[(row + r, col + c)] = BLACK
            else:
                result[(row + r, col + c)] = WHITE
    return result


def get_finder_and_seperator(grid_size) -> CoordinateValueMap:
    top_left = _finder_and_seperator_pattern_generator(0, 0, grid_size)
    bottom_left = _finder_and_seperator_pattern_generator(grid_size - 7, 0, grid_size)
    top_right = _finder_and_seperator_pattern_generator(0, grid_size - 7, grid_size)
    return {**top_left, **bottom_left, **top_right}


def add_quiet_zone(grid, border: int = 4):
    horizontal_zone = np.zeros((grid.shape[0], border), dtype=int)
    grid = np.hstack((grid, horizontal_zone))
    grid = np.hstack((horizontal_zone, grid))

    vertical_zone = np.zeros((border, grid.shape[1]), dtype=int)
    grid = np.vstack((grid, vertical_zone))
    grid = np.vstack((vertical_zone, grid))

    assert grid.dtype.name == "int64"
    return grid


def override_grid(grid: NDArray, indexes: Dict[tuple, int]) -> NDArray:
    for index, value in indexes.items():
        i, j = index
        grid[i][j] = value
    return grid


def draw_grid_with_pil(grid: NDArray, cell_size: int = 20, outline: Optional[str] = None) -> None:
    """
    Draw a grid using PIL based on a 2D numpy array.

    Parameters:
    - grid: A 2D numpy array of shape (n, n) containing 0, 1, -1, -2.
    - cell_size: The size of each cell in the grid in pixels.
    """
    # Validate the shape of the grid
    if grid.shape[0] != grid.shape[1]:
        raise ValueError("The input grid must be square (n x n).")

    # Initialize an image object with white background
    img_size = grid.shape[0] * cell_size
    img = Image.new("RGB", (img_size, img_size), "lightgray")
    draw = ImageDraw.Draw(img)

    color_map = {WHITE: "white", BLACK: "black", DEFAULT_VALUE: "lightgray", DUMMY_VALUE: "red"}

    for i in range(grid.shape[0]):  # Rows
        for j in range(grid.shape[1]):  # Columns
            x0, y0 = j * cell_size, i * cell_size  # Corrected here
            x1, y1 = x0 + cell_size, y0 + cell_size
            cell_value = grid[i, j]
            cell_color = color_map.get(cell_value, "white")
            draw.rectangle(((x0, y0), (x1, y1)), fill=cell_color, outline=outline)

    img.show()


def _iterate_over_grid(grid_size) -> List[Tuple[int, int]]:
    """Iterates over all grid cells in zig-zag pattern and returns an iterator of tuples (row, col)
    in order, starting from bottom right."""
    result = []
    up = True
    for column in range(grid_size - 1, 0, -2):
        if column <= 6:  # skip column 6 because of timing pattern
            column -= 1

        if up:
            row = grid_size - 1
        else:
            row = 0

        for _ in range(grid_size):
            for col in (column, column - 1):
                result.append((row, col))
            if up:
                row -= 1
            else:
                row += 1
        if up:
            up = False
        else:
            up = True
    return result


def get_codeword_placement(binary_str, grid, grid_size) -> CoordinateValueMap:
    result = {}
    grid_iterator = _iterate_over_grid(grid_size)
    for row, col in grid_iterator:
        if not binary_str:
            # Pad with white blocks.
            if grid[row][col] == -1:
                result[(row, col)] = WHITE
        elif grid[row][col] == -1:
            result[(row, col)] = binary_str[0]
            binary_str = binary_str[1:]
        else:
            continue

    return result


def get_format_information(ecl: str, mask_reference: int) -> int:
    generator_polynomial = 1335
    mask = 21522
    ecl_binary_indicator_map = {"L": 1, "M": 0, "Q": 3, "H": 2}
    ecl_binary_indicator = ecl_binary_indicator_map[ecl]

    data: int = ecl_binary_indicator << 3 | mask_reference  # errCorrLvl is uint2, mask is uint3
    rem: int = data
    for _ in range(10):
        rem = (rem << 1) ^ ((rem >> 9) * generator_polynomial)
    bits: int = (data << 10 | rem) ^ mask  # uint15
    assert bits >> 15 == 0
    return bits


def get_dummy_format_information(grid_size) -> CoordinateValueMap:
    result = {}
    for col in range(grid_size):
        if (col <= 7) or (col >= grid_size - 8):
            result[(row := 8, col)] = DUMMY_VALUE

    for row in range(grid_size):
        if row <= 8 or row >= grid_size - 8:
            result[(row, col := 8)] = DUMMY_VALUE

    result[(grid_size - 8, 8)] = BLACK
    return result


def get_format_placement(grid_size, format_info: int = DUMMY_VALUE) -> CoordinateValueMap:
    result = {}
    if format_info == DUMMY_VALUE:
        format_info_to_draw = [DUMMY_VALUE] * 15
    else:
        format_info_to_draw = [int(x) for x in bin(format_info)[2:].zfill(15)]
        assert len(format_info_to_draw) == 15

    index = 14
    for row in range(grid_size):
        if (row <= 8) or (row >= grid_size - 8):
            if row in (6, 13):
                continue
            result[(row, col := 8)] = format_info_to_draw[index]
            index -= 1

    index = 0
    for col in range(grid_size):
        if (col <= 7) or (col >= grid_size - 8):
            if col == 6:
                continue
            result[(row := 8, col)] = format_info_to_draw[index]
            index += 1

    result[(grid_size - 8, 8)] = BLACK
    return result


def apply_mask(mask: Callable, data: CoordinateValueMap) -> CoordinateValueMap:
    result = {}
    for coordinate, value in data.items():
        i, j = coordinate
        result[(i, j)] = mask(i, j) ^ int(value)  # int(value) may not be needed if value already int
    return result


def _get_alignment_pattern_coords(version, grid_size) -> List[int]:
    """Returns a list of row/col coordinates of center modules for alignment patterns."""
    if version == 1:
        return []
    else:
        numalign: int = version // 7 + 2
        step: int = 26 if (version == 32) else (version * 4 + numalign * 2 + 1) // (numalign * 2 - 2) * 2
        result: List[int] = [(grid_size - 7 - i * step) for i in range(numalign - 1)] + [6]
        return list(reversed(result))


def get_alignment_pattern_positions(alignment_pattern_coords: List):
    num_coords = len(alignment_pattern_coords)
    skip = [(0, 0), (0, num_coords - 1), (num_coords - 1, 0)]

    positions = []
    for i in range(num_coords):
        for j in range(num_coords):
            if (i, j) not in skip:
                position = (alignment_pattern_coords[i], alignment_pattern_coords[j])
                positions.append(position)

    return positions


def get_alignment_patterns(positions) -> CoordinateValueMap:
    result = {}
    for position in positions:
        x, y = position
        xstart, xend = x - 2, x + 2
        ystart, yend = y - 2, y + 2
        for i in range(xstart, xend + 1):
            for j in range(ystart, yend + 1):
                if (i == xstart) or (i == xend):
                    result[i, j] = BLACK
                elif (j == ystart) or (j == yend):
                    result[i, j] = BLACK
                elif (i == x) and (j == y):
                    result[i, j] = BLACK
                else:
                    result[i, j] = WHITE
    return result


def get_version_information(version: int) -> Optional[int]:
    if version <= 6:
        return

    generator_polynomial = 7973

    data: int = version
    rem: int = data
    for _ in range(12):
        rem = (rem << 1) ^ ((rem >> 11) * generator_polynomial)
    bits: int = data << 12 | rem
    assert bits >> 18 == 0
    return bits


def get_version_placement(version_information: Optional[int], grid_size: int) -> CoordinateValueMap:
    if not version_information:
        return {}

    result = {}
    value = [int(x) for x in bin(version_information)[2:].zfill(18)]
    value = value[::-1]  # reversed

    value_index = 0
    top_right_start_index = (0, grid_size - 11)
    bottom_left_start_index = (grid_size - 11, 0)
    for row in range(6):
        for col in range(3):
            row_index = row
            col_index = top_right_start_index[1] + col
            result[(row_index, col_index)] = value[value_index]
            value_index += 1

    value_index = 0
    for col in range(6):
        for row in range(3):
            col_index = col
            row_index = bottom_left_start_index[0] + row
            result[(row_index, col_index)] = value[value_index]
            value_index += 1

    return result


def draw(binary_string: str, version: int, ecl: str, quiet_zone_border: int = 4):
    grid_size = get_grid_size(version)

    version_information = get_version_information(version)
    version_information_pattern = get_version_placement(version_information, grid_size)

    dummy_format_information = get_dummy_format_information(grid_size)
    finder_and_seperator_pattern = get_finder_and_seperator(grid_size)
    timing_pattern = get_timing_pattern(grid_size)

    alignment_pattern_coords = _get_alignment_pattern_coords(version, grid_size)
    alignment_pattern_positions = get_alignment_pattern_positions(alignment_pattern_coords)
    alignment_pattern = get_alignment_patterns(alignment_pattern_positions)

    grid = np.full((grid_size, grid_size), -1, dtype=int)

    grid = override_grid(grid, dummy_format_information)
    grid = override_grid(grid, timing_pattern)
    grid = override_grid(grid, finder_and_seperator_pattern)
    grid = override_grid(grid, version_information_pattern)
    grid = override_grid(grid, alignment_pattern)

    codeword_placement = get_codeword_placement(binary_string, grid, grid_size)
    grid = override_grid(grid, codeword_placement)

    masks = get_masks()
    best_mask_ref, lowest_penalty_points = (0, 100_000)  # arbitrary large number
    for mask_reference, mask in enumerate(masks):
        masked_codewords = apply_mask(mask, codeword_placement)
        masked_grid = override_grid(grid, masked_codewords)

        format_information = get_format_information(ecl, mask_reference)
        format_information_placement = get_format_placement(grid_size, format_information)
        masked_grid = override_grid(masked_grid, format_information_placement)

        adjacent_modules_points = get_adjacent_modules_penalty(masked_grid)
        same_color_block_penalty = get_same_color_block_penalty(masked_grid)

        masked_grid_with_quiet_zone = add_quiet_zone(masked_grid, quiet_zone_border)
        finder_pattern_penalty = get_finder_pattern_penalty(masked_grid_with_quiet_zone)

        proportion_penalty = get_proportion_penalty(masked_grid)

        total_penalty_points = (
            adjacent_modules_points + same_color_block_penalty + finder_pattern_penalty + proportion_penalty
        )

        if total_penalty_points < lowest_penalty_points:
            best_mask_ref, lowest_penalty_points = (mask_reference, total_penalty_points)

    best_mask = masks[best_mask_ref]
    masked_codewords = apply_mask(best_mask, codeword_placement)
    masked_grid = override_grid(grid, masked_codewords)

    format_information = get_format_information(ecl, best_mask_ref)
    format_information_placement = get_format_placement(grid_size, format_information)
    masked_grid = override_grid(masked_grid, format_information_placement)

    masked_grid = add_quiet_zone(masked_grid, quiet_zone_border)
    draw_grid_with_pil(masked_grid)

    return masked_grid
