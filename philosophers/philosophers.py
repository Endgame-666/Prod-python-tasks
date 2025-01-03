
from enum import StrEnum
from typing import Optional
import time

from typing import List
import threading
import random

import logging
from typing import Callable
from functools import partial

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)



class Fork:
    def __init__(self, index: int):
        self.lock: threading.Lock = threading.Lock()
        self.index: int = index

    def is_locked(self) -> bool:
        return self.lock.locked()

class PhilosopherState(StrEnum):
    THINKING = "thinking"
    HUNGRY = "hungry"
    EATING = "eating"

class Philosopher(threading.Thread):
    def __init__(
        self,
        index: int,
        left_fork: Fork,
        right_fork: Fork,
        get_think_time: Callable[[], float],
        get_eat_time: Callable[[], float],
        dinner,
        max_meals: Optional[int] = None,

    ):
        super().__init__()
        self.index: int = index
        self.left_fork: Fork = left_fork
        self.right_fork: Fork = right_fork
        self.max_meals = max_meals
        self.get_think_time = get_think_time
        self.get_eat_time = get_eat_time
        self.state = PhilosopherState.THINKING
        self.eaten_meals: int = 0
        self.running = True
        self.dinner = dinner
        self.last_eaten_time = time.time()
        self.forks = ((self.left_fork, self.right_fork) if min(self.left_fork.index,
                                                          self.right_fork.index) == self.left_fork else (
        self.right_fork, self.left_fork))


    def run(self):
        logging.info(f"Философ {self.index} начал симуляцию.")
        while self.running and (self.max_meals is None or self.eaten_meals < self.max_meals):
            self.think()
            self.hungry()
            self.eat()
        logging.info(f"Философ {self.index} завершил симуляцию. Всего съел {self.eaten_meals} раз.")

    def think(self):
        self.state = PhilosopherState.THINKING
        think_time = self.get_think_time()
        logging.info(f"Философ {self.index} думает в течение {think_time:.2f} секунд.")
        time.sleep(think_time)

    def hungry(self):
        self.state = PhilosopherState.HUNGRY
        logging.info(f"Философ {self.index} стал голодным и пытается взять вилки.")

    def eat(self):
        while True:
            with self.dinner.lock:
                if self.dinner.global_meal_counter % self.dinner.num_philosophers == self.index:
                    break
            time.sleep(0.01)

        forks = ((self.left_fork, self.right_fork) if min(self.left_fork.index,
                                                          self.right_fork.index) == self.left_fork else (
        self.right_fork, self.left_fork))
        first_fork, second_fork = forks

        acquired_first = first_fork.lock.acquire(timeout=0.1)
        if not acquired_first:
            time.sleep(random.uniform(0.01, 0.05))
            return

        acquired_second = second_fork.lock.acquire(timeout=0.1)
        if not acquired_second:
            first_fork.lock.release()
            time.sleep(random.uniform(0.01, 0.05))
            return

        # Eating process
        self.state = PhilosopherState.EATING
        eat_time = self.get_eat_time()
        logging.info(f"Философ {self.index} начинает есть в течение {eat_time:.2f} секунд.")
        time.sleep(eat_time)
        self.eaten_meals += 1

        # Release forks
        second_fork.lock.release()
        first_fork.lock.release()

        with self.dinner.lock:
            self.dinner.global_meal_counter += 1

    def stop(self):
        self.running = False
        logging.info(f"Философ {self.index} получает сигнал остановки.")

    def is_eating(self) -> bool:
        return self.state == PhilosopherState.EATING

    def is_hungry(self) -> bool:
        return self.state == PhilosopherState.HUNGRY

    def is_thinking(self) -> bool:
        return self.state == PhilosopherState.THINKING

    def count_meals(self) -> int:
        return self.eaten_meals

class Dinner:
    def __init__(
        self,
        num_philosophers: int,
        get_think_time: List[Callable[[], float]],
        get_eat_time: List[Callable[[], float]],
        max_meals: Optional[int] = None
    ):
        self.num_philosophers = num_philosophers
        self.forks = [Fork(i) for i in range(num_philosophers)]
        self.philosophers = [
            Philosopher(
                i,
                self.forks[i],
                self.forks[(i + 1) % num_philosophers],
                get_think_time[i],
                get_eat_time[i],
                self,
                max_meals
            ) for i in range(num_philosophers)
        ]
        self.global_meal_counter = 0
        self.lock = threading.Lock()

    def run_simulation(self, duration: Optional[float] = None, max_cycles: Optional[int] = None):
        logging.info("Запуск симуляции ужина философов.")
        for philosopher in self.philosophers:
            philosopher.start()

        if duration is not None:
            logging.info(f"Симуляция будет работать {duration} секунд.")
            time.sleep(duration)
            self.stop_simulation()
        elif max_cycles is not None:
            for philosopher in self.philosophers:
                philosopher.join()

        logging.info("Симуляция ужина завершена.")

    def stop_simulation(self):
        logging.info("Остановка симуляции ужина.")
        for philosopher in self.philosophers:
            philosopher.stop()
        for philosopher in self.philosophers:
            philosopher.join()
        logging.info("Все философы остановлены.")


def think_time():
    return random.uniform(0.5, 2.0)

def eat_time():
    return random.uniform(0.5, 1.5)



