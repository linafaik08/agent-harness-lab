def chunked(items: list, size: int) -> list[list]:
    """Splits a list into consecutive chunks of at most `size` items."""
    chunks = []
    for start in range(0, len(items) - size + 1, size):
        chunks.append(items[start:start + size])
    return chunks
