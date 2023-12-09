from qpyr.encode import encode
from qpyr.draw import draw


def main(data, ecl="M"):
    version, binary_str = encode(data, ecl=ecl)
    grid = draw(binary_str, version, ecl=ecl)
    return grid
