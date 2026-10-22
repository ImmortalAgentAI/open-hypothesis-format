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
    card['added']['layers']['evidence']['lines'][0].update(copy.deepcopy(LINE_CONDITIONS))
    return card


# Item 1: the conditions of the study behind an evidence line.
LINE_CONDITIONS = {
    'system': {'taxon': {'value': 'Mus musculus', 'src': 'prior_work'},
               'taxon_id': {'value': 'NCBITaxon:10090', 'src': 'prior_work'},
               'sex': {'value': 'female', 'src': 'prior_work'}},
    'intervention': {'agent': {'value': 'agent Q, fictional', 'src': 'prior_work'},
                     'dose': {'value': '2 mg/kg', 'src': 'prior_work'},
                     'route': {'value': 'in the feed', 'src': 'prior_work', 'term': 'diet'}},
    'sample_size': {'value': 48, 'src': 'prior_work'},
    'multi_site_program': {'value': {'program': 'fictional programme P', 'sites': 3}, 'src': 'prior_work'},
    # Item 2: a subgroup result on a secondary outcome, as PEARL's HbA1c in males on the lower dose
    'sample': {'value': {'population': 'subgroup', 'subgroup': 'females on the lower dose, fictional',
                         'outcome': 'secondary', 'analysis': 'not_stated'}, 'src': 'prior_work'},
}


def line(card):
    return card['added']['layers']['evidence']['lines'][0]


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
    # M1: conditions of an evidence line
    'v1_0_with_line_system': lambda card: (as_1_0(card), card['vocabularies'].pop('terms'),
                                           card['added']['layers']['predictions'].clear(),
                                           [line(card).pop(key) for key in ('intervention', 'sample_size',
                                                                            'multi_site_program', 'sample')],
                                           line(card)['system'].pop('taxon_id')),
    'taxon_id_not_ncbi': lambda card: line(card)['system']['taxon_id'].__setitem__('value', 'NCBITaxon:mouse'),
    'line_route_without_term': lambda card: line(card)['intervention']['route'].pop('term'),
    'line_unknown_condition': lambda card: line(card)['system'].__setitem__('cage', {'value': 'x', 'src': 'x'}),
    'sample_size_zero': lambda card: line(card)['sample_size'].__setitem__('value', 0),
    'single_site_program': lambda card: line(card)['multi_site_program']['value'].__setitem__('sites', 1),
    # M2: the sample of a result
    'subgroup_unnamed': lambda card: line(card)['sample']['value'].pop('subgroup'),
    'whole_sample_with_subgroup': lambda card: line(card)['sample']['value'].__setitem__('population', 'whole_sample'),
    'sample_not_a_term': lambda card: line(card)['sample']['value'].__setitem__('population', 'subgroup_only'),
    'sample_outcome_missing': lambda card: line(card)['sample']['value'].pop('outcome'),
    'v1_0_with_sample': lambda card: (as_1_0(card), card['vocabularies'].pop('terms'),
                                      card['added']['layers']['predictions'].clear(),
                                      [line(card).pop(key) for key in ('system', 'intervention', 'sample_size',
                                                                       'multi_site_program')]),
}
PREDICTION = '/added/layers/predictions/0'
LINE = '/added/layers/evidence/lines/0'
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
    'v1_0_with_line_system': LINE,
    'taxon_id_not_ncbi': LINE + '/system/taxon_id/value',
    'line_route_without_term': LINE + '/intervention/route',
    'line_unknown_condition': LINE + '/system',
    'sample_size_zero': LINE + '/sample_size/value',
    'single_site_program': LINE + '/multi_site_program/value/sites',
    'subgroup_unnamed': LINE + '/sample/value',
    'whole_sample_with_subgroup': LINE + '/sample/value',
    'sample_not_a_term': LINE + '/sample/value/population',
    'sample_outcome_missing': LINE + '/sample/value',
    'v1_0_with_sample': LINE,
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


def test_line_conditions_need_no_domain_profile():
    """Unlike predictions[].intervention, a line's intervention describes the study, not the claim."""
    card = load(ROOT / 'tests/fixtures/fictional/fx_eight.json')
    assert card['added']['layers']['profile']['domain'] == 'none'
    card['standard_version'] = '1.1'
    card['vocabularies']['terms'] = {'id': 'ohf:terms@1', 'sha256': terms_pin()}
    source = card['added']['layers']['evidence']['lines'][0]['src']
    card['added']['layers']['evidence']['lines'][0]['intervention'] = {
        'agent': {'value': 'agent Q, fictional', 'src': source},
        'route': {'value': 'released in the field', 'src': source, 'term': 'environmental_release'}}
    assert not validation_errors(SCHEMA, card)


