import asyncio
import time
import statistics
from typing import List
import asyncio.exceptions


class EventLoopMonitor:
    def __init__(self):
        self.blocking_times: List[float] = []
        self.threshold = 0.002
    async def monitor_callback(self) -> None:
        """
        Callback для измерения времени между итерациями цикла событий.
        Работает асинхронно как фоновая задача в event loop.
        """
        last_time = time.time()
        while True:
            await asyncio.sleep(0.0)
            elapsed = time.time() - last_time
            elapsed = round(elapsed, 6)
            if elapsed > self.threshold + 0.0001:
                self.blocking_times.append(elapsed)
            last_time = time.time()

    def get_statistics(self) -> dict:
        """
        Подсчет статистики о времени блокировки.
        Возвращает словарь со средним, медианным, максимальным временем и числом блокировок.
        """
        if not self.blocking_times:
            return {
                "count": 0,
                "average": 0.0,
                "median": 0.0,
                "max": 0.0,
                "num_blocking": 0
            }
        print(self.blocking_times)
        avg_blocking = sum(self.blocking_times) / len(self.blocking_times)
        median_blocking = round(abs(statistics.median_grouped(sorted(self.blocking_times), 0.015)), 4)
        max_blocking = max(self.blocking_times)
        min_blocking = min(self.blocking_times)

        return {
            "count": len(self.blocking_times),
            "average": avg_blocking,
            "median": median_blocking,
            "max": max_blocking,
            "min": min_blocking,
            "num_blocking": len(self.blocking_times)
        }
