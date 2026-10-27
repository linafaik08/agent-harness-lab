from nesting import flatten


def test_deep_nesting():
    assert flatten([1, [2, [3, 4]]]) == [1, 2, 3, 4]
