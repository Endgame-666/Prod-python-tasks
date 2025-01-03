import hashlib
import os
import shutil

from contextlib import suppress
from pathlib import Path
from tempfile import gettempdir
from uuid import uuid4

import pytest

from database import StorageAdapter


KEY: str = "key"
VALUE: str = "value"

ANOTHER_KEY: str = "another_key"
ANOTHER_VALUE: str = "another_value"

KEY_FILENAME: str = hashlib.sha256(KEY.encode()).hexdigest()


@pytest.fixture(scope="function")
def sandbox() -> Path:
    """Фикстура песочницы."""
    base_dir = Path(gettempdir())

    sandbox_dir = base_dir / str(uuid4())
    sandbox_dir.mkdir(parents=True)

    os.chdir(sandbox_dir)

    return sandbox_dir


@pytest.fixture(scope="function")
def adapter(sandbox: Path) -> StorageAdapter:
    return StorageAdapter(_storage_directory=sandbox)


def test__read_write(adapter: StorageAdapter) -> None:  # 1
    """Тест цикла 'запись - чтение'."""
    adapter.update(KEY, VALUE)
    adapter.commit()

    value = adapter.get(KEY)

    print(value)
    assert value == VALUE


def test__read_write__uncommited(adapter: StorageAdapter) -> None:
    """Тест цикла 'запись - чтение' без коммита."""
    adapter.update(KEY, VALUE)

    value = adapter.get(KEY)


    assert value is None


def test__overwrite__commited_step(adapter: StorageAdapter) -> None:  # 3
    """Тест перезаписи при промежуточных коммитах."""
    adapter.update(KEY, ANOTHER_VALUE)
    adapter.commit()

    adapter.update(KEY, VALUE)
    adapter.commit()

    value = adapter.get(KEY)

    assert value == VALUE


def test__overwrite__uncommited_step(adapter: StorageAdapter) -> None:
    """Тест перезаписи без промежуточных коммитов."""
    adapter.update(KEY, ANOTHER_VALUE)
    adapter.update(KEY, VALUE)
    adapter.commit()

    value = adapter.get(KEY)

    assert value == VALUE


def test__get__not_exists(adapter: StorageAdapter) -> None:  # 5
    """Тест метода `get`, если значения по ключу нет."""
    value = adapter.get(KEY)

    assert value is None

def test__delete__commited_step(adapter: StorageAdapter) -> None:
    """Тест метода `delete` при промежуточных коммитах."""
    adapter.update(KEY, VALUE)
    adapter.commit()

    adapter.delete(KEY)
    adapter.commit()

    value = adapter.get(KEY)

    assert value is None


def test__delete__uncommited_step(adapter: StorageAdapter) -> None:   # 7
    """Тест метода `delete` без промежуточных коммитов."""
    adapter.update(KEY, VALUE)
    adapter.delete(KEY)
    adapter.commit()

    value = adapter.get(KEY)

    assert value is None


def test__delete__uncommited(adapter: StorageAdapter) -> None:
    """Тест метода `delete` без коммита."""
    adapter.update(KEY, VALUE)
    adapter.commit()

    adapter.delete(KEY)

    value = adapter.get(KEY)

    assert value == VALUE


def test__clear__commited_step(adapter: StorageAdapter) -> None:  # 9
    """Тест метода `clear` при промежуточных коммитах."""
    adapter.update(KEY, VALUE)
    adapter.update(ANOTHER_KEY, ANOTHER_VALUE)
    adapter.commit()

    adapter.clear()
    adapter.commit()

    value = adapter.get(KEY)

    assert value is None


def test__clear__uncommited_step(adapter: StorageAdapter) -> None:
    """Тест метода `clear` без промежуточных коммитов."""
    adapter.update(KEY, VALUE)
    adapter.update(ANOTHER_KEY, ANOTHER_VALUE)

    adapter.clear()
    adapter.commit()

    value = adapter.get(KEY)
    another_value = adapter.get(ANOTHER_KEY)

    assert value is None
    assert another_value is None


def test__clear__update(adapter: StorageAdapter) -> None:  # 11
    """Тест метода `clear`, если до коммита, но после чистки была запись."""
    adapter.update(KEY, VALUE)
    adapter.clear()
    adapter.update(ANOTHER_KEY, ANOTHER_VALUE)
    adapter.commit()

    value = adapter.get(KEY)
    another_value = adapter.get(ANOTHER_KEY)

    assert value is None
    assert another_value == ANOTHER_VALUE


