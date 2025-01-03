import pytest

from parse_duration import parse_duration

def test_all_units():
    assert parse_duration("10ns") == 10
    assert parse_duration("10us") == 10_000
    assert parse_duration("10ms") == 10_000_000
    assert parse_duration("10s") == 10_000_000_000
    assert parse_duration("10m") == 600_000_000_000
    assert parse_duration("10h") == 36_000_000_000_000

def test_negative_durations():
    assert parse_duration("-10ns") == -10
    assert parse_duration("-10us") == -10_000
    assert parse_duration("-10ms") == -10_000_000
    assert parse_duration("-10s") == -10_000_000_000
    assert parse_duration("-10m") == -600_000_000_000
    assert parse_duration("-10h") == -36_000_000_000_000

def test_fractional_all_units():
    assert parse_duration("0.5ns") == 0
    assert parse_duration("0.5us") == 500
    assert parse_duration("0.5ms") == 500_000
    assert parse_duration("0.5s") == 500_000_000
    assert parse_duration("0.5m") == 30_000_000_000
    assert parse_duration("0.5h") == 1_800_000_000_000

def test_combined_fractional_durations():
    assert parse_duration("1h30m") == 5_400_000_000_000
    assert parse_duration("0.5h30m") == 3_600_000_000_000

def test_invalid_units():
    with pytest.raises(ValueError):
        parse_duration("1q")
    with pytest.raises(ValueError):
        parse_duration("1hour")

def test_empty_string():
    with pytest.raises(ValueError):
        parse_duration("")

def test_invalid_format_1():
    with pytest.raises(ValueError):
        parse_duration("5..5s")

def test_multiple_units():
    assert parse_duration("2h30m45s") == 9_045_000_000_000
    assert parse_duration("1h15m30.5s") == 4_530_500_000_000

def test_large_durations():
    assert parse_duration("999999h") == 3_599_996_400_000_000_000
    assert parse_duration("12345678ms") == 12_345_678_000_000

def test_small_durations():
    assert parse_duration("1ns") == 1
    assert parse_duration("500µs") == 500_000

def test_signs_in_durations():
    assert parse_duration("-1m") == -60_000_000_000
    assert parse_duration("+2h") == 7_200_000_000_000

def test_missing_unit():
    with pytest.raises(ValueError, match="missing unit"):
        parse_duration("10")


def test_invalid_unit():
    with pytest.raises(ValueError, match="unknown unit"):
        parse_duration("10xs")

def test_overflow_error():
    with pytest.raises(ValueError):
        parse_duration("9999999999999999999999999h")

def test_invalid_format_2():
    with pytest.raises(ValueError, match="invalid duration"):
        parse_duration("abc")


