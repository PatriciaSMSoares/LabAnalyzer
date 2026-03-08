from pathlib import Path


def scan_folder(path: str | Path, extensions: list, recursive: bool = False) -> list:
    """Scan folder for files with given extensions."""
    path = Path(path)
    if not path.is_dir():
        return []

    files = []
    ext_set = {e.lower() if e.startswith('.') else f'.{e.lower()}' for e in extensions}

    if recursive:
        for f in path.rglob('*'):
            if f.is_file() and f.suffix.lower() in ext_set:
                files.append(f)
    else:
        for f in path.iterdir():
            if f.is_file() and f.suffix.lower() in ext_set:
                files.append(f)

    return sorted(files)


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    if size_bytes < 1024:
        return f'{size_bytes} B'
    elif size_bytes < 1024 ** 2:
        return f'{size_bytes / 1024:.1f} KB'
    elif size_bytes < 1024 ** 3:
        return f'{size_bytes / 1024**2:.1f} MB'
    else:
        return f'{size_bytes / 1024**3:.1f} GB'


def get_file_size(path: str | Path) -> int:
    """Get file size in bytes."""
    try:
        return Path(path).stat().st_size
    except OSError:
        return 0
