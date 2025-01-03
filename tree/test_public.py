import os

from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from tempfile import gettempdir
from textwrap import dedent
from uuid import uuid4

import pytest

from pytest import CaptureFixture

from tree import main

PROG = "tree"


@pytest.fixture(scope="function")
def sandbox() -> Path:
    base_dir = Path(gettempdir())

    sandbox_dir = base_dir / str(uuid4())
    sandbox_dir.mkdir(parents=True)

    return sandbox_dir.resolve()


@contextmanager
def cd(path: Path) -> Generator[None, None, None]:
    """Сменить рабочий каталог."""
    cwd = Path.cwd()
    os.chdir(path)

    try:
        yield

    finally:
        os.chdir(cwd)


def test__tree__01(sandbox: Path, capsys: CaptureFixture) -> None:  # 1
    """Кейс: Обычный вызов `tree`."""
    file = sandbox / "file.txt"
    file.touch()

    main([sandbox.as_posix()])

    captured = capsys.readouterr()
    stdout = captured.out
    print(stdout)
    expected = f"""\
    {sandbox.as_posix()}/
        file.txt
    """

    assert stdout == dedent(expected)


def test__tree__02(sandbox: Path, capsys: CaptureFixture) -> None:
    """Кейс: Обычный вызов `tree`."""
    file = sandbox / "file.txt"
    file.touch()

    directory = sandbox / "directory"
    directory.mkdir()

    directory_file = directory / "file.txt"
    directory_file.touch()

    main([sandbox.as_posix()])

    captured = capsys.readouterr()
    stdout = captured.out

    expected = f"""\
    {sandbox.as_posix()}/
        directory/
            file.txt
        file.txt
    """

    assert stdout == dedent(expected)


def test__tree__03(sandbox: Path, capsys: CaptureFixture) -> None:  # 3
    """Кейс: Обычный вызов `tree`."""
    file = sandbox / "file.txt"
    file.touch()

    directory = sandbox / "directory"
    directory.mkdir()

    directory_file = directory / "file.txt"
    directory_file.touch()

    another_directory = sandbox / "another_directory"
    another_directory.mkdir()

    yet_another_directory = sandbox / "yet_another_directory"
    yet_another_directory.mkdir()

    nested_directory = yet_another_directory / "directory"
    nested_directory.mkdir()

    nested_file_1 = nested_directory / "file_1.txt"
    nested_file_1.touch()

    nested_file_2 = nested_directory / "file_2.txt"
    nested_file_2.touch()

    main([sandbox.as_posix()])

    captured = capsys.readouterr()
    stdout = captured.out

    expected = f"""\
    {sandbox.as_posix()}/
        another_directory/
        directory/
            file.txt
        yet_another_directory/
            directory/
                file_1.txt
                file_2.txt
        file.txt
    """

    assert stdout == dedent(expected)


def test__tree__symlink(sandbox: Path, capsys: CaptureFixture) -> None:
    """Кейс: дерево содержит символическую ссылку."""
    file = sandbox / "file.txt"
    file.touch()

    symlink = sandbox / "symlink"
    symlink.symlink_to(file)

    main([sandbox.as_posix()])

    captured = capsys.readouterr()
    stdout = captured.out

    expected = f"""\
    {sandbox.as_posix()}/
        file.txt
    """

    assert stdout == dedent(expected)


def test__tree__multiple_symlinks(sandbox: Path, capsys: CaptureFixture) -> None:  # 5
    """Кейс: дерево содержит несколько символических ссылок."""
    file = sandbox / "file.txt"
    file.touch()

    symlink = sandbox / "symlink"
    symlink.symlink_to(file)

    another_symlink = sandbox / "another_symlink"
    another_symlink.symlink_to(file)

    yet_another_symlink = sandbox / "yet_another_symlink"
    yet_another_symlink.symlink_to(another_symlink)

    main([sandbox.as_posix()])

    captured = capsys.readouterr()
    stdout = captured.out

    expected = f"""\
    {sandbox.as_posix()}/
        file.txt
    """

    assert stdout == dedent(expected)


