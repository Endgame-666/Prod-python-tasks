import time
from mock import patch

import aiohttp
import aioresponses
import pytest
import pytest_asyncio


import request_app
import server


@pytest.fixture
def reset_server_state():
    """автообновлятор"""
    server.request_count = 0
    server.first_request_time = None
    server.test_complete = False


@pytest_asyncio.fixture
async def mock_server(aiohttp_server, reset_server_state):
    app = server.create_app()
    return await aiohttp_server(app)


@pytest.mark.asyncio
async def test_request_app_basic(mock_server):
    """Базовый тест: тестируем отправку 100 запросов"""
    total_requests = 100
    concurrent_requests = 10
    url = f"http://{mock_server.host}:{mock_server.port}/"

    await request_app.main(url, total_requests, concurrent_requests)

    assert server.request_count == total_requests


class MockResponse:
    def __init__(self, status):
        self.status = status

    async def text(self):
        return 'Mocked response'

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


class MockClientSession:
    def __init__(self, *args, **kwargs):
        pass

    def get(self, url, *args, **kwargs):
        return MockResponse(status=200)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


@pytest.mark.asyncio
async def test_send_10000_requests_under_one_second():
    """Проверяем, что 10 000 запросов выполняются менее чем за одну секунду."""
    url = 'http://example.com/test'
    total_requests = 10000
    concurrent_requests = 10000

    with patch('builtins.print'), patch('aiohttp.ClientSession', new=MockClientSession):
        start_time = time.time()
        await request_app.main(url, total_requests, concurrent_requests)
        end_time = time.time()

    total_time = end_time - start_time

    assert total_time <= 1.0, f'Время выполнения {total_time:.2f} сек превышает 1 секунду'

    print(f"Total time taken: {total_time:.4f} seconds")


@pytest.mark.asyncio
async def test_send_request_exception():
    """Проверяем что ошибки обрабатываются"""
    with aioresponses.aioresponses() as m:
        url = "http://testserver/"
        m.get(url, exception=Exception("Network error"))
        async with aiohttp.ClientSession() as session:
            await request_app.send_request(session, url)