# D3: numbers in the quote of an evidence line, both sides of each rule.
RESULT_QUOTE = 'Counter Y rose by 12% with agent Q at 2 mg/kg (p = 0.01), fictional.'


def quoted_card(quote=RESULT_QUOTE, estimate=True):
    card = card_1_1()
    line(card)['quote'] = {'value': quote, 'src': 'prior_work'}
    if estimate:
        line(card)['result_estimate'] = {'value': {'reported': 'rose by 12%', 'measure': 'percentage change',
                                                   'contrast': 'agent Q against vehicle', 'scale': 'not_stated'},
                                         'src': 'prior_work'}
    return card


def ref_codes(card, kind='errors'):
    return {item['code'] for item in check_refs(card)[kind]}


def gap(path, disposition):
    return {'path': path, 'disposition': disposition, 'reason': 'fictional reason', 'query_ids': [],
            'inspected_artifacts': []}


def test_quoted_result_with_estimate_passes():
    card = quoted_card()
    assert not validation_errors(SCHEMA, card)
    assert not ref_codes(card)
    assert 'REF_CONDITION_IN_QUOTE' not in ref_codes(card, 'warnings')


def test_quoted_result_without_estimate_is_an_error():
    assert 'REF_ESTIMATE_IN_QUOTE' in ref_codes(quoted_card(estimate=False))


def test_not_supplied_gap_does_not_excuse_a_quoted_result():
    card = quoted_card(estimate=False)
    card['added']['gaps'].append(gap('evidence.lines[].result_estimate', 'not_supplied'))
    assert 'REF_ESTIMATE_IN_QUOTE' in ref_codes(card)


def test_gap_with_another_reason_excuses_a_quoted_result():
    card = quoted_card(estimate=False)
    card['added']['gaps'].append(gap('evidence.lines[0].result_estimate', 'blocked'))
    assert 'REF_ESTIMATE_IN_QUOTE' not in ref_codes(card)


def test_estimate_must_quote_its_words():
    card = quoted_card()
    line(card)['result_estimate']['value']['reported'] = 'rose by 21%'
    assert 'REF_ESTIMATE_NOT_QUOTED' in ref_codes(card)


@pytest.mark.parametrize('quote', ['Counter Y rose with agent Q in system four, fictional.',
                                   'Agent Q was given at 2 mg/kg from 6 months of age, fictional.'])
def test_quote_without_a_result_number_needs_no_estimate(quote):
    assert 'REF_ESTIMATE_IN_QUOTE' not in ref_codes(quoted_card(quote, estimate=False))


def test_dose_and_age_in_quote_are_warnings_only():
    card = quoted_card('Agent Q was given at 2 mg/kg from 6 months of age, fictional.', estimate=False)
    line(card)['intervention'].pop('dose')
    warnings = [item['path'] for item in check_refs(card)['warnings'] if item['code'] == 'REF_CONDITION_IN_QUOTE']
    assert warnings == ['evidence.lines[0].intervention.dose', 'evidence.lines[0].system.age_at_start']
    assert check_refs(card)['valid']


def test_recorded_dose_silences_the_warning():
    card = quoted_card('Agent Q was given at 2 mg/kg, fictional.', estimate=False)
    assert 'REF_CONDITION_IN_QUOTE' not in ref_codes(card, 'warnings')


def test_a_1_0_card_is_not_held_to_the_quote_rules():
    card = load(ROOT / 'tests/fixtures/fictional/fx_eight.json')
    card['added']['layers']['evidence']['lines'][0]['quote'] = {'value': RESULT_QUOTE, 'src': 'prior_work'}
    assert 'REF_ESTIMATE_IN_QUOTE' not in ref_codes(card)


@pytest.mark.parametrize('value,version', [
    ('rose by 12%', '1.1'),
    ({'reported': 'rose by 12%', 'measure': 'x', 'contrast': 'x', 'scale': 'x'}, '1.0')])
def test_estimate_form_follows_the_version(value, version):
    card = quoted_card()
    line(card)['result_estimate']['value'] = value
    if version == '1.0':
        as_1_0(card)
    assert LINE + '/result_estimate/value' in {pointer(error) for error in validation_errors(SCHEMA, card)}


