"""OHF 1.1: each new rule accepts a card that follows it and rejects a mutation that breaks it."""
import copy
import hashlib
from pathlib import Path

import pytest

from tools.check_gaps import check as check_gaps
from tools.check_refs import check as check_refs
from tools.strict_json import load
from tools.validate import pointer, validation_errors

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = load(ROOT / 'schema/hypothesis-1.schema.json')
TERMS = load(ROOT / 'vocabularies/terms-1.json')
BASE = load(ROOT / 'tests/fixtures/fictional/fx_four.json')
POLICY = load(ROOT / 'spec/gap-path-policy.json')
CATALOGUE = load(ROOT / 'spec/field-catalogue.json')
MAPPING = load(ROOT / 'spec/mapping.json')


def terms_pin():
    return 'sha256:' + hashlib.sha256((ROOT / 'vocabularies/terms-1.json').read_bytes()).hexdigest()


def card_1_1():
    """fx_four as an OHF 1.1 card, with a closed route, endpoint kind and control type."""
    card = copy.deepcopy(BASE)
    card['standard_version'] = '1.1'
    card['vocabularies']['terms'] = {'id': 'ohf:terms@1', 'sha256': terms_pin()}
    prediction = card['added']['layers']['predictions'][0]
    prediction['intervention'] = {'route': {'value': 'mixed into the feed, fictional', 'src': 'statement',
                                            'term': 'diet'}}
    prediction['endpoint_kind'] = {'value': 'level of counter Y', 'src': 'statement', 'term': 'biomarker'}
    prediction['control_type'] = {'value': ['vehicle'], 'src': 'statement'}
    return card


def prediction(card):
    return card['added']['layers']['predictions'][0]


def as_1_0(card):
    card['standard_version'] = '1.0'


MUTATIONS = {
    # M0a: a 1.0 card cannot carry a 1.1 field
    'v1_0_with_term': lambda card: as_1_0(card),
    'v1_0_with_control_type': lambda card: (as_1_0(card), prediction(card)['intervention']['route'].pop('term'),
                                            prediction(card)['endpoint_kind'].pop('term'),
                                            card['vocabularies'].pop('terms')),
    # M0b: a 1.1 card needs the closed term, not only the 1.0 wording
    'v1_1_route_without_term': lambda card: prediction(card)['intervention']['route'].pop('term'),
    'v1_1_endpoint_without_term': lambda card: prediction(card)['endpoint_kind'].pop('term'),
    # M0c: the terms vocabulary is pinned by hash, and a 1.1 card pins it
    'wrong_terms_pin': lambda card: card['vocabularies']['terms'].__setitem__('sha256', 'sha256:' + '0' * 64),
    'v1_1_without_terms_pin': lambda card: card['vocabularies'].pop('terms'),
    # M8a-c: closed terms; other needs a note and only other has one
    'route_not_a_term': lambda card: prediction(card)['intervention']['route'].__setitem__('term', 'orally'),
    'other_without_note': lambda card: prediction(card)['intervention']['route'].__setitem__('term', 'other'),
    'note_without_other': lambda card: prediction(card)['endpoint_kind'].__setitem__('note', 'a fictional note'),
    'control_not_a_term': lambda card: prediction(card)['control_type'].__setitem__('value', ['sham']),
    'control_other_without_note': lambda card: prediction(card)['control_type'].__setitem__('value', ['other']),
    'control_empty': lambda card: prediction(card)['control_type'].__setitem__('value', []),
}
PREDICTION = '/added/layers/predictions/0'
# Where the schema reports each mutation.
EXPECTED = {
    'v1_0_with_term': PREDICTION + '/intervention/route',
    'v1_0_with_control_type': PREDICTION,
    'v1_1_route_without_term': PREDICTION + '/intervention/route',
    'v1_1_endpoint_without_term': PREDICTION + '/endpoint_kind',
    'wrong_terms_pin': '/vocabularies/terms/sha256',
    'v1_1_without_terms_pin': '/vocabularies',
    'route_not_a_term': PREDICTION + '/intervention/route/term',
    'other_without_note': PREDICTION + '/intervention/route',
    'note_without_other': PREDICTION + '/endpoint_kind',
    'control_not_a_term': PREDICTION + '/control_type/value/0',
    'control_other_without_note': PREDICTION + '/control_type',
    'control_empty': PREDICTION + '/control_type/value',
}


def test_card_1_1_is_valid():
    assert not validation_errors(SCHEMA, card_1_1())


def test_other_with_note_is_valid():
    card = card_1_1()
    prediction(card)['intervention']['route'].update({'term': 'other', 'note': 'fictional mist chamber'})
    prediction(card)['control_type'].update({'value': ['vehicle', 'other'], 'note': 'fictional sham run'})
    assert not validation_errors(SCHEMA, card)


@pytest.mark.parametrize('mutation', MUTATIONS)
def test_mutation_is_rejected(mutation):
    card = card_1_1()
    MUTATIONS[mutation](card)
    assert EXPECTED[mutation] in {pointer(error) for error in validation_errors(SCHEMA, card)}


def test_terms_pin_matches_the_vocabulary():
    pinned = SCHEMA['properties']['vocabularies']['properties']['terms']['properties']['sha256']['const']
    assert pinned == terms_pin()


@pytest.mark.parametrize('field,vocabulary', [
    (('$defs', 'added:intervention', 'properties', 'route', 'properties', 'term'), 'route'),
    (('properties', 'added', 'properties', 'layers', 'properties', 'predictions', 'items', 'properties',
      'endpoint_kind', 'properties', 'term'), 'endpoint_kind'),
    (('properties', 'added', 'properties', 'layers', 'properties', 'predictions', 'items', 'properties',
      'control_type', 'properties', 'value', 'items'), 'control_type'),
])
def test_schema_terms_are_the_vocabulary(field, vocabulary):
    node = SCHEMA
    for key in field:
        node = node[key]
    assert node['enum'] == [term['id'] for term in TERMS['vocabularies'][vocabulary]]


def test_checkers_accept_a_1_1_card():
    card = card_1_1()
    assert check_refs(card)['valid'], check_refs(card)['errors']
    gaps = check_gaps(card, POLICY, CATALOGUE, MAPPING)
    assert gaps['valid'], gaps['errors']
