"""Moving predictions[].system and .intervention into $defs changed no rule of the 1.0.1 schema."""
import copy
import hashlib
import json
from pathlib import Path

import pytest

from tools.strict_json import load
from tools.validate import validation_errors

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = load(ROOT / 'schema/hypothesis-1.schema.json')
FIXTURES = sorted((ROOT / 'tests/fixtures/fictional').glob('fx_*.json'))
MOVED = [(zone, field) for zone in ('author', 'added') for field in ('system', 'intervention')]
# sha256 of the canonical JSON of schema/hypothesis-1.schema.json at tag v1.0.1
SCHEMA_1_0_1 = '84c0e01067a71204d66e83025b2c39caf65528ddb06108b4c8a2c50ffc382a80'


def canonical_sha256(document):
    text = json.dumps(document, sort_keys=True, ensure_ascii=False, separators=(',', ':'))
    return hashlib.sha256(text.encode()).hexdigest()


def prediction_fields(schema, zone):
    return schema['properties'][zone]['properties']['layers']['properties']['predictions']['items']['properties']


def test_inlining_the_moved_definitions_gives_the_1_0_1_schema():
    schema = copy.deepcopy(SCHEMA)
    for zone, field in MOVED:
        name = f'{zone}:{field}'
        fields = prediction_fields(schema, zone)
        assert fields[field] == {'$ref': '#/$defs/' + name.replace(':', '%3A')}
        fields[field] = schema['$defs'].pop(name)
    assert canonical_sha256(schema) == SCHEMA_1_0_1


@pytest.mark.parametrize('zone,field', MOVED)
def test_unknown_member_is_still_rejected(zone, field):
    card = load(FIXTURES[0])
    member = {'value': 'x', 'locator': 'p1'} if zone == 'author' else {'value': 'x', 'src': 'x'}
    predictions = card[zone]['layers'].setdefault('predictions', [])
    if not predictions:
        predictions.append({})
    predictions[0].setdefault(field, {})['made_up'] = member
    assert any('made_up' in error.message for error in validation_errors(SCHEMA, card))
