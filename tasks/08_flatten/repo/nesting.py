def flatten(nested: list) -> list:
    """Flattens arbitrarily nested lists into a single flat list."""
    flat = []
    for item in nested:
        if isinstance(item, list):
            flat.extend(item)
        else:
            flat.append(item)
    return flat
