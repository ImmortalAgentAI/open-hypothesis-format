"""The completeness level is computed from its conditions and compared with the declared one."""
import copy
from pathlib import Path

import pytest

from tests.test_references import with_mechanism
from tools.check_completeness import CONDITIONS
from tools.check_refs import check as check_refs
from tools.content_hash import content_hash
from tools.strict_json import load
from tools.validate import validation_errors

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = load(ROOT / 'schema/hypothesis-1.schema.json')
CARD = load(ROOT / 'examples/cards/muller-sheltering.json')
# The full conditions the example card does not meet.
# The full conditions the example card does not meet.
FULL = [text for key, text in CONDITIONS['full'] if key not in ('claim atom', 'challenge search')]


def result(document):
    assert not validation_errors(SCHEMA, document), 'test card must stay schema-valid'
    return check_refs(document)


def declare(document, level, missing):
    document['added']['completeness'].update({'level': level, 'missing_for_next': missing})
    return document


def full_card(outcome='found'):
    """The example card with a typed step, a disputing evidence line and a challenge search."""
    document = with_mechanism(copy.deepcopy(CARD))
    lines = document['added']['layers']['evidence']['lines']
    disputing = copy.deepcopy(lines[4])
    disputing.update({'id': 'e_dosage_against', 'direction': 'disputes'})
    lines.append(disputing)
    refs = [{'kind': 'card', 'pointer': f'/added/layers/evidence/lines/{len(lines) - 1}'}]
    document['added']['challenge_search'] = {'query_ids': ['q1'], 'inspected_artifacts': [], 'outcome': outcome,
                                             'evidence_refs': refs if outcome == 'found' else []}
    return declare(document, 'full', [])


def codes(outcome, kind='errors'):
    return [e['code'] for e in outcome[kind]]


def test_example_declares_its_computed_level():
    outcome = result(CARD)
    assert outcome['completeness']['computed'] == outcome['completeness']['declared'] == 'comparable'
    assert outcome['completeness']['missing_for_next'] == CARD['added']['completeness']['missing_for_next']
    assert not outcome['warnings']


def test_example_hash_is_current():
    assert CARD['content_hash'] == content_hash(CARD)


def test_full_card_is_full():
    outcome = result(full_card())
    assert outcome['valid'], outcome['errors']
    assert outcome['completeness']['computed'] == 'full' and not outcome['warnings']


def test_recorded_search_stands_for_a_disputing_line():
    document = full_card('not_found')
    document['added']['layers']['evidence']['lines'].pop()
    outcome = result(document)
    assert outcome['valid'] and outcome['completeness']['computed'] == 'full'


def test_challenge_search_is_optional_with_a_disputing_line():
    document = full_card()
    del document['added']['challenge_search']
    outcome = result(document)
    assert outcome['valid'] and outcome['completeness']['computed'] == 'full'


def test_incomplete_search_needs_review():
    document = full_card('incomplete')
    document['added']['layers']['evidence']['lines'].pop()
    outcome = result(document)
    assert outcome['valid']
    assert outcome['completeness']['computed'] == 'comparable'
    assert [e['level'] for e in outcome['completeness']['manual_review_required']] == ['full']


@pytest.mark.parametrize('mutation, reason', [
    ('no_step', 'no mechanism step'),
    ('untyped_step', 'subject_ref, relation and object_ref'),
    ('no_disputing_line', 'records no completed search'),
    ('challenge_names_no_disputing_line', 'names no disputing evidence line'),
    ('no_atoms', 'no claim atoms'),
])
def test_unmet_full_condition_rejects_full(mutation, reason):
    document = full_card()
    layers = document['added']['layers']
    if mutation == 'no_step':
        del layers['mechanism']['steps']
    elif mutation == 'untyped_step':
        del layers['mechanism']['steps'][0]['relation']
    elif mutation == 'no_disputing_line':
        layers['evidence']['lines'].pop()
        del document['added']['challenge_search']
    elif mutation == 'challenge_names_no_disputing_line':
        document['added']['challenge_search']['evidence_refs'] = [{'kind': 'card', 'pointer': '/added/layers/evidence/lines/0'}]
    else:
        layers['core']['atoms'] = []
        document['author']['layers']['core'].pop('atoms', None)
        for name in ('explains', 'reinterprets', 'opens'):
            del layers['core'][name]
        for prediction in layers['predictions']:
            del prediction['derives_from_atom_refs']
        for line in layers['evidence']['lines']:
            line['target_ref'] = 'p_x_rate'
    outcome = result(document)
    errors = [e for e in outcome['errors'] if e['code'] == 'REF_COMPLETENESS_OVERSTATED']
    assert errors and reason in errors[0]['message']


