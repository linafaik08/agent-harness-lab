def moving_average(values: list[float], window: int) -> list[float]:
    """Returns the mean of every full window of consecutive values."""
    averages = []
    for end in range(window, len(values)):
        averages.append(sum(values[end - window:end]) / window)
    return averages
