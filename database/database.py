from abc import abstractmethod
from dataclasses import dataclass
from pathlib import Path
from types import TracebackType
from typing import Protocol, Callable
import hashlib
import json


class SupportsStr(Protocol):
    """Класс с абстрактным методом `__str__`."""

    @abstractmethod
    def __str__(self) -> str:
        """Привести тип к `str`"""


@dataclass
class StorageAdapter:
    """Адаптер базы данных."""

    _storage_directory: Path

    def __post_init__(self) -> None:
        self.storage_queue: list[tuple] = list()

    @staticmethod
    def defer(func: Callable) -> Callable:
        """Декоратор для отложенного вызова функции"""
        def wrapper(self: 'StorageAdapter', *args, **kwargs):
            self.storage_queue.append((func, args, kwargs))
        return wrapper

    def _is_directory_exists(self) -> None:
        """Проверить и создать директорию, если её нет или она была заменена символической ссылкой."""
        if self._storage_directory.exists(follow_symlinks = False):
            if self._storage_directory.is_symlink() or self._storage_directory.is_file():
                 self._storage_directory.unlink()
        if not self._storage_directory.exists():
            self._storage_directory.mkdir(parents=True, exist_ok=True)

    def get(self, key: SupportsStr) -> str | None:
        """Получить объект, если он существует."""
        self._is_directory_exists()
        path = self._storage_directory / hashlib.sha256(str(key).encode()).hexdigest()
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    hash = hashlib.sha256()
                    hash.update(str(key).encode())
                    hash.update(str(data["value"]).encode())
                    if data["hash"] == str(hash.hexdigest()):
                        return data["value"]
            except json.JSONDecodeError:
                return None
        return None

    @defer
    def update(self, key: SupportsStr, value: SupportsStr) -> None:
        """Обновить (или добавить) значение по ключу."""
        self._is_directory_exists()
        path = self._storage_directory / hashlib.sha256(str(key).encode()).hexdigest()
        hash = hashlib.sha256()
        hash.update(str(key).encode())
        hash.update(str(value).encode())
        data = {
            "hash": str(hash.hexdigest()),
            "value": value
        }

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f)

    @defer
    def delete(self, key: SupportsStr) -> None:
        """Удалить ключ вместе со значением."""
        self._is_directory_exists()
        path = self._storage_directory / hashlib.sha256(str(key).encode()).hexdigest()
        path.unlink(missing_ok=True)

    @defer
    def clear(self) -> None:
        """Удалить все ключи вместе со значениями."""
        self._is_directory_exists()
        for data in self._storage_directory.iterdir():
            data.unlink(missing_ok=True)

    def commit(self) -> None:
        """Подтвердить изменения."""
        while self.storage_queue:
            func, args, kwargs = self.storage_queue.pop(0)
            func(self, *args, **kwargs)

    def rollback(self) -> None:
        """Откатить неподтвержденные изменения."""
        self.storage_queue.clear()

    def __getitem__(self, key: SupportsStr) -> str | None:
        """Получить объект, если он существует."""
        return self.get(key)

    def __setitem__(self, key: SupportsStr, value: SupportsStr) -> None:
        """Обновить (или добавить) значение по ключу."""
        self.update(key, value)

    def __delitem__(self, key: SupportsStr) -> None:
        """Удалить ключ вместе со значением."""
        self.delete(key)

    def __enter__(self) -> 'StorageAdapter':
        """Открыть транзакцию."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Закрыть транзакцию."""
        if exc_type is not None:
            self.rollback()
        else:
            self.commit()
