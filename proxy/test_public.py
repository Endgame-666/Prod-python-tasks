import asyncio
import time

import aiohttp
from aiohttp import web
from aiohttp.test_utils import AioHTTPTestCase, make_mocked_request
from yarl import URL

from proxy import request_handler, initialize_app, close_app


class ProxyFetchTests(AioHTTPTestCase):
    async def get_application(self) -> web.Application:
        async def success_endpoint(request: web.Request) -> web.Response:
            raise web.HTTPOk(text='Success')

        async def error_endpoint(request: web.Request) -> web.Response:
            raise web.HTTPInternalServerError(text='Internal server error')

        async def delay_endpoint(request: web.Request) -> web.Response:
            await asyncio.sleep(1)
            raise web.HTTPOk(text='Delayed response')

        app_instance = web.Application()
        app_instance.router.add_get('/success', success_endpoint)
        app_instance.router.add_get('/error', error_endpoint)
        app_instance.router.add_get('/delay', delay_endpoint)
        return app_instance

    def generate_server_url(self, path: str) -> str:
        return str(URL.build(
            scheme='http',
            host=self.server.host,
            port=self.server.port,
            path=path
        ))

    @staticmethod
    def prepare_fetch_url(destination_url: str) -> str:
        return str(URL.build(
            path='/fetch',
            query={'url': destination_url}
        ))

    async def test_fetch_success(self) -> None:
        async with aiohttp.ClientSession() as session:
            request = make_mocked_request(
                'GET', self.prepare_fetch_url(self.generate_server_url('/success'))
            )
            request.app['session'] = session
            try:
                response = await request_handler(request)
            except web.HTTPException as exc:
                response = exc
        assert response.body == b'Success'
        assert response.status == 200

    async def test_fetch_error(self) -> None:
        async with aiohttp.ClientSession() as session:
            request = make_mocked_request(
                'GET', self.prepare_fetch_url(self.generate_server_url('/error'))
            )
            request.app['session'] = session
            try:
                response = await request_handler(request)
            except web.HTTPException as exc:
                response = exc
        assert response.body == b'Internal server error'
        assert response.status == 500

    async def test_invalid_url(self) -> None:
        async with aiohttp.ClientSession() as session:
            request = make_mocked_request('GET', self.prepare_fetch_url('invalid_url'))
            request.app['session'] = session
            try:
                response = await request_handler(request)
            except web.HTTPException as exc:
                response = exc
        assert response.status == 400
        assert response.body == b'Empty url scheme'

    async def test_missing_url(self) -> None:
        async with aiohttp.ClientSession() as session:
            request = make_mocked_request('GET', '/fetch')
            request.app['session'] = session
            try:
                response = await request_handler(request)
            except web.HTTPException as exc:
                response = exc
        assert response.status == 400
        assert response.body == b'No url to fetch'

    async def test_unsupported_scheme(self) -> None:
        async with aiohttp.ClientSession() as session:
            request = make_mocked_request(
                'GET', self.prepare_fetch_url('ftp://example.com/')
            )
            request.app['session'] = session
            try:
                response = await request_handler(request)
            except web.HTTPException as exc:
                response = exc
        assert response.status == 400
        assert response.body == b'Bad url scheme: ftp'

    async def test_concurrent_fetches(self) -> None:
        async with aiohttp.ClientSession() as session:
            tasks = []
            start = time.time()
            for _ in range(3):
                request = make_mocked_request(
                    'GET', self.prepare_fetch_url(self.generate_server_url('/delay'))
                )
                request.app['session'] = session
                tasks.append(request_handler(request))
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            end = time.time()
        assert end - start < 1.5
        assert all(response.status == 200 for response in responses)


class AppLifecycleTests(AioHTTPTestCase):
    async def get_application(self) -> web.Application:
        app_instance = web.Application()
        await initialize_app(app_instance)

        async def test_endpoint(request: web.Request) -> web.Response:
            raise web.HTTPOk(text='pong')

        app_instance.router.add_get('/ping', test_endpoint)
        return app_instance

    async def tearDownAsync(self) -> None:
        await close_app(self.server.app)

    def generate_full_url(self, path: str, query: dict[str, str] | None = None) -> str:
        return str(URL.build(
            scheme='http',
            host=self.server.host,
            port=self.server.port,
            path=path,
            query=query
        ))

    async def execute_fetch(
        self, session: aiohttp.ClientSession, url_to_fetch: str
    ) -> aiohttp.ClientResponse:
        url = str(URL(
            self.generate_full_url(
                path='/fetch',
                query={'url': url_to_fetch}
            )
        ))

        return await session.get(url)

    async def test_app_fetching(self) -> None:
        async with aiohttp.ClientSession() as session:
            response = await self.execute_fetch(
                session, self.generate_full_url(path='/ping')
            )
            assert response.status == 200
            assert await response.text() == 'pong'
            response = await self.execute_fetch(
                session, self.generate_full_url(path='/ping')
            )
            assert response.status == 200
