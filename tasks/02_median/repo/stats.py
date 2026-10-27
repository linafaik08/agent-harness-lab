def median(values: list[float]) -> float:
    """Returns the median of a non-empty list of numbers."""
    ordered = sorted(values)
    return ordered[len(ordered) // 2]
