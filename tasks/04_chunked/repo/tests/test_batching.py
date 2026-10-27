from batching import chunked


def test_last_partial_chunk_is_kept():
    assert chunked([1, 2, 3, 4, 5], 2) == [[1, 2], [3, 4], [5]]