# Item 11a: a gap for a whole empty list.
LIST_GAP = {'path': 'core.assumptions', 'disposition': 'not_supplied',
            'reason': 'The fictional source states no assumption.', 'query_ids': [], 'inspected_artifacts': []}


def gap_codes(card):
    return {item['code'] for item in check_gaps(card, POLICY, CATALOGUE, MAPPING)['errors']}


def test_gap_for_an_empty_list_is_accepted():
    card = card_1_1()
    assert not card['added']['layers']['core'].get('assumptions')
    card['added']['gaps'].append(dict(LIST_GAP))
    assert not validation_errors(SCHEMA, card)
    assert not gap_codes(card)


def test_gap_for_a_list_with_an_element_is_populated():
    card = card_1_1()
    card['added']['layers']['core']['assumptions'] = [
        {'id': {'value': 'as1', 'src': 'statement'}, 'text': {'value': 'A fictional premise.', 'src': 'statement'}}]
    card['added']['gaps'].append(dict(LIST_GAP))
    assert 'GAP_PATH_POPULATED' in gap_codes(card)


def test_gap_for_a_list_that_is_not_one_is_unknown():
    card = card_1_1()
    card['added']['gaps'].append(dict(LIST_GAP, path='core.assumptionz'))
    assert 'GAP_PATH_UNKNOWN' in gap_codes(card)
    assert '/added/gaps/' + str(len(card['added']['gaps']) - 1) + '/path' in {
        pointer(error) for error in validation_errors(SCHEMA, card)}


def test_identity_lists_take_no_gap():
    card = card_1_1()
    card['added']['gaps'].append(dict(LIST_GAP, path='identity.supersedes'))
    assert 'GAP_PATH_UNKNOWN' in gap_codes(card)


def test_a_1_0_card_cannot_gap_a_whole_list():
    card = load(ROOT / 'tests/fixtures/fictional/fx_eight.json')
    card['added']['gaps'].append(dict(LIST_GAP))
    assert 'GAP_PATH_UNKNOWN' in gap_codes(card)
    assert validation_errors(SCHEMA, card)


# Item 3 and D2: an alternative has an identifier and can be a line's target; list elements carry their src.
def alternatives_card():
    card = card_1_1()
    core = card['added']['layers']['core']
    core['alternative_explanations']['value'][0].update({'id': 'alt_u', 'src': 'alternative'})
    core['uncertainties']['value'][0]['src'] = 'open_question'
    line(card)['target_ref'] = {'value': 'alt_u', 'src': 'prior_work'}
    return card


def entailment(pointer):
    return {'pointer': pointer, 'basis': 'src', 'verdict': 'entails',
            'checker': {'name': 'fictional-checker', 'version': '1.0.0', 'prompt_sha256': 'sha256:' + '1' * 64},
            'checked_at': '2026-01-01T00:00:00Z'}


ALTERNATIVE = '/added/layers/core/alternative_explanations/value/0'


def test_line_can_target_an_alternative():
    card = alternatives_card()
    assert not validation_errors(SCHEMA, card)
    assert check_refs(card)['valid'], check_refs(card)['errors']
    line(card)['target_ref']['value'] = {'kind': 'card', 'pointer': ALTERNATIVE}
    assert check_refs(card)['valid'], check_refs(card)['errors']


@pytest.mark.parametrize('target,code', [
    ({'kind': 'card', 'pointer': '/added/layers/core/alternative_explanations/value/9'}, 'REF_UNRESOLVED'),
    ('u1', 'REF_WRONG_TARGET'),
    ('alt_none', 'REF_UNKNOWN_ID'),
])
def test_line_target_must_name_an_existing_alternative(target, code):
    card = alternatives_card()
    line(card)['target_ref']['value'] = target
    assert code in ref_codes(card)


def test_alternative_id_shared_with_a_prediction_is_ambiguous():
    card = alternatives_card()
    card['added']['layers']['core']['alternative_explanations']['value'][0]['id'] = 'p1'
    line(card)['target_ref']['value'] = 'p1'
    assert 'REF_WRONG_TARGET' in ref_codes(card)


def test_duplicate_alternative_id_is_rejected():
    card = alternatives_card()
    alternatives = card['added']['layers']['core']['alternative_explanations']['value']
    alternatives.append(copy.deepcopy(alternatives[0]))
    assert 'REF_DUPLICATE_ID' in ref_codes(card)


