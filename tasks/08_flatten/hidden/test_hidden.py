from nesting import flatten


def test_deep():
    assert flatten([1, [2, [3, [4, [5]]]]]) == [1, 2, 3, 4, 5]


def test_empty_lists():
    assert flatten([[], [[]], 1]) == [1]


def test_strings_are_not_split():
    assert flatten(["ab", ["cd"]]) == ["ab", "cd"]
