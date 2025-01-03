from pathlib import Path


def is_cpython() -> bool:
    """Проверить, что используется `CPython`."""


def is_linux() -> bool:
    """Проверить, что используется `Linux`."""


def is_windows() -> bool:
    """Проверить, что используется `Windows`."""


def is_macos() -> bool:
    """Проверить, что используется `is_macOS`."""


def is_supported_platform() -> bool:
    """Проверить, что платформа поддерживается."""


def is_supported_python_version() -> bool:
    """Проверить, что версия `Python` поддерживается."""


def get_cpython_root() -> Path:
    """Получить путь до корня `CPython`."""


def get_interface_library() -> Path | None:
    """Получить путь до библиотеки-интерфейса, если она существует."""


def get_shared_library() -> Path:
    """Получить путь до разделяемой библиотеки."""


def get_header_files() -> list[Path]:
    """Получить список загловочных файлов."""


def get_include_directories() -> list[Path]:
    """Получить список директорий-префиксов."""


def main() -> None:
    """Запустить скрипт."""


if __name__ == "__main__":
    main()
