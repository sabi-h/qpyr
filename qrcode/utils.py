def convert_to_version(grid_size):
    return int((grid_size - 17) / 4)


def convert_to_grid_size(version):
    return int(version * 4 + 17)
