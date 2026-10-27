from roman import roman_to_int


def test_subtractive():
    assert roman_to_int("IV") == 4
    assert roman_to_int("XL") == 40


def test_additive():
    assert roman_to_int("III") == 3


def test_long():
    assert roman_to_int("MCMXCIV") == 1994
