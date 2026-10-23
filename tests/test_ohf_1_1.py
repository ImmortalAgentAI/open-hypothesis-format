"""OHF 1.1: each new rule accepts a card that follows it and rejects a mutation that breaks it."""
import copy
import hashlib
from pathlib import Path

import pytest

from tools.check_completeness import both_sides
from tools.check_gaps import check as check_gaps
from tools.check_refs import check as check_refs
from tools.check_relations import check as check_relations
from tools.content_hash import content_hash
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


# Item 9: links between atoms of a card; atom-level edges and two new types between cards.
RELATIONS = load(ROOT / 'schema/hypothesis-relations-1.schema.json')
PAIR_BRIEF = load(ROOT / 'schema/pair-brief-1.schema.json')
EDGES = load(ROOT / 'tests/fixtures/fictional/relations-six-seven.json')


def atom(ident, **links):
    record = {'id': ident, 'statement': {'value': f'Fictional claim {ident}.', 'src': 'statement'},
              'claim_type': {'value': 'causal_effect', 'src': 'statement'},
              'role': {'value': 'core', 'src': 'statement'},
              'modality': {'value': 'proposed', 'src': 'statement', 'basis_quote': 'It is proposed, fictional.'}}
    record.update({name: {'value': refs, 'src': 'statement'} for name, refs in links.items()})
    return record


def atoms_card(*atoms):
    card = card_1_1()
    card['added']['layers']['core']['atoms'] = list(atoms)
    return card


def test_atom_links_are_valid():
    card = atoms_card(atom('a1', requires=['a2']), atom('a2'), atom('a3', contradicts=['a1']))
    assert not validation_errors(SCHEMA, card)
    assert check_refs(card)['valid'], check_refs(card)['errors']


@pytest.mark.parametrize('atoms,code', [
    ((atom('a1', requires=['a1']),), 'REF_ATOM_LINK'),
    ((atom('a1', contradicts=['a1']),), 'REF_ATOM_LINK'),
    ((atom('a1', requires=['a2']), atom('a2', requires=['a3']), atom('a3', requires=['a1'])), 'REF_ATOM_LINK'),
    ((atom('a1', contradicts=['a9']),), 'REF_UNKNOWN_ID'),
    ((atom('a1', requires=['p1']),), 'REF_WRONG_TARGET'),
], ids=['requires_itself', 'contradicts_itself', 'requires_cycle', 'contradicts_nothing', 'requires_a_prediction'])
def test_atom_link_mutation_is_reported(atoms, code):
    assert code in ref_codes(atoms_card(*atoms))


def test_a_1_0_card_has_no_atom_links():
    card = atoms_card(atom('a1', requires=['a2']), atom('a2'))
    as_1_0(card)
    assert '/added/layers/core/atoms/0' in {pointer(error) for error in validation_errors(SCHEMA, card)}


def test_edge_between_atoms_with_a_new_type_is_valid():
    edges = copy.deepcopy(EDGES)
    edges['edges'][0]['type'] = 'mechanism_neighbour'
    edges['edges'][0]['source']['pointer'] = '/added/layers/core/atoms/4'
    edges['edges'][0]['target']['pointer'] = '/added/layers/core/atoms/4'
    assert not validation_errors(RELATIONS, edges)


@pytest.mark.parametrize('mutate', [
    lambda edge: edge.__setitem__('type', 'contradiction'),
    lambda edge: edge['source'].__setitem__('pointer', 'core/atoms/4'),
    lambda edge: edge['target'].__setitem__('pointer', '/appendix/notes'),
], ids=['contradiction_type', 'pointer_not_absolute', 'pointer_outside_layers'])
def test_edge_mutation_is_rejected(mutate):
    edges = copy.deepcopy(EDGES)
    mutate(edges['edges'][0])
    assert validation_errors(RELATIONS, edges)


