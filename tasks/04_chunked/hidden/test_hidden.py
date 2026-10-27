from batching import chunked


def test_partial():
    assert chunked([1, 2, 3, 4, 5], 2) == [[1, 2], [3, 4], [5]]


def test_exact_multiple():
    assert chunked([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_size_larger_than_list():
    assert chunked([1, 2], 5) == [[1, 2]]


def test_empty():
    assert chunked([], 3) == []
