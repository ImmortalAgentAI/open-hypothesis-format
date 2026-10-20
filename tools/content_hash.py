"""Compute or check a card's content hash: SHA-256 of its RFC 8785 form without `content_hash`."""
import argparse
import hashlib
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

import rfc8785  # noqa: E402

from strict_json import load  # noqa: E402


def content_hash(card):
    body = {key: value for key, value in card.items() if key != 'content_hash'}
    return 'sha256:' + hashlib.sha256(rfc8785.dumps(body)).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true',
                        help='fail when a stored content_hash differs')
    parser.add_argument('cards', type=Path, nargs='+')
    args = parser.parse_args()
    failed = False
    for path in args.cards:
        card = load(path)
        actual = content_hash(card)
        if args.check:
            if card.get('content_hash') != actual:
                print(f'{path}: content_hash {card.get("content_hash")} != {actual}',
                      file=sys.stderr)
                failed = True
        else:
            print(f'{actual}  {path}')
    return int(failed)


if __name__ == '__main__':
    raise SystemExit(main())