def test_relation_types_agree_across_relations_pair_brief_and_catalogue():
    types = RELATIONS['properties']['edges']['items']['properties']['type']['enum']
    assert PAIR_BRIEF['properties']['relation']['enum'] == types
    row = next(row for row in CATALOGUE['fields'] if row['path'] == 'pair.relation')
    assert row['vocabulary'].split(': ', 1)[1].split(' | ') == types


def test_given_taxa_extend_the_table_and_never_override_it():
    pigeon = {'id': 'NCBITaxon:8932', 'label': 'Columba livia', 'proximity': 'non_mammal_vertebrate',
              'by': 'NCBITaxon:7742 Vertebrata'}
    yeast = {'id': 'NCBITaxon:4932', 'label': 'Saccharomyces cerevisiae', 'proximity': None, 'by': 'not an animal'}
    mouse_as_human = {'id': 'NCBITaxon:10090', 'label': 'Mus musculus', 'proximity': 'human'}
    taxa = [pigeon, yeast, mouse_as_human]
    codes = lambda card: {item['code'] for kind in ('errors', 'warnings') for item in check_refs(card, taxa)[kind]}
    assert not codes(proximity_card('NCBITaxon:8932', 'lifespan', 'non_mammal_vertebrate')) & {
        'REF_PROXIMITY_MISMATCH', 'REF_PROXIMITY_NOT_DERIVED'}
    assert 'REF_PROXIMITY_MISMATCH' in codes(proximity_card('NCBITaxon:8932', 'lifespan', 'mammal'))
    assert 'REF_PROXIMITY_NOT_DERIVED' in codes(proximity_card('NCBITaxon:4932', 'molecular', 'invertebrate'))
    assert 'REF_PROXIMITY_MISMATCH' in codes(proximity_card('NCBITaxon:10090', 'biomarker', 'human_marker'))


# Item 11b: an independence group keyed by where its data first appeared.
def keyed_card():
    card = alternatives_card()
    lines = card['added']['layers']['evidence']['lines']
    lines.append({'id': {'value': 'e2', 'src': 'prior_work'}})
    for record in lines:
        record['independence_group'] = {'value': 'g_trial', 'src': 'prior_work',
                                        'key': {'scheme': 'registry', 'id': 'NCT00000000'}}
    return card


def groups(card):
    return [record['independence_group'] for record in card['added']['layers']['evidence']['lines']]


def test_keyed_groups_are_valid():
    card = keyed_card()
    assert not validation_errors(SCHEMA, card)
    assert check_refs(card)['valid'], check_refs(card)['errors']


def test_one_key_with_two_labels_is_rejected():
    card = keyed_card()
    groups(card)[1]['value'] = 'g_other_label'
    assert 'REF_INDEPENDENCE_KEY' in ref_codes(card)


def test_one_label_with_two_keys_is_rejected():
    card = keyed_card()
    groups(card)[1]['key'] = {'scheme': 'doi', 'id': '10.0000/fictional'}
    assert 'REF_INDEPENDENCE_KEY' in ref_codes(card)


@pytest.mark.parametrize('scheme,ident', [('doi', 'not-a-doi'), ('pmid', '0123'), ('pmcid', '12345'),
                                          ('isbn', '978')])
def test_key_identifier_follows_its_scheme(scheme, ident):
    card = keyed_card()
    groups(card)[0]['key'] = {'scheme': scheme, 'id': ident}
    assert any(path.startswith(LINE + '/independence_group/key') for path in map(
        pointer, validation_errors(SCHEMA, card)))


def test_a_1_0_card_has_no_group_key():
    card = keyed_card()
    as_1_0(card)
    assert LINE + '/independence_group' in {pointer(error) for error in validation_errors(SCHEMA, card)}


# Item 11c: prompt and time of a machine author's generation.
def generated_card(kind='ai_system'):
    card = card_1_1()
    card['author']['generator'].update({'kind': kind, 'prompt': {'kind': 'artifact', 'sha256': 'sha256:' + '4' * 64},
                                        'generated_at': '2025-12-31T23:00:00Z'})
    return card


