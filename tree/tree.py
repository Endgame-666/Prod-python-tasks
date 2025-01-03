import dataclasses
from argparse import ArgumentParser, Namespace
from pathlib import Path
import sys


@dataclasses.dataclass
class RecursionSettings:
    """Настройки рекурсии."""
    indent: int = 4
    prune: bool = False
    depth: int | None = None
    extension: set[str] | None = None
    output: str | None = None
    path: str | None = None


def get_parser() -> ArgumentParser:
    """Получить парсер аргументов командной строки."""
    PROG = "tree"
    parser = ArgumentParser(prog=PROG)
    parser.add_argument(
        "path",
        type=Path,
        nargs='?',
        default=Path.cwd().as_posix(),
        help="Путь к директории (по умолчанию: текущая директория)"
    )
    parser.add_argument(
        "-i", "--indent",
        type=int,
        metavar="I",
        default=4,
        help="Выставляет значение отступа, по умолчанию 4"
    )

    parser.add_argument(
        "-p", "--prune",
        action='store_true',
        help="Выводит пустые директории"
    )

    parser.add_argument(
        "-d", "--depth",
        type=int,
        default=None,
        metavar="D",
        help="Ограничивает глубину вывода"
    )


    parser.add_argument(
        "-e", "--extension",
        action='append',
        type=lambda s: {ext.lstrip('.') for ext in s.split(',')},
        default=None,
        help="Фильтр по расширениям файлов (например: 'py,txt')"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="Перенаправляет поток вывода в указанный файл"
    )
    return parser


def has_valid_args(args: Namespace) -> tuple[bool, str | None]:
    """Проверить, что аргументы валидны."""
    path = args.path
    PROG = "tree"


    if args.indent < 1:
        return False, f"usage: {PROG} {PROG}: error: "

    if args.depth is not None and args.depth < 0:
        return False, "Глубина вывода >= 1"

    if args.output is not None and (Path(args.output).is_dir() or Path(args.output).is_symlink()):
        return False, f"usage: {PROG} {PROG}: error: "
    return True, None


def get_extension(path: Path) -> str:
    """Получить расширение файла, включая многоуровневые расширения."""
    parts = path.name.split('.')
    if len(parts) > 2 and not path.is_dir():
        return '.'.join(parts[-2:])
    return path.suffix.lstrip('.')


def is_dir_empty(dir: Path, path: Path, settings: RecursionSettings) -> None:
    if settings.extension is None:
        if dir == path:
            return
        if len(list(dir.iterdir())) == 0:
            parent = dir.parent
            dir.rmdir()
            is_dir_empty(parent, path, settings)
            return
        for file in dir.iterdir():
            if file.is_file() and not file.is_symlink():
                return
            if file.is_symlink():
                file.unlink()
                continue
            if file.is_dir():
                 is_dir_empty(file, path, settings)
    else:
        all_extensions = set().union(*settings.extension)
        if dir == path:
            return
        if len(list(dir.iterdir())) == 0:
            parent = dir.parent
            dir.rmdir()
            is_dir_empty(parent, path, settings)
            return
        for file in dir.iterdir():
            if file.parent.is_symlink():
                file.parent.unlink()
                continue
            if file.is_file() and get_extension(file) in all_extensions:
                return
            elif file.is_file() and get_extension(file) not in all_extensions:
                parent = file.parent
                file.unlink()
                is_dir_empty(parent, path, settings)
            elif file.is_dir():
                 is_dir_empty(file, path, settings)


def tree(path: Path, settings: RecursionSettings, current_depth: int = 0) -> None:
    """Вывести файловое древо."""
    if settings.depth is not None and settings.depth != 0:
        if current_depth >= settings.depth:
            return

    entries = sorted(path.iterdir(), key=lambda e: (e.is_file(), e.name))

    if settings.extension is not None:
        all_extensions = set().union(*settings.extension)
        entries = [e for e in entries if (get_extension(e) in all_extensions) or e.is_dir()]

    if current_depth == 0:
        if entries or not settings.prune:
            print(f"{path.as_posix()}/")
            if settings.depth == 0:
                return

    if settings.prune or settings.extension is not None:
        for entrie in entries:
            if not entrie.is_dir():
                continue
            else:
                is_dir_empty(entrie, path, settings)

    entries = sorted(path.iterdir(), key=lambda e: (e.is_file(), e.name))


    if settings.extension is not None:
        all_extensions = set().union(*settings.extension)
        entries = [e for e in entries if (get_extension(e) in all_extensions) or e.is_dir()]

    for entry in entries:
        if not entry.is_symlink():
            print(" " * (settings.indent * (current_depth + 1)) + f"{entry.name}{'/' if entry.is_dir() else ''}")
        if entry.is_dir():
            tree(entry, settings, current_depth + 1)





def main(argv: list[str] | None = None) -> None:
    """Запустить консольную утилиту."""

    parser = get_parser()
    args = parser.parse_args(argv)

    valid, error = has_valid_args(args)
    if not valid:
        print(error, file=sys.stderr)
        sys.exit(2)

    settings = RecursionSettings(
        indent=args.indent,
        prune=args.prune,
        depth=args.depth,
        extension=args.extension,
        output=args.output,
        path=args.path
    )

    if args.output is None:
        tree(Path(args.path).resolve(), settings)
    else:
        with open(args.output, 'w') as output:
            original_stdout = sys.stdout
            sys.stdout = output
            try:
                tree(Path(args.path).resolve(), settings)
            finally:
                sys.stdout = original_stdout


if __name__ == "__main__":
    main()
