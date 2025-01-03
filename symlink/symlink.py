from pathlib import Path


def is_circular_symlink(symlink: Path) -> bool:
    try:
        if not symlink.lstat():
            raise FileNotFoundError()

        if not symlink.is_symlink():
            raise RuntimeError()

        visited_links = set()

        while symlink.is_symlink():
            if symlink in visited_links:
                return True

            visited_links.add(symlink)

            next_link = symlink.readlink()

            if not next_link.is_absolute():
                next_link = symlink.parent / next_link

            symlink = next_link

        return False
    except FileNotFoundError:
        raise
    except OSError:
        return False





