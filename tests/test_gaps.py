"""Gap records follow the gap policy and field classes; each violation is reported."""
import copy
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from tools.check_gaps import check
from tools.strict_json import load
from tools.validate import validation_errors

ROOT = Path(__file__).resolve().parents[1]
POLICY = load(ROOT / 'spec/gap-path-policy.json')
CATALOGUE = load(ROOT / 'spec/field-catalogue.json')
MAPPING = load(ROOT / 'spec/mapping.json')
SCHEMA = load(ROOT / 'schema/hypothesis-1.schema.json')
FIVE = load(ROOT / 'tests/fixtures/fictional/fx_five.json')
FOUR = load(ROOT / 'tests/fixtures/fictional/fx_four.json')
STATEMENT = {'kind': 'card', 'pointer': '/author/layers/core/statement'}


def gap(path, disposition='not_supplied', **extra):
    return {'path': path, 'disposition': disposition, 'reason': 'Test reason.',
            'query_ids': [], 'inspected_artifacts': [], **extra}


def run(card):
    assert not validation_errors(SCHEMA, card), 'test card must stay schema-valid'
    return check(card, POLICY, CATALOGUE, MAPPING)


def codes(result):
    return {error['code'] for error in result['errors']}


def with_gaps(card, *gaps):
    card = copy.deepcopy(card)
    card['added']['gaps'] = list(gaps)
    return card


@pytest.mark.parametrize('path', [f'tests/fixtures/fictional/fx_{n}' for n in
                                  ('one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine')]
                         + ['examples/cards/muller-sheltering'])
def test_cards_pass(path):
    assert run(load(ROOT / f'{path}.json'))['valid']


def test_claim_without_intervention_needs_no_pharmacology_gap():
    result = run(FIVE)
    assert result['valid'] and not result['review_required']
    card = with_gaps(FIVE, gap('profile.dose_response.shape', 'not_applicable_scope', scope_ref=STATEMENT))
    assert codes(run(card)) == {'GAP_PROFILE_FIELD'}


def test_policy_counts():
    counts = {}
    for row in POLICY['fields']:
        counts[row['na_allowed']] = counts.get(row['na_allowed'], 0) + 1
    assert counts == {'never': 195, 'scope': 5, 'contract': 13}


def test_intervention_claim_cannot_declare_pharmacology_inapplicable():
    card = with_gaps(FOUR, gap('profile.dose_response.shape', 'not_applicable_scope', scope_ref=STATEMENT))
    assert 'GAP_NA_FORBIDDEN' in codes(run(card))


def test_scope_ref_must_resolve():
    missing = {'kind': 'card', 'pointer': '/author/layers/core/scope'}
    card = with_gaps(FOUR, gap('profile.combination.effect', 'not_applicable_scope', scope_ref=missing))
    assert 'GAP_SCOPE_UNBOUND' in codes(run(card))


@pytest.mark.parametrize('path', ['core.potential_benefit', 'profile.human_testability',
                                  'profile.biomarker.role', 'profile.biomarker.validation'])
def test_benefit_testability_biomarker_have_no_inapplicability(path):
    card = with_gaps(FIVE, gap(path, 'not_applicable_scope', scope_ref=STATEMENT))
    assert 'GAP_NA_FORBIDDEN' in codes(run(card))


@pytest.mark.parametrize('path', ['evidence.lines[].negated_flag', 'provenance.foreknowledge'])
def test_source_readable_fields_accept_search(path):
    card = with_gaps(FIVE, gap(path, 'searched_not_found', query_ids=['q1']))
    assert run(card)['valid']


def test_never_path_rejects_inapplicability():
    card = with_gaps(FIVE, gap('core.falsification_condition', 'not_applicable_scope', scope_ref=STATEMENT))
    assert 'GAP_NA_FORBIDDEN' in codes(run(card))


@pytest.mark.parametrize('path', ['core.assumptions[].fundamental', 'identity.duplicate_cluster_ref'])
def test_search_is_not_meaningful_for_author_only_and_system(path):
    card = with_gaps(FIVE, gap(path, 'searched_not_found', query_ids=['q1']))
    assert 'GAP_SEARCH_NOT_MEANINGFUL' in codes(run(card))


def test_searchable_field_accepts_search():
    card = with_gaps(FIVE, gap('core.falsification_condition', 'searched_not_found', query_ids=['q1']))
    assert run(card)['valid']


def test_pair_relation_is_a_contract_extension():
    assert run(with_gaps(FIVE, gap('pair.relation', 'not_applicable_contract')))['valid']
    card = with_gaps(FIVE, gap('core.scope', 'not_applicable_contract'))
    assert 'GAP_NA_FORBIDDEN' in codes(run(card))


def test_scope_without_condition_needs_review():
    result = run(with_gaps(FOUR, gap('profile.combination.effect', 'not_applicable_scope', scope_ref=STATEMENT)))
    assert result['valid'] and result['review_required']


@pytest.mark.parametrize('mutation, code', [
    ('unknown', 'GAP_PATH_UNKNOWN'),
    ('duplicate', 'GAP_PATH_DUPLICATE'),
    ('populated', 'GAP_PATH_POPULATED'),
    ('unbound_component', 'GAP_COMPONENT_UNBOUND'),
])
def test_structural_errors(mutation, code):
    if mutation == 'unknown':
        # The schema already rejects an unknown gap path; the checker reports it too.
        card = with_gaps(FIVE, gap('core.invented_field'))
        assert validation_errors(SCHEMA, card)
        assert code in codes(check(card, POLICY, CATALOGUE, MAPPING))
        return
    elif mutation == 'duplicate':
        card = with_gaps(FIVE, gap('core.scope'), gap('core.scope'))
    elif mutation == 'populated':
        card = with_gaps(FIVE, gap('core.statement'))
    else:
        card = with_gaps(FIVE, gap('predictions[0].test_cost.money_range'))
    assert code in codes(run(card))


def test_component_gap_with_parent_passes():
    card = copy.deepcopy(FOUR)
    del card['added']['layers']['predictions'][0]['test_cost']['value']['money_range']
    card['added']['gaps'] = [gap('predictions[0].test_cost.money_range')]
    assert run(card)['valid']


def test_other_standard_version_is_not_linted():
    card = copy.deepcopy(FIVE)
    card['standard_version'] = '1.2'
    assert codes(check(card, POLICY, CATALOGUE, MAPPING)) == {'GAP_STANDARD_VERSION'}


def test_policy_schema():
    schema = load(ROOT / 'schema/gap-path-policy-1.schema.json')
    Draft202012Validator.check_schema(schema)
    assert not validation_errors(schema, POLICY)
    bad = copy.deepcopy(POLICY)
    never = next(row for row in bad['fields'] if row['na_allowed'] == 'never')
    never['condition'] = {'id': 'no_translation_with_original_language',
                          'original_language_path': 'author.source.language', 'requires_no_translation': True}
    assert validation_errors(schema, bad)
    bad = copy.deepcopy(POLICY)
    scoped = next(row for row in bad['fields'] if 'condition' in row)
    scoped['condition'] = {**scoped['condition'], 'id': 'invented'}
    assert validation_errors(schema, bad)


def test_policy_covers_catalogue_exactly():
    assert [row['path'] for row in POLICY['fields']] and \
        {row['path'] for row in POLICY['fields']} == {row['path'] for row in CATALOGUE['fields']}
