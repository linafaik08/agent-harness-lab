from counting import word_count


def test_counting_ignores_case():
    assert word_count("The cat and the hat")["the"] == 2