def test__tree__nested_symlinks(sandbox: Path, capsys: CaptureFixture) -> None:
    """Кейс: дерево содержит вложенные символические ссылки."""
    file = sandbox / "file.txt"
    file.touch()

    symlink = sandbox / "symlink"
    symlink.symlink_to(file)

    directory = sandbox / "directory"
    directory.mkdir()

    another_directory = directory / "another_directory"
    another_directory.mkdir()

    another_symlink = another_directory / "symlink"
    another_symlink.symlink_to(file)

    main([sandbox.as_posix()])

    captured = capsys.readouterr()
    stdout = captured.out

    expected = f"""\
    {sandbox.as_posix()}/
        directory/
            another_directory/
        file.txt
    """

    assert stdout == dedent(expected)


def test__tree__normalized_argument_path(sandbox: Path, capsys: CaptureFixture) -> None:  # 7
    """Кейс: нормализация аргумента-пути."""
    file = sandbox / "file.txt"
    file.touch()

    # Равносильно `./` - остаемся в песочнице
    suffix = "./directory/dev///./.././/.././"

    main([sandbox.joinpath(suffix).as_posix()])

    captured = capsys.readouterr()
    stdout = captured.out

    expected = f"""\
    {sandbox.as_posix()}/
        file.txt
    """

    assert stdout == dedent(expected)


def test__tree__default_path(sandbox: Path, capsys: CaptureFixture) -> None:
    """Кейс: аргумент по умолчанию."""
    with cd(sandbox):
        file = sandbox / "file.txt"
        file.touch()

        main([])
    captured = capsys.readouterr()

    stdout = captured.out
    print(stdout)
    expected = f"""\
    {sandbox.as_posix()}/
        file.txt
    """

    assert stdout == dedent(expected)


def test__tree__empty_directory(sandbox: Path, capsys: CaptureFixture) -> None:  # 9
    """Кейс: пустая директория."""
    main([sandbox.as_posix()])

    captured = capsys.readouterr()
    stdout = captured.out

    expected = f"""\
    {sandbox.as_posix()}/
    """

    assert stdout == dedent(expected)


def test__tree__help(capsys: CaptureFixture) -> None:
    """Кейс: вызов помощи."""
    with pytest.raises(SystemExit) as context:
        main(["--help"])

    captured = capsys.readouterr()
    stdout = captured.out
    stderr = captured.err

    usage_prefix = f"usage: {PROG} "

    assert context.value.code == 0
    assert stdout.startswith(usage_prefix)
    assert stderr == ""


@pytest.mark.parametrize("option", ["-i", "--indent"])
def test__tree__indent__2(option: str, sandbox: Path, capsys: CaptureFixture) -> None:  # 11 12
    """Кейс: отступ равен двум."""
    file = sandbox / "file.txt"
    file.touch()

    directory = sandbox / "directory"
    directory.mkdir()

    directory_file = directory / "file.txt"
    directory_file.touch()

    another_directory = sandbox / "another_directory"
    another_directory.mkdir()

    yet_another_directory = sandbox / "yet_another_directory"
    yet_another_directory.mkdir()

    nested_directory = yet_another_directory / "directory"
    nested_directory.mkdir()

    nested_file_1 = nested_directory / "file_1.txt"
    nested_file_1.touch()

    nested_file_2 = nested_directory / "file_2.txt"
    nested_file_2.touch()

    main([option, "2", sandbox.as_posix()])

    captured = capsys.readouterr()
    stdout = captured.out

    expected = f"""\
    {sandbox.as_posix()}/
      another_directory/
      directory/
        file.txt
      yet_another_directory/
        directory/
          file_1.txt
          file_2.txt
      file.txt
    """

    assert stdout == dedent(expected)


@pytest.mark.parametrize("option", ["-i", "--indent"])
def test__tree__indent__8(option: str, sandbox: Path, capsys: CaptureFixture) -> None:  # 13 14
    """Кейс: отступ равен 8."""
    file = sandbox / "file.txt"
    file.touch()

    directory = sandbox / "directory"
    directory.mkdir()

    directory_file = directory / "file.txt"
    directory_file.touch()

    another_directory = sandbox / "another_directory"
    another_directory.mkdir()

    yet_another_directory = sandbox / "yet_another_directory"
    yet_another_directory.mkdir()

    nested_directory = yet_another_directory / "directory"
    nested_directory.mkdir()

    nested_file_1 = nested_directory / "file_1.txt"
    nested_file_1.touch()

    nested_file_2 = nested_directory / "file_2.txt"
    nested_file_2.touch()

    main([option, "8", sandbox.as_posix()])

    captured = capsys.readouterr()
    stdout = captured.out

    expected = f"""\
    {sandbox.as_posix()}/
            another_directory/
            directory/
                    file.txt
            yet_another_directory/
                    directory/
                            file_1.txt
                            file_2.txt
            file.txt
    """

    assert stdout == dedent(expected)


