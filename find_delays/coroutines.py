import asyncio


# Текущая реализация не проходит тесты! Вам нужно настроить задачи, так чтобы оно проходило тесты!
a = 2.2
b = 2.4
c = 2.6

async def coroutine_1(delay=0.1):
    print("First message from coroutine 1")
    await asyncio.sleep(delay * 2.6)
    print("Second message from coroutine 1")
    await asyncio.sleep(delay * 2.6)
    print("Third message from coroutine 1")
    await asyncio.sleep(delay * 1.75)
    print("Forth message from coroutine 1")
    await asyncio.sleep(delay * 2.35)
    print("Fifth message from coroutine 1")


async def coroutine_2(delay=0.1):
    print("First message from coroutine 2")
    await asyncio.sleep(delay * 2.4)
    print("Second message from coroutine 2")
    await asyncio.sleep(delay * 2.2)
    print("Third message from coroutine 2")
    await asyncio.sleep(delay * 2.6)
    print("Forth message from coroutine 2")
    await asyncio.sleep(delay * 1.8)
    print("Fifth message from coroutine 2")


async def coroutine_3(delay=0.1):
    print("First message from coroutine 3")
    await asyncio.sleep(delay * 2.25)
    print("Second message from coroutine 3")
    await asyncio.sleep(delay * b)
    print("Third message from coroutine 3")
    await asyncio.sleep(delay * b)
    print("Forth message from coroutine 3")
    await asyncio.sleep(delay * c)
    print("Fifth message from coroutine 3")


async def main():
    await asyncio.gather(
        coroutine_1(),
        coroutine_2(),
        coroutine_3(),
    )


asyncio.run(main())