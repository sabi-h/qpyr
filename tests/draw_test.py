from qpyr._lib.draw import _get_alignment_pattern_coords, get_alignment_pattern_positions, get_format_information


def test_get_format_information():
    result_format_info = get_format_information("M", 5)
    expected_format_info = 16590
    assert result_format_info == expected_format_info


def test__get_alignment_pattern_coords():
    assert _get_alignment_pattern_coords(version=1, grid_size=21) == []
    assert _get_alignment_pattern_coords(version=2, grid_size=25) == [6, 18]
    assert _get_alignment_pattern_coords(version=13, grid_size=69) == [6, 34, 62]
    assert _get_alignment_pattern_coords(version=19, grid_size=93) == [6, 30, 58, 86]
    assert _get_alignment_pattern_coords(version=40, grid_size=177) == [6, 30, 58, 86, 114, 142, 170]


def test_get_alignment_pattern_positions():
    # fmt: off
    assert get_alignment_pattern_positions([]) == []
    assert get_alignment_pattern_positions([6, 34]) == [(34, 34)]

    assert get_alignment_pattern_positions([6, 34, 62]) == [(6, 34), (34, 6), (34, 34), (34, 62), (62, 34), (62, 62)]

    coords = [6, 34, 62, 90]
    positions = [(6, 34), (6, 62), (34, 6), (34, 34), (34, 62), (34, 90), (62, 6), (62, 34), (62, 62), (62, 90), (90, 34), (90, 62), (90, 90)]
    assert get_alignment_pattern_positions(coords) == positions

    coords = [6, 30, 58, 86, 114, 142, 170]
    positions = [(6, 30), (6, 58), (6, 86), (6, 114), (6, 142), (30, 6), (30, 30), (30, 58), (30, 86), (30, 114), (30, 142), (30, 170), (58, 6), (58, 30), (58, 58), (58, 86), (58, 114), (58, 142), (58, 170), (86, 6), (86, 30), (86, 58), (86, 86), (86, 114), (86, 142), (86, 170), (114, 6), (114, 30), (114, 58), (114, 86), (114, 114), (114, 142), (114, 170), (142, 6), (142, 30), (142, 58), (142, 86), (142, 114), (142, 142), (142, 170), (170, 30), (170, 58), (170, 86), (170, 114), (170, 142), (170, 170)]
    assert get_alignment_pattern_positions(coords) == positions