def test__rollback__update(adapter: StorageAdapter) -> None:
    """Тест метода `rollback` для `update`."""
    adapter.update(KEY, VALUE)
    adapter.rollback()

    value = adapter.get(KEY)

    assert value is None


def test__rollback__clear(adapter: StorageAdapter) -> None:  #13
    """Тест метода `rollback` для `clear`."""
    adapter.update(KEY, VALUE)
    adapter.commit()

    adapter.clear()
    adapter.rollback()

    value = adapter.get(KEY)

    assert value == VALUE


def test__rollback__multiple_steps(adapter: StorageAdapter) -> None:
    """Тест метода `rollback` после нескольких команд."""
    adapter.update(KEY, VALUE)
    adapter.commit()

    adapter.update(KEY, ANOTHER_VALUE)
    adapter.update(ANOTHER_KEY, ANOTHER_VALUE)

    adapter.rollback()

    value = adapter.get(KEY)
    another_value = adapter.get(ANOTHER_KEY)

    assert value == VALUE
    assert another_value is None


def test__read_write__magic_methods(adapter: StorageAdapter) -> None:  # 15
    """Тест цикла 'запись - чтение'."""
    adapter[KEY] = VALUE
    adapter.commit()

    value = adapter[KEY]

    assert value == VALUE


def test__read_write__uncommited__magic_methods(adapter: StorageAdapter) -> None:
    """Тест цикла 'запись - чтение' без коммита."""
    adapter[KEY] = VALUE

    value = adapter[KEY]

    assert value is None


def test__overwrite__commited_step__magic_methods(adapter: StorageAdapter) -> None:  # 17
    """Тест перезаписи при промежуточных коммитах."""
    adapter[KEY] = ANOTHER_VALUE
    adapter.commit()

    adapter[KEY] = VALUE
    adapter.commit()

    value = adapter[KEY]

    assert value == VALUE


def test__overwrite__uncommited_step__magic_methods(adapter: StorageAdapter) -> None:
    """Тест перезаписи без промежуточных коммитов."""
    adapter[KEY] = ANOTHER_VALUE
    adapter[KEY] = VALUE
    adapter.commit()

    value = adapter[KEY]

    assert value == VALUE


def test__get__not_exists__magic_methods(adapter: StorageAdapter) -> None:  # 19
    """Тест метода `get`, если значения по ключу нет."""
    value = adapter[KEY]

    assert value is None


def test__delete__commited_step__magic_methods(adapter: StorageAdapter) -> None:
    """Тест метода `delete` при промежуточных коммитах."""
    adapter[KEY] = VALUE
    adapter.commit()

    del adapter[KEY]
    adapter.commit()

    value = adapter[KEY]

    assert value is None


def test__delete__uncommited_step__magic_methods(adapter: StorageAdapter) -> None:  # 21
    """Тест метода `delete` без промежуточных коммитов."""
    adapter[KEY] = VALUE
    del adapter[KEY]
    adapter.commit()

    value = adapter[KEY]

    assert value is None


def test__delete__uncommited__magic_methods(adapter: StorageAdapter) -> None:
    """Тест метода `delete` без коммита."""
    adapter[KEY] = VALUE
    adapter.commit()

    del adapter[KEY]

    value = adapter[KEY]

    assert value == VALUE


def test__clear__commited_step__magic_methods(adapter: StorageAdapter) -> None:  # 23
    """Тест метода `clear` при промежуточных коммитах."""
    adapter[KEY] = VALUE
    adapter[ANOTHER_KEY] = ANOTHER_VALUE
    adapter.commit()

    adapter.clear()
    adapter.commit()

    value = adapter[KEY]

    assert value is None


def test__clear__uncommited_step__magic_methods(adapter: StorageAdapter) -> None:
    """Тест метода `clear` без промежуточных коммитов."""
    adapter[KEY] = VALUE
    adapter[ANOTHER_KEY] = ANOTHER_VALUE

    adapter.clear()
    adapter.commit()

    value = adapter[KEY]
    another_value = adapter[ANOTHER_KEY]

    assert value is None
    assert another_value is None


