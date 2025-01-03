from pathlib import Path
from tempfile import gettempdir
from uuid import uuid4

import pytest

from symlink import is_circular_symlink


@pytest.fixture(scope="function")
def sandbox() -> Path:
    base_dir = Path(gettempdir())

    sandbox_dir = base_dir / str(uuid4())
    sandbox_dir.mkdir(parents=True)

    return sandbox_dir


def test__not_circular_symlink(sandbox: Path) -> None:
    """Кейс: обычная символическая ссылка."""
    file = sandbox / Path("file.txt")
    file.touch()

    symlink = sandbox / Path("symlink")
    symlink.symlink_to(file)

    assert not is_circular_symlink(symlink)


def test__circular_symlink(sandbox: Path) -> None:
    """Кейс: простая циклическая ссылка."""
    first_symlink = sandbox / Path("first_symlink")
    second_symlink = sandbox / Path("second_symlink")

    second_symlink.symlink_to(first_symlink)
    first_symlink.symlink_to(second_symlink)

    assert is_circular_symlink(first_symlink)
    assert is_circular_symlink(second_symlink)
