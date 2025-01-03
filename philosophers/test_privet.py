import time
from typing import List
import threading
import random
import pytest
import test_public
import importlib
import logging
from typing import Callable
from functools import partial
from philosophers import Dinner, Philosopher, Fork, PhilosopherState


class PhilosopherSimulationChecker:
    def __init__(self, dinner: Dinner):
        self.dinner: Dinner = dinner
        self.philosophers: List[Philosopher] = dinner.philosophers
        self.forks: List[Fork] = dinner.forks
        self.meal_counts: List[int] = [0] * len(self.philosophers)
        self.last_check_time: float = time.time()

    def _check_deadlock_inner(self) -> bool:
        """
        Check if the system is in a deadlock state.
        A deadlock occurs when all philosophers are hungry and each has one fork.
        """
        state_snapshot = [(phil.is_hungry(), phil.left_fork.is_locked(), phil.right_fork.is_locked())
                          for phil in self.philosophers]

        # Check for deadlock using the snapshot
        if all(is_hungry for is_hungry, _, _ in state_snapshot) and \
                all(left_locked ^ right_locked for _, left_locked, right_locked in state_snapshot):
            return True
        return False

    def check_deadlock(self) -> bool:
        count_down = 10
        while count_down > 0:
            if not self._check_deadlock_inner():
                return False
            count_down -= 1
        return True

    def check_starvation(self, interval: float, min_meals_per_interval: int = 1) -> bool:
        current_time = time.time()
        if current_time - self.last_check_time >= interval:
            current_meal_counts = [phil.count_meals() for phil in self.philosophers]
            meals_in_interval = [current - previous for current, previous in zip(current_meal_counts, self.meal_counts)]
            self.meal_counts = current_meal_counts
            self.last_check_time = current_time
            return any(meals < min_meals_per_interval for meals in meals_in_interval)
        return False

    def check_mutual_exclusion(self) -> bool:
        """
        Check if no two adjacent philosophers are eating simultaneously.
        """
        n = len(self.philosophers)
        for i in range(n):
            if (self.philosophers[i].is_eating() and
                    self.philosophers[(i + 1) % n].is_eating()):
                return False
        return True

    def check_long_term_fairness(self, duration: float, tolerance: float = 0.6) -> bool:
        """
        Check if all philosophers are getting a fair chance to eat over a longer period.
        """
        initial_meal_counts = [phil.count_meals() for phil in self.philosophers]
        time.sleep(duration)
        final_meal_counts = [phil.count_meals() for phil in self.philosophers]
        meal_differences = [final - initial for initial, final in zip(initial_meal_counts, final_meal_counts)]
        avg_meals = sum(meal_differences) / len(meal_differences)
        return all(abs(count - avg_meals) / avg_meals <= tolerance for count in meal_differences)

    def comprehensive_check(self, duration: float, interval: float) -> bool:
        """
        Run a comprehensive check for a specified duration.
        """
        cycle_duration: float = 0.0001

        stop_event = threading.Event()
        results = {'deadlock': False, 'starvation': False, 'mutual_exclusion': True, 'long_term_fairness': True}

        def run_simulation_thread():
            self.dinner.run_simulation(duration=duration * 1.05)

        def check_deadlock_thread():
            while not stop_event.is_set():
                if self.check_deadlock():
                    if not stop_event.is_set():
                        results['deadlock'] = True
                        print("Deadlock detected!")
                        stop_event.set()
                time.sleep(cycle_duration)

        def check_starvation_thread():
            while not stop_event.is_set():
                if self.check_starvation(interval=interval):
                    if not stop_event.is_set():
                        results['starvation'] = True
                        print("Starvation detected!")
                        stop_event.set()
                time.sleep(cycle_duration)

        def check_mutual_exclusion_thread():
            while not stop_event.is_set():
                if not self.check_mutual_exclusion():
                    results['mutual_exclusion'] = False
                    print("Mutual exclusion violated!")
                    stop_event.set()
                time.sleep(cycle_duration)

        def check_long_term_fairness_thread():
            if not self.check_long_term_fairness(duration):
                results['long_term_fairness'] = False
                print("Long-term fairness violated!")
                stop_event.set()

        threads = [
            threading.Thread(target=run_simulation_thread),
            threading.Thread(target=check_deadlock_thread),
            threading.Thread(target=check_starvation_thread),
            threading.Thread(target=check_mutual_exclusion_thread),
            threading.Thread(target=check_long_term_fairness_thread)
        ]

        for thread in threads:
            thread.start()

        time.sleep(duration)
        stop_event.set()

        self.dinner.stop_simulation()
        for thread in threads:
            thread.join()
        print(f"Simulation completed, that's how dinner looks like:\n {self.dinner}")
        return not results['deadlock'] and not results['starvation'] and results['mutual_exclusion'] and results[
            'long_term_fairness']


@pytest.mark.timeout(15)
def test_varying_eating_times():
    num_philosophers = 5
    thinking_time = 0.0
    base_eating_time = 0.1
    duration = 5
    interval = 1.5

    def get_thinking_time():
        return thinking_time

    def get_eating_times():
        # Create varying eating times for each philosopher
        return [base_eating_time * (i + 1) for i in range(num_philosophers)]

    eating_times = get_eating_times()

    def get_eating_time(philosopher_index):
        return eating_times[philosopher_index]

    dinner = Dinner(num_philosophers, [get_thinking_time] * num_philosophers,
                    [partial(get_eating_time, i) for i in range(num_philosophers)])
    checker = PhilosopherSimulationChecker(dinner)

    assert checker.comprehensive_check(duration=duration, interval=interval), (
        f"Test failed for {num_philosophers} philosophers with varying eating times: {eating_times}"
    )


