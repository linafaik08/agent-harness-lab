from ordering import dedupe


def test_numbers():
    assert dedupe([3, 1, 3, 2, 1]) == [3, 1, 2]


def test_strings():
    assert dedupe(["b", "a", "b", "c"]) == ["b", "a", "c"]


def test_empty_and_unique():
    assert dedupe([]) == []
    assert dedupe([9, 8, 7]) == [9, 8, 7]
