from philosophers import Dinner, Philosopher, Fork, think_time, eat_time
from typing import List
import logging
import time

class PhilosopherSimulationChecker:
    def __init__(self, dinner: Dinner):
        self.dinner: Dinner = dinner
        self.philosophers: List[Philosopher] = dinner.philosophers
        self.forks: List[Fork] = dinner.forks

    def check_deadlock(self) -> bool:
        """
        Check if the system is in a deadlock state.
        """

        for philosopher in self.philosophers:
            if philosopher.is_hungry() and not philosopher.is_eating():

                if (self.forks[philosopher.index].is_locked() and
                        self.forks[(philosopher.index + 1) % len(self.forks)].is_locked()):
                    return True
        return False

    def check_starvation(self, timeout: int = 10) -> bool:
        """
        Check if any philosopher is starving (hasn't eaten for a long time).
        """
        for philosopher in self.philosophers:
            if time.time() - philosopher.last_eaten_time > timeout and philosopher.count_meals() == 0:
                return True
        return False

    def check_mutual_exclusion(self) -> bool:
        """
        Check if no two adjacent philosophers are eating simultaneously.
        """
        for i in range(len(self.philosophers)):
            if self.philosophers[i].is_eating() and self.philosophers[(i + 1) % len(self.philosophers)].is_eating():
                return False
        return True

    def comprehensive_check(self, duration: float) -> bool:
        """
        Run a comprehensive check for a specified duration.
        """
        start_time = time.time()
        while time.time() - start_time <= duration:
            if (self.check_deadlock() or
                    self.check_starvation() or
                    not self.check_mutual_exclusion()):
                logging.warning("Проблема в симуляции философов!")
                return False
            time.sleep(0.1)
        return True

import unittest
import random

class TestPhilosopherSimulation(unittest.TestCase):
    def setUp(self):
        thinking_time_range, eating_time_range = (0.01, 0.005), (0.01, 0.005)
        get_random_thinking = lambda: random.uniform(*thinking_time_range)
        get_random_eating = lambda: random.uniform(*eating_time_range)
        self.dinner = Dinner(5, [get_random_thinking] * 5, [get_random_eating] * 5)
        self.checker = PhilosopherSimulationChecker(self.dinner)

    def test_deadlock(self):
        """
        Проверяем, что симуляция корректно обрабатывает взаимоблокировки.
        """
        result = self.checker.comprehensive_check(duration=5.0)
        self.assertTrue(result, "Симуляция попала в взаимоблокировку.")

    def test_starvation(self):
        """
        Проверяем, что симуляция корректно обрабатывает проблему голодания.
        """
        # Тайм-аут голодания 10 секунд (можно настроить)
        result = not self.checker.check_starvation(timeout=10)
        self.assertTrue(result, "В симуляции произошло голодание философа.")

    def test_thinking(self):
        """
        Проверяем, что философы корректно размышляют.
        """
        philosophers_thinking = all(philosopher.is_thinking() for philosopher in self.dinner.philosophers)
        self.assertTrue(philosophers_thinking, "Некоторые философы не думают.")

    def test_comprehensive_check(self):
        """
        Полный тест на корректность симуляции: проверка взаимоблокировок, голодания, и взаимного исключения.
        """
        result = self.checker.comprehensive_check(duration=5.0)
        self.assertTrue(result, "Общая проверка симуляции не пройдена.")

if __name__ == '__main__':
    unittest.main()
