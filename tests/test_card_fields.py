"""Explanatory, prediction and domain-profile fields: their rules and reference checks fail closed."""
import copy
import hashlib
from pathlib import Path

import pytest

from tools.check_gaps import check as check_gaps
from tools.check_refs import check as check_refs
from tools.strict_json import load
from tools.validate import validation_errors

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = load(ROOT / 'schema/hypothesis-1.schema.json')
PROFILES = load(ROOT / 'vocabularies/profiles-1.json')
POLICY = load(ROOT / 'spec/gap-path-policy.json')
CATALOGUE = load(ROOT / 'spec/field-catalogue.json')
MAPPING = load(ROOT / 'spec/mapping.json')
STATEMENT = {'kind': 'card', 'pointer': '/author/layers/core/statement'}
ASSESSMENT = {'assessor': 'fixture-builder', 'assessed_at': '2026-01-01T00:00:00Z',
              'evidence_ref': {'kind': 'artifact', 'sha256': 'sha256:' + '0' * 64}}


def gap(path, disposition='not_supplied', **extra):
    return {'path': path, 'disposition': disposition, 'reason': 'Test reason.',
            'query_ids': [], 'inspected_artifacts': [], **extra}


def base():
    """The fictional card fx_five with no domain profile, one explained observation and one prediction."""
    card = copy.deepcopy(load(ROOT / 'tests/fixtures/fictional/fx_five.json'))
    core = card['author']['layers']['core']
    core['atoms'] = [{'id': {'value': 'a1', 'locator': 'JSON:/statement'},
                      'statement': {'value': 'Part M activates part N.', 'locator': 'JSON:/statement'}}]
    core['explains'] = {'value': [{'id': 'x1', 'observation': 'Counter Y oscillates.',
                                   'status': 'unexplained', 'mode': 'direct', 'atom_refs': ['a1']}],
                        'locator': 'JSON:/statement'}
    card['added']['layers']['core']['atoms'] = [{
        'id': 'a1', 'statement': {'value': 'Part M activates part N.', 'src': 'statement'},
        'claim_type': {'value': 'mechanism', 'src': 'statement'}, 'role': {'value': 'core', 'src': 'statement'},
        'modality': {'value': 'proposed', 'src': 'statement', 'basis_quote': 'counter Y oscillates because'}}]
    card['added']['layers']['predictions'] = [{
        'id': 'p1', 'epistemic_status': {'value': 'novel', 'src': 'statement'},
        'form': {'value': 'pattern', 'src': 'statement'},
        'endpoint': {'value': 'period of Y', 'src': 'statement'},
        'system': {'kind': {'value': 'in_silico', 'src': 'statement'}},
        'discrimination': {'value': 'weak', 'src': 'statement', 'assessment': ASSESSMENT}}]
    return card


def errors(card):
    return validation_errors(SCHEMA, card)


def test_profile_vocabulary_hash_is_pinned():
    pinned = SCHEMA['properties']['vocabularies']['properties'][
        'profiles']['properties']['sha256']['const']
    data = (ROOT / 'vocabularies/profiles-1.json').read_bytes()
    assert pinned == 'sha256:' + hashlib.sha256(data).hexdigest()


def test_pharmacology_profile_has_22_catalogue_paths():
    pharm = next(p for p in PROFILES['profiles'] if p['id'] == 'ohf:intervention-pharmacology@1')
    catalogue = {row['path'] for row in CATALOGUE['fields']}
    assert len(pharm['paths']) == len(set(pharm['paths'])) == 22
    assert set(pharm['paths']) <= catalogue
    assert not any(p.startswith(('profile.biomarker', 'profile.human_testability')) for p in pharm['paths'])


def test_explanatory_rows_are_linked_to_question_parts():
    rows = {row['path']: row for row in CATALOGUE['fields']}
    assert {rows[p]['question_part'] for p in ('core.explains[]', 'core.reinterprets[]', 'core.opens[]')} == {
        'gaps_closed', 'data_reinterpreted', 'directions_opened'}
    assert rows['predictions[].discrimination']['zones'] == ['added']


