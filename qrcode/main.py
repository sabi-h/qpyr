from qrcode.encode import encode
from qrcode.draw import draw


def main(data, ecl="M"):
    version, binary_str = encode(data, ecl=ecl)
    draw(binary_str, version, ecl=ecl)


if __name__ == "__main__":
    url = "google.comg/google.comg/google.comg/google.comg/google.comg/google.comg/google.comg/google.comg/google.comg/google.comg/google.comg/google.comg/google.comg/google.comg/"
    main(url, ecl="H")