def test_machine_generation_with_prompt_and_time_is_valid():
    card = generated_card()
    assert not validation_errors(SCHEMA, card)
    assert 'REF_TIME_ORDER' not in ref_codes(card)


@pytest.mark.parametrize('kind', ['human', 'unknown'])
def test_prompt_needs_a_machine_author(kind):
    assert '/author/generator' in {pointer(error) for error in validation_errors(SCHEMA, generated_card(kind))}


def test_generation_after_submission_is_rejected():
    card = generated_card()
    card['author']['generator']['generated_at'] = '2099-01-01T00:00:00Z'
    assert 'REF_TIME_ORDER' in ref_codes(card)


def test_a_1_0_card_has_no_prompt():
    card = generated_card()
    as_1_0(card)
    assert '/author/generator' in {pointer(error) for error in validation_errors(SCHEMA, card)}


# Item 10: the aging profile, a superset of the intervention profile, with the hallmarks of aging.
def vocabulary_pin(name):
    return 'sha256:' + hashlib.sha256((ROOT / 'vocabularies' / name).read_bytes()).hexdigest()


def aging_card(hallmark='deregulated_nutrient_sensing', refs=('a1',)):
    card = atoms_card(atom('a1'))
    card['vocabularies'].update(profiles={'id': 'ohf:profiles@2', 'sha256': vocabulary_pin('profiles-2.json')},
                                hallmarks={'id': 'ohf:hallmarks@1', 'sha256': vocabulary_pin('hallmarks-1.json')})
    profile = card['added']['layers']['profile']
    profile['domain'] = 'ohf:aging@1'
    profile['aging_hallmarks'] = {'value': [{'hallmark': hallmark, 'atom_refs': list(refs)}], 'src': 'statement'}
    return card


PROFILE = '/added/layers/profile'


def test_aging_card_with_hallmarks_is_valid():
    card = aging_card()
    assert not validation_errors(SCHEMA, card)
    assert check_refs(card)['valid'], check_refs(card)['errors']
    assert check_gaps(card, POLICY, CATALOGUE, MAPPING)['valid']


def test_aging_profile_keeps_the_intervention_fields():
    card = aging_card()
    card['added']['gaps'].append({'path': 'profile.harm', 'disposition': 'not_supplied'})
    assert 'GAP_PROFILE_FIELD' not in gap_codes(card)
    card['added']['layers']['profile']['domain'] = 'none'
    del card['added']['layers']['profile']['aging_hallmarks']
    card['vocabularies'].pop('hallmarks')
    assert 'GAP_PROFILE_FIELD' in gap_codes(card)


def test_hallmarks_outside_the_aging_profile_are_rejected():
    # M10a: hallmarks with domain none
    card = aging_card()
    card['added']['layers']['profile']['domain'] = 'none'
    assert PROFILE in {pointer(error) for error in validation_errors(SCHEMA, card)}
    card['added']['gaps'].append({'path': 'profile.aging_hallmarks[]', 'disposition': 'not_supplied'})
    del card['added']['layers']['profile']['aging_hallmarks']
    assert 'GAP_PROFILE_FIELD' in gap_codes(card)


def test_hallmark_outside_the_vocabulary_is_rejected():
    # M10b: autophagy is not one of the twelve; disabled_macroautophagy is
    card = aging_card(hallmark='autophagy')
    assert PROFILE + '/aging_hallmarks/value/0/hallmark' in {pointer(e) for e in validation_errors(SCHEMA, card)}


def test_hallmark_naming_no_atom_is_reported():
    # M10c: a dangling atom reference
    assert 'REF_UNKNOWN_ID' in ref_codes(aging_card(refs=('a9',)))


@pytest.mark.parametrize('name,pin,at', [
    ('profiles', {'id': 'ohf:profiles@1', 'sha256': vocabulary_pin('profiles-1.json')}, '/vocabularies/profiles/id'),
    ('hallmarks', None, '/vocabularies')], ids=['profiles_1', 'no_hallmarks_pin'])
