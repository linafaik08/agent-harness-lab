def merge_intervals(intervals: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Merges overlapping closed intervals."""
    merged = []
    for start, end in intervals:
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return [tuple(pair) for pair in merged]
