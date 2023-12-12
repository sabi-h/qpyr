from qpyr._lib.static import ECC_CODEWORDS_PER_BLOCK, NUM_ERROR_CORRECTION_BLOCKS, TOTAL_NUMBER_OF_CODEWORDS


def bits_to_bytearray(bit_string):
    byte_array = bytearray()

    # Split the string into 8-bit chunks and convert to bytes
    for i in range(0, len(bit_string), 8):
        byte_chunk = bit_string[i : i + 8]
        byte = int(byte_chunk, 2)
        byte_array.append(byte)

    return byte_array


def bytearray_to_bits(byte_array):
    bit_string = ""
    for byte in byte_array:
        binary_representation = bin(byte)[2:]  # Remove the '0b' prefix
        padded_binary = binary_representation.zfill(8)  # Pad with zeros to make it 8 bits long
        bit_string += padded_binary
    return bit_string


def get_version(grid_size: int):
    return int((grid_size - 17) / 4)


def get_grid_size(version: int):
    return int(version * 4 + 17)


def get_segment_character_bits_length(mode: str, version: int):
    result = 0
    if mode == "byte":
        if version <= 9:
            result = 8
        else:
            result = 16
    return result


def get_total_data_capacity_bytes(ecl: str, version: int) -> int:
    total_codewords = TOTAL_NUMBER_OF_CODEWORDS[version]
    total_ecc_codewords = ECC_CODEWORDS_PER_BLOCK[ecl][version] * NUM_ERROR_CORRECTION_BLOCKS[ecl][version]
    total_data_codewords = total_codewords - total_ecc_codewords
    return total_data_codewords


def get_num_raw_data_modules(version: int) -> int:
    """Returns the number of data bits that can be stored in a QR Code of the given version number, after
    all function modules are excluded. This includes remainder bits, so it might not be a multiple of 8.
    The result is in the range [208, 29648]. This could be implemented as a 40-entry lookup table."""
    if not (1 <= version <= 40):
        raise ValueError("Version number out of range")
    result: int = (16 * version + 128) * version + 64
    if version >= 2:
        numalign: int = version // 7 + 2
        result -= (25 * numalign - 10) * numalign - 55
        if version >= 7:
            result -= 36
    assert 208 <= result <= 29648
    return result