@pytest.mark.parametrize("option", ["-i", "--indent"])
@pytest.mark.parametrize("indent", ["0", "-1", "-2", "-4"])
def test__tree__indent__non_positive(
    indent: str, option: str, sandbox: Path, capsys: CaptureFixture
) -> None:
    """Кейс: отступ не положительный."""
    with pytest.raises(SystemExit) as context:
        main([option, indent, sandbox.as_posix()])

    captured = capsys.readouterr()
    stderr = captured.err

    usage_prefix = f"usage: {PROG} "
    error_text = f"{PROG}: error: "

    assert context.value.code == 2
    assert stderr.startswith(usage_prefix)

    assert error_text in stderr


@pytest.mark.parametrize("option", ["-p", "--prune"])
def test__tree__prune__simple(
    option: str, sandbox: Path, capsys: CaptureFixture
) -> None:
    """Кейс: исключение пустых директорий."""
    directory = sandbox / "directory"
    directory.mkdir()

    main([option, sandbox.as_posix()])

    captured = capsys.readouterr()
    stdout = captured.out

    # print(stdout)
    expected = f"""\
    {sandbox.as_posix()}/
    """
    # print(expected)
    assert stdout == dedent(expected)


@pytest.mark.parametrize("option", ["-p", "--prune"])
def test__tree__prune__nested__01(
    option: str, sandbox: Path, capsys: CaptureFixture
) -> None:
    """Кейс: исключение пустых вложенных директорий."""
    file = sandbox / "file.txt"
    file.touch()

    directory = sandbox / "directory"
    directory.mkdir()

    empty_directory_01 = directory / "empty_1"
    empty_directory_01.mkdir()

    empty_directory_02 = directory / "empty_2"
    empty_directory_02.mkdir()

    main([option, sandbox.as_posix()])

    captured = capsys.readouterr()
    stdout = captured.out
   # print(stdout)
    expected = f"""\
    {sandbox.as_posix()}/
        file.txt
    """

    assert stdout == dedent(expected)


@pytest.mark.parametrize("option", ["-p", "--prune"])
def test__tree__prune__nested__02(
    option: str, sandbox: Path, capsys: CaptureFixture
) -> None:
    """Кейс: исключение пустых вложенных директорий."""
    file = sandbox / "file.txt"
    file.touch()

    directory = sandbox / "directory"
    directory.mkdir()

    empty_directory = directory / "empty"
    empty_directory.mkdir()

    another_directory = directory / "another_directory"
    another_directory.mkdir()

    another_empty_directory = another_directory / "empty"
    another_empty_directory.mkdir()

    yet_another_directory = another_directory / "yet_another_directory"
    yet_another_directory.mkdir()

    yet_another_file = yet_another_directory / "file.txt"
    yet_another_file.touch()

    main([option, sandbox.as_posix()])

    captured = capsys.readouterr()
    stdout = captured.out

    expected = f"""\
    {sandbox.as_posix()}/
        directory/
            another_directory/
                yet_another_directory/
                    file.txt
        file.txt
    """

    assert stdout == dedent(expected)


@pytest.mark.parametrize("option", ["-p", "--prune"])
def test__tree__prune__nested__03(
    option: str, sandbox: Path, capsys: CaptureFixture
) -> None:
    """Кейс: исключение пустых вложенных директорий."""
    file = sandbox / "file.txt"
    file.touch()

    directory = sandbox / "directory"
    directory.mkdir()

    empty_directory = directory / "empty"
    empty_directory.mkdir()

    another_directory = directory / "another_directory"
    another_directory.mkdir()

    another_empty_directory = another_directory / "empty"
    another_empty_directory.mkdir()

    yet_another_directory = another_directory / "yet_another_directory"
    yet_another_directory.mkdir()

    yet_another_file = yet_another_directory / "file.txt"
    yet_another_file.touch()

    main([option, sandbox.as_posix()])

    captured = capsys.readouterr()
    stdout = captured.out

    expected = f"""\
    {sandbox.as_posix()}/
        directory/
            another_directory/
                yet_another_directory/
                    file.txt
        file.txt
    """

    assert stdout == dedent(expected)