def test_element_src_must_name_a_source():
    card = alternatives_card()
    card['added']['layers']['core']['uncertainties']['value'][0]['src'] = 'no_such_source'
    assert 'REF_SOURCE_UNKNOWN' in ref_codes(card)


def test_entailment_record_may_name_an_element_with_its_own_src():
    card = alternatives_card()
    card['added']['integrity'] = {'entailment': [entailment(ALTERNATIVE)]}
    assert not validation_errors(SCHEMA, card)
    assert check_refs(card)['valid'], check_refs(card)['errors']


def test_entailment_record_cannot_name_an_element_without_src():
    card = alternatives_card()
    card['added']['layers']['core']['alternative_explanations']['value'][0].pop('src')
    card['added']['integrity'] = {'entailment': [entailment(ALTERNATIVE)]}
    assert 'REF_WRONG_TARGET' in ref_codes(card)


@pytest.mark.parametrize('member', ['id', 'src'])
def test_a_1_0_card_has_no_element_id_or_src(member):
    card = load(ROOT / 'tests/fixtures/fictional/fx_four.json')
    card['added']['layers']['core']['alternative_explanations']['value'][0][member] = 'alternative'
    assert ALTERNATIVE in {pointer(error) for error in validation_errors(SCHEMA, card)}


# Item 7: no novelty. The one relaxation of 1.1: known_result needs no new_content.
SEARCH = {'kind': 'artifact', 'sha256': 'sha256:' + '2' * 64}


def known_result_card():
    card = card_1_1()
    card['added']['layers']['core']['novelty_assessment'] = {'value': {
        'status': 'known_result', 'prior_claim_refs': [{'kind': 'external', 'uri': 'https://example.org/fictional',
                                                        'limitation': 'Fictional prior report.'}],
        'shared_content': 'Agent Q raises counter Y, as reported before.',
        'search_scope_ref': SEARCH, 'as_of': '2026-01-01T00:00:00Z'}, 'src': 'prior_work'}
    return card


def novelty(card):
    return card['added']['layers']['core']['novelty_assessment']['value']


NOVELTY = '/added/layers/core/novelty_assessment/value'


def test_known_result_without_new_content_is_valid():
    assert not validation_errors(SCHEMA, known_result_card())


@pytest.mark.parametrize('mutate', [
    lambda value: value.__setitem__('prior_claim_refs', []),
    lambda value: value.pop('prior_claim_refs'),
    lambda value: value.pop('search_scope_ref'),
    lambda value: value.__setitem__('new_content', 'Something new after all.'),
], ids=['no_prior_claim', 'prior_claims_absent', 'no_search', 'with_new_content'])
def test_known_result_mutation_is_rejected(mutate):
    card = known_result_card()
    mutate(novelty(card))
    assert any(path.startswith(NOVELTY) for path in map(pointer, validation_errors(SCHEMA, card)))


@pytest.mark.parametrize('status', ['claimed', 'bounded_search', 'expert_review'])
def test_the_relaxation_does_not_spread(status):
    card = known_result_card()
    novelty(card)['status'] = status
    assert any(path.startswith(NOVELTY) for path in map(pointer, validation_errors(SCHEMA, card)))


def test_a_1_0_card_cannot_state_a_known_result():
    card = known_result_card()
    as_1_0(card)
    assert NOVELTY + '/status' in {pointer(error) for error in validation_errors(SCHEMA, card)}


# Item 5: evidence found and not used, one record each.
def excluded_card():
    card = alternatives_card()
    card['added']['layers']['evidence']['excluded'] = [{
        'id': 'x1', 'target_ref': 'p1', 'reason': 'inherited_mismatch',
        'quote': 'In fictional system six, agent Q left counter Y unchanged.',
        'artifact': {'artifact': 'fx_four.json', 'sha256': 'sha256:' + '3' * 64, 'locator': 'JSON:/excluded'},
        'record': 'doi:10.0000/fictional', 'src': 'prior_work'}]
    return card


def excluded(card):
    return card['added']['layers']['evidence']['excluded'][0]


EXCLUDED = '/added/layers/evidence/excluded/0'


def test_excluded_record_is_valid():
    card = excluded_card()
    assert not validation_errors(SCHEMA, card)
    assert check_refs(card)['valid'], check_refs(card)['errors']


