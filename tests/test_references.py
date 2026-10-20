"""Typed references, identifier namespaces, source records and record invariants fail closed."""
import copy
from pathlib import Path

import pytest

from tools.check_refs import check as check_refs
from tools.strict_json import load
from tools.validate import validation_errors

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = load(ROOT / 'schema/hypothesis-1.schema.json')
CARD = load(ROOT / 'examples/cards/muller-sheltering.json')
LINE = '/added/layers/evidence/lines/0'


def card():
    return copy.deepcopy(CARD)


def added(document):
    return document['added']['layers']


def with_mechanism(document):
    """Add two entities and one typed step to the example card."""
    added(document)['mechanism']['entities'] = [
        {'id': 'en_lof', 'label': {'value': 'loss-of-function allele', 'src': 'conditions'}},
        {'id': 'en_y', 'label': {'value': 'Y-linked gene', 'src': 'conditions'}}]
    added(document)['mechanism']['steps'] = [{
        'id': {'value': 's_loss', 'src': 'conditions'},
        'subject_ref': {'value': 'en_lof', 'src': 'conditions'},
        'relation': {'value': 'decreases', 'src': 'conditions'},
        'object_ref': {'value': 'en_y', 'src': 'conditions'},
        'evidence_refs': [{'value': 'e_early_models', 'src': 'conditions'}]}]
    return document


def result(document):
    assert not validation_errors(SCHEMA, document), 'test card must stay schema-valid'
    return check_refs(document)


def codes(document):
    return {e['code'] for e in result(document)['errors']}


def step(document):
    return added(document)['mechanism']['steps'][0]


def test_typed_mechanism_references_resolve():
    document = with_mechanism(card())
    assert result(document)['valid'], result(document)['errors']


@pytest.mark.parametrize('mutation, code', [
    ('subject_names_a_line', 'REF_WRONG_TARGET'),
    ('subject_pointer_to_a_line', 'REF_WRONG_TARGET'),
    ('object_external', 'REF_WRONG_TARGET'),
    ('step_evidence_unknown', 'REF_UNKNOWN_ID'),
    ('step_evidence_names_an_atom', 'REF_WRONG_TARGET'),
    ('target_entity_unknown', 'REF_UNKNOWN_ID'),
    ('duplicate_entity', 'REF_DUPLICATE_ID'),
    ('duplicate_step', 'REF_DUPLICATE_ID'),
])
def test_mechanism_reference_rejects(mutation, code):
    document = with_mechanism(card())
    mechanism = added(document)['mechanism']
    if mutation == 'subject_names_a_line':
        step(document)['subject_ref']['value'] = 'e_early_models'
    elif mutation == 'subject_pointer_to_a_line':
        step(document)['subject_ref']['value'] = {'kind': 'card', 'pointer': LINE}
    elif mutation == 'object_external':
        step(document)['object_ref']['value'] = {'kind': 'external', 'uri': 'urn:example:y', 'limitation': 'Test.'}
    elif mutation == 'step_evidence_unknown':
        step(document)['evidence_refs'][0]['value'] = 'e_missing'
    elif mutation == 'step_evidence_names_an_atom':
        step(document)['evidence_refs'][0]['value'] = 'a_y_decay'
    elif mutation == 'target_entity_unknown':
        mechanism['molecular_targets'] = {'value': [{'label': 'Target', 'id': 'GO:0000001', 'id_scheme': 'GO',
                                                     'role': 'primary', 'entity_ref': 'en_missing'}], 'src': 'conditions'}
    elif mutation == 'duplicate_entity':
        mechanism['entities'].append(copy.deepcopy(mechanism['entities'][0]))
    else:
        mechanism['steps'].append(copy.deepcopy(step(document)))
    assert code in codes(document)


def test_molecular_target_names_a_declared_entity():
    document = with_mechanism(card())
    added(document)['mechanism']['molecular_targets'] = {'value': [{
        'label': 'Target', 'id': 'GO:0000001', 'id_scheme': 'GO', 'role': 'primary', 'entity_ref': 'en_y'}],
        'src': 'conditions'}
    assert result(document)['valid']


def atom(document, index=0):
    return added(document)['core']['atoms'][index]


@pytest.mark.parametrize('parent', [
    None, 'a_y_decay', {'kind': 'card', 'pointer': '/added/layers/core/atoms/3'}, 'h_other-proposition@2'])
