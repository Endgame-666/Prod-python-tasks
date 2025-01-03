import asyncio
import random
import time
from typing import Set
from event_loop_monitor import EventLoopMonitor
import pytest


class TaskManager:
    def __init__(
            self,
            num_tasks: int,
            blocking_chance: float = 0.3,
            max_blocking_time: float = 0.05,
            min_blocking_time: float = 0.01,
            max_non_blocking_time: float = 0.01,
            min_non_blocking_time: float = 0.001,
    ):
        self.num_tasks = num_tasks
        self.active_tasks: Set[asyncio.Task] = set()
        self.running = True
        self.blocking_chance = blocking_chance
        self.max_blocking_time = max_blocking_time
        self.min_blocking_time = min_blocking_time
        self.max_non_blocking_time = max_non_blocking_time
        self.min_non_blocking_time = min_non_blocking_time

        # semaphores to ensure execution order
        # when we aquire a semaphore, we prevent other blocking/non-blocking 
        # tasks from running and they wait for each other
        self.blocking_semaphore = asyncio.Semaphore(1)
        self.non_blocking_semaphore = asyncio.Semaphore(1)

    async def mixed_blocking_operation(self):
        """Randomly mix blocking and non-blocking operations."""
        try:
            if random.random() < self.blocking_chance: 
                async with self.blocking_semaphore:
                    time.sleep(random.uniform(self.min_blocking_time, self.max_blocking_time))
            else:
                async with self.non_blocking_semaphore:
                    await asyncio.sleep(random.uniform(self.min_non_blocking_time, self.max_non_blocking_time))
        except asyncio.CancelledError:
            pass

    async def maintain_tasks(self):
        """Maintain a constant number of running tasks."""
        while self.running:
            self.active_tasks = {task for task in self.active_tasks if not task.done()}
            
            # Create new tasks to maintain desired count
            while len(self.active_tasks) < self.num_tasks:
                task = asyncio.create_task(self.mixed_blocking_operation())
                self.active_tasks.add(task)
            
            await asyncio.sleep(1e-10)  # Small delay to prevent busing loop

    def stop(self):
        """Stop task management and cancel all tasks."""
        self.running = False
        for task in self.active_tasks:
            task.cancel()

async def main(
        duration: int = 10, 
        num_tasks: int = 50, 
        blocking_chance: float = 0.3,
        max_blocking_time: float = 0.05,
        min_blocking_time: float = 0.01,
        max_non_blocking_time: float = 0.01,
        min_non_blocking_time: float = 0.001
):
    """Main function to run the blocking analysis."""
    monitor = EventLoopMonitor()
    task_manager = TaskManager(num_tasks, blocking_chance, max_blocking_time, min_blocking_time, max_non_blocking_time, min_non_blocking_time)
    
    # Start the monitor
    monitor_task = asyncio.create_task(monitor.monitor_callback())
    manager_task = asyncio.create_task(task_manager.maintain_tasks())
    
    # Run for specified duration
    try:
        await asyncio.sleep(duration)
    finally:
        # Cleanup
        task_manager.stop()
        monitor_task.cancel()
        manager_task.cancel()
        
        # Wait for all tasks to complete
        pending = asyncio.all_tasks() - {asyncio.current_task()}
        await asyncio.gather(*pending, return_exceptions=True)
    
    return monitor.get_statistics()


@pytest.mark.parametrize(
    "blocking_chance,num_tasks,duration,max_blocking_time,min_blocking_time,max_non_blocking_time,min_non_blocking_time",
    [
         (0.5, 10, 4, 0.005, 0.001, 0.01, 0.001),
         (0.5, 100, 4, 0.005, 0.001, 0.01, 0.001),
         (0.5, 100, 5, 0.005, 0.001, 0.1, 0.01),
         (0.5, 10, 10, 0.5, 0.1, 0.01, 0.001)
    ],
)
@pytest.mark.asyncio
async def test_multiple_blocking_detection(
        blocking_chance: float, 
        num_tasks: int, 
        duration: int, 
        max_blocking_time: float, 
        min_blocking_time: float, 
        max_non_blocking_time: float, 
        min_non_blocking_time: float
):
    """Test if multiple blocking operations are detected."""
    stats = await main(duration=duration, num_tasks=num_tasks, blocking_chance=blocking_chance,
                       max_blocking_time=max_blocking_time, min_blocking_time=min_blocking_time,
                       max_non_blocking_time=max_non_blocking_time, min_non_blocking_time=min_non_blocking_time)
    print('\n')
    print(stats)

    assert stats["count"] > 1, "Should detect multiple blocking operations"
    assert stats["max"] > stats["min"], "Should have different blocking durations"
    expected_blocking_time = (max_blocking_time + min_blocking_time) / 2
    # average is much less accurate than median here due to the high variance
    print('\n')
    print(expected_blocking_time * 0.5, stats["median"], expected_blocking_time * 2)
    print('\n')
    print(expected_blocking_time * 0.5 < stats["median"])
    assert expected_blocking_time / 10 < stats["average"] < expected_blocking_time * 10, f"Average blocking time should be around the expected blocking time: {expected_blocking_time}, got {stats['average']}"
    assert expected_blocking_time * 0.5 < stats["median"] < expected_blocking_time * 2, f"Median blocking time should be around the expected blocking time: {expected_blocking_time}, got {stats['median']}"
    assert stats["max"] < max_blocking_time * num_tasks, f"Should not have blocking times longer than max_blocking_time * num_tasks: {max_blocking_time * num_tasks}, got {stats['max']}"