def test__clear__update__magic_methods(adapter: StorageAdapter) -> None:  #25
    """Тест метода `clear`, если до коммита, но после чистки была запись."""
    adapter[KEY] = VALUE
    adapter.clear()
    adapter[ANOTHER_KEY] = ANOTHER_VALUE
    adapter.commit()

    value = adapter[KEY]
    another_value = adapter[ANOTHER_KEY]

    assert value is None
    assert another_value == ANOTHER_VALUE


def test__rollback__update__magic_methods(adapter: StorageAdapter) -> None:
    """Тест метода `rollback` для `update`."""
    adapter[KEY] = VALUE
    adapter.rollback()

    value = adapter[KEY]

    assert value is None


def test__rollback__clear__magic_methods(adapter: StorageAdapter) -> None:  #27
    """Тест метода `rollback` для `clear`."""
    adapter[KEY] = VALUE
    adapter.commit()

    adapter.clear()
    adapter.rollback()

    value = adapter[KEY]

    assert value == VALUE


def test__rollback__multiple_steps__magic_methods(adapter: StorageAdapter) -> None:
    """Тест метода `rollback` после нескольких команд."""
    adapter[KEY] = VALUE
    adapter.commit()

    adapter[KEY] = ANOTHER_VALUE
    adapter[ANOTHER_KEY] = ANOTHER_VALUE

    adapter.rollback()

    value = adapter[KEY]
    another_value = adapter[ANOTHER_KEY]

    assert value == VALUE
    assert another_value is None


def test__transaction__context(adapter: StorageAdapter) -> None:  #29
    """Тест контекстного менеджера."""
    with adapter as context:
        context.update(KEY, VALUE)

    value = adapter.get(KEY)

    assert value == VALUE


def test__transaction__self(adapter: StorageAdapter) -> None:
    """Тест контекстного менеджера."""
    with adapter:
        adapter.update(KEY, VALUE)

    value = adapter.get(KEY)

    assert value == VALUE


def test__transaction__context_and_self(adapter: StorageAdapter) -> None:  # 31
    """Тест контекстного менеджера."""
    with adapter as context:
        adapter.update(KEY, VALUE)
        context.update(ANOTHER_KEY, ANOTHER_VALUE)

    value = adapter.get(KEY)
    another_value = adapter.get(ANOTHER_KEY)

    assert value == VALUE
    assert another_value == ANOTHER_VALUE


def test__transaction__inner_commit(adapter: StorageAdapter) -> None:
    """Тест контекстного менеджера."""
    with adapter:
        adapter.update(KEY, VALUE)
        adapter.update(ANOTHER_KEY, ANOTHER_VALUE)
        adapter.commit()

        adapter.delete(ANOTHER_KEY)

    value = adapter.get(KEY)
    another_value = adapter.get(ANOTHER_KEY)

    assert value == VALUE
    assert another_value is None


def test__transaction__clear(adapter: StorageAdapter) -> None:  # 33
    """Тест контекстного менеджера."""
    with adapter:
        adapter.update(KEY, VALUE)
        adapter.update(ANOTHER_KEY, ANOTHER_VALUE)
        adapter.clear()

    value = adapter.get(KEY)
    another_value = adapter.get(ANOTHER_KEY)

    assert value is None
    assert another_value is None


def test__transaction__multiple_calls(adapter: StorageAdapter) -> None:
    """Тест контекстного менеджера."""
    with adapter:
        adapter.update(KEY, VALUE)

    with adapter:
        adapter.update(ANOTHER_KEY, ANOTHER_VALUE)

    value = adapter.get(KEY)
    another_value = adapter.get(ANOTHER_KEY)

    assert value == VALUE
    assert another_value == ANOTHER_VALUE


def test__transaction__rollback(adapter: StorageAdapter) -> None:  # 35
    """Тест контекстного менеджера при исключении."""
    with suppress(OSError), adapter:
        adapter.update(KEY, VALUE)

        detail = "Hello, HSE"
        raise OSError(detail)

    value = adapter.get(KEY)

    assert value is None


def test__transaction__rollback_and_inner_commit(adapter: StorageAdapter) -> None:
    """Тест контекстного менеджера при исключении."""
    with suppress(OSError), adapter:
        adapter.update(KEY, VALUE)
        adapter.commit()

        adapter.update(KEY, ANOTHER_VALUE)

        detail = "Hello, HSE"
        raise OSError(detail)

    value = adapter.get(KEY)

    assert value == VALUE


