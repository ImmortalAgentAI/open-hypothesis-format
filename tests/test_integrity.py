"""Integrity, first-proposal, atom and evidence-quality fields: their rules fail closed."""
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
POLICY = load(ROOT / 'spec/gap-path-policy.json')
CATALOGUE = load(ROOT / 'spec/field-catalogue.json')
MAPPING = load(ROOT / 'spec/mapping.json')
EIGHT = load(ROOT / 'tests/fixtures/fictional/fx_eight.json')
CARDS = sorted((ROOT / 'examples/cards').glob('*.json'))


def card():
    return copy.deepcopy(EIGHT)


def errors(document):
    return validation_errors(SCHEMA, document)


def atom(document):
    return document['added']['layers']['core']['atoms'][0]


def line(document, index=0):
    return document['added']['layers']['evidence']['lines'][index]


def entailment(document):
    return document['added']['integrity']['entailment']


def test_added_only_rows():
    rows = {row['path']: row for row in CATALOGUE['fields']}
    added = ('core.atoms[].claim_type', 'core.atoms[].role', 'core.atoms[].modality',
             'evidence.lines[].indirectness', 'evidence.lines[].risk_of_bias',
             'evidence.lines[].independence_group', 'evidence.lines[].argument_kind',
             'evidence.selection_record')
    assert all(rows[path]['zones'] == ['added'] for path in added)
    assert 'zones' not in rows['core.first_proposed']


def test_failure_example_is_valid():
    assert not errors(EIGHT)
    assert check_refs(EIGHT)['valid']
    assert check_gaps(EIGHT, POLICY, CATALOGUE, MAPPING)['valid']


@pytest.mark.parametrize('mutation', [
    'no_produced_by', 'no_source_verification', 'unknown_producer', 'mismatch_without_hash',
    'not_refetchable_with_hash', 'atom_without_claim_type', 'atom_without_role', 'atom_without_modality',
    'modality_without_quote', 'other_without_note', 'note_without_other', 'unknown_claim_type',
    'indirectness_without_assessment', 'indirectness_incomplete', 'bias_without_assessment',
    'unknown_argument_kind', 'negative_count', 'entailment_unknown_verdict', 'entailment_outside_added',
    'checker_without_prompt', 'date_precision_mismatch', 'search_without_scope', 'claimed_novelty_in_added',
    'first_proposed_free_date',
])
def test_schema_rule_rejects(mutation):
    document = card()
    added = document['added']
    if mutation == 'no_produced_by':
        del added['produced_by']
    elif mutation == 'no_source_verification':
        del added['source_verification']
    elif mutation == 'unknown_producer':
        added['produced_by']['kind'] = 'unknown_producer'
    elif mutation == 'mismatch_without_hash':
        del added['source_verification']['sha256']
    elif mutation == 'not_refetchable_with_hash':
        added['source_verification']['status'] = 'not_refetchable'
        added['source_verification']['reason'] = 'Offline.'
    elif mutation.startswith('atom_without_'):
        del atom(document)[mutation.removeprefix('atom_without_')]
    elif mutation == 'modality_without_quote':
        del atom(document)['modality']['basis_quote']
    elif mutation == 'other_without_note':
        atom(document)['claim_type']['value'] = 'other'
    elif mutation == 'note_without_other':
        atom(document)['claim_type']['note'] = 'A mechanism.'
    elif mutation == 'unknown_claim_type':
        atom(document)['claim_type']['value'] = 'law_of_nature'
    elif mutation == 'indirectness_without_assessment':
        del line(document)['indirectness']['assessment']
    elif mutation == 'indirectness_incomplete':
        del line(document)['indirectness']['value']['comparison']
    elif mutation == 'bias_without_assessment':
        del line(document)['risk_of_bias']['assessment']
    elif mutation == 'unknown_argument_kind':
        line(document)['argument_kind']['value'] = 'anecdote'
    elif mutation == 'negative_count':
        added['layers']['evidence']['selection_record']['value']['screened'] = -1
    elif mutation == 'entailment_unknown_verdict':
        entailment(document)[0]['verdict'] = 'maybe'
    elif mutation == 'entailment_outside_added':
        entailment(document)[0]['pointer'] = '/author/layers/core/statement'
    elif mutation == 'checker_without_prompt':
        del entailment(document)[0]['checker']['prompt_sha256']
    elif mutation == 'date_precision_mismatch':
        added['layers']['core']['first_proposed']['value']['precision'] = 'day'
    elif mutation == 'search_without_scope':
        added['layers']['core']['first_proposed']['value']['basis'] = 'bounded_search'
    elif mutation == 'claimed_novelty_in_added':
        added['layers']['core']['novelty_assessment'] = {
            'value': {'status': 'claimed', 'new_content': 'A threshold store.'}, 'src': 'statement'}
    elif mutation == 'first_proposed_free_date':
        added['layers']['core']['first_proposed']['value']['date'] = 'early 2026'
    assert errors(document)


