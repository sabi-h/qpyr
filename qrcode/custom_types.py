from enum import Enum
from typing import Dict, Literal, Tuple, TypeAlias


CoordinateValueMap: TypeAlias = Dict[Tuple[int, int], int]


class ECL(Enum):
    L = "L"
    M = "M"
    Q = "Q"
    H = "H"