@pytest.mark.parametrize("option", ["-d", "--depth"])
def test__tree__limited_depth__0(
    option: str, sandbox: Path, capsys: CaptureFixture
) -> None:
    """Кейс: ограничение на глубину."""
    file = sandbox / "file.txt"
    file.touch()

    main([option, "0", sandbox.as_posix()])

    captured = capsys.readouterr()
    stdout = captured.out
  #  print(stdout)
    expected = f"""\
    {sandbox.as_posix()}/
    """
  #  print(expected)
    assert stdout == dedent(expected)


@pytest.mark.parametrize("option", ["-d", "--depth"])
def test__tree__limited_depth__1(
    option: str, sandbox: Path, capsys: CaptureFixture
) -> None:
    """Кейс: ограничение на глубину."""
    file = sandbox / "file.txt"
    file.touch()

    directory = sandbox / "directory"
    directory.mkdir()

    directory_file = directory / "file.txt"
    directory_file.touch()

    another_directory = sandbox / "another_directory"
    another_directory.mkdir()

    yet_another_directory = sandbox / "yet_another_directory"
    yet_another_directory.mkdir()

    nested_directory = yet_another_directory / "directory"
    nested_directory.mkdir()

    nested_file_1 = nested_directory / "file_1.txt"
    nested_file_1.touch()

    nested_file_2 = nested_directory / "file_2.txt"
    nested_file_2.touch()

    main([option, "1", sandbox.as_posix()])

    captured = capsys.readouterr()
    stdout = captured.out
   # print(stdout)
    expected = f"""\
    {sandbox.as_posix()}/
        another_directory/
        directory/
        yet_another_directory/
        file.txt
    """
   # print(expected)
    assert stdout == dedent(expected)


@pytest.mark.parametrize("option", ["-d", "--depth"])
def test__tree__limited_depth__2(
    option: str, sandbox: Path, capsys: CaptureFixture
) -> None:
    """Кейс: ограничение на глубину."""
    file = sandbox / "file.txt"
    file.touch()

    directory = sandbox / "directory"
    directory.mkdir()

    directory_file = directory / "file.txt"
    directory_file.touch()

    another_directory = sandbox / "another_directory"
    another_directory.mkdir()

    yet_another_directory = sandbox / "yet_another_directory"
    yet_another_directory.mkdir()

    nested_directory = yet_another_directory / "directory"
    nested_directory.mkdir()

    nested_file_1 = nested_directory / "file_1.txt"
    nested_file_1.touch()

    nested_file_2 = nested_directory / "file_2.txt"
    nested_file_2.touch()

    main([option, "2", sandbox.as_posix()])

    captured = capsys.readouterr()
    stdout = captured.out

    expected = f"""\
    {sandbox.as_posix()}/
        another_directory/
        directory/
            file.txt
        yet_another_directory/
            directory/
        file.txt
    """

    assert stdout == dedent(expected)


@pytest.mark.parametrize("option", ["-d", "--depth"])
def test__tree__limited_depth__3(
    option: str, sandbox: Path, capsys: CaptureFixture
) -> None:
    """Кейс: ограничение на глубину."""
    file = sandbox / "file.txt"
    file.touch()

    directory = sandbox / "directory"
    directory.mkdir()

    directory_file = directory / "file.txt"
    directory_file.touch()

    another_directory = sandbox / "another_directory"
    another_directory.mkdir()

    yet_another_directory = sandbox / "yet_another_directory"
    yet_another_directory.mkdir()

    nested_directory = yet_another_directory / "directory"
    nested_directory.mkdir()

    nested_file_1 = nested_directory / "file_1.txt"
    nested_file_1.touch()

    nested_file_2 = nested_directory / "file_2.txt"
    nested_file_2.touch()

    main([option, "3", sandbox.as_posix()])

    captured = capsys.readouterr()
    stdout = captured.out

    expected = f"""\
    {sandbox.as_posix()}/
        another_directory/
        directory/
            file.txt
        yet_another_directory/
            directory/
                file_1.txt
                file_2.txt
        file.txt
    """

    assert stdout == dedent(expected)


@pytest.mark.parametrize("option", ["-o", "--output"])
def test__tree__redirect_output(
    option: str, sandbox: Path, capsys: CaptureFixture
) -> None:
    """Кейс: перенаправить вывод в файл."""
    filename = "file.txt"

    with cd(sandbox):
        main([option, f"./{filename}", sandbox.as_posix()])

    captured = capsys.readouterr()
    stdout = captured.out

    expected = f"""\
    {sandbox.as_posix()}/
        file.txt
    """

    file = sandbox / filename
    contents = file.read_text()

    assert stdout == ""
    assert contents == dedent(expected)


