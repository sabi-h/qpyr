from typing import Optional
from numpy.typing import NDArray
from PIL import Image, ImageDraw

from qpyr._lib.static import ColorValue


def draw(grid: NDArray, cell_size: int = 20, outline=None) -> Image.Image:
    """
    Draw a grid using PIL based on a 2D numpy array.

    Parameters:
    - grid: A 2D numpy array of shape (n, n) containing 0, 1, -1, -2.
    - cell_size: The size of each cell in the grid in pixels.
    - outline: Color of outline, e.g. blue, #00ff00, (0, 0, 255), (0, 0, 255, 128)
    """
    # Validate the shape of the grid
    if grid.shape[0] != grid.shape[1]:
        raise ValueError("The input grid must be square (n x n).")

    # Initialize an image object with white background
    img_size = grid.shape[0] * cell_size
    img = Image.new("RGB", (img_size, img_size), "lightgray")
    draw = ImageDraw.Draw(img)

    color_map = {
        ColorValue.WHITE: "white",
        ColorValue.BLACK: "black",
        ColorValue.DEFAULT_VALUE: "lightgray",
        ColorValue.DUMMY_VALUE: "red",
    }

    for i in range(grid.shape[0]):  # Rows
        for j in range(grid.shape[1]):  # Columns
            x0, y0 = j * cell_size, i * cell_size  # Corrected here
            x1, y1 = x0 + cell_size, y0 + cell_size
            cell_value = grid[i, j]
            cell_color = color_map.get(cell_value, "white")
            draw.rectangle(((x0, y0), (x1, y1)), fill=cell_color, outline=outline)
    return img
