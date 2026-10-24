"""OHF 1.2: each new rule accepts a card that follows it and rejects a mutation that breaks it.

Item 2 of the plan: how a value is checked. Each catalogue row says whether its added value is
checked against a passage, against an external record (resolution) or against the card itself,
and an OHF 1.2 card's entailment records follow it. The released 1.1 example cards are the base:
`as_1_2` gives the same card as an OHF 1.2 card, with no record that 1.2 does not allow.
"""
import copy
import hashlib
from pathlib import Path

import pytest

from tools import check_ledger
from tools.check_ledger import check_class, logical_path, target_statement
from tools.check_gaps import check as check_gaps
from tools.check_mapping import check_classes
from tools.check_refs import check as check_refs
from tools.content_hash import content_hash
from tools.strict_json import load
from tools.validate import validation_errors

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = load(ROOT / 'schema/hypothesis-1.schema.json')
CATALOGUE = load(ROOT / 'spec/field-catalogue.json')
RAPA = load(ROOT / 'examples/cards/intermittent-rapamycin-mtorc2.json')
PETO = load(ROOT / 'examples/cards/peto-paradox-mammals.json')
LEGACY = sorted((ROOT / 'examples/cards').glob('*.json')) + sorted((ROOT / 'tests/fixtures').rglob('*.json'))

WITHHELD = 52  # rapa: the first line whose quote is withheld
REASON = f'/added/layers/evidence/lines/{WITHHELD}/quote_withheld/value/reason'
PARAPHRASE = f'/added/layers/evidence/lines/{WITHHELD}/quote_withheld/value/paraphrase'
TARGET = f'/added/layers/evidence/lines/{WITHHELD}/target_ref'
MODEL = {'name': 'fictional-checker', 'version': '1.0.0', 'prompt_sha256': 'sha256:' + '1' * 64}
TOOL = {'kind': 'tool', 'name': 'fictional-resolver', 'version': '1.0.0', 'tool_sha256': 'sha256:' + '2' * 64}
RESPONSE = 'sha256:' + '3' * 64
PREDICATES = load(ROOT / 'vocabularies/predicates-1.json')
LATER = '2026-10-24T00:00:00Z'


def as_1_2(card):
    """The card as an OHF 1.2 card: its domain is a list, a target_ref is a bare reference, and only
    values checked against a passage keep their records."""
    card = copy.deepcopy(card)
    card['standard_version'] = '1.2'
    card['vocabularies']['predicates'] = {'id': 'ohf:predicates@1', 'sha256': predicates_pin()}
    for zone in ('author', 'added'):
        profile = card[zone]['layers'].get('profile', {})
        if isinstance(profile.get('domain'), str):
            profile['domain'] = [profile['domain']]
    for line in card['added']['layers']['evidence']['lines']:
        if isinstance(line.get('target_ref'), dict) and 'src' in line['target_ref']:
            line['target_ref'] = line['target_ref']['value']
    records = card['added'].get('integrity', {}).get('entailment', [])
    records[:] = [r for r in records if check_class(card, r['pointer']) == 'passage']
    return card


def predicates_pin(data=None):
    data = data if data is not None else (ROOT / 'vocabularies/predicates-1.json').read_bytes()
    return 'sha256:' + hashlib.sha256(data).hexdigest()


def rapa():
    return as_1_2(RAPA)


def record(pointer, basis='src', checker=MODEL, **more):
    return {'pointer': pointer, 'basis': basis, 'verdict': 'entails', 'checker': dict(checker),
            'checked_at': LATER, **more}


def withheld_source(card):
    """The PubMed record of the withheld line, with the sha256 of its response."""
    name = card['added']['layers']['evidence']['lines'][WITHHELD]['quote_withheld']['src']
    card['added']['sources'][name]['sha256'] = RESPONSE
    return name


def resolution(card, pointer=REASON, key=None):
    name = withheld_source(card)
    pmid = card['added']['layers']['evidence']['lines'][WITHHELD]['quote_withheld']['value']['record_ref']['id']
    return record(pointer, 'resolution', TOOL, resolved_against={'source': name, 'response_sha256': RESPONSE,
                                                                  'key': key or pmid})


def add(card, *records):
    card['added']['integrity']['entailment'].extend(records)
    return card


def codes(card, kind='errors'):
    return {issue['code'] for issue in check_refs(card)[kind]}


