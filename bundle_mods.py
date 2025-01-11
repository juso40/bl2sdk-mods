import zipfile
from pathlib import Path

FILE_EXTENSION = ".sdkmod"

print(Path().absolute())


def get_mod_dirs() -> list[Path]:
    mod_dirs = []
    for path in Path().iterdir():
        if not path.is_dir():
            continue
        if path.name.startswith(("__", ".")):
            continue
        mod_dirs.append(path)
    return mod_dirs


def create_mod_zip(mod_dir: Path) -> None:
    with zipfile.ZipFile(mod_dir/mod_dir.with_suffix(FILE_EXTENSION), "w") as zf:
        for child in mod_dir.rglob("*"):
            if child.is_dir() or "__pycache__" in str(child.absolute()) or child.suffix == FILE_EXTENSION:
                continue
            zf.write(child, mod_dir.name / child.relative_to(mod_dir))


def main() -> None:
    for mod_dir in get_mod_dirs():
        create_mod_zip(mod_dir)


if __name__ == "__main__":
    main()