def test_aging_profile_needs_its_pins(name, pin, at):
    card = aging_card()
    if pin is None:
        card['vocabularies'].pop(name)
    else:
        card['vocabularies'][name] = pin
    assert at in {pointer(error) for error in validation_errors(SCHEMA, card)}


def test_hallmarks_pin_needs_the_aging_profile():
    card = card_1_1()
    card['vocabularies']['hallmarks'] = {'id': 'ohf:hallmarks@1', 'sha256': vocabulary_pin('hallmarks-1.json')}
    assert '/vocabularies' in {pointer(error) for error in validation_errors(SCHEMA, card)}


def test_profiles_2_is_a_superset_of_profiles_1():
    one, two = load(ROOT / 'vocabularies/profiles-1.json'), load(ROOT / 'vocabularies/profiles-2.json')
    pharm = {p['id']: p for p in two['profiles']}
    assert all(pharm[p['id']] == p for p in one['profiles'])
    assert set(pharm['ohf:intervention-pharmacology@1']['paths']) < set(pharm['ohf:aging@1']['paths'])
    assert {t['id'] for t in load(ROOT / 'vocabularies/hallmarks-1.json')['terms']} == set(
        SCHEMA['properties']['added']['properties']['layers']['properties']['profile']['properties']
        ['aging_hallmarks']['properties']['value']['items']['properties']['hallmark']['enum'])


def test_a_1_0_card_has_no_aging_profile():
    card = aging_card()
    as_1_0(card)
    errors = {pointer(error) for error in validation_errors(SCHEMA, card)}
    assert PROFILE in errors and '/vocabularies' in errors


# Item 4: an optional typed triple on an atom. The relation ids were checked against RO in OLS
# (RO:0002212 negatively regulates) and the Biolink Model slots (affects).
def triple(relation='RO:0002212', subject=None, **extra):
    value = {'subject': subject or {'id': 'CHEBI:9168', 'label': 'sirolimus'},
             'relation': {'id': relation, 'label': 'negatively regulates'},
             'object': {'entity_ref': 'm_target'}}
    value.update(extra)
    return {'value': value, 'src': 'statement'}


def triple_card(**kwargs):
    record = atom('a1')
    record['triple'] = triple(**kwargs)
    card = atoms_card(record)
    card['added']['layers']['mechanism']['entities'] = [
        {'id': 'm_target', 'label': {'value': 'fictional complex T', 'src': 'statement'}}]
    return card


TRIPLE = '/added/layers/core/atoms/0/triple/value'


@pytest.mark.parametrize('kwargs', [{}, {'relation': 'biolink:affects'},
                                    {'qualifiers': [{'type': 'biolink:object_direction_qualifier',
                                                     'value': 'decreased'}]}],
                         ids=['ro', 'biolink', 'qualifier'])
def test_atom_triple_is_valid(kwargs):
    card = triple_card(**kwargs)
    assert not validation_errors(SCHEMA, card)
    assert check_refs(card)['valid'], check_refs(card)['errors']


@pytest.mark.parametrize('relation', ['slows_aging_in', 'GO:0008150', 'RO:123', 'biolink:Affects'],
                         ids=['M4a_free_word', 'M4b_not_a_relation_ontology', 'ro_short', 'biolink_class'])
def test_triple_relation_outside_ro_and_biolink_is_rejected(relation):
    assert TRIPLE + '/relation/id' in {pointer(e) for e in validation_errors(SCHEMA, triple_card(relation=relation))}


def test_triple_subject_needs_a_curie_or_an_entity():
    card = triple_card(subject={'id': 'sirolimus', 'label': 'sirolimus'})
    assert TRIPLE + '/subject' in {pointer(e) for e in validation_errors(SCHEMA, card)}


@pytest.mark.parametrize('ref,code', [('m_missing', 'REF_UNKNOWN_ID'), ('a1', 'REF_WRONG_TARGET')],
                         ids=['M4c_dangling_entity', 'atom_as_entity'])