def schema_rejects(card):
    return bool(validation_errors(SCHEMA, card))


# ------------------------------------------------------------------ positive controls

@pytest.mark.parametrize('card', [RAPA, PETO], ids=['rapa', 'peto'])
def test_1_1_examples_as_1_2_cards_are_valid(card):
    card = as_1_2(card)
    assert not validation_errors(SCHEMA, card)
    assert check_refs(card)['valid'], check_refs(card)['errors']


def test_resolution_record_on_a_member_is_valid():  # P2a
    card = add(rapa(), resolution(rapa()))
    withheld_source(card)
    assert not validation_errors(SCHEMA, card)
    assert check_refs(card)['valid'], check_refs(card)['errors']


def test_passage_record_on_a_member_is_valid():  # P2b
    card = add(rapa(), record(PARAPHRASE))
    assert not validation_errors(SCHEMA, card)
    assert check_refs(card)['valid'], check_refs(card)['errors']


def test_value_checked_by_resolution_without_its_record_is_a_warning():  # P2d
    card = rapa()
    assert REASON in {w['path'] for w in check_refs(card)['warnings'] if w['code'] == 'REF_NOT_RESOLVED'}
    add(card, resolution(card))
    withheld_source(card)
    assert REASON not in {w['path'] for w in check_refs(card)['warnings']}


@pytest.mark.parametrize('path', LEGACY, ids=lambda p: p.name)
def test_released_cards_and_fixtures_are_unchanged_controls(path):  # P2e
    card = load(path)
    if 'content_hash' not in card:
        pytest.skip('a fragment, not a whole card')
    assert card['standard_version'] in ('1.0', '1.1')
    assert not validation_errors(SCHEMA, card)
    assert check_refs(card)['valid'], check_refs(card)['errors']


# ------------------------------------------------------------------ mutations

def test_passage_record_on_a_bare_target_ref_is_the_wrong_basis():  # M2a, before any test of its src
    card = add(rapa(), record(TARGET))
    assert not validation_errors(SCHEMA, card)
    assert codes(card) == {'REF_BASIS_KIND'}


def test_target_ref_with_a_src_is_rejected_in_1_2():  # M2b
    card = rapa()
    line = card['added']['layers']['evidence']['lines'][WITHHELD]
    line['target_ref'] = {'value': line['target_ref'], 'src': line['quote_withheld']['src']}
    assert schema_rejects(card)


def test_resolution_has_no_partial():  # M2c
    card = add(rapa(), dict(resolution(rapa()), verdict='partial'))
    withheld_source(card)
    assert schema_rejects(card)


@pytest.mark.parametrize('basis,checker', [('resolution', MODEL), ('src', TOOL),
                                           ('resolution', {**TOOL, 'kind': 'model'}),
                                           ('resolution', {k: v for k, v in TOOL.items() if k != 'tool_sha256'})])
def test_checker_kind_follows_the_basis(basis, checker):  # M2d
    made = resolution(rapa()) if basis == 'resolution' else record(PARAPHRASE)
    card = add(rapa(), dict(made, checker=dict(checker)))
    withheld_source(card)
    assert schema_rejects(card)


def test_every_catalogue_row_has_a_check():  # M2e
    assert check_classes(CATALOGUE['fields'], SCHEMA) == []
    rows = copy.deepcopy(CATALOGUE['fields'])
    del rows[0]['check']
    assert check_classes(rows, SCHEMA)
    withheld = next(r for r in rows if r['path'] == 'evidence.lines[].quote_withheld')
    del withheld['check']['reason']
    assert len(check_classes(rows, SCHEMA)) == 2


def test_passage_record_on_a_member_checked_by_resolution_is_the_wrong_basis():  # M2f
    card = add(rapa(), record(REASON))
    assert not validation_errors(SCHEMA, card)
    assert codes(card) == {'REF_BASIS_KIND'}


def test_a_value_checked_member_by_member_takes_no_whole_record():
    card = add(rapa(), record(f'/added/layers/evidence/lines/{WITHHELD}/quote_withheld'))
    assert codes(card) == {'REF_BASIS_KIND'}


def test_resolution_record_on_a_value_checked_against_its_passage_is_the_wrong_basis():
    card = add(rapa(), resolution(rapa(), pointer=PARAPHRASE))
    withheld_source(card)
    assert codes(card) == {'REF_BASIS_KIND'}


