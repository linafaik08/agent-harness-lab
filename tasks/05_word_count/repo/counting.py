import re
from collections import Counter


def word_count(text: str) -> Counter:
    """Counts how often each word appears in a text."""
    return Counter(re.findall(r"[A-Za-z']+", text))
