"""predictions[].system and .intervention live in $defs and still reject unknown members.

The move itself was checked at commit c44a364 by inlining the definitions again and comparing the
canonical hash with the schema at v1.0.1; 1.1 then changes these definitions on purpose."""
from pathlib import Path

import pytest

from tools.strict_json import load
from tools.validate import validation_errors

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = load(ROOT / 'schema/hypothesis-1.schema.json')
FIXTURES = sorted((ROOT / 'tests/fixtures/fictional').glob('fx_*.json'))
MOVED = [(zone, field) for zone in ('author', 'added') for field in ('system', 'intervention')]


@pytest.mark.parametrize('zone,field', MOVED)
def test_unknown_member_is_still_rejected(zone, field):
    card = load(FIXTURES[0])
    member = {'value': 'x', 'locator': 'p1'} if zone == 'author' else {'value': 'x', 'src': 'x'}
    predictions = card[zone]['layers'].setdefault('predictions', [])
    if not predictions:
        predictions.append({})
    predictions[0].setdefault(field, {})['made_up'] = member
    assert any('made_up' in error.message for error in validation_errors(SCHEMA, card))