def test_resolution_needs_what_it_was_resolved_against():  # M2g
    card = add(rapa(), {k: v for k, v in resolution(rapa()).items() if k != 'resolved_against'})
    assert schema_rejects(card)
    card = add(rapa(), resolution(rapa()))
    card['added']['integrity']['entailment'][-1]['resolved_against']['source'] = 'no_such_source'
    assert codes(card) == {'REF_SOURCE_UNKNOWN'}


@pytest.mark.parametrize('mutate', [
    lambda card, r: r['resolved_against'].update(response_sha256='sha256:' + '4' * 64),
    lambda card, r: r['resolved_against'].update(key='99999999'),
    lambda card, r: card['added']['sources'][r['resolved_against']['source']].pop('sha256'),
], ids=['other_response', 'other_key', 'source_without_sha256'])
def test_resolution_is_bound_to_the_response_and_the_key(mutate):  # Codex condition 2
    card = rapa()
    made = resolution(card)
    add(card, made)
    mutate(card, made)
    assert codes(card) == {'REF_RESOLUTION_BINDING'}


def test_a_source_record_without_sha256_cannot_be_resolved_against():
    card = add(rapa(), resolution(rapa()))
    assert codes(card) == {'REF_RESOLUTION_BINDING'}


def test_the_resolver_is_not_the_converter():  # M2i
    card = rapa()
    made = resolution(card)
    made['checker']['tool_sha256'] = card['added']['by']['converter_hash']
    add(card, made)
    assert 'REF_CHECKER_NOT_INDEPENDENT' in codes(card)


@pytest.mark.parametrize('mutate', [
    lambda card: card['added']['integrity']['entailment'].append(resolution(card)),
    lambda card: card['added']['integrity']['entailment'].append(dict(record(PARAPHRASE), checker=dict(MODEL, kind='model'))),
    lambda card: withheld_source(card),
], ids=['resolution_record', 'checker_kind', 'source_sha256'])
def test_a_1_1_card_has_none_of_the_1_2_members(mutate):
    card = copy.deepcopy(RAPA)
    mutate(card)
    assert schema_rejects(card)


# ------------------------------------------------------------------ the class of a pointer

@pytest.mark.parametrize('pointer,path,check', [
    (REASON, 'evidence.lines[].quote_withheld.reason', 'resolution'),
    (PARAPHRASE, 'evidence.lines[].quote_withheld.paraphrase', 'passage'),
    (f'/added/layers/evidence/lines/{WITHHELD}/quote_withheld/value/locator', 'evidence.lines[].quote_withheld.locator',
     'card'),
    (f'/added/layers/evidence/lines/{WITHHELD}/quote_withheld', 'evidence.lines[].quote_withheld', None),
    (TARGET, 'evidence.lines[].target_ref', 'card'),
    ('/added/layers/evidence/lines/0/direction', 'evidence.lines[].direction', 'passage'),
    ('/added/layers/evidence/lines/0/system/taxon_id', 'evidence.lines[].system.taxon_id', 'resolution'),
    ('/added/layers/evidence/lines/0/independence_group', 'evidence.lines[].independence_group', 'card'),
    ('/added/layers/core/alternative_explanations', 'core.alternative_explanations', 'passage'),
])
def test_pointer_maps_to_its_catalogue_row(pointer, path, check):
    card = rapa()
    assert logical_path(card, pointer) == path
    assert check_class(card, pointer) == check


# ------------------------------------------------------------------ what a line bears on

def targets_card():
    """rapa with a mechanism step, so that a line can target each of the five kinds."""
    card = rapa()
    mechanism = card['added']['layers'].setdefault('mechanism', {})
    mechanism.setdefault('entities', []).extend([{'id': 'ent_x', 'label': 'entity X, fictional', 'src': 'frb'},
                                                  {'id': 'ent_y', 'label': 'entity Y, fictional', 'src': 'frb'}])
    mechanism.setdefault('steps', []).append({'id': 'step_x', 'subject_ref': 'ent_x', 'relation': 'inhibits',
                                              'object_ref': 'ent_y', 'src': 'frb'})
    return card


def alternative_id(card):
    return next(a['id'] for a in card['added']['layers']['core']['alternative_explanations']['value'] if 'id' in a)