def test_atom_parent_is_an_atom_or_external(parent):
    document = card()
    atom(document)['parent_ref'] = {'value': parent, 'src': 'assumptions'} if parent else None
    outcome = result(document)
    assert outcome['valid'], outcome['errors']
    listed = [entry['reference'] for entry in outcome['external']]
    assert ('h_other-proposition@2' in listed) == (parent == 'h_other-proposition@2')


@pytest.mark.parametrize('parent, code', [
    ({'value': {'kind': 'card', 'pointer': LINE}, 'src': 'assumptions'}, 'REF_WRONG_TARGET'),
    ('e_early_models', 'REF_WRONG_TARGET'),
    ('a_sex_dimorphic', 'REF_WRONG_TARGET'),
])
def test_atom_parent_rejects(parent, code):
    document = card()
    atom(document)['parent_ref'] = parent
    assert code in codes(document)


def test_atom_parent_cycle_is_rejected():
    document = card()
    atom(document, 0)['parent_ref'] = 'a_recessive'
    atom(document, 1)['parent_ref'] = 'a_sex_dimorphic'
    assert 'REF_WRONG_TARGET' in codes(document)


def line(document, index=0):
    return added(document)['evidence']['lines'][index]


@pytest.mark.parametrize('target', [
    'a_y_decay', 'p_x_rate', 's_loss', 'h_other-proposition@1', 'h_muller-sheltering-extension@1',
    {'value': {'kind': 'card', 'pointer': '/author/layers/core/statement'}, 'src': 'rejection'},
    {'value': {'kind': 'card', 'pointer': '/added/layers/predictions/1'}, 'src': 'rejection'},
])
def test_evidence_target_names_an_atom_prediction_step_or_proposition(target):
    document = with_mechanism(card())
    line(document)['target_ref'] = target
    outcome = result(document)
    assert outcome['valid'], outcome['errors']
    listed = [entry['reference'] for entry in outcome['external']]
    assert ('h_other-proposition@1' in listed) == (target == 'h_other-proposition@1')
    assert 'h_muller-sheltering-extension@1' not in listed


@pytest.mark.parametrize('target, code', [
    ('a_missing', 'REF_UNKNOWN_ID'),
    ('e_neo_x', 'REF_WRONG_TARGET'),
    ('u_dominance', 'REF_WRONG_TARGET'),
    ({'value': {'kind': 'card', 'pointer': LINE}, 'src': 'rejection'}, 'REF_WRONG_TARGET'),
])
def test_evidence_target_rejects(target, code):
    document = card()
    line(document)['target_ref'] = target
    assert code in codes(document)


def test_identifier_of_two_target_kinds_is_ambiguous():
    document = card()
    added(document)['predictions'][0]['id'] = 'a_y_decay'
    assert 'REF_WRONG_TARGET' in codes(document)


def test_same_evidence_line_in_both_zones_is_one_record():
    document = card()
    document['author']['layers']['evidence']['lines'] = [
        {'id': {'value': 'e_early_models', 'locator': 'XML .//p[7] (1-based document order)'}}]
    assert result(document)['valid']


@pytest.mark.parametrize('mutation, code', [
    ('alternative_predicts_a_line', 'REF_WRONG_TARGET'),
    ('uncertainty_target_dangling', 'REF_UNRESOLVED'),
    ('duplicate_uncertainty', 'REF_DUPLICATE_ID'),
    ('duplicate_assumption', 'REF_DUPLICATE_ID'),
    ('attribution_unknown_line', 'REF_UNKNOWN_ID'),
    ('challenge_names_an_atom', 'REF_WRONG_TARGET'),
])
def test_core_reference_rejects(mutation, code):
    document = card()
    core = added(document)['core']
    if mutation == 'alternative_predicts_a_line':
        core['alternative_explanations']['value'][0]['distinguishing_prediction_refs'] = [
            {'kind': 'card', 'pointer': LINE}]
    elif mutation == 'uncertainty_target_dangling':
        core['uncertainties']['value'][0]['target_ref'] = {'kind': 'card', 'pointer': '/added/layers/core/atoms/9'}
    elif mutation == 'duplicate_uncertainty':
        core['uncertainties']['value'].append(copy.deepcopy(core['uncertainties']['value'][0]))
    elif mutation == 'duplicate_assumption':
        core['assumptions'] = [{'id': 'as_1', 'text': {'value': 'A premise.', 'src': 'assumptions'}},
                               {'id': 'as_1', 'text': {'value': 'Another premise.', 'src': 'assumptions'}}]
    elif mutation == 'attribution_unknown_line':
        line(document)['items'].append({'value': {
            'line_id': 'e_missing', 'agent_type_scope': 'Test.', 'agent_justification': 'Test.',
            'knowledge_level_justification': 'Test.'}, 'src': 'rejection'})
    else:
        document['added']['challenge_search'] = {
            'query_ids': ['q1'], 'inspected_artifacts': [], 'outcome': 'found',
            'evidence_refs': [{'kind': 'card', 'pointer': '/added/layers/core/atoms/0'}]}
    assert code in codes(document)


