from qpyr._lib.encode import encode
from qpyr._lib.matrix import matrix
from qpyr._lib.draw import draw


def main(data: str, filepath: str = "", fileformat="", ecl="M", show_image=False):
    version, binary_str = encode(data, ecl=ecl)
    qr_matrix = matrix(binary_str, version, ecl=ecl)
    image = draw(qr_matrix)

    if filepath:
        image.save(fp=filepath, format=fileformat)

    if show_image:
        image.show()

    return image
