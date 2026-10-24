"""Every end assertion of a schema pattern is the end of the string, in Python's re as in ECMA-262.

In Python's re, `$` also matches before one final line feed, so `^[0-9a-f]{40}$` accepted 40 hex digits
and a line feed; ECMA-262 does not. A pattern anchored at the end therefore uses the schema's own end
anchor `(?![\\s\\S])`, the same in both. A value with a final line feed never had the meaning of the pattern.
The few patterns that match a prefix or any non-blank text are listed by name, so a pattern that loses its
end cannot pass as one of them.
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
# The number of distinct patterns that use the end anchor, and of the pattern nodes that use it. A new
# pattern needs a sample below and these counts raised, so a pattern added or left without its end cannot
# pass unnoticed, even where another copy of the same pattern keeps its end.
ANCHORED = 33
ANCHORED_NODES = 107
# The patterns that are not anchored at the end, on purpose.
UNANCHORED = {
    '\\S': 'any text with a non-blank character',
    '^[Ll][Ii][Cc][Ee][Nn][Ss][Ee][Rr][Ee][Ff]-': 'a LicenseRef- id, in any letter case, that needs the licence pin',
    '^\\d{4}-\\d{2}-\\d{2}[Tt]': 'a date with a time, telling it from a date; the format date-time checks the rest',
    '^/': 'a JSON pointer, telling it from a reference by id',
}
# One value each pattern accepts; a pattern may accept several of them.
SAMPLES = ['', 'x', '42', '2026', '2026-10', '2026-10-24', 'USD', '1.3.0', 'h_abc', 'h_abc@1', 'PMC123',
           '0' * 40, '0' * 64, 'sha256:' + '0' * 64, 'RO:0002211', 'biolink:affects', 'NCBITaxon:9606',
           'doi:10.1/x', '10.1234/abc', '/a', '/added/layers/core', '/author/layers/core',
           'core.atoms', 'core.atoms[0].requires', 'core.atoms[].scope', 'provenance.claim_author_coi',
           'appendix.rationale', 'core.explains[0].id', 'core.first_proposed', 'core.names']


def pattern_nodes():
    """Every pattern of every schema, once for each node that holds it."""
    found = []

    def walk(node, where):
        if isinstance(node, dict):
            if isinstance(node.get('pattern'), str):
                found.append((node['pattern'], where))
            for key, value in node.items():
                walk(value, f'{where}/{key}')
        elif isinstance(node, list):
            for i, value in enumerate(node):
                walk(value, f'{where}/{i}')
    for path in sorted((ROOT / 'schema').glob('*.json')):
        walk(json.loads(path.read_text()), path.name)
    return found


def patterns():
    return {pattern: where for pattern, where in reversed(pattern_nodes())}


def pointer(pattern):
    """A JSON pointer pattern: a key may hold any character but `~` and `/`, a line feed too."""
    return '[^~/]' in pattern


def test_no_pattern_uses_a_dollar():
    assert not [p for p in patterns() if DOLLAR.search(p)]


def test_the_anchored_patterns_are_counted():
    assert sum(END in p for p in patterns()) == ANCHORED
    assert sum(END in p for p, _ in pattern_nodes()) == ANCHORED_NODES


def test_every_pattern_node_is_anchored_or_named_as_unanchored():
    assert not [(p, where) for p, where in pattern_nodes() if END not in p and p not in UNANCHORED]
    assert {p for p, _ in pattern_nodes() if END not in p} == set(UNANCHORED)


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
