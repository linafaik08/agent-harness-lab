from series import moving_average


def test_final_window():
    assert moving_average([1, 2, 3, 4], 2) == [1.5, 2.5, 3.5]


def test_window_equals_length():
    assert moving_average([2, 4], 2) == [3.0]


def test_window_of_one():
    assert moving_average([1, 2], 1) == [1.0, 2.0]