@pytest.mark.parametrize('mutate,where', [
    (lambda record: record.__setitem__('reason', 'irrelevant'), EXCLUDED + '/reason'),
    (lambda record: record.pop('quote'), EXCLUDED),
    (lambda record: record.__setitem__('reason', 'other'), EXCLUDED),
    (lambda record: record.__setitem__('note', 'a note without other'), EXCLUDED),
], ids=['reason_not_a_term', 'no_quote', 'other_without_note', 'note_without_other'])
def test_excluded_schema_mutation_is_rejected(mutate, where):
    card = excluded_card()
    mutate(excluded(card))
    assert where in {pointer(error) for error in validation_errors(SCHEMA, card)}


@pytest.mark.parametrize('target,code', [('p9', 'REF_UNKNOWN_ID'), ('u1', 'REF_WRONG_TARGET')])
def test_excluded_target_must_resolve(target, code):
    card = excluded_card()
    excluded(card)['target_ref'] = target
    assert code in ref_codes(card)


def test_excluded_ids_are_unique():
    card = excluded_card()
    card['added']['layers']['evidence']['excluded'].append(copy.deepcopy(excluded(card)))
    assert 'REF_DUPLICATE_ID' in ref_codes(card)


def test_a_1_0_card_has_no_excluded_records():
    card = excluded_card()
    as_1_0(card)
    assert '/added/layers/evidence' in {pointer(error) for error in validation_errors(SCHEMA, card)}


# Item 6: rung of proximity to humans, derived from the taxon and the endpoint kind.
def proximity_card(taxon_id, term, declared):
    card = card_1_1()
    line(card)['system']['taxon_id']['value'] = taxon_id
    line(card)['endpoint_kind'] = {'value': 'fictional readout', 'src': 'prior_work', 'term': term}
    line(card)['human_proximity'] = {'value': declared, 'src': 'prior_work'}
    return card


@pytest.mark.parametrize('taxon_id,term,declared', [
    ('NCBITaxon:10090', 'lifespan', 'mammal'),
    ('NCBITaxon:10090', 'molecular', 'in_vitro'),
    ('NCBITaxon:9606', 'biomarker', 'human_marker'),
    ('NCBITaxon:9606', 'function', 'human_clinical'),
    ('NCBITaxon:9606', 'behaviour', 'human_clinical'),
    ('NCBITaxon:7955', 'lifespan', 'non_mammal_vertebrate'),
    ('NCBITaxon:6239', 'lifespan', 'invertebrate'),
])
def test_rung_that_follows_is_accepted(taxon_id, term, declared):
    card = proximity_card(taxon_id, term, declared)
    assert not validation_errors(SCHEMA, card)
    assert 'REF_PROXIMITY_MISMATCH' not in ref_codes(card)


@pytest.mark.parametrize('taxon_id,term,declared', [
    ('NCBITaxon:10090', 'lifespan', 'human_clinical'),
    ('NCBITaxon:9606', 'biomarker', 'human_clinical'),
    ('NCBITaxon:9606', 'disease', 'human_marker'),
    ('NCBITaxon:7955', 'lifespan', 'mammal'),
    ('NCBITaxon:9606', 'lifespan', 'mammal'),
], ids=['mouse_as_human', 'marker_as_clinical', 'clinical_as_marker', 'fish_as_mammal', 'human_as_mammal'])
def test_rung_that_does_not_follow_is_an_error(taxon_id, term, declared):
    assert 'REF_PROXIMITY_MISMATCH' in ref_codes(proximity_card(taxon_id, term, declared))


def test_rung_outside_the_taxon_table_is_a_warning():
    card = proximity_card('NCBITaxon:9999999', 'lifespan', 'mammal')
    assert 'REF_PROXIMITY_NOT_DERIVED' in ref_codes(card, 'warnings')
    assert 'REF_PROXIMITY_MISMATCH' not in ref_codes(card)


def test_line_endpoint_kind_needs_its_term_in_1_1():
    card = proximity_card('NCBITaxon:10090', 'lifespan', 'mammal')
    line(card)['endpoint_kind'].pop('term')
    assert LINE + '/endpoint_kind' in {pointer(error) for error in validation_errors(SCHEMA, card)}


def test_rung_not_a_term_is_rejected():
    card = proximity_card('NCBITaxon:10090', 'lifespan', 'rodent')
    assert LINE + '/human_proximity/value' in {pointer(error) for error in validation_errors(SCHEMA, card)}


def test_taxon_table_ids_are_ncbi_and_rungs_are_terms():
    rungs = {term['id'] for term in TERMS['vocabularies']['human_proximity']} | {'human'}
    for row in TERMS['taxa']:
        assert row['id'].startswith('NCBITaxon:') and row['proximity'] in rungs