@pytest.mark.parametrize('kind', ['atom', 'prediction', 'step', 'alternative', 'proposition', 'wrapped_1_1'])
def test_target_statement_for_each_kind_of_target(kind):  # P2c
    card = targets_card()
    layers = card['added']['layers']
    line = layers['evidence']['lines'][0]
    atom, prediction = layers['core']['atoms'][0], layers['predictions'][0]
    statement = card['author']['layers']['core']['statement']['value']
    expected = {
        'atom': lambda: (atom['id'], atom['statement']['value']),
        'prediction': lambda: (prediction['id'], {k: prediction[k]['value'] for k in ('population', 'endpoint',
                                                                                         'direction') if k in prediction}),
        'step': lambda: ('step_x', {'subject': 'entity X, fictional', 'relation': 'inhibits',
                                    'object': 'entity Y, fictional'}),
        'alternative': lambda: (alternative_id(card), None),
        'proposition': lambda: ({'kind': 'card', 'pointer': '/author/layers/core/statement'}, statement),
        'wrapped_1_1': lambda: ({'value': atom['id'], 'src': 'frb'}, atom['statement']['value']),
    }[kind]()
    line['target_ref'] = expected[0]
    statement = target_statement(card, line)
    if kind == 'alternative':
        alternative = next(a for a in layers['core']['alternative_explanations']['value'] if a.get('id') == expected[0])
        assert statement == alternative['claim_or_ref'].get('text', alternative['claim_or_ref'].get('ref'))
    else:
        assert statement == expected[1]


def test_target_statement_of_an_alternative_named_by_pointer():
    card = targets_card()
    alternatives = card['added']['layers']['core']['alternative_explanations']['value']
    line = card['added']['layers']['evidence']['lines'][0]
    for pointer in ('/added/layers/core/alternative_explanations/value/0', '/added/layers/core/alternative_explanations/0'):
        line['target_ref'] = {'kind': 'card', 'pointer': pointer}
        claim = alternatives[0]['claim_or_ref']
        assert target_statement(card, line) == claim.get('text', claim.get('ref'))


def ledger_errors(card):
    """check_ledger errors for the card against a ledger with one check per record, as a merge writes it."""
    ledger = check_ledger.new_ledger(card)
    records = {check_ledger.key_of(r): r for r in card['added']['integrity']['entailment']}
    for item in check_ledger.value_items(card):
        key = check_ledger.key_of(item)
        if key in records:
            item = dict(item, source_passage=item.get('source_passage', 'passage not in the repository'))
            check_ledger.add_entry(ledger, key, check_ledger.entry(item, records[key]), records[key].get('note'))
    return ledger


def test_a_retargeted_line_loses_its_direction_check():  # M2h
    card = rapa()
    card['content_hash'] = content_hash(card)
    ledger = ledger_errors(card)
    before = set(check_ledger.check(card, ledger))
    lines = card['added']['layers']['evidence']['lines']
    index = next(i for i, l in enumerate(lines) if isinstance(l.get('target_ref'), str)
                 and f'/added/layers/evidence/lines/{i}/direction|src' in ledger['entries'])
    atoms = [a['id'] for a in card['added']['layers']['core']['atoms']]
    lines[index]['target_ref'] = next(a for a in atoms if a != lines[index]['target_ref'])
    card['content_hash'] = ledger['content_hash'] = content_hash(card)
    after = set(check_ledger.check(card, ledger)) - before
    assert [e for e in after if e.startswith(f'/added/layers/evidence/lines/{index}/direction|src: the value differs')]


def test_resolution_records_are_not_ledger_items():
    card = add(rapa(), resolution(rapa()))
    assert REASON not in {item['pointer'] for item in check_ledger.value_items(card)}
    assert PARAPHRASE in {item['pointer'] for item in check_ledger.value_items(card)}


def test_target_statement_of_the_cards_own_version():  # Codex R1
    card = rapa()
    line = card['added']['layers']['evidence']['lines'][0]
    statement = card['author']['layers']['core']['statement']['value']
    own = {f"{card['id']}@{card['version']}", f"{card['identity']['proposition_id']}@{card['identity']['version']}"}
    for ref in own:
        line['target_ref'] = ref
        assert target_statement(card, line) == statement
    line['target_ref'] = 'h_fictional-other-card@1'
    assert target_statement(card, line) == 'h_fictional-other-card@1'


