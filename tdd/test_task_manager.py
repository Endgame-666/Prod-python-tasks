import pytest
from task_manager import TaskManager


@pytest.fixture(scope='function')
def task_manager():
    return TaskManager()


def test_add_task_success(task_manager):
    task_manager.add_task('Task1')
    assert task_manager.get_all_tasks() == ['Task1']


def test_add_task_empty(task_manager):
    with pytest.raises(ValueError) as exc:
        task_manager.add_task('')
    assert str(exc.value) == 'Задача не может быть пустой и должна быть строкой!'


def test_add_task_none(task_manager):
    with pytest.raises(ValueError) as exc:
        task_manager.add_task(None)
    assert str(exc.value) == 'Задача не может быть пустой и должна быть строкой!'


def test_process_next_task_no_tasks(task_manager):
    with pytest.raises(IndexError) as exc:
        task_manager.process_next_task()
    assert str(exc.value) == 'Нет задач для обработки.'


def test_remove_task_success(task_manager):
    tasks = ['Task1', 'Task2', 'Task3']
    for task in tasks:
        task_manager.add_task(task)
    task_manager.remove_task('Task2')
    assert task_manager.get_all_tasks() == ['Task1', 'Task3']


def test_remove_task_not_found(task_manager):
    task_manager.add_task('Task1')
    with pytest.raises(ValueError) as exc:
        task_manager.remove_task('Task3')
    assert str(exc.value) == "Задача 'Task3' не найдена."


def test_process_next_task_exception(task_manager):
    task_manager.tasks.append(None)
    with pytest.raises(Exception) as exc:
        task_manager.process_next_task()
    assert "Ошибка при обработке задачи" in str(exc.value)
