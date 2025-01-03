import yarl
from aiohttp import web
import aiohttp
from urllib.parse import urlparse

async def request_handler(request: web.Request) -> web.Response:
    """
    Проверяет, что запрос содержит корректный http(s) URL в параметрах:
    /fetch?url=http%3A%2F%2Fexample.com%2F
    Затем выполняет асинхронную загрузку указанного ресурса и возвращает его содержимое с кодом HTTP-статуса.
    Если URL не содержит схему (http или https) или является некорректным, возвращается ответ с кодом 400 (Bad Request).
    При ошибках запроса возвращается 502 (Bad Gateway).
    :param request: Объект запроса aiohttp.web.Request
    :return: Объект ответа aiohttp.web.Response
    """
    url = request.query.get("url")
    if not url:
        return web.Response(text="No url to fetch", status=400)
    parsed_url = urlparse(url)
    if parsed_url.scheme is '':
        return web.Response(text="Empty url scheme", status=400)

    if parsed_url.scheme not in ('http', 'https'):
        return web.Response(text=f"Bad url scheme: {parsed_url.scheme}", status=400)

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                content = await response.text()
                return web.Response(text=content, status=response.status)
    except aiohttp.ClientError:
        return web.Response(text="Bad Gateway", status=502)


async def initialize_app(app: web.Application) -> None:
    """
    Настраивает hanler'ы для приложения и инициализирует aiohttp-сессию для выполнения запросов.
    :param app: app to apply settings with
    """
    app['session'] = aiohttp.ClientSession()
    app.router.add_get('/fetch', request_handler)
    app.on_cleanup.append(close_app)


async def close_app(app: web.Application) -> None:
    """
    Завершение приложения: закрывает aiohttp-сессию
    :param app: приложение, которое должно завершиться
    """
    await app['session'].close()