@pytest.mark.parametrize("option", ["-o", "--output"])
def test__tree__redirect_output__overwrite(
    option: str, sandbox: Path, capsys: CaptureFixture
) -> None:
    """Кейс: перезаписать файл."""
    filename = "file.txt"

    file = sandbox / filename
    file.touch()

    text = "Hello, HSE"
    file.write_text(text)

    with cd(sandbox):
        main([option, f"./{filename}", sandbox.as_posix()])

    captured = capsys.readouterr()
    stdout = captured.out

    expected = f"""\
    {sandbox.as_posix()}/
        file.txt
    """

    contents = file.read_text()

    assert stdout == ""
    assert contents == dedent(expected)


@pytest.mark.parametrize("option", ["-o", "--output"])
def test__tree__redirect_output__directory(
    option: str, sandbox: Path, capsys: CaptureFixture
) -> None:
    """Кейс: вывод перенаправили в директорию."""
    file = sandbox / "file.txt"
    file.touch()

    with cd(sandbox), pytest.raises(SystemExit) as context:
        main([option, ".", sandbox.as_posix()])

    captured = capsys.readouterr()
    stderr = captured.err

    usage_prefix = f"usage: {PROG} "
    error_text = f"{PROG}: error: "

    assert context.value.code == 2
    assert stderr.startswith(usage_prefix)
    assert error_text in stderr


@pytest.mark.parametrize("option", ["-o", "--output"])
def test__tree__redirect_output__symlink_to_file(
    option: str, sandbox: Path, capsys: CaptureFixture
) -> None:
    """Кейс: вывод перенаправили в символическую ссылку, которая указывает на файл."""
    symlink_name = "symlink"

    file = sandbox / "file.txt"
    file.touch()

    symlink = sandbox / symlink_name
    symlink.symlink_to(file)

    with cd(sandbox), pytest.raises(SystemExit) as context:
        main([option, f"./{symlink_name}", sandbox.as_posix()])

    captured = capsys.readouterr()
    stderr = captured.err

    usage_prefix = f"usage: {PROG} "
    error_text = f"{PROG}: error: "

    assert context.value.code == 2
    assert stderr.startswith(usage_prefix)
    assert error_text in stderr


@pytest.mark.parametrize("option", ["-e", "--extension"])
def test__tree__filter_by_extension(
    option: str, sandbox: Path, capsys: CaptureFixture
) -> None:
    """Кейс: фильтр по расширению."""
    file = sandbox / "file.txt"
    file.touch()

    another_file = sandbox / "file.md"
    another_file.touch()

    main([option, ".txt", sandbox.as_posix()])

    captured = capsys.readouterr()
    stdout = captured.out

    expected = f"""\
    {sandbox.as_posix()}/
        file.txt
    """

    assert stdout == dedent(expected)


@pytest.mark.parametrize("option", ["-e", "--extension"])
def test__tree__filter_by_extension__no_dot(
    option: str, sandbox: Path, capsys: CaptureFixture
) -> None:
    """Кейс: фильтр по расширению без начальной точки."""
    file = sandbox / "file.txt"
    file.touch()

    another_file = sandbox / "file.md"
    another_file.touch()

    main([option, "txt", sandbox.as_posix()])

    captured = capsys.readouterr()
    stdout = captured.out

    expected = f"""\
    {sandbox.as_posix()}/
        file.txt
    """

    assert stdout == dedent(expected)


@pytest.mark.parametrize("option", ["-e", "--extension"])
def test__tree__filter_by_extension__empty_string(
    option: str, sandbox: Path, capsys: CaptureFixture
) -> None:
    """Кейс: пустое расширение."""
    file = sandbox / "file.txt"
    file.touch()

    another_file = sandbox / "file.md"
    another_file.touch()

    yet_another_file = sandbox / "file"
    yet_another_file.touch()

    main([option, "", sandbox.as_posix()])

    captured = capsys.readouterr()
    stdout = captured.out

    expected = f"""\
    {sandbox.as_posix()}/
        file
    """

    assert stdout == dedent(expected)