def test_a_changed_own_statement_makes_the_direction_check_stale():  # Codex R1
    card = rapa()
    line = card['added']['layers']['evidence']['lines'][0]
    line['target_ref'] = f"{card['id']}@{card['version']}"
    card['content_hash'] = content_hash(card)
    assert not validation_errors(SCHEMA, card) and check_refs(card)['valid']
    ledger = ledger_errors(card)
    assert '/added/layers/evidence/lines/0/direction|src' in ledger['entries']
    before = set(check_ledger.check(card, ledger))
    card['author']['layers']['core']['statement']['value'] = 'A changed proposition, fictional.'
    card['content_hash'] = ledger['content_hash'] = content_hash(card)
    after = set(check_ledger.check(card, ledger)) - before
    assert [e for e in after if e.startswith('/added/layers/evidence/lines/0/direction|src: the value differs')]


def keyed_group(card, assessed_at):
    """rapa with line 0 in a group whose key is resolved against a PubMed record, assessed at a given time."""
    group = card['added']['layers']['evidence']['lines'][0]['independence_group']
    group['value'] = 'g_fictional_resolution_time'
    group['key'] = {'scheme': 'pmid', 'id': '123456'}
    group['assessment'] = {'assessor': 'fictional-reviewer', 'assessed_at': assessed_at,
                           'evidence_ref': {'kind': 'artifact', 'sha256': 'sha256:' + '4' * 64}}
    card['added']['at'] = '2030-01-03T00:00:00Z'
    name = withheld_source(card)
    add(card, record('/added/layers/evidence/lines/0/independence_group/key', 'resolution', TOOL,
                     resolved_against={'source': name, 'response_sha256': RESPONSE, 'key': '123456'}))
    card['content_hash'] = content_hash(card)
    return card


def test_a_resolution_is_checked_after_the_assessment_of_its_value():  # Codex R2
    early = keyed_group(rapa(), '2030-01-02T00:00:00Z')
    assert not validation_errors(SCHEMA, early)
    assert codes(early) == {'REF_TIME_ORDER'}
    assert not codes(keyed_group(rapa(), LATER))


# ------------------------------------------------------------------ closed predicates (item 1)

def triple(card):
    """The relation of the first atom with a triple, and that atom's triple value."""
    atom = next(a for a in card['added']['layers']['core']['atoms'] if 'triple' in a)
    return atom['triple']['value']


def schema_clause(versions):
    for clause in SCHEMA['allOf']:
        version = clause['if']['properties'].get('standard_version', {})
        if version.get('enum', [version.get('const')]) == versions:
            return clause['then']['allOf']
    raise KeyError(versions)


def test_predicates_pin_matches_the_vocabulary():
    assert SCHEMA['properties']['vocabularies']['properties']['predicates']['properties']['sha256']['const'] == predicates_pin()


def test_schema_predicates_are_the_vocabulary():
    clause = schema_clause(['1.2'])
    value = next(c for c in clause if 'atoms' in str(c) and 'enum' in str(c))
    value = value['properties']['added']['properties']['layers']['properties']['core']['properties']['atoms']['items']
    value = value['properties']['triple']['properties']['value']['properties']
    assert value['relation']['properties']['id']['enum'] == [p['id'] for p in PREDICATES['predicates']]
    assert value['qualifiers']['items']['properties']['type']['enum'] == [q['id'] for q in PREDICATES['qualifier_slots']]


def test_vocabulary_rows_are_well_formed():
    ids = [p['id'] for p in PREDICATES['predicates']]
    assert len(ids) == len(set(ids))
    for row in PREDICATES['predicates']:
        assert row['source'] in PREDICATES['sources'] and row['label'].strip()
        assert row['kind'] in ('causal', 'regulatory', 'associative')
        assert row['id'].startswith('RO:' if row['source'] == 'RO' else 'biolink:')
    assert 'other' not in ids


# (id, label, inverse) as read in ro.json release 2026-09-04
# (sha256 17eab8be4f47c73d2905ba45752154ae8e2e7b0bf03ba3cc62a326b42a38e5a5: node lbl, inverseOf edges)
# and biolink-model.yaml v4.4.6
# (sha256 5837907e1eb579812856579feea5a099665252f2454bd6f950d63fbb00f4c9f0: `affected by` has `inverse: affects`).
SOURCE_ROWS = [
    ('RO:0002211', 'regulates', 'RO:0002334'),
    ('RO:0002213', 'positively regulates', 'RO:0002336'),
    ('RO:0002212', 'negatively regulates', 'RO:0002335'),
    ('RO:0002411', 'causally upstream of', 'RO:0002404'),
    ('RO:0003304', 'contributes to condition', None),
    ('RO:0002610', 'correlated with', None),
    ('biolink:affects', 'affects', 'biolink:affected_by'),
]


