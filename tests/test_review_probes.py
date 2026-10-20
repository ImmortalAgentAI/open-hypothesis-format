"""Mutations of the example card from an external review: each defect is reported."""
import copy
from pathlib import Path

import pytest

from tools.check_gaps import check as check_gaps
from tools.check_refs import check as check_refs
from tools.content_hash import content_hash
from tools.strict_json import load
from tools.validate import validation_errors

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = load(ROOT / 'schema/hypothesis-1.schema.json')
POLICY = load(ROOT / 'spec/gap-path-policy.json')
CATALOGUE = load(ROOT / 'spec/field-catalogue.json')
MAPPING = load(ROOT / 'spec/mapping.json')
PROFILES = load(ROOT / 'vocabularies/profiles-1.json')
CARD = load(ROOT / 'examples/cards/muller-sheltering.json')


def empty_science_full(card):
    card['author']['layers'] = {}
    card['added']['layers'] = {'profile': {'domain': 'none'}}
    card['added']['gaps'] = []
    card['added']['integrity']['entailment'] = []
    card['added']['completeness']['level'] = 'full'


MUTATIONS = {
    'baseline': lambda card: None,
    'dangling_src': lambda card: card['added']['layers']['core']['scope'].__setitem__('src', 'NONEXISTENT_SOURCE'),
    'empty_source_registry': lambda card: card['added'].__setitem__('sources', {}),
    'missing_atom_parent': lambda card: card['added']['layers']['core']['atoms'][0].__setitem__(
        'parent_ref', 'NOT_AN_ATOM'),
    'dangling_mechanism_entity': lambda card: card['added']['layers']['mechanism'].__setitem__(
        'steps', [{'subject_ref': 'MISSING_ENTITY', 'object_ref': 'ALSO_MISSING'}]),
    'no_gaps': lambda card: card['added'].__setitem__('gaps', []),
    'false_full_label': lambda card: card['added']['completeness'].__setitem__('level', 'full'),
    'empty_science_full': empty_science_full,
    'future_assessments': lambda card: card['added']['integrity']['entailment'][0].__setitem__(
        'checked_at', '1900-01-01T00:00:00Z'),
    'duplicate_evidence_id': lambda card: card['added']['layers']['evidence']['lines'][1].__setitem__(
        'id', card['added']['layers']['evidence']['lines'][0]['id']),
    'contradictory_generation': lambda card: card['author'].__setitem__(
        'generation', {'run_id': 'run-1', 'generated': 1, 'submitted': 50, 'submits_all': True}),
    'impossible_gap_subfield': lambda card: card['added']['gaps'].append({
        'path': 'core.statement.made_up', 'disposition': 'not_supplied', 'reason': 'test',
        'query_ids': [], 'inspected_artifacts': []}),
}
# The reference check that reports each mutation; None where only the schema or the gap check does.
EXPECTED = {
    'dangling_src': 'REF_SOURCE_UNKNOWN',
    'empty_source_registry': 'REF_SOURCES_EMPTY',
    'missing_atom_parent': 'REF_UNKNOWN_ID',
    'dangling_mechanism_entity': 'REF_UNKNOWN_ID',
    'false_full_label': 'REF_COMPLETENESS_OVERSTATED',
    'empty_science_full': 'REF_COMPLETENESS_OVERSTATED',
    'future_assessments': 'REF_TIME_ORDER',
    'duplicate_evidence_id': 'REF_DUPLICATE_ID',
    'contradictory_generation': 'REF_GENERATION_INCONSISTENT',
    'impossible_gap_subfield': None,
}


def run(name):
    card = copy.deepcopy(CARD)
    MUTATIONS[name](card)
    card['content_hash'] = content_hash(card)
    return (list(validation_errors(SCHEMA, card)), check_refs(card),
            check_gaps(card, POLICY, CATALOGUE, MAPPING, PROFILES))


def test_every_mutation_has_an_expectation():
    assert set(MUTATIONS) == set(EXPECTED) | {'baseline', 'no_gaps'}


def test_baseline_passes():
    schema, refs, gaps = run('baseline')
    assert not schema and refs['valid'] and gaps['valid']
    assert not refs['warnings']


@pytest.mark.parametrize('name', sorted(EXPECTED))
def test_mutation_is_caught(name):
    schema, refs, gaps = run(name)
    assert schema or not refs['valid'] or not gaps['valid']
    if EXPECTED[name]:
        assert EXPECTED[name] in {e['code'] for e in refs['errors']}


def test_removed_gaps_are_out_of_scope():
    # check_gaps checks the gaps a card lists; it does not show that every missing
    # applicable field is listed. A coverage report is a separate, later tool.
    schema, refs, gaps = run('no_gaps')
    assert not schema and refs['valid'] and gaps['valid']
