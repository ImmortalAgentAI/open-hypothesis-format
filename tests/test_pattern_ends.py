"""Every schema pattern ends where the string ends, in Python's re as in ECMA-262.

In Python's re, `$` also matches before one final line feed, so `^[0-9a-f]{40}$` accepted 40 hex digits
and a line feed; ECMA-262 does not. Each pattern therefore ends with the schema's own end anchor
`(?![\\s\\S])`, the same in both. A value with a final line feed never had the meaning of the pattern.
"""
import json
import re
from pathlib import Path

import pytest

from tests.test_ohf_1_2 import PETO, SCHEMA, as_1_2
from tools.validate import validation_errors

ROOT = Path(__file__).resolve().parents[1]
END = r'(?![\s\S])'
DOLLAR = re.compile(r'(?<!\\)(?:\\\\)*\$')
# The number of distinct patterns that use the end anchor. A new pattern needs a sample below and
# this count raised, so a pattern added without its end cannot pass unnoticed.
ANCHORED = 32
# One value each pattern accepts; a pattern may accept several of them.
SAMPLES = ['', 'x', '42', '2026', '2026-10', '2026-10-24', 'USD', '1.3.0', 'h_abc', 'h_abc@1', 'PMC123',
           '0' * 40, '0' * 64, 'sha256:' + '0' * 64, 'RO:0002211', 'biolink:affects', 'NCBITaxon:9606',
           'doi:10.1/x', '10.1234/abc', '/a', '/added/layers/core', '/author/layers/core',
           'core.atoms', 'core.atoms[0].requires', 'core.atoms[].scope', 'provenance.claim_author_coi',
           'appendix.rationale', 'core.explains[0].id', 'core.first_proposed']


def patterns():
    found = {}

    def walk(node, name):
        if isinstance(node, dict):
            if isinstance(node.get('pattern'), str):
                found.setdefault(node['pattern'], name)
            for value in node.values():
                walk(value, name)
        elif isinstance(node, list):
            for value in node:
                walk(value, name)
    for path in sorted((ROOT / 'schema').glob('*.json')):
        walk(json.loads(path.read_text()), path.name)
    return found


def pointer(pattern):
    """A JSON pointer pattern: a key may hold any character but `~` and `/`, a line feed too."""
    return '[^~/]' in pattern


def test_no_pattern_uses_a_dollar():
    assert not [p for p in patterns() if DOLLAR.search(p)]


def test_the_anchored_patterns_are_counted():
    assert sum(END in p for p in patterns()) == ANCHORED


@pytest.mark.parametrize('pattern', [p for p in patterns() if END in p], ids=lambda p: p[:40])
def test_a_final_line_feed_is_not_accepted(pattern):
    accepted = [value for value in SAMPLES if re.search(pattern, value)]
    assert accepted, 'add a value this pattern accepts to SAMPLES'
    for value in accepted:
        # In a pointer a final line feed ends a key, so it is accepted after any non-empty pointer.
        expected = pointer(pattern) and value != ''
        assert bool(re.search(pattern, value + '\n')) == expected, value


def test_a_card_value_with_a_final_line_feed_is_rejected():
    card = as_1_2(PETO)
    assert not validation_errors(SCHEMA, card)
    card['author']['source']['source_text_sha256'] += '\n'
    assert validation_errors(SCHEMA, card)
