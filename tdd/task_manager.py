class TaskManager:
    def __init__(self):
        self.tasks = []

    def add_task(self, task_name: str):
        if task_name == '' or task_name is None:
            raise ValueError('Задача не может быть пустой и должна быть строкой!')
        self.tasks.append(task_name)

    def remove_task(self, task_name: str):
        if task_name in self.tasks:
            self.tasks.remove(task_name)
        else:
            raise ValueError(f"Задача '{task_name}' не найдена.")


    def process_next_task(self):
        if len(self.tasks) == 0:
            raise IndexError('Нет задач для обработки.')
        for task in self.tasks:
            if task is None:
                raise Exception("Ошибка при обработке задачи")


    def get_all_tasks(self):
        return self.tasks