@pytest.mark.parametrize("option", ["-e", "--extension"])
def test__tree__filter_by_extension__multidot_extension__01(
    option: str, sandbox: Path, capsys: CaptureFixture
) -> None:
    """Кейс: многоуровневое расширение."""
    file = sandbox / "file.tar.gz"
    file.touch()

    main([option, ".tar.gz", sandbox.as_posix()])

    captured = capsys.readouterr()
    stdout = captured.out

    expected = f"""\
    {sandbox.as_posix()}/
        file.tar.gz
    """

    assert stdout == dedent(expected)


@pytest.mark.parametrize("option", ["-e", "--extension"])
def test__tree__filter_by_extension__multidot_extension__02(
    option: str, sandbox: Path, capsys: CaptureFixture
) -> None:
    """Кейс: многоуровневое расширение."""
    file = sandbox / "file.tar.gz"
    file.touch()

    main([option, ".gz", sandbox.as_posix()])

    captured = capsys.readouterr()
    stdout = captured.out

    expected = f"""\
    {sandbox.as_posix()}/
    """

    assert stdout == dedent(expected)


@pytest.mark.parametrize("option", ["-e", "--extension"])
def test__tree__filter_by_extension__starts_with_dot__01(
    option: str, sandbox: Path, capsys: CaptureFixture
) -> None:
    """Кейс: многоуровневое расширение."""
    file = sandbox / ".gitignore"
    file.touch()

    main([option, ".gitignore", sandbox.as_posix()])

    captured = capsys.readouterr()
    stdout = captured.out

    expected = f"""\
    {sandbox.as_posix()}/
    """

    assert stdout == dedent(expected)


@pytest.mark.parametrize("option", ["-e", "--extension"])
def test__tree__filter_by_extension__starts_with_dot__02(
    option: str, sandbox: Path, capsys: CaptureFixture
) -> None:
    """Кейс: многоуровневое расширение."""
    file = sandbox / ".gitignore"
    file.touch()

    main([option, "", sandbox.as_posix()])

    captured = capsys.readouterr()
    stdout = captured.out

    expected = f"""\
    {sandbox.as_posix()}/
        .gitignore
    """

    assert stdout == dedent(expected)


@pytest.mark.parametrize("option", ["-e", "--extension"])
def test__tree__filter_by_multiple_extensions__01(
    option: str, sandbox: Path, capsys: CaptureFixture
) -> None:
    """Кейс: фильтр по расширениям."""
    file = sandbox / "file.txt"
    file.touch()

    directory = sandbox / "directory"
    directory.mkdir()

    directory_file = directory / "file.md"
    directory_file.touch()

    another_directory = sandbox / "another_directory"
    another_directory.mkdir()

    nested_directory = another_directory / "directory"
    nested_directory.mkdir()

    nested_file_1 = nested_directory / "file.py"
    nested_file_1.touch()

    nested_file_2 = nested_directory / "file.txt"
    nested_file_2.touch()

    main([option, ".txt", option, ".md", sandbox.as_posix()])

    captured = capsys.readouterr()
    stdout = captured.out

 #   print(stdout)
    expected = f"""\
    {sandbox.as_posix()}/
        another_directory/
            directory/
                file.txt
        directory/
            file.md
        file.txt
    """

    assert stdout == dedent(expected)


@pytest.mark.parametrize("option", ["-e", "--extension"])
def test__tree__filter_by_multiple_extensions__02(
    option: str, sandbox: Path, capsys: CaptureFixture
) -> None:
    """Кейс: фильтр по расширениям."""
    file = sandbox / "file.txt"
    file.touch()

    directory = sandbox / "directory"
    directory.mkdir()

    directory_file = directory / "file.md"
    directory_file.touch()

    another_directory = sandbox / "another_directory"
    another_directory.mkdir()

    nested_directory = another_directory / "directory"
    nested_directory.mkdir()

    nested_file_1 = nested_directory / "file.py"
    nested_file_1.touch()

    nested_file_2 = nested_directory / "file.txt"
    nested_file_2.touch()

    main([option, "txt", option, "md", option, ".py", sandbox.as_posix()])

    captured = capsys.readouterr()
    stdout = captured.out

    expected = f"""\
    {sandbox.as_posix()}/
        another_directory/
            directory/
                file.py
                file.txt
        directory/
            file.md
        file.txt
    """

    assert stdout == dedent(expected)