def test_triple_entity_reference_is_resolved(ref, code):
    assert code in ref_codes(triple_card(subject={'entity_ref': ref}))


def test_a_1_0_card_has_no_triple():
    card = triple_card()
    as_1_0(card)
    assert '/added/layers/core/atoms/0' in {pointer(error) for error in validation_errors(SCHEMA, card)}


# A line whose quote is withheld counts, but not as the disputing side for full.
WITHHELD = {'reason': 'nc_nd', 'locator': 'Table 2', 'record_ref': {'scheme': 'doi', 'id': '10.1000/fictional.1'},
            'paraphrase': 'Agent Q did not change counter Y in the fictional cohort.',
            'abstract_quote': 'Counter Y was unchanged by agent Q, fictional.'}


def sides_card(withheld=True):
    card = card_1_1()
    lines = card['added']['layers']['evidence']['lines']
    lines.append({'id': {'value': 'e_for', 'src': 'prior_work'}, 'direction': {'value': 'supports', 'src': 'prior_work'},
                  'quote': {'value': 'Counter Y rose under agent Q, fictional.', 'src': 'prior_work'}})
    against = {'id': {'value': 'e_against', 'src': 'prior_work'}, 'direction': {'value': 'disputes', 'src': 'prior_work'}}
    if withheld:
        against['quote_withheld'] = {'value': copy.deepcopy(WITHHELD), 'src': 'prior_work'}
    else:
        against['quote'] = {'value': 'Counter Y was unchanged by agent Q, fictional.', 'src': 'prior_work'}
    lines.append(against)
    return card


AGAINST = LINE[:-1] + '2'


def test_withheld_quote_line_is_valid_but_not_the_disputing_side():
    card = sides_card()
    assert not validation_errors(SCHEMA, card)
    assert check_refs(card)['valid'], check_refs(card)['errors']
    status, reason = both_sides(card)
    assert status == 'unmet' and 'withheld' in reason


def test_quoted_disputing_line_makes_the_disputing_side():
    assert both_sides(sides_card(withheld=False))[0] == 'met'


@pytest.mark.parametrize('change,at', [
    (lambda w: w.__setitem__('reason', 'paywall'), '/reason'),
    (lambda w: w['record_ref'].__setitem__('id', '0123') or w['record_ref'].__setitem__('scheme', 'pmid'),
     '/record_ref/id'),
    (lambda w: w.pop('abstract_quote'), ''),
    (lambda w: w.pop('locator'), ''),
], ids=['reason_not_in_list', 'pmid_with_zero', 'no_abstract_quote', 'no_locator'])
def test_withheld_quote_mutation_is_rejected(change, at):
    card = sides_card()
    change(card['added']['layers']['evidence']['lines'][2]['quote_withheld']['value'])
    assert AGAINST + '/quote_withheld/value' + at in {pointer(e) for e in validation_errors(SCHEMA, card)}


def test_line_has_a_quote_or_a_withheld_quote_not_both():
    card = sides_card()
    card['added']['layers']['evidence']['lines'][2]['quote'] = {'value': 'Counter Y, fictional.', 'src': 'prior_work'}
    assert AGAINST in {pointer(error) for error in validation_errors(SCHEMA, card)}


def test_a_1_0_card_has_no_withheld_quote():
    card = sides_card()
    as_1_0(card)
    assert AGAINST in {pointer(error) for error in validation_errors(SCHEMA, card)}


# An edge names the endpoint, population or system on which the two cards differ.
def scoped(endpoint='mean amplitude of counter Y', aspect='endpoint', pointer='/added/layers/predictions/0/endpoint'):
    """fx_six and fx_seven, the second measuring another endpoint, with an edge that says so."""
    six = load(ROOT / 'tests/fixtures/fictional/fx_six.json')
    seven = load(ROOT / 'tests/fixtures/fictional/fx_seven.json')
    seven['added']['layers']['predictions'][0]['endpoint']['value'] = endpoint
    seven['content_hash'] = content_hash(seven)
    edges = copy.deepcopy(EDGES)
    edges['edges'][0]['target']['content_hash'] = seven['content_hash']
    edges['edges'][0]['scope_differs'] = [{'aspect': aspect, 'source_pointer': pointer, 'target_pointer': pointer}]
    return edges, [six, seven]