def test_claim_type_other_with_note_is_valid():
    document = card()
    atom(document)['claim_type'] = {'value': 'other', 'src': 'statement', 'note': 'A claim about stored charge.'}
    assert not errors(document)


@pytest.mark.parametrize('mutation, code', [
    ('match_with_other_hash', 'REF_SOURCE_MISMATCH'),
    ('mismatch_with_stored_hash', 'REF_SOURCE_MISMATCH'),
    ('checker_is_converter', 'REF_CHECKER_NOT_INDEPENDENT'),
    ('checker_uses_converter_rules', 'REF_CHECKER_NOT_INDEPENDENT'),
    ('dangling_entailment', 'REF_UNRESOLVED'),
    ('entailment_on_unsourced', 'REF_WRONG_TARGET'),
    ('basis_quote_missing', 'REF_WRONG_TARGET'),
    ('duplicate_entailment', 'REF_DUPLICATE_ID'),
    ('author_atom_unclassified', 'REF_ATOM_UNCLASSIFIED'),
    ('first_proposed_dangling', 'REF_UNRESOLVED'),
])
def test_reference_check_rejects(mutation, code):
    document = card()
    added = document['added']
    stored = document['author']['source']['source_text_sha256']
    if mutation == 'match_with_other_hash':
        added['source_verification']['status'] = 'refetched_match'
    elif mutation == 'mismatch_with_stored_hash':
        added['source_verification']['sha256'] = stored
    elif mutation == 'checker_is_converter':
        entailment(document)[0]['checker']['name'] = added['by']['converter']
    elif mutation == 'checker_uses_converter_rules':
        entailment(document)[0]['checker']['prompt_sha256'] = added['by']['converter_hash']
    elif mutation == 'dangling_entailment':
        entailment(document)[0]['pointer'] = '/added/layers/core/atoms/7/statement'
    elif mutation == 'entailment_on_unsourced':
        entailment(document)[0]['pointer'] = '/added/layers/core/atoms/0'
    elif mutation == 'basis_quote_missing':
        entailment(document)[0]['basis'] = 'basis_quote'
    elif mutation == 'duplicate_entailment':
        entailment(document).append(copy.deepcopy(entailment(document)[0]))
    elif mutation == 'author_atom_unclassified':
        document['author']['layers']['core']['atoms'] = [
            {'id': {'value': 'a_other', 'locator': 'JSON:/statement'},
             'statement': {'value': 'part P stores charge', 'locator': 'JSON:/statement'}}]
    elif mutation == 'first_proposed_dangling':
        added['layers']['core']['first_proposed']['value']['source_ref'] = {
            'kind': 'card', 'pointer': '/author/layers/core/assumptions'}
    assert not errors(document)
    assert code in {e['code'] for e in check_refs(document)['errors']}


def test_author_atom_classified_in_added_zone_is_valid():
    document = card()
    document['author']['layers']['core']['atoms'] = [
        {'id': {'value': 'a_store', 'locator': 'JSON:/statement'},
         'statement': {'value': 'part P stores charge and releases it at a threshold', 'locator': 'JSON:/statement'}}]
    assert not errors(document)
    assert check_refs(document)['valid']


def test_mechanism_card_with_only_descriptive_atoms_is_warned():
    document = card()
    atom(document)['claim_type']['value'] = 'association'
    result = check_refs(document)
    assert result['valid']
    # The fixture's declared completeness is reported separately; see test_completeness.py.
    completeness = {'REF_COMPLETENESS_UNDERSTATED', 'REF_MISSING_FOR_NEXT'}
    assert [w['code'] for w in result['warnings'] if w['code'] not in completeness] == ['REF_KIND_ATOMS']


def test_selection_record_accepts_a_gap():
    document = card()
    del document['added']['layers']['evidence']['selection_record']
    document['added']['gaps'].append({'path': 'evidence.selection_record', 'disposition': 'not_supplied',
                                      'reason': 'Test reason.', 'query_ids': [], 'inspected_artifacts': []})
    assert not errors(document)
    assert check_gaps(document, POLICY, CATALOGUE, MAPPING)['valid']


@pytest.mark.parametrize('path', CARDS, ids=lambda p: p.name)
def test_converted_cards_pass_integrity_checks(path):
    document = load(path)
    result = check_refs(document)
    assert result['valid'], result['errors']
    assert not result['warnings']
    verification = document['added']['source_verification']
    assert verification['status'] == 'refetched_match'
    assert verification['sha256'] == document['author']['source']['source_text_sha256']


@pytest.mark.parametrize('path', CARDS, ids=lambda p: p.name)
def test_entailment_checker_is_pinned_and_independent(path):
    document = load(path)
    prompt = 'sha256:' + hashlib.sha256((ROOT / 'examples/cards/ENTAILMENT-PROMPT.md').read_bytes()).hexdigest()
    records = entailment(document)
    assert {r['checker']['prompt_sha256'] for r in records} == {prompt}
    assert {r['checker']['name'] for r in records} == {'ohf-entailment-check'}
    assert all(('note' in r) == (r['verdict'] != 'entails') for r in records)
