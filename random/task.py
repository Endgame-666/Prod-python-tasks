import random
import unittest.mock
from unittest.mock import patch


def patch_random(x: int):
    """
    Функция которая должна патчить в исполнении randint
    """
    blat_numbers = [111, 222, 333, 444, 555, 666, 777, 888, 999]
    return min(blat_numbers, key=lambda b: int(abs(b - x)))


def broken_random() -> int:
    """
    Генерация случайного числа с использованием patch.
    """
    original_random = random.randint
    with patch('random.randint') as mock_randint:
        mock_randint.return_value = patch_random(original_random(100, 1000))
        return random.randint(100, 1000)