def test_vocabulary_rows_are_as_the_sources_state_them():
    assert [(p['id'], p['label'], p.get('inverse')) for p in PREDICATES['predicates']] == SOURCE_ROWS


def test_examples_and_fixtures_use_only_listed_predicates():
    listed = {p['id']: p['label'] for p in PREDICATES['predicates']}
    for path in LEGACY:
        card = load(path)
        for atom in card.get('added', {}).get('layers', {}).get('core', {}).get('atoms', []):
            if 'triple' in atom:
                relation = atom['triple']['value']['relation']
                assert listed.get(relation['id']) == relation['label'], (path.name, relation)


def test_the_rapa_triple_is_valid_in_1_2():
    card = rapa()
    assert not validation_errors(SCHEMA, card)
    assert 'REF_PREDICATE_LABEL' not in codes(card)


def test_a_predicate_outside_the_vocabulary_is_rejected():  # M1a
    card = rapa()
    assert not validation_errors(SCHEMA, card)
    triple(card)['relation'] = {'id': 'RO:0009999', 'label': 'negatively regulates'}
    assert schema_rejects(card)


def test_a_predicate_with_another_label_is_rejected():  # M1b
    card = rapa()
    triple(card)['relation']['label'] = 'positively regulates'
    assert not validation_errors(SCHEMA, card)
    assert codes(card) == {'REF_PREDICATE_LABEL'}


def test_a_qualifier_outside_the_slots_is_rejected():  # M1c
    card = rapa()
    triple(card)['qualifiers'] = [{'type': 'biolink:made_up_qualifier', 'value': 'increased'}]
    assert schema_rejects(card)
    triple(card)['qualifiers'] = [{'type': 'biolink:object_direction_qualifier', 'value': 'increased'}]
    assert not validation_errors(SCHEMA, card)


def test_a_changed_vocabulary_breaks_the_pin():  # M1d
    data = bytearray((ROOT / 'vocabularies/predicates-1.json').read_bytes())
    data[data.index(b'negatively')] ^= 0x20
    card = rapa()
    assert not validation_errors(SCHEMA, card)
    card['vocabularies']['predicates']['sha256'] = predicates_pin(bytes(data))
    assert schema_rejects(card)


def test_a_1_2_triple_needs_the_pin():  # M1e
    card = rapa()
    del card['vocabularies']['predicates']
    assert schema_rejects(card)
    for atom in card['added']['layers']['core']['atoms']:
        atom.pop('triple', None)
    records = card['added']['integrity']['entailment']
    records[:] = [r for r in records if '/triple' not in r['pointer']]
    assert not validation_errors(SCHEMA, card)


def test_a_1_1_card_keeps_the_open_relation():  # M1f, M1g
    card = copy.deepcopy(RAPA)
    assert not validation_errors(SCHEMA, card)
    triple(card)['relation'] = {'id': 'RO:0009999', 'label': 'a relation not in the vocabulary'}
    assert not validation_errors(SCHEMA, card)
    assert 'REF_PREDICATE_LABEL' not in codes(card)
    card['vocabularies']['predicates'] = {'id': 'ohf:predicates@1', 'sha256': predicates_pin()}
    assert schema_rejects(card)


# ------------------------------------------------------------------ item 4(c): the scope of an atom

DIET = 8  # peto: a_diet, read on a diet data set of terrestrial mammals only
DIET_SCOPE = {'value': 'Terrestrial mammals of the global diet data set; marine mammals of the sample are not covered.',
              'src': 'diet_models', 'paraphrase': True,
              'basis_quote': 'Diet information was obtained from a global diet dataset for terrestrial mammals32'}


def peto(scope=DIET_SCOPE, card=None):
    card = copy.deepcopy(card) if card is not None else as_1_2(PETO)
    if scope is not None:
        card['added']['layers']['core']['atoms'][DIET]['scope'] = copy.deepcopy(scope)
    return card


