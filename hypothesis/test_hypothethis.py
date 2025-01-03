import string
import random
from hypothesis import given, settings, HealthCheck
from hypothesis import strategies as st
import pytest
from unittest.mock import patch

from hypothethis import generate_unique_strings


def test_check_realization():
    result = generate_unique_strings(100)

    assert len(result) == 100
    assert sorted(set(result)) == sorted(result)

def test_for_rez():
    assert generate_unique_strings(1) != generate_unique_strings(1)
    assert generate_unique_strings(0) == []


@given(st.integers(min_value=1, max_value=1000))
@settings(suppress_health_check=[HealthCheck.too_slow])
def test_generate_unique_strings(n):
    result = generate_unique_strings(n)
    assert len(result) == n
    assert len(set(result)) == len(result)
    for s in result:
        assert 5 <= len(s) <= 10, f"Длина строки {len(s)} не соответствует диапазону!"
        assert all(c.isalnum() for c in s), "Строка содержит неразрешенные символы"


def test_import_usage():
    random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    assert len(random_str) == 8, "Функция random.choices не сработала корректно"
    assert random_str.isalnum(), "Сгенерированная строка содержит недопустимые символы"


def test_function_called():
    with patch('hypothethis.generate_unique_strings') as mock_func:
        from hypothethis import generate_unique_strings
        generate_unique_strings(5)
        assert mock_func.called


def test_module_import():
    from hypothethis import generate_unique_strings
    assert callable(generate_unique_strings), "Функция generate_unique_strings должна быть доступна"


def test_empty_case():
    result = generate_unique_strings(0)
    assert result == []

def test_single_string():
    result = generate_unique_strings(1)
    assert len(result) == 1
    assert 5 <= len(result[0]) <= 10
    assert len(set(result)) == len(result)

@pytest.mark.parametrize("n", [1, 5, 10, 100])
def test_various_lengths(n):
    result = generate_unique_strings(n)
    assert len(result) == n
    assert len(set(result)) == len(result)

    for s in result:
        assert 5 <= len(s) <= 10
        assert all(c.isalnum() for c in s), "Строка содержит недопустимые символы!"