def test_understated_level_is_warned():
    outcome = result(declare(copy.deepcopy(CARD), 'accepted', ['A comparable prediction.']))
    assert outcome['valid']
    assert codes(outcome, 'warnings') == ['REF_COMPLETENESS_UNDERSTATED', 'REF_MISSING_FOR_NEXT']


@pytest.mark.parametrize('missing, warned', [
    (FULL, 0),
    ([item.upper() for item in FULL], 0),
    (FULL[:1], 1),
    (FULL + ['A falsification condition stated by the authors.'], 1),
    ([], 2),
])
def test_missing_for_next_names_each_derived_condition(missing, warned):
    outcome = result(declare(copy.deepcopy(CARD), 'comparable', missing))
    assert outcome['valid']
    assert codes(outcome, 'warnings') == ['REF_MISSING_FOR_NEXT'] * warned


@pytest.mark.parametrize('status', ['not_refetchable', 'refetched_mismatch'])
def test_unverified_source_needs_review_but_is_not_overstated(status):
    document = copy.deepcopy(CARD)
    verification = document['added']['source_verification']
    if status == 'not_refetchable':
        document['added']['source_verification'] = {'status': status, 'reason': 'The server refused the request.'}
    else:
        verification.update({'status': status, 'sha256': 'sha256:' + '0' * 64})
    outcome = result(document)
    assert outcome['valid'], outcome['errors']
    review = outcome['completeness']['manual_review_required']
    assert [e['level'] for e in review] == ['accepted'] and outcome['completeness']['computed'] is None


def test_missing_licence_basis_fails_accepted():
    document = copy.deepcopy(CARD)
    document['author']['source']['rights_basis'] = ''
    outcome = result(document)
    assert 'REF_COMPLETENESS_OVERSTATED' in codes(outcome)
    assert outcome['completeness']['missing_for_next'] == [CONDITIONS['accepted'][2][1]]


def test_card_without_comparable_prediction_cannot_be_comparable():
    document = copy.deepcopy(CARD)
    for prediction in document['added']['layers']['predictions']:
        del prediction['form']
    outcome = result(document)
    assert 'REF_COMPLETENESS_OVERSTATED' in codes(outcome)
    assert outcome['completeness']['computed'] == 'accepted'


def test_human_card_without_generation_log_reaches_accepted():
    document = load(ROOT / 'tests/fixtures/fictional/fx_nine.json')
    assert document['author']['generator'] == {'kind': 'human', 'system': None, 'system_version': None, 'model': None}
    assert set(document['author']['generation'].values()) == {None}
    assert 'integrity' not in document['added'] and document['added']['budget']['model_calls'] == 0
    outcome = result(document)
    assert outcome['valid'] and not outcome['warnings']
    assert outcome['completeness']['computed'] == 'accepted'


@pytest.mark.parametrize('member', [('author', 'generation'), ('added', 'budget'), ('added', 'by')])
def test_process_members_are_required(member):
    # The schema requires these members even for a card written by a person without a tool;
    # such a card states them with null counts and the converter model "none".
    document = load(ROOT / 'tests/fixtures/fictional/fx_nine.json')
    del document[member[0]][member[1]]
    assert validation_errors(SCHEMA, document)


def test_card_without_generation_tool_follows_the_convention():
    # spec/README.md: for a human generator, null generation members, model "none",
    # zero model calls and null token counts mean not applicable, not unknown.
    document = load(ROOT / 'tests/fixtures/fictional/fx_nine.json')
    assert document['author']['generator']['kind'] == 'human'
    assert all(value is None for value in document['author']['generation'].values())
    assert document['added']['by']['model'] == 'none'
    budget = document['added']['budget']
    assert budget['model_calls'] == 0 and budget['input_tokens'] is None and budget['output_tokens'] is None
    outcome = result(document)
    assert outcome['valid'] and outcome['completeness']['computed'] == 'accepted' and not outcome['warnings']


@pytest.mark.parametrize('path', ['evidence.lines[].risk_of_bias', 'evidence.lines[].direction'])
def test_gap_on_a_line_member_is_not_a_search_for_disputing_evidence(path):
    document = full_card()
    document['added']['layers']['evidence']['lines'].pop()
    del document['added']['challenge_search']
    document['added']['gaps'].append({'path': path, 'disposition': 'searched_not_found', 'reason': 'Test.',
                                      'query_ids': ['q1'], 'inspected_artifacts': []})
    outcome = result(document)
    both = [e for e in outcome['completeness']['unmet'] if e['condition'].startswith('Evidence on both sides')]
    assert both and 'REF_COMPLETENESS_OVERSTATED' in codes(outcome)