@pytest.mark.timeout(15)
@pytest.mark.parametrize(
    "num_philosophers, thinking_time_range, eating_time_range, duration, interval", [
        (2, (0.0001, 0.001), (0.0001, 0.001), 5, 1.5),
        (5, (0, 0), (0.00001, 0.01), 5, 1.5),
        (5, (0, 0), (0.001, 0.001), 5, 1.5),
        (7, (0, 0), (0.00001, 0.01), 5, 1.5),
        (7, (0, 0), (0.001, 0.001), 5, 1.5),
        (9, (0, 0), (0.00001, 0.01), 5, 1.5),
        (9, (0, 0), (0.001, 0.001), 5, 1.5),
        (10, (0.000001, 0.00001), (0.000001, 0.00001), 5, 1.5),
        (3, (0.0001, 0.001), (0.0001, 0.001), 5, 1.5),
        (5, (0.0001, 0.001), (0.0001, 0.001), 5, 1.5),
        (10, (0.0001, 0.001), (0.0001, 0.001), 5, 1.5),
        (7, (0.00001, 0.0001), (0.001, 0.01), 5, 1.5),
        (7, (0.001, 0.01), (0.00001, 0.0001), 5, 1.5),
        (5, (0, 0.0001), (0, 0.0001), 5, 1.5),
        (8, (0.0001, 0.1), (0.0001, 0.1), 5, 1.5),
        (6, (0, 0.01), (0, 0.01), 5, 1.5),
    ])
def test_n_philosophers(num_philosophers, thinking_time_range, eating_time_range, duration, interval):
    get_random_thinking = lambda: random.uniform(*thinking_time_range)
    get_random_eating = lambda: random.uniform(*eating_time_range)
    dinner = Dinner(num_philosophers, [get_random_thinking] * num_philosophers, [get_random_eating] * num_philosophers)
    checker = PhilosopherSimulationChecker(dinner)
    assert checker.comprehensive_check(duration=duration, interval=interval)


class PhilosopherBugged(threading.Thread):
    def __init__(
            self,
            index: int,
            left_fork: Fork,
            right_fork: Fork,
            get_think_time: Callable[[], float],
            get_eat_time: Callable[[], float]
    ):
        super().__init__()
        self.index: int = index
        self.left_fork: Fork = left_fork
        self.right_fork: Fork = right_fork
        self.state: str = PhilosopherState.THINKING
        self.eating_count: int = 0
        self.running: bool = True
        self.get_think_time: Callable[[], float] = get_think_time
        self.get_eat_time: Callable[[], float] = get_eat_time

    def run(self) -> None:
        while self.running:
            self.think()
            self.eat()

    def stop(self) -> None:
        self.running = False

    def think(self) -> None:
        self.state = PhilosopherState.THINKING
        think_time = self.get_think_time()
        logging.info(f"Philosopher {self.index} is thinking for {think_time:.2f} seconds.")
        time.sleep(think_time)

    def eat(self) -> None:
        self.state = PhilosopherState.HUNGRY
        logging.info(f"Philosopher {self.index} is hungry for a {self.count_meals()} time and trying to acquire forks.")

        first_fork, second_fork = self.left_fork, self.right_fork

        first_fork.pick_up()
        logging.info(f"Philosopher {self.index} acquired {first_fork}.")
        second_fork.pick_up()
        logging.info(f"Philosopher {self.index} acquired {second_fork}.")

        eat_time = self.get_eat_time()
        self.state = PhilosopherState.EATING
        logging.info(f"Philosopher {self.index} is eating for {eat_time:.2f} seconds.")
        time.sleep(eat_time)
        self.eating_count += 1
        self.state = PhilosopherState.THINKING
        first_fork.put_down()
        second_fork.put_down()
        logging.info(
            f"Philosopher {self.index} finished eating for a {self.count_meals()} time and released both forks.")

    def is_eating(self) -> bool:
        return self.state == PhilosopherState.EATING

    def is_hungry(self) -> bool:
        return self.state == PhilosopherState.HUNGRY

    def is_thinking(self) -> bool:
        return self.state == PhilosopherState.THINKING

    def count_meals(self) -> int:
        return self.eating_count


@pytest.fixture
def use_bugged_implementation():
    # Store the original Philosopher class
    import philosophers
    original_philosopher = philosophers.Philosopher

    # Replace with the bugged implementation
    philosophers.Philosopher = PhilosopherBugged

    # Reload the test_public module to use the bugged implementation
    importlib.reload(test_public)

    yield  # This is where the test runs

    # Restore the original Philosopher class
    philosophers.Philosopher = original_philosopher
    # Reload test_public to restore original implementation
    importlib.reload(test_public)


@pytest.mark.timeout(60)
def test_bugged_implementation_catches_all_public_tests(use_bugged_implementation):
    # Run all tests from test_public
    test_results = pytest.main(["-n", "auto", "-v", "--tb=no", "test_public.py"])
    print(f"Test results: {test_results}")
    # Check if any test failed (non-zero exit code)
    assert test_results != 0, "Expected at least one test in test_public to fail with the bugged implementation"