from aiohttp import web
import asyncio
import time

request_count = 0
first_request_time = None

test_complete = False


async def handle_request(request):
    global request_count, first_request_time, test_complete
    if first_request_time is None:
        first_request_time = time.time()
    request_count += 1

    if request_count > 10000 and (time.time() - first_request_time) <= 1:
        print("Поздравляем! Сервер успешно обработал более 10000 запросов за одну секунду и будет остановлен.")
        test_complete = True
        return web.Response(text="Server is shutting down due to high load.")
    elif (time.time() - first_request_time) > 1 and request_count <= 100:
        raise web.HTTPInternalServerError(
            text="Cлишком медленно: не удалось обработать 10000 запросов за одну секунду.")

    return web.Response(text="Request processed!")


async def handle_count(request):
    return web.Response(text=f"Total requests: {request_count}")


async def shutdown():
    await asyncio.sleep(0.1)
    loop.stop()


def create_app():
    app = web.Application()
    app.router.add_get('/', handle_request)
    app.router.add_get('/count', handle_count)
    return app


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    app = create_app()
    runner = web.AppRunner(app)
    loop.run_until_complete(runner.setup())
    site = web.TCPSite(runner, 'localhost', 8888)
    loop.run_until_complete(site.start())
    print("Server is running on http://localhost:8888/")
    print("Request count available at http://localhost:8888/count")
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("Server stopped by user")