def gap_codes(card):
    return {issue['code'] for issue in check_gaps(card, load(ROOT / 'spec/gap-path-policy.json'), CATALOGUE,
                                                  load(ROOT / 'spec/mapping.json'), schema=SCHEMA)['errors']}


def scope_gap(card):
    card['added']['gaps'].append({'path': f'core.atoms[{DIET}].scope', 'disposition': 'not_supplied',
                                  'reason': 'The paragraph names no narrower scope for this atom.', 'query_ids': [],
                                  'inspected_artifacts': copy.deepcopy(card['added']['gaps'][0]['inspected_artifacts'])})
    return card


def test_an_atom_scope_is_valid_in_1_2():  # P4a
    card = peto()
    assert not validation_errors(SCHEMA, card)
    result = check_refs(card)
    assert result['valid'], result['errors']
    assert 'REF_ATOM_SCOPE_SAME' not in codes(card, 'warnings')
    assert check_class(card, f'/added/layers/core/atoms/{DIET}/scope') == 'passage'


def test_the_atom_scope_is_the_only_1_2_path():
    assert [row['path'] for row in CATALOGUE['fields'] if row.get('since') == '1.2'] == ['core.atoms[].scope']


def test_an_atom_scope_without_its_src_is_rejected():  # M4a
    assert not validation_errors(SCHEMA, peto())
    assert schema_rejects(peto({'value': DIET_SCOPE['value']}))


def test_a_1_1_card_has_no_atom_scope():  # M4b
    card = peto(card=PETO)
    assert card['standard_version'] == '1.1'
    assert schema_rejects(card)


def test_an_atom_scope_that_repeats_the_card_scope_is_a_warning():  # M4c
    card = as_1_2(PETO)
    text = card['added']['layers']['core']['scope']['value']
    card = peto({'value': '  ' + text.upper() + ' ', 'src': 'diet_models'}, card)
    assert not validation_errors(SCHEMA, card)
    assert 'REF_ATOM_SCOPE_SAME' in codes(card, 'warnings')
    assert check_refs(card)['valid']


def test_a_gap_on_an_atom_scope_is_a_1_2_path():  # M4d
    card = scope_gap(peto(None))
    assert not validation_errors(SCHEMA, card)
    assert not gap_codes(card)
    card = scope_gap(copy.deepcopy(PETO))
    assert schema_rejects(card)
    assert 'GAP_PATH_UNKNOWN' in gap_codes(card)


# ------------------------------------------------------------------ item 3: the domain as a list

PHARMACOLOGY, AGING = 'ohf:intervention-pharmacology@1', 'ohf:aging@1'


def with_domain(domain, card=None):
    """rapa (an aging card with hallmarks) as a 1.2 card, or the given card, naming these profiles."""
    card = copy.deepcopy(card) if card is not None else rapa()
    for zone in ('author', 'added'):
        profile = card[zone]['layers'].get('profile')
        if profile is not None and 'domain' in profile:
            profile['domain'] = copy.deepcopy(domain)
    return card


def without_hallmarks(card):
    card['added']['layers']['profile'].pop('aging_hallmarks')
    card['vocabularies'].pop('hallmarks')
    records = card['added']['integrity']['entailment']
    records[:] = [r for r in records if '/aging_hallmarks' not in r['pointer']]
    return card


def test_a_1_2_domain_is_a_list():  # P3a
    for card, domain in ((rapa(), [AGING]), (as_1_2(PETO), ['none'])):
        assert card['added']['layers']['profile']['domain'] == domain
        assert not validation_errors(SCHEMA, card)
        assert check_refs(card)['valid']
        assert 'REF_PROFILE_REDUNDANT' not in codes(card, 'warnings')


def test_an_empty_domain_list_is_rejected():  # M3a
    card = without_hallmarks(rapa())
    assert not validation_errors(SCHEMA, with_domain([PHARMACOLOGY], card))
    assert schema_rejects(with_domain([], card))


def test_none_stands_alone():  # M3b
    assert not validation_errors(SCHEMA, as_1_2(PETO))
    assert schema_rejects(with_domain(['none', AGING]))
    assert schema_rejects(with_domain(['none', AGING], as_1_2(PETO)))


def test_a_profile_is_named_once():  # M3c
    assert schema_rejects(with_domain([AGING, AGING]))


