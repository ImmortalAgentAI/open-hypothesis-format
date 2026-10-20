"""Explicit calendar and RFC3339 validation independent of optional format extras."""
import datetime
import re

STAMP = re.compile(
    r'[0-9]{4}-[0-9]{2}-[0-9]{2}[Tt](?:[01][0-9]|2[0-3]):'
    r'[0-5][0-9]:[0-5][0-9](?:\.[0-9]+)?'
    r'(?:[Zz]|[+-](?:[01][0-9]|2[0-3]):[0-5][0-9])'
)


def date_time(value):
    """Validate a complete timestamp; this profile does not support leap seconds."""
    if not isinstance(value, str) or not STAMP.fullmatch(value):
        return False
    try:
        datetime.datetime.fromisoformat(
            value.replace('t', 'T').replace('z', 'Z').replace('Z', '+00:00')
        )
    except ValueError:
        return False
    return True


def date(value):
    if not isinstance(value, str) or not re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}', value):
        return False
    try:
        datetime.date.fromisoformat(value)
    except ValueError:
        return False
    return True


def self_check():
    positives = ['2026-10-16T15:00:00Z', '2026-10-16T15:00:00.123456+05:30',
                 '2024-02-29T23:59:59-03:45']
    negatives = ['2026-10-16T15:00:00+05:99', '2026-02-30T15:00:00Z',
                 '2026-10-16T15:00:00+00:60', '2026-10-16T15:00:00+25:00',
                 '2026-10-16T15:00:00', '2026-10-16T24:00:00Z',
                 '2026-10-16T15:00:60Z', '2026-10-16T15:00:00Z\n']
    if (not all(date_time(x) for x in positives) or any(date_time(x) for x in negatives)
            or not date('2024-02-29') or date('2026-02-29')):
        raise RuntimeError('Strict date validator failed its self-check')


def format_checker():
    """Register direct parsers explicitly, even when jsonschema extras are absent."""
    from jsonschema import FormatChecker
    checker = FormatChecker(formats=[])
    checker.checks('date-time')(lambda value: not isinstance(value, str) or date_time(value))
    checker.checks('date')(lambda value: not isinstance(value, str) or date(value))
    # Test the installed checker itself, not just the underlying parser.
    if (checker.conforms('2026-10-16T12:00:00+05:99', 'date-time')
            or not checker.conforms('2026-10-16T12:00:00Z', 'date-time')):
        raise RuntimeError('Strict timestamp format checking is unavailable')
    return checker


self_check()