@pytest.mark.parametrize("option", ["-e", "--extension"])
def test__tree__filter_by_extension__prune__01(
    option: str, sandbox: Path, capsys: CaptureFixture
) -> None:
    """Кейс: фильтр по расширению, c пустыми директориями."""
    file = sandbox / "file.md"
    file.touch()

    directory = sandbox / "directory"
    directory.mkdir()

    directory_file = directory / "file.py"
    directory_file.touch()

    main([option, ".md", sandbox.as_posix()])

    captured = capsys.readouterr()
    stdout = captured.out
  #  print(stdout)
    expected = f"""\
    {sandbox.as_posix()}/
        file.md
    """

    assert stdout == dedent(expected)


@pytest.mark.parametrize("option", ["-e", "--extension"])
def test__tree__filter_by_extension__prune__02(
    option: str, sandbox: Path, capsys: CaptureFixture
) -> None:
    """Кейс: фильтр по расширению, c пустыми директориями."""
    directory = sandbox / "directory"
    directory.mkdir()

    another_directory = sandbox / "another_directory"
    another_directory.mkdir()

    another_file = another_directory / "file.md"
    another_file.touch()

    nested_directory = directory / "nested_directory"
    nested_directory.mkdir()

    nested_file_1 = nested_directory / "file_1.txt"
    nested_file_1.touch()

    nested_file_2 = nested_directory / "file_2.txt"
    nested_file_2.touch()

    main([option, ".md", sandbox.as_posix()])

    captured = capsys.readouterr()
    stdout = captured.out

    expected = f"""\
    {sandbox.as_posix()}/
        another_directory/
            file.md
    """

    assert stdout == dedent(expected)


@pytest.mark.parametrize("option", ["-e", "--extension"])
def test__tree__filter_by_extension__prune__03(
    option: str, sandbox: Path, capsys: CaptureFixture
) -> None:
    """Кейс: фильтр по расширению, c пустыми директориями."""
    file = sandbox / "file.cpp"
    file.touch()

    directory = sandbox / "directory"
    directory.mkdir()

    directory_file = directory / "file.cpp"
    directory_file.touch()

    another_directory = sandbox / "another_directory"
    another_directory.mkdir()

    another_file = another_directory / "another_file.hpp"
    another_file.touch()

    yet_another_directory = sandbox / "yet_another_directory"
    yet_another_directory.mkdir()

    nested_directory = yet_another_directory / "directory"
    nested_directory.mkdir()

    nested_file_1 = nested_directory / "file_1.txt"
    nested_file_1.touch()

    nested_file_2 = nested_directory / "file_2.txt"
    nested_file_2.touch()

    main([option, ".hpp", sandbox.as_posix()])

    captured = capsys.readouterr()
    stdout = captured.out

    expected = f"""\
    {sandbox.as_posix()}/
        another_directory/
            another_file.hpp
    """

    assert stdout == dedent(expected)


@pytest.mark.parametrize("indent_option", ["-i", "--indent"])
@pytest.mark.parametrize("output_option", ["-o", "--output"])
@pytest.mark.parametrize("extension_option", ["-e", "--extension"])
def test__tree__multiple_options(
    extension_option: str,
    output_option: str,
    indent_option: str,
    sandbox: Path,
    capsys: CaptureFixture,
) -> None:
    """Кейс: несколько опций."""
    filename = "file.txt"

    directory = sandbox / "directory"
    directory.mkdir()

    directory_file = directory / "directory_file.md"
    directory_file.touch()

    another_directory = sandbox / "another_directory"
    another_directory.mkdir()

    yet_another_directory = sandbox / "yet_another_directory"
    yet_another_directory.mkdir()

    nested_directory = yet_another_directory / "directory"
    nested_directory.mkdir()

    nested_file_1 = nested_directory / "file_1.md"
    nested_file_1.touch()

    nested_file_2 = nested_directory / "file_2.py"
    nested_file_2.touch()

    nested_symlink = nested_directory / "symlink"
    nested_symlink.symlink_to(nested_directory)

    with cd(sandbox):
        options = [output_option, f"./{filename}", indent_option, "8", extension_option, ".py"]
        main([*options, sandbox.as_posix()])

    captured = capsys.readouterr()
    stdout = captured.out

    expected = f"""\
    {sandbox.as_posix()}/
            yet_another_directory/
                    directory/
                            file_2.py
    """

    file = sandbox / filename
    contents = file.read_text()
  #  print(nested_symlink.is_symlink())
  #   print(contents)
    assert stdout == ""
    assert contents == dedent(expected)