def relation_codes(edges, cards):
    return {item['code'] for item in check_relations(edges, cards)['errors']}


def test_scope_difference_shown_by_both_cards_is_valid():
    edges, cards = scoped()
    assert not validation_errors(RELATIONS, edges)
    assert check_relations(edges, cards)['valid'], check_relations(edges, cards)['errors']


@pytest.mark.parametrize('change', [
    lambda item: item.__setitem__('aspect', 'outcome'),
    lambda item: item.pop('target_pointer'),
    lambda item: item.__setitem__('source_pointer', 'predictions/0/endpoint'),
], ids=['aspect_not_in_list', 'qualifier_without_basis', 'pointer_not_absolute'])
def test_scope_difference_form_is_checked(change):
    edges, _ = scoped()
    change(edges['edges'][0]['scope_differs'][0])
    assert validation_errors(RELATIONS, edges)


@pytest.mark.parametrize('kwargs,code', [
    ({'endpoint': 'oscillation of counter Y'}, 'REL_SCOPE_SAME'),
    ({'pointer': '/added/layers/predictions/0/comparator'}, 'REL_SCOPE_FIELD'),
    ({'aspect': 'system'}, 'REL_SCOPE_FIELD'),
    ({'pointer': '/added/layers/predictions/3/endpoint'}, 'REL_POINTER_UNRESOLVED'),
], ids=['same_values', 'not_a_scope_field', 'endpoint_as_system', 'pointer_resolves_nowhere'])
def test_scope_difference_must_be_shown_by_the_cards(kwargs, code):
    assert code in relation_codes(*scoped(**kwargs))


def bind_scope_cards(edges, cards):
    """Keep regressions schema- and reference-valid, including exact edge hashes."""
    for end, card in zip(('source', 'target'), cards):
        card['content_hash'] = content_hash(card)
        edges['edges'][0][end]['content_hash'] = card['content_hash']
        assert not validation_errors(SCHEMA, card)
        assert check_refs(card)['valid']
    assert not validation_errors(RELATIONS, edges)


@pytest.mark.parametrize('suffix', ['', '/value'])
def test_scope_endpoint_scientific_value_accepts_difference_and_rejects_same(suffix):
    path = '/added/layers/predictions/0/endpoint' + suffix
    edges, cards = scoped(pointer=path)
    bind_scope_cards(edges, cards)
    assert check_relations(edges, cards)['valid']
    edges, cards = scoped(endpoint='oscillation of counter Y', pointer=path)
    bind_scope_cards(edges, cards)
    assert relation_codes(edges, cards) == {'REL_SCOPE_SAME'}


@pytest.mark.parametrize('aspect,field', [('endpoint', 'endpoint'),
                                        ('population', 'population'), ('system', 'system/kind')])
def test_scope_source_metadata_cannot_fake_a_difference(aspect, field):
    base = '/added/layers/predictions/0/' + field
    edges, cards = scoped(endpoint='oscillation of counter Y',
                          aspect=aspect, pointer=base + '/src')
    for i, card in enumerate(cards):
        node = card['added']['layers']['predictions'][0]
        if field == 'population':
            node['population'] = {'value': 'same population', 'src': 'prediction'}
        for key in field.split('/'):
            node = node[key]
        node['src'] = 'prediction' if i == 0 else 'statement'
    bind_scope_cards(edges, cards)
    assert relation_codes(edges, cards) == {'REL_SCOPE_FIELD'}
    for side in ('source_pointer', 'target_pointer'):
        edges['edges'][0]['scope_differs'][0][side] = base
    assert relation_codes(edges, cards) == {'REL_SCOPE_SAME'}