def test_core_references_resolve():
    document = card()
    core = added(document)['core']
    core['alternative_explanations']['value'][0]['distinguishing_prediction_refs'] = [
        {'kind': 'card', 'pointer': '/added/layers/predictions/0'}]
    core['uncertainties']['value'][0]['target_ref'] = {'kind': 'card', 'pointer': '/added/layers/core/atoms/1'}
    line(document)['items'].append({'value': {
        'line_id': 'e_neo_x', 'agent_type_scope': 'Test.', 'agent_justification': 'Test.',
        'knowledge_level_justification': 'Test.'}, 'src': 'rejection'})
    assert result(document)['valid'], result(document)['errors']


def test_record_level_src_must_name_a_source():
    document = card()
    line(document)['src'] = 'missing_record'
    errors = result(document)['errors']
    assert [(e['code'], e['path']) for e in errors] == [('REF_SOURCE_UNKNOWN', 'added.evidence.lines[0]')]


def test_empty_registry_without_src_is_valid():
    document = load(ROOT / 'tests/fixtures/fictional/fx_one.json')
    assert document['added']['sources'] == {}
    assert check_refs(document)['valid']


@pytest.mark.parametrize('generation', [
    {'run_id': None, 'generated': None, 'submitted': None, 'submits_all': None},
    {'run_id': 'run-1', 'generated': 5, 'submitted': 5, 'submits_all': True},
    {'run_id': 'run-1', 'generated': 5, 'submitted': 2, 'submits_all': False},
    {'run_id': 'run-1', 'generated': None, 'submitted': 2, 'submits_all': True},
])
def test_consistent_generation_is_valid(generation):
    document = card()
    document['author']['generation'] = generation
    assert result(document)['valid']


@pytest.mark.parametrize('generation', [
    {'run_id': 'run-1', 'generated': 5, 'submitted': 2, 'submits_all': True},
    {'run_id': 'run-1', 'generated': 5, 'submitted': 5, 'submits_all': False},
    {'run_id': 'run-1', 'generated': 2, 'submitted': 5, 'submits_all': None},
])
def test_inconsistent_generation_rejects(generation):
    document = card()
    document['author']['generation'] = generation
    assert codes(document) == {'REF_GENERATION_INCONSISTENT'}


def entailment(document, pointer):
    return next(r for r in document['added']['integrity']['entailment'] if r['pointer'] == pointer)


def test_entailment_before_its_assessment_is_rejected():
    document = card()
    entailment(document, '/added/layers/core/testability')['checked_at'] = '2026-10-20T17:04:00Z'
    errors = result(document)['errors']
    assert [e['code'] for e in errors] == ['REF_TIME_ORDER']


def test_entailment_after_its_assessment_and_source_is_valid():
    document = card()
    entailment(document, '/added/layers/core/testability')['checked_at'] = '2026-10-20T17:04:22Z'
    assert result(document)['valid']


def test_assessment_after_the_added_zone_is_rejected():
    document = card()
    added(document)['core']['testability']['assessment']['assessed_at'] = '2026-10-21T00:00:00Z'
    entailment(document, '/added/layers/core/testability')['checked_at'] = '2026-10-21T00:00:00Z'
    errors = result(document)['errors']
    assert [(e['code'], e['path']) for e in errors] == [('REF_TIME_ORDER', 'added.core.testability.assessment')]


def test_independent_times_are_not_ordered():
    # A refetch or an entailment check may follow the added zone; neither is ordered against it.
    document = card()
    document['added']['at'] = '2026-10-20T17:04:22Z'
    document['added']['source_verification']['fetched_at'] = '2026-10-25T00:00:00Z'
    entailment(document, '/added/layers/core/kind')['checked_at'] = '2026-10-25T00:00:00Z'
    assert result(document)['valid']


def test_timestamp_without_offset_is_not_compared():
    # The schema rejects a time without an offset; the reference checker must not crash on one.
    from tools.check_refs import moment
    assert moment('2026-10-20T12:00:01') is None
    assert moment('2026-10-20T12:00:01Z') is not None
