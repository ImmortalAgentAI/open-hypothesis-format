"""Compute or check a converter pin: SHA-256 of the listing of the converter's rule files.

The rules of a converter are kept in examples/converters/<converter>-<version>/. The listing
has one line per file, `<path> sha256:<hex of the file>`, with the path relative to that
directory in POSIX form, sorted by path, each line ending in a newline. Only files under the
directory are hashed, so the pin reproduces from the repository alone. The converter name and
version may hold only [a-z0-9.-], and the directory may hold no symbolic link.
"""
import argparse
import hashlib
import os
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from strict_json import load  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CONVERTERS = ROOT / 'examples/converters'
# Converted under the rules in examples/cards/CONVERSION.md, pinned by that file's SHA-256.
SINGLE_FILE = {'ohf-example-conversion': ROOT / 'examples/cards/CONVERSION.md'}
NAME = re.compile(r'[a-z0-9.-]+')


def sha256(data):
    return 'sha256:' + hashlib.sha256(data).hexdigest()


def converter_hash(directory):
    directory = Path(directory)
    if directory.is_symlink():
        raise ValueError(f'{directory}: the rules directory is a symbolic link')
    files = []
    for top, dirs, names in os.walk(directory):
        for name in dirs + names:
            path = Path(top) / name
            if path.is_symlink():
                raise ValueError(f'{path}: a symbolic link in the rules directory')
            if name in names:
                files.append(path)
    files.sort(key=lambda f: f.relative_to(directory).as_posix())
    listing = ''.join(f'{f.relative_to(directory).as_posix()} {sha256(f.read_bytes())}\n' for f in files)
    return sha256(listing.encode('utf-8'))


def pin_errors(card):
    """Errors when the card's converter_hash is not the hash of rules kept in the repository."""
    by = card['added']['by']
    name, version, pinned = by['converter'], by['converter_version'], by['converter_hash']
    if name in SINGLE_FILE:
        actual = sha256(SINGLE_FILE[name].read_bytes())
    else:
        if not (isinstance(name, str) and isinstance(version, str) and NAME.fullmatch(name) and NAME.fullmatch(version)):
            return [f'converter {name!r} {version!r}: name and version may hold only [a-z0-9.-]']
        directory = CONVERTERS / f'{name}-{version}'
        if CONVERTERS.is_symlink():
            return [f'{CONVERTERS.relative_to(ROOT)}: a symbolic link']
        if not directory.is_dir():
            return [f'converter {name} {version}: no rules in {directory.relative_to(ROOT)}']
        try:
            actual = converter_hash(directory)
        except ValueError as e:
            return [str(e)]
    return [] if pinned == actual else [f'converter_hash {pinned} is not the hash of the rules, {actual}']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true',
                        help='treat the paths as cards and fail when a converter pin differs')
    parser.add_argument('paths', type=Path, nargs='+')
    args = parser.parse_args()
    failed = False
    for path in args.paths:
        if args.check:
            errors = pin_errors(load(path))
            for error in errors:
                print(f'{path}: {error}')
            failed |= bool(errors)
        else:
            print(f'{converter_hash(path)}  {path}')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
