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
