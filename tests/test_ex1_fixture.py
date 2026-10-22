"""hyp-arena Example 1 as an OHF 1.1 card: the new fields on real content, and mutations that break them.

The fixture is built by arena-standard from docs/spec/hypothesis-card-examples.md of hyp-arena (MIT, Daniil Radyush,
commit 1c38659) on the skeleton of fx_four; its quotes are those of the PubMed abstracts that Example 1 gives.
"""
import copy
from pathlib import Path

import pytest

from tools.check_gaps import check as check_gaps
from tools.check_refs import check as check_refs
from tools.content_hash import content_hash
from tools.strict_json import load
from tools.validate import pointer, validation_errors

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = load(ROOT / 'schema/hypothesis-1.schema.json')
CARD = load(ROOT / 'tests/fixtures/ex1-rapamycin-1.1.json')


def layers(card):
    return card['added']['layers']


def test_ex1_is_a_valid_1_1_card():
    assert CARD['standard_version'] == '1.1' and CARD['content_hash'] == content_hash(CARD)
    assert not validation_errors(SCHEMA, CARD)
    outcome = check_refs(CARD)
    assert outcome['valid'], outcome['errors']
    assert not [w for w in outcome['warnings'] if w['code'].startswith('REF_PROXIMITY')]
    assert check_gaps(CARD, load(ROOT / 'spec/gap-path-policy.json'), load(ROOT / 'spec/field-catalogue.json'),
                      load(ROOT / 'spec/mapping.json'))['valid']


def test_ex1_shows_the_new_fields():
    lines = layers(CARD)['evidence']['lines']
    assert [line['sample']['value']['population'] for line in lines[1:]] == ['subgroup', 'whole_sample']  # item 2
    assert {atom['id'] for atom in layers(CARD)['core']['atoms'] if 'triple' in atom} == {'c1', 'c3'}  # item 4
    assert layers(CARD)['evidence']['excluded'][0]['reason'] == 'inherited_mismatch'  # item 5
    assert [line['human_proximity']['value'] for line in lines] == ['mammal', 'human_marker', 'human_marker']  # item 6
    assert layers(CARD)['core']['atoms'][1]['requires']['value'] == ['c1']  # item 9


def mutate(path, value):
    def change(card):
        *head, last = path
        node = card
        for key in head:
            node = node[key]
        node[last] = value
    return change


L = ['added', 'layers']
LINES = L + ['evidence', 'lines']


@pytest.mark.parametrize('change,code', [
    (mutate(LINES + [2, 'human_proximity', 'value'], 'human_clinical'), 'REF_PROXIMITY_MISMATCH'),
    (mutate(L + ['core', 'atoms', 0, 'requires'], {'value': ['c2'], 'src': 'raw'}), 'REF_ATOM_LINK'),
    (mutate(L + ['profile', 'aging_hallmarks', 'value', 0, 'atom_refs'], ['c9']), 'REF_UNKNOWN_ID'),
    (mutate(LINES + [2, 'result_estimate'], None), 'REF_ESTIMATE_IN_QUOTE'),
], ids=['visceral_adiposity_as_clinical', 'c1_requires_c2_cycle', 'hallmark_on_no_atom', 'numbers_without_estimate'])
def test_ex1_mutation_is_reported(change, code):
    card = copy.deepcopy(CARD)
    change(card)
    if card['added']['layers']['evidence']['lines'][2].get('result_estimate', 1) is None:
        del card['added']['layers']['evidence']['lines'][2]['result_estimate']
    assert code in {item['code'] for item in check_refs(card)['errors']}


@pytest.mark.parametrize('change,at', [
    (mutate(LINES + [1, 'sample', 'value', 'population'], 'whole_sample'), '/added/layers/evidence/lines/1/sample/value'),
    (mutate(L + ['core', 'atoms', 2, 'triple', 'value', 'relation', 'id'], 'extends_lifespan_in'),
     '/added/layers/core/atoms/2/triple/value/relation/id'),
    (mutate(L + ['evidence', 'excluded', 0, 'reason'], 'species'), '/added/layers/evidence/excluded/0/reason'),
], ids=['subgroup_wording_on_whole_sample', 'hyparena_relation_word', 'reason_outside_list'])
def test_ex1_schema_mutation_is_rejected(change, at):
    card = copy.deepcopy(CARD)
    change(card)
    assert at in {pointer(error) for error in validation_errors(SCHEMA, card)}
