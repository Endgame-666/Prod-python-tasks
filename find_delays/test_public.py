import pytest
from unittest.mock import patch
from coroutines import main
import time
from io import StringIO

@pytest.mark.asyncio
async def test_coroutines_output():
    expected_output = (
        "First message from coroutine 1\n"
        "First message from coroutine 2\n"
        "First message from coroutine 3\n"
        "Second message from coroutine 3\n"
        "Second message from coroutine 2\n"
        "Second message from coroutine 1\n"
        "Third message from coroutine 2\n"
        "Third message from coroutine 3\n"
        "Third message from coroutine 1\n"
        "Forth message from coroutine 1\n"
        "Forth message from coroutine 3\n"
        "Forth message from coroutine 2\n"
        "Fifth message from coroutine 2\n"
        "Fifth message from coroutine 1\n"
        "Fifth message from coroutine 3\n"
    )

    with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
        await main()
        output = mock_stdout.getvalue()
        assert output == expected_output, "Вывод программы не совпадает с ожидаемым"
            

@pytest.mark.asyncio
async def test_execution_time():
    start_time = time.perf_counter()
    await main()
    end_time = time.perf_counter()
    execution_time = end_time - start_time
    assert 0.9 <= execution_time <= 1.3, f"Код должен выполняться в диапазоне от 0.9 до 1.3 секунды, но занял {execution_time} секунд"