def test_scope_author_locator_cannot_fake_a_difference():
    path = '/author/layers/predictions/0/endpoint/locator'
    edges, cards = scoped(pointer=path)
    for i, card in enumerate(cards):
        card['author']['layers']['predictions'] = [
            {'id': 'p_author', 'endpoint': {'value': 'same outcome', 'locator': f'paragraph {i + 1}'}}]
    bind_scope_cards(edges, cards)
    assert relation_codes(edges, cards) == {'REL_SCOPE_FIELD'}


def test_scope_generator_system_is_provenance_not_study_system():
    # The relations schema already restricts pointers to layers; the standalone
    # checker must also reject a real, resolvable generator metadata field.
    edges, cards = scoped(aspect='system', pointer='/author/generator/system')
    for i, (side, card) in enumerate(zip(('source', 'target'), cards)):
        card['author']['generator']['system'] = f'generator {i}'
        card['content_hash'] = content_hash(card)
        edges['edges'][0][side]['content_hash'] = card['content_hash']
        assert not validation_errors(SCHEMA, card)
        assert check_refs(card)['valid']
    assert validation_errors(RELATIONS, edges)
    assert relation_codes(edges, cards) == {'REL_SCOPE_FIELD'}


@pytest.mark.parametrize('zone', ['author', 'added'])
@pytest.mark.parametrize('aspect,field', [('population', 'population'), ('system', 'system/taxon')])
def test_scope_population_and_system_value_descendants_remain_valid(zone, aspect, field):
    path = f'/{zone}/layers/predictions/0/{field}/value'
    edges, cards = scoped(aspect=aspect, pointer=path)
    for i, card in enumerate(cards):
        fields = card[zone]['layers']['predictions']
        if not fields:
            fields.append({'id': 'p_author'})
        node = fields[0]
        for key in field.split('/')[:-1]:
            node = node.setdefault(key, {})
        node[field.split('/')[-1]] = {'value': f'scientific group {i}',
                                    'locator' if zone == 'author' else 'src':
                                    'paragraph 1' if zone == 'author' else 'statement'}
    bind_scope_cards(edges, cards)
    assert check_relations(edges, cards)['valid']


def test_scope_checker_rejects_assessment_descendants_even_without_prior_schema_check():
    # The schema already rejects this extra metadata. The standalone checker
    # must not turn it into a scientific difference if called without that gate.
    edges, cards = scoped(pointer='/added/layers/predictions/0/endpoint/assessment/assessor')
    for i, card in enumerate(cards):
        card['added']['layers']['predictions'][0]['endpoint']['assessment'] = {'assessor': f'reviewer {i}'}
        card['content_hash'] = content_hash(card)
        edges['edges'][0]['source' if i == 0 else 'target']['content_hash'] = card['content_hash']
        assert validation_errors(SCHEMA, card)
    assert relation_codes(edges, cards) == {'REL_SCOPE_FIELD'}


def test_relations_check_needs_the_named_cards():
    edges, cards = scoped()
    assert 'REL_CARD_MISSING' in relation_codes(edges, cards[:1])
    edges['edges'][0]['source']['pointer'] = '/added/layers/core/atoms/9'
    assert 'REL_POINTER_UNRESOLVED' in relation_codes(edges, cards)


# A 1.0 card is checked against the 1.0 catalogue: a gap may not name a field of OHF 1.1.
NEW_PATHS = [row['path'] for row in CATALOGUE['fields'] if row.get('since') == '1.1']
MULLER = load(ROOT / 'examples/cards/muller-sheltering.json')


def test_new_paths_are_marked_since_1_1():
    assert len(NEW_PATHS) == 36
    assert {row.get('since', '1.0') for row in CATALOGUE['fields']} == {'1.0', '1.1'}


