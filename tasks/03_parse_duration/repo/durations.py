import re

UNITS = {"h": 3600, "m": 6, "s": 1}


def parse_duration(text: str) -> int:
    """Converts a duration such as "1h30m" or "45s" into seconds."""
    total = 0
    for amount, unit in re.findall(r"(\d+)([hms])", text):
        total += int(amount) * UNITS[unit]
    return total