def test_minimal_card_is_valid():
    card = base()
    assert not errors(card)
    assert check_refs(card)['valid']
    assert check_gaps(card, POLICY, CATALOGUE, MAPPING)['valid']


def explains(card):
    return card['author']['layers']['core']['explains']['value'][0]


def prediction(card):
    return card['added']['layers']['predictions'][0]


@pytest.mark.parametrize('mutation', [
    'rival_without_ref', 'ref_without_rival', 'no_atom_or_prediction', 'unknown_status',
    'retrodicted_without_result', 'free_text_alternative', 'discrimination_without_assessment',
    'discrimination_in_author', 'none_with_harm', 'none_with_intervention', 'no_domain',
    'old_domain_name', 'pharmacology_without_facet', 'no_profile_vocabulary', 'unknown_system_kind',
])
def test_schema_rule_rejects(mutation):
    card = base()
    if mutation == 'rival_without_ref':
        explains(card)['status'] = 'explained_by_rival'
    elif mutation == 'ref_without_rival':
        explains(card)['rival_ref'] = STATEMENT
    elif mutation == 'no_atom_or_prediction':
        del explains(card)['atom_refs']
    elif mutation == 'unknown_status':
        explains(card)['status'] = 'partly_explained'
    elif mutation == 'retrodicted_without_result':
        prediction(card)['epistemic_status']['value'] = 'retrodicted'
    elif mutation == 'free_text_alternative':
        prediction(card)['also_expected_under'] = {'value': [{'kind': 'literal', 'text': 'drift'}],
                                                   'src': 'statement'}
    elif mutation == 'discrimination_without_assessment':
        del prediction(card)['discrimination']['assessment']
    elif mutation == 'discrimination_in_author':
        card['author']['layers']['predictions'] = [
            {'id': 'p1', 'discrimination': {'value': 'weak', 'locator': 'JSON:/statement'}}]
    elif mutation == 'none_with_harm':
        card['added']['layers']['profile']['harm'] = {'value': STATEMENT, 'src': 'statement'}
    elif mutation == 'none_with_intervention':
        card['author']['layers']['predictions'] = [{'id': 'p1', 'intervention': {}}]
    elif mutation == 'no_domain':
        del card['added']['layers']['profile']['domain']
    elif mutation == 'old_domain_name':
        card['added']['layers']['profile']['domain'] = 'aging-pharmacology@1'
    elif mutation == 'pharmacology_without_facet':
        card['added']['layers']['profile']['domain'] = 'ohf:intervention-pharmacology@1'
    elif mutation == 'no_profile_vocabulary':
        del card['vocabularies']['profiles']
    else:
        prediction(card)['system']['kind']['value'] = 'galaxy'
    assert errors(card)


def test_retrodicted_prediction_with_known_result_is_valid():
    card = base()
    prediction(card)['epistemic_status']['value'] = 'retrodicted'
    prediction(card)['known_result_ref'] = {'value': STATEMENT, 'src': 'statement'}
    assert not errors(card)
    result = check_refs(card)
    assert {e['code'] for e in result['errors']} == {'REF_WRONG_TARGET'}


