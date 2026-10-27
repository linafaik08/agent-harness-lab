from durations import parse_duration


def test_hours_and_minutes():
    assert parse_duration("1h30m") == 5400


def test_minutes_and_seconds():
    assert parse_duration("2m5s") == 125


def test_single_units():
    assert parse_duration("45s") == 45
    assert parse_duration("1h") == 3600
