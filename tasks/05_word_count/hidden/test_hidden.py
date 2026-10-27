from counting import word_count


def test_case_insensitive():
    assert word_count("The cat and the hat")["the"] == 2


def test_keys_are_lowercase():
    assert set(word_count("Dog DOG dog")) == {"dog"}


def test_apostrophes():
    assert word_count("It's it's")["it's"] == 2