@pytest.mark.parametrize('mutation, code', [
    ('unknown_atom', 'REF_UNKNOWN_ID'),
    ('unknown_prediction', 'REF_UNKNOWN_ID'),
    ('dangling_pointer', 'REF_UNRESOLVED'),
    ('duplicate_id', 'REF_DUPLICATE_ID'),
    ('domain_mismatch', 'REF_DOMAIN_MISMATCH'),
    ('alternative_not_alternative', 'REF_WRONG_TARGET'),
    ('duplicate_prediction', 'REF_DUPLICATE_ID'),
    ('duplicate_atom', 'REF_DUPLICATE_ID'),
])
def test_reference_check_rejects(mutation, code):
    card = base()
    item = explains(card)
    if mutation == 'unknown_atom':
        item['atom_refs'] = ['a9']
    elif mutation == 'unknown_prediction':
        item['prediction_refs'] = ['p9']
    elif mutation == 'dangling_pointer':
        item['observation_ref'] = {'kind': 'card', 'pointer': '/author/layers/evidence/lines/3'}
    elif mutation == 'duplicate_id':
        card['author']['layers']['core']['explains']['value'].append(copy.deepcopy(item))
    elif mutation == 'duplicate_prediction':
        card['added']['layers']['predictions'].append(copy.deepcopy(prediction(card)))
    elif mutation == 'duplicate_atom':
        atoms = card['author']['layers']['core']['atoms']
        atoms.append(copy.deepcopy(atoms[0]))
    elif mutation == 'domain_mismatch':
        card['author']['layers']['profile']['domain'] = 'ohf:intervention-pharmacology@1'
    else:
        prediction(card)['also_expected_under'] = {
            'value': [{'kind': 'alternative', 'ref': STATEMENT}], 'src': 'statement'}
    assert not errors(card)
    assert code in {e['code'] for e in check_refs(card)['errors']}


def test_comparability_is_reported():
    card = base()
    assert check_refs(card)['comparable'] == ['p1']
    prediction(card)['form']['value'] = 'directional_contrast'
    assert check_refs(card)['not_comparable'] == [{'id': 'p1', 'missing': ['direction']}]
    del prediction(card)['form']
    assert check_refs(card)['not_comparable'] == [{'id': 'p1', 'missing': ['form']}]


def test_gap_for_unselected_profile_field_is_rejected():
    card = base()
    card['added']['gaps'].append(gap('profile.dose_response.shape'))
    assert not errors(card)
    result = check_gaps(card, POLICY, CATALOGUE, MAPPING)
    assert {e['code'] for e in result['errors']} == {'GAP_PROFILE_FIELD'}


def test_explanatory_path_accepts_a_search_gap():
    card = base()
    card['added']['gaps'].append(gap('core.opens[]', 'searched_not_found', query_ids=['q1']))
    assert not errors(card)
    assert check_gaps(card, POLICY, CATALOGUE, MAPPING)['valid']


def test_search_gap_on_assessment_field_is_rejected():
    card = base()
    del prediction(card)['discrimination']
    card['added']['gaps'].append(gap('predictions[0].discrimination', 'searched_not_found',
                                     query_ids=['q1']))
    assert not errors(card)
    assert 'GAP_SEARCH_NOT_MEANINGFUL' in {
        e['code'] for e in check_gaps(card, POLICY, CATALOGUE, MAPPING)['errors']}


@pytest.mark.parametrize('name', ['fx_six', 'fx_seven'])
def test_example_references_resolve(name):
    result = check_refs(load(ROOT / f'tests/fixtures/fictional/{name}.json'))
    assert result['valid'], result['errors']
    assert result['comparable'] and not result['not_comparable']


@pytest.mark.parametrize('name', ['fx_six', 'fx_seven'])
def test_duplicate_prediction_in_example_is_reported_once(name):
    card = load(ROOT / f'tests/fixtures/fictional/{name}.json')
    card['added']['layers']['predictions'].append(copy.deepcopy(card['added']['layers']['predictions'][0]))
    assert not errors(card)
    result = check_refs(card)
    assert [e['code'] for e in result['errors']] == ['REF_DUPLICATE_ID']
    assert result['errors'][0]['path'] == 'added.predictions[1]'


def test_same_id_in_both_zones_is_one_record():
    card = base()
    card['author']['layers']['predictions'] = [
        {'id': 'p1', 'endpoint': {'value': 'period of Y', 'locator': 'JSON:/statement'}}]
    assert not errors(card)
    result = check_refs(card)
    assert result['valid'] and result['comparable'] == ['p1']
