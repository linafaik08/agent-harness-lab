from intervals import merge_intervals


def test_unsorted_input_is_merged():
    assert merge_intervals([(5, 7), (1, 3), (2, 4)]) == [(1, 4), (5, 7)]
