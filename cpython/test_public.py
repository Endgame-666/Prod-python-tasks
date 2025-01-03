import ast
import os

from pathlib import Path
from tempfile import gettempdir
from uuid import uuid4

import pytest

from cpython import main


@pytest.fixture(scope="function")
def sandbox() -> Path:
    """Фикстура песочницы."""
    base_dir = Path(gettempdir())

    sandbox_dir = base_dir / str(uuid4())
    sandbox_dir.mkdir(parents=True)

    os.chdir(sandbox_dir)

    return sandbox_dir


def get_keyword(keywords: list[ast.keyword], argname: str) -> ast.keyword:
    """Найти нужный аргумент по ключу."""
    return next(keyword for keyword in keywords if keyword.arg == argname)


def test__build_file(sandbox: Path) -> None:
    """Кейс: проверяем валидность файла сборки."""
    main()

    build_file = sandbox / "third_party" / "cpython" / "BUILD.bazel"
    tree = ast.parse(build_file.read_text())

    detail = "Файл `BUILD.bazel` должен состоять из одной инструкции"
    assert len(tree.body) == 1, detail

    cc_import = tree.body[0].value  # type: ignore

    detail = "Файл `BUILD.bazel` содержит только `cc_import`"
    assert cc_import.func.id == "cc_import", detail

    keywords = cc_import.keywords

    name: str = get_keyword(keywords, "name").value.value  # type: ignore
    assert name == "cpython"

    visibility: list[str] = [node.value for node in get_keyword(keywords, "visibility").value.elts]  # type: ignore
    assert visibility == ["//visibility:public"]

    shared_library = Path(get_keyword(keywords, "shared_library").value.value)  # type: ignore
    assert shared_library.exists()

    includes: list[str] = [node.value for node in get_keyword(keywords, "includes").value.elts]  # type: ignore
    assert len(includes) > 0

    headers: list[str] = [node.value for node in get_keyword(keywords, "hdrs").value.elts]  # type: ignore
    assert len(headers) > 0

    assert includes == sorted(includes)
    assert headers == sorted(headers)

    detail = "Было оговорено, что все `includes` должны начинаться на `internal`"
    assert all(include.startswith("internal") for include in includes), detail

    detail = "Было оговорено, что все `hdrs` должны начинаться на `internal`"
    assert all(header.startswith("internal") for header in headers), detail

    for include in includes:
        detail = "Директории из `includes` должны быть префиксом для всех файлов"
        assert all(header.startswith(include) for header in headers), detail

    for header in map(Path, headers):
        assert header.exists()
