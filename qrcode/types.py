from typing import Dict, Literal, Tuple, TypeAlias


CoordinateValueMap: TypeAlias = Dict[Tuple[int, int], int]
ErrorCorrectionLevels = Literal["L", "M", "Q", "H"]
