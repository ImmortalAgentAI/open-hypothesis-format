"""Validate JSON documents against an OHF schema."""
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from jsonschema import Draft202012Validator  # noqa: E402
from jsonschema.exceptions import SchemaError  # noqa: E402

from strict_dates import format_checker, self_check  # noqa: E402
from strict_json import load  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA = ROOT / 'schema/hypothesis-1.schema.json'


def validation_errors(schema, document):
    """Return every schema error, sorted by location; format checks are explicit."""
    self_check()
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=format_checker())
    return sorted(validator.iter_errors(document),
                  key=lambda error: (tuple(str(x) for x in error.absolute_path), error.message))


def pointer(error):
    return '/' + '/'.join(str(x).replace('~', '~0').replace('/', '~1')
                          for x in error.absolute_path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--schema', type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument('documents', type=Path, nargs='+')
    args = parser.parse_args()
    try:
        schema = load(args.schema)
        Draft202012Validator.check_schema(schema)
    except (OSError, ValueError, SchemaError) as error:
        print(f'{args.schema}: invalid schema: {error}', file=sys.stderr)
        return 2
    failed = False
    for path in args.documents:
        try:
            errors = validation_errors(schema, load(path))
        except (OSError, ValueError) as error:
            print(f'{path}: {error}', file=sys.stderr)
            failed = True
            continue
        for error in errors:
            print(f'{path}:{pointer(error)}: {error.message}', file=sys.stderr)
        if not errors:
            print(f'{path}: OK')
        failed |= bool(errors)
    return int(failed)


if __name__ == '__main__':
    raise SystemExit(main())
