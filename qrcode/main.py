from qrcode.encode import encode
from qrcode.draw import draw


def main(data, ecc_level="LOW"):
    binary_str = encode(data, ecc_level=ecc_level)
    draw(binary_str)


if __name__ == "__main__":
    main("hello")
