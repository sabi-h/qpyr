from qpyr.encode import encode
from qpyr.draw import draw


def main(data, ecl="M"):
    version, binary_str = encode(data, ecl=ecl)
    draw(binary_str, version, ecl=ecl)


if __name__ == "__main__":
    # data = "google.comg/google.comg/google.comg/google.comg/google.comg/google.comg/google.comg/google.comg/google.comg/google.comg/google.comg/google.comg/google.comg/google.comg/"
    data = "£30,000 åßç"
    main(data, ecl="H")
