from hypothesis import given, settings, assume, HealthCheck
from hypothesis import strategies as st
import pytest
from example import generate_unique_numbers


@given(
    n=st.integers(min_value=1, max_value=1000),
    min_value=st.integers(min_value=1, max_value=5000),
    max_value=st.integers(min_value=5001, max_value=10000)
)
@settings(suppress_health_check=[HealthCheck.too_slow])
def test_generate_unique_numbers(n, min_value, max_value):
    assume(max_value - min_value + 1 >= n)

    result = generate_unique_numbers(n, min_value, max_value)

    assert len(result) == n, f"Длина результата {len(result)} не совпадает с n != {n}"
    assert len(result) == len(set(result)), "Есть дубликаты!!!!"

    for num in result:
        assert min_value <= num <= max_value, f"Число {num} выходит за пределы {min_value}-{max_value}"


@pytest.mark.parametrize("n, min_value, max_value", [
    (1, 1, 10000),
    (1000, 1, 1000),
])
def test_extreme_values_for_numbers(n, min_value, max_value):
    result = generate_unique_numbers(n, min_value, max_value)

    assert len(result) == n, f"Длина результата {len(result)} не совпадает с n != {n}"
    assert len(result) == len(set(result)), "Список содержит дубликаты"

    for num in result:
        assert min_value <= num <= max_value, f"Число {num} выходит за пределы {min_value}-{max_value}"
