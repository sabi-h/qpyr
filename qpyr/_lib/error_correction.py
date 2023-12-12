from typing import List

from qpyr._lib.static import ECC_CODEWORDS_PER_BLOCK, NUM_ERROR_CORRECTION_BLOCKS
from qpyr._lib.utils import get_num_raw_data_modules


def _reed_solomon_compute_divisor(degree: int) -> bytes:
    """Returns a Reed-Solomon ECC generator polynomial for the given degree. This could be
    implemented as a lookup table over all possible parameter values, instead of as an algorithm."""
    if not (1 <= degree <= 255):
        raise ValueError("Degree out of range")
    # Polynomial coefficients are stored from highest to lowest power, excluding the leading term which is always 1.
    # For example the polynomial x^3 + 255x^2 + 8x + 93 is stored as the uint8 array [255, 8, 93].
    result = bytearray([0] * (degree - 1) + [1])  # Start off with the monomial x^0

    # Compute the product polynomial (x - r^0) * (x - r^1) * (x - r^2) * ... * (x - r^{degree-1}),
    # and drop the highest monomial term which is always 1x^degree.
    # Note that r = 0x02, which is a generator element of this field GF(2^8/0x11D).
    root: int = 1
    for _ in range(degree):  # Unused variable i
        # Multiply the current product by (x - r^i)
        for j in range(degree):
            result[j] = _reed_solomon_multiply(result[j], root)
            if j + 1 < degree:
                result[j] ^= result[j + 1]
        root = _reed_solomon_multiply(root, 0x02)
    return result


def _reed_solomon_compute_remainder(data: bytes, divisor: bytes) -> bytes:
    """Returns the Reed-Solomon error correction codeword for the given data and divisor polynomials."""
    result = bytearray([0] * len(divisor))
    for b in data:  # Polynomial division
        factor: int = b ^ result.pop(0)
        result.append(0)
        for i, coef in enumerate(divisor):
            result[i] ^= _reed_solomon_multiply(coef, factor)
    return result


def _reed_solomon_multiply(x: int, y: int) -> int:
    """Returns the product of the two given field elements modulo GF(2^8/0x11D). The arguments and result
    are unsigned 8-bit integers. This could be implemented as a lookup table of 256*256 entries of uint8."""
    if (x >> 8 != 0) or (y >> 8 != 0):
        raise ValueError("Byte out of range")
    # Russian peasant multiplication
    z: int = 0
    for i in reversed(range(8)):
        z = (z << 1) ^ ((z >> 7) * 0x11D)
        z ^= ((y >> i) & 1) * x
    assert z >> 8 == 0
    return z


def add_ecc_and_interleave(version: int, ecl: str, data: bytearray) -> bytearray:
    """Returns a new byte string representing the given data with the appropriate error correction
    codewords appended to it, based on this object's version and error correction level."""
    # Calculate parameter numbers
    numblocks: int = NUM_ERROR_CORRECTION_BLOCKS[ecl][version]
    blockecclen: int = ECC_CODEWORDS_PER_BLOCK[ecl][version]
    rawcodewords: int = get_num_raw_data_modules(version) // 8
    numshortblocks: int = numblocks - rawcodewords % numblocks
    shortblocklen: int = rawcodewords // numblocks

    # Split data into blocks and append ECC to each block
    blocks: List[bytes] = []
    rsdiv: bytes = _reed_solomon_compute_divisor(blockecclen)
    k: int = 0
    for i in range(numblocks):
        dat: bytearray = data[k : k + shortblocklen - blockecclen + (0 if i < numshortblocks else 1)]
        k += len(dat)
        ecc: bytes = _reed_solomon_compute_remainder(dat, rsdiv)
        if i < numshortblocks:
            dat.append(0)
        blocks.append(dat + ecc)
    assert k == len(data)

    # Interleave (not concatenate) the bytes from every block into a single sequence
    result = bytearray()
    for i in range(len(blocks[0])):
        for j, blk in enumerate(blocks):
            # Skip the padding byte in short blocks
            if (i != shortblocklen - blockecclen) or (j >= numshortblocks):
                result.append(blk[i])
    assert len(result) == rawcodewords
    return result
