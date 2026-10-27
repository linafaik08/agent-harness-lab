VALUES = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}


def roman_to_int(numeral: str) -> int:
    """Converts a Roman numeral such as "MCMXCIV" into an integer."""
    return sum(VALUES[ch] for ch in numeral)