def test_a_hallmark_needs_a_profile_that_has_it():  # M3d
    assert not validation_errors(SCHEMA, with_domain([AGING]))
    assert schema_rejects(with_domain([PHARMACOLOGY]))
    assert not validation_errors(SCHEMA, with_domain([PHARMACOLOGY], without_hallmarks(rapa())))


def test_a_profile_held_by_another_is_a_warning():  # M3e
    card = with_domain([PHARMACOLOGY, AGING])
    assert not validation_errors(SCHEMA, card)
    result = check_refs(card)
    assert result['valid'], result['errors']
    assert [w['path'] for w in result['warnings'] if w['code'] == 'REF_PROFILE_REDUNDANT'] == ['added.profile.domain[0]']


def test_a_1_2_domain_is_not_a_string():  # M3f
    assert schema_rejects(with_domain(AGING))
    assert schema_rejects(with_domain([AGING], RAPA))  # a list in a 1.1 card


def test_gaps_follow_the_union_of_the_named_profiles():
    card = without_hallmarks(with_domain([PHARMACOLOGY]))
    card['added']['gaps'].append({'path': 'profile.aging_hallmarks[]', 'disposition': 'not_supplied'})
    assert 'GAP_PROFILE_FIELD' in gap_codes(card)
    assert 'GAP_PROFILE_FIELD' not in gap_codes(with_domain([PHARMACOLOGY, AGING], card))


# ------------------------------------------------------------------ erratum E7: a work in the public domain by its term

PUBLIC_DOMAIN = 'LicenseRef-public-domain-term'
EXPIRY = ['imprint year 1918', 'year of death of the author: 1950, from the record of the national library',
          'United States: published in 1930 or earlier', 'life plus 70 years: every author died in 1955 or earlier']


def public_domain(conditions=EXPIRY, basis='public_domain_term', card=None):
    """Peto as a 1.2 card whose source is in the public domain by its term, with the record of the expiry."""
    card = copy.deepcopy(card) if card is not None else as_1_2(PETO)
    card['author']['source'].update(license=PUBLIC_DOMAIN, rights_basis='public_domain_term')
    if conditions is not None:
        card['added']['layers'].setdefault('provenance', {})['licence'] = {'value': {
            'publication_allowed': True, 'usage': 'publication_permitted_under_recorded_terms', 'spdx': None,
            'basis': basis, 'conditions': list(conditions)}, 'src': 'abstract'}
    return card


def test_a_public_domain_source_with_its_expiry_is_valid():  # P7a, (a) and (d)
    card = public_domain()
    assert not validation_errors(SCHEMA, card)
    result = check_refs(card)
    assert result['valid'], result['errors']


def test_the_public_domain_basis_has_its_own_licence_id():  # M7b
    card = public_domain()
    card['author']['source']['license'] = 'CC-PDDC'
    assert schema_rejects(card)
    card = as_1_2(PETO)
    card['author']['source']['license'] = PUBLIC_DOMAIN
    assert card['author']['source']['rights_basis'] == 'license'
    assert schema_rejects(card)


@pytest.mark.parametrize('conditions, basis', [(None, 'public_domain_term'), ([], 'public_domain_term'),
                                               (EXPIRY, 'license')], ids=['no_record', 'no_conditions', 'other_basis'])
def test_the_expiry_is_recorded(conditions, basis):  # M7c
    card = public_domain(conditions, basis)
    assert not validation_errors(SCHEMA, card)
    assert 'REF_RIGHTS_BASIS' in codes(card)


def test_the_public_domain_basis_permits_publication():  # M7d
    terms = public_domain()['added']['layers']['provenance']['licence']['value']
    assert terms['usage'] == 'publication_permitted_under_recorded_terms' and terms['publication_allowed'] is True
    assert not validation_errors(SCHEMA, public_domain())


def test_a_1_1_card_has_no_public_domain_basis():  # M7e
    card = copy.deepcopy(PETO)
    card['author']['source'].update(license=PUBLIC_DOMAIN, rights_basis='public_domain_term')
    assert schema_rejects(card)
    card = copy.deepcopy(PETO)
    card['added']['layers'].setdefault('provenance', {})['licence'] = copy.deepcopy(
        public_domain()['added']['layers']['provenance']['licence'])
    assert schema_rejects(card)
    card['added']['layers']['provenance']['licence']['value']['basis'] = 'license'
    assert not validation_errors(SCHEMA, card)
