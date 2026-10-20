"""Catalogue, reference data and card examples stay consistent."""
from pathlib import Path

import pytest

from tools.strict_json import load

ROOT = Path(__file__).resolve().parents[1]
CATALOGUE = load(ROOT / 'spec/field-catalogue.json')['fields']
REFERENCE = load(ROOT / 'spec/field-reference.json')['fields']
CARDS = {'muller-sheltering': 'examples/cards/muller-sheltering.json',
         **{f'fx_{name}': f'tests/fixtures/fictional/fx_{name}.json'
            for name in ('one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight')}}


def resolve(document, pointer):
    for token in pointer.split('/')[1:]:
        token = token.replace('~1', '/').replace('~0', '~')
        document = document[int(token)] if isinstance(document, list) else document[token]
    return document


def test_reference_matches_catalogue_row_for_row():
    assert [{k: v for k, v in row.items() if k != 'card_example'} for row in REFERENCE] == CATALOGUE
    assert all(row['card_example']['card'] in CARDS for row in REFERENCE if 'card_example' in row)


def test_every_field_has_a_class():
    assert {row['field_class'] for row in CATALOGUE} <= {'searchable', 'author_only', 'system'}
    assert all('field_class' in row for row in CATALOGUE)


@pytest.mark.parametrize('row', [r for r in REFERENCE if 'pointer' in r.get('card_example', {})],
                         ids=lambda r: r['path'])
def test_example_value_is_the_card_value(row):
    example = row['card_example']
    card = load(ROOT / CARDS[example['card']])
    assert resolve(card, example['pointer']) == example['value']


def test_gap_examples_are_card_gaps():
    gaps = [r for r in REFERENCE if 'gap' in r.get('card_example', {})]
    assert gaps
    for row in gaps:
        card = load(ROOT / CARDS[row['card_example']['card']])
        assert any(row['card_example']['gap'].startswith(f"`{gap['path']}`") for gap in card['added']['gaps'])
