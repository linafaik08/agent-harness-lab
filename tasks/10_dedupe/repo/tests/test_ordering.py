from ordering import dedupe


def test_order_is_preserved():
    assert dedupe([3, 1, 3, 2, 1]) == [3, 1, 2]
