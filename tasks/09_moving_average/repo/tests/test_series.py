from series import moving_average


def test_includes_final_window():
    assert moving_average([1, 2, 3, 4], 2) == [1.5, 2.5, 3.5]
