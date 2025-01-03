from unittest.mock import patch

from task import broken_random, patch_random

BLAT_NUMBERS = [111, 222, 333, 444, 555, 666, 777, 888, 999]


def test_mock_called_in_module():
    """
    Проверяет, что модуль mock был вызван в коде. Специальный тест, если у вас падает, подумайте почему!
    """
    with patch('task.patch') as mock_patch:
        from task import broken_random
        broken_random()
        assert mock_patch.called, "Функция patch должна быть вызвана в модуле tdd)\n" \
                                  "Если увидели это условие в CI прогоняйте локально в начале!"


def test_patch_random_non_blat_number():
    """
    Тест проверяет как был написана функция которая патчит рандом. Если не проходит, чините ее.
    """

    assert patch_random(543) == 555, "Функция должна скорректировать число до 555."
    assert patch_random(876) == 888, "Функция должна скорректировать число до 888."
    assert patch_random(112) == 111, "Функция должна скорректировать число до 111."


def test_check_multiple_calls():
    """
    Продолжение теста, выше. Только детальнее.
    """
    with patch('random.randint', side_effect=[543, 666, 777]):
        assert broken_random() == 555, "Функция должна число 543 докрутить до 555"
        assert broken_random() == 666, "Функция должна вернуть 666 как есть."
        assert broken_random() == 777, "Функция должна вернуть 777 как есть!"


def test_check_function_return_blat_numbers():
    """
    Тест-убийца. Проверяет полную корректность работы решение задачи
    """
    assert broken_random() in BLAT_NUMBERS