@pytest.mark.parametrize('path', NEW_PATHS)
@pytest.mark.parametrize('form', ['logical', 'indexed'])
def test_a_1_0_card_cannot_gap_a_1_1_field(path, form):
    card = copy.deepcopy(MULLER)
    assert card['standard_version'] == '1.0'
    gap_path = path.removesuffix('[]') if form == 'logical' else path.replace('[]', '[0]')
    card['added']['gaps'].append({'path': gap_path, 'disposition': 'not_supplied', 'reason': 'Test reason.',
                                  'query_ids': [], 'inspected_artifacts': []})
    assert '/added/gaps/' + str(len(card['added']['gaps']) - 1) + '/path' in {
        pointer(error) for error in validation_errors(SCHEMA, card)}
    assert 'GAP_PATH_UNKNOWN' in {error['code'] for error in check_gaps(card, POLICY, CATALOGUE, MAPPING)['errors']}


def test_the_1_0_gap_rule_of_the_schema_is_the_catalogue():
    import re
    rule = next(branch for branch in SCHEMA['allOf'] if branch.get('if', {}).get('properties', {})
                .get('standard_version', {}).get('const') == '1.0')
    patterns = [r['properties']['added']['properties']['gaps']['items']['properties']['path']['not']['pattern']
                for r in rule['then']['allOf'] if 'gaps' in str(r)]
    expected = '^(?:' + '|'.join(sorted(re.escape(p.removesuffix('[]')).replace(r'\[\]', r'\[[0-9]*\]')
                                         for p in NEW_PATHS)) + r')(?:$|[.\[])'
    assert expected in patterns


# Review of PR 4, should-fix 5-7.
@pytest.mark.parametrize('term', ['behaviour', 'other'])
def test_human_rung_without_a_marker_or_clinical_kind_is_not_derived(term):
    card = proximity_card('NCBITaxon:9606', term, 'human_clinical')
    if term == 'other':
        line(card)['endpoint_kind']['note'] = 'A fictional kind.'
    assert 'REF_PROXIMITY_NOT_DERIVED' in ref_codes(card, 'warnings')
    assert check_refs(card)['valid']


def test_a_given_taxon_row_cannot_make_a_card_invalid():
    pigeon = {'id': 'NCBITaxon:8932', 'label': 'Columba livia', 'proximity': 'non_mammal_vertebrate'}
    result = check_refs(proximity_card('NCBITaxon:8932', 'lifespan', 'mammal'), [pigeon])
    assert result['valid']
    assert 'REF_PROXIMITY_MISMATCH' in {item['code'] for item in result['warnings']}


def test_excluded_record_needs_an_artifact_or_a_record():
    card = excluded_card()
    excluded(card).pop('artifact')
    assert not validation_errors(SCHEMA, card)
    excluded(card).pop('record')
    assert EXCLUDED in {pointer(error) for error in validation_errors(SCHEMA, card)}


def test_a_group_with_a_key_has_it_on_every_line():
    card = keyed_card()
    groups(card)[1].pop('key')
    assert 'REF_INDEPENDENCE_KEY' in ref_codes(card)


def test_a_doi_key_is_compared_without_case():
    card = keyed_card()
    groups(card)[0]['key'] = {'scheme': 'doi', 'id': '10.1000/ABC'}
    groups(card)[1]['key'] = {'scheme': 'doi', 'id': '10.1000/abc'}
    assert check_refs(card)['valid'], check_refs(card)['errors']
    groups(card)[1]['value'] = 'g_other_label'
    assert 'REF_INDEPENDENCE_KEY' in ref_codes(card)


@pytest.mark.parametrize('types,valid', [(['none'], True), (['placebo', 'baseline'], True),
                                         (['none', 'placebo'], False), (['not_stated', 'vehicle'], False)])
def test_none_and_not_stated_stand_alone_among_control_types(types, valid):
    card = card_1_1()
    prediction(card)['control_type'] = {'value': types, 'src': 'prior_work'}
    errors = {pointer(error) for error in validation_errors(SCHEMA, card)}
    assert (not any('/control_type' in p for p in errors)) == valid