def test__transaction__reraise(adapter: StorageAdapter) -> None:  # 37
    """Тест контекстного менеджера при исключении."""
    with pytest.raises(OSError), adapter:
        adapter.update(KEY, VALUE)

        detail = "Hello, HSE"
        raise OSError(detail)


def test__virus__rename_file(sandbox: Path, adapter: StorageAdapter) -> None:
    """Вирус переименовал файл."""
    with adapter:
        adapter.update(KEY, VALUE)

    new_filename = f"test_{KEY_FILENAME}"
    new_file = sandbox / new_filename

    file = sandbox / KEY_FILENAME
    file.rename(new_file)

    value = adapter.get(KEY)

    assert value is None


def test__virus__delete_file(sandbox: Path, adapter: StorageAdapter) -> None:  # 39
    """Вирус удалил файл."""
    with adapter:
        adapter.update(KEY, VALUE)

    file = sandbox / KEY_FILENAME
    file.unlink(missing_ok=True)

    value = adapter.get(KEY)

    assert value is None


def test__virus__overwrite_file(sandbox: Path, adapter: StorageAdapter) -> None:
    """Вирус перезаписал файл."""
    with adapter:
        adapter.update(KEY, VALUE)

    file = sandbox / KEY_FILENAME
    file.write_text("Hello, HSE")

    value = adapter.get(KEY)

    assert value is None


def test__virus__delete_storage_directory_after(sandbox: Path, adapter: StorageAdapter) -> None:  #41
    """Вирус удалил директорию-хранилище после выполнения операции."""
    with adapter:
        adapter.update(KEY, VALUE)

    shutil.rmtree(sandbox)

    value = adapter.get(KEY)

    assert value is None


def test__virus__delete_storage_directory_before(sandbox: Path, adapter: StorageAdapter) -> None:
    """Вирус удалил директорию-хранилище до выполнения операции."""
    shutil.rmtree(sandbox)

    with adapter:
        adapter.update(KEY, VALUE)

    value = adapter.get(KEY)

    assert value == VALUE


def test__virus__storage_directory_as_file(sandbox: Path, adapter: StorageAdapter) -> None:  # 43
    """Вирус сделал директорию-хранилище файлом."""
    shutil.rmtree(sandbox)
    sandbox.touch()

    with adapter:
        adapter.update(KEY, VALUE)

    value = adapter.get(KEY)

    assert value == VALUE


def test__virus__storage_directory_as_symlink(sandbox: Path, adapter: StorageAdapter) -> None:
    """Вирус сделал директорию-хранилище файлом."""
    shutil.rmtree(sandbox)
    sandbox.symlink_to(sandbox)

    with adapter:
        adapter.update(KEY, VALUE)

    value = adapter.get(KEY)

    assert value == VALUE


def test__algorithm__shared_read_write(sandbox: Path) -> None:  # 45
    """Алгоритм разделяет память между адаптерами."""
    lhs = StorageAdapter(_storage_directory=sandbox)
    rhs = StorageAdapter(_storage_directory=sandbox)

    with lhs:
        lhs.update(KEY, VALUE)

    value = rhs.get(KEY)

    assert value == VALUE


def test__algorithm__shared_delete(sandbox: Path) -> None:
    """Алгоритм разделяет память между адаптерами."""
    lhs = StorageAdapter(_storage_directory=sandbox)
    rhs = StorageAdapter(_storage_directory=sandbox)

    with lhs:
        lhs.update(KEY, VALUE)

    with rhs:
        rhs.delete(KEY)

    value = lhs.get(KEY)

    assert value is None


def test__algorithm__shared_clear(sandbox: Path) -> None:  # 47
    """Алгоритм разделяет память между адаптерами."""
    lhs = StorageAdapter(_storage_directory=sandbox)
    rhs = StorageAdapter(_storage_directory=sandbox)

    with lhs:
        lhs.update(KEY, VALUE)
        lhs.update(ANOTHER_KEY, ANOTHER_VALUE)

    with rhs:
        rhs.clear()

    value = lhs.get(KEY)
    another_value = lhs.get(ANOTHER_KEY)

    assert value is None
    assert another_value is None
