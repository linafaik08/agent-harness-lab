from intervals import merge_intervals


def test_unsorted():
    assert merge_intervals([(5, 7), (1, 3), (2, 4)]) == [(1, 4), (5, 7)]


def test_touching_and_nested():
    assert merge_intervals([(1, 2), (2, 3)]) == [(1, 3)]
    assert merge_intervals([(1, 10), (2, 3)]) == [(1, 10)]


def test_empty():
    assert merge_intervals([]) == []
