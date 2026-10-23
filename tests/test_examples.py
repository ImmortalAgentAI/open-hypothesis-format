"""Cards validate against the schema; selectors, hashes and strict parsing fail closed."""
import copy
import hashlib
import json
from pathlib import Path

import pytest

from tools.content_hash import content_hash
from tools.converter_hash import pin_errors
from tools.strict_json import load, loads
from tools.validate import validation_errors

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = load(ROOT / 'schema/hypothesis-1.schema.json')
CARDS = sorted((ROOT / 'examples/cards').glob('*.json'))
FICTIONAL = sorted((ROOT / 'tests/fixtures/fictional').glob('fx_*.json'))


def test_one_profile():
    assert 'oneOf' not in SCHEMA
    assert SCHEMA['properties']['standard_version'] == {'enum': ['1.0', '1.1']}
    assert 'standard_version' in SCHEMA['required']


@pytest.mark.parametrize('path', CARDS + FICTIONAL, ids=lambda p: p.name)
def test_cards_validate(path):
    card = load(path)
    assert card['standard_version'] in ('1.0', '1.1')
    assert not validation_errors(SCHEMA, card)


@pytest.mark.parametrize('path', CARDS, ids=lambda p: p.name)
def test_example_cards_are_licensed_and_without_domain(path):
    card = load(path)
    # The rapa example shows the aging profile; the other examples select no domain.
    expected = 'ohf:aging@1' if path.stem == 'intermittent-rapamycin-mtorc2' else 'none'
    assert card['added']['layers']['profile']['domain'] == expected
    assert card['author']['source']['license'] in ('CC-BY-4.0', 'CC-BY-3.0')


@pytest.mark.parametrize('path', CARDS, ids=lambda p: p.name)
def test_conversion_rules_are_pinned(path):
    assert pin_errors(load(path)) == []


@pytest.mark.parametrize('path', CARDS + FICTIONAL, ids=lambda p: str(p)[-12:])
def test_content_hashes_match(path):
    card = load(path)
    assert card['content_hash'] == content_hash(card)


def test_index_pins_example_cards():
    index = load(ROOT / 'examples/index.json')
    assert sorted(index) == [path.stem for path in CARDS]
    for name, entry in index.items():
        card = load(ROOT / f'examples/cards/{name}.json')
        assert (entry['id'], entry['version'], entry['content_hash']) == (
            card['id'], card['version'], card['content_hash'])


@pytest.mark.parametrize('path', FICTIONAL, ids=lambda p: p.name)
def test_fictional_source_bytes_are_bound(path):
    card = load(path)
    source = ROOT / 'tests/fixtures/fictional/sources' / path.name
    digest = 'sha256:' + hashlib.sha256(source.read_bytes()).hexdigest()
    assert card['author']['source']['source_text_sha256'] == digest


def test_vocabulary_hash_matches_schema_pin():
    pinned = SCHEMA['properties']['vocabularies']['properties'][
        'heuristics']['properties']['sha256']['const']
    data = (ROOT / 'vocabularies/heuristics-1.json').read_bytes()
    assert pinned == 'sha256:' + hashlib.sha256(data).hexdigest()


@pytest.mark.parametrize('version', ['1.2', '2.0', '1', '1.0.0', '1.1.0', None])
def test_unknown_selector_rejects(version):
    card = load(FICTIONAL[0])
    card['standard_version'] = version
    assert validation_errors(SCHEMA, card)


def test_missing_selector_rejects():
    card = load(FICTIONAL[0])
    del card['standard_version']
    assert validation_errors(SCHEMA, card)


def test_structured_gap_required():
    card = load(FICTIONAL[0])
    card['added']['gaps'] = ['core.kind: not stated']
    assert validation_errors(SCHEMA, card)


def test_invalid_calendar_timestamp_rejects():
    card = copy.deepcopy(load(FICTIONAL[0]))
    card['added']['at'] = '2026-02-30T00:00:00Z'
    assert validation_errors(SCHEMA, card)


def test_changed_card_breaks_hash():
    card = load(CARDS[0])
    card['version'] += 1
    assert card['content_hash'] != content_hash(card)


@pytest.mark.parametrize('text', ['{"a": 1, "a": 2}', '{"a": NaN}', '{"a": 1e999}'])
def test_strict_json_rejects(text):
    with pytest.raises(ValueError):
        loads(text)


def test_fragment_is_not_a_card():
    fragment = load(ROOT / 'tests/fixtures/fragments/sourced-fields.json')
    assert validation_errors(SCHEMA, fragment)


PAIR_BRIEF = load(ROOT / 'schema/pair-brief-1.schema.json')
RELATIONS_2 = load(ROOT / 'schema/hypothesis-relations-1.schema.json')
BRIEF = load(ROOT / 'tests/fixtures/fictional/pair-brief-six-seven.json')
EDGES = load(ROOT / 'tests/fixtures/fictional/relations-six-seven.json')


def test_pair_brief_and_relations_examples_validate():
    assert not validation_errors(PAIR_BRIEF, BRIEF)
    assert not validation_errors(RELATIONS_2, EDGES)


def test_pair_brief_pins_both_cards():
    for ref, name in zip(BRIEF['hypothesis_refs'], ['fx_six', 'fx_seven']):
        card = load(ROOT / f'tests/fixtures/fictional/{name}.json')
        assert ref == {'id': card['id'], 'version': card['version'], 'content_hash': card['content_hash']}


@pytest.mark.parametrize('mutation', ['same_expectation', 'third_card', 'judge_field', 'old_relation'])
def test_pair_brief_rejects(mutation):
    brief = copy.deepcopy(BRIEF)
    if mutation == 'same_expectation':
        brief['distinguishing_observations'][0]['predicted_by_b'] = {'expectation': 'not_expected'}
    elif mutation == 'third_card':
        brief['hypothesis_refs'].append(brief['hypothesis_refs'][0])
    elif mutation == 'judge_field':
        brief['winner'] = 'a'
    else:
        brief['relation'] = 'competes_with'
    assert validation_errors(PAIR_BRIEF, brief)


@pytest.mark.parametrize('relation', ['supports', 'contradicts', 'competes', 'shares_principle'])
def test_relations_2_drops_evidence_relations(relation):
    edges = copy.deepcopy(EDGES)
    edges['edges'][0]['type'] = relation
    assert validation_errors(RELATIONS_2, edges)


@pytest.mark.parametrize('path', sorted((ROOT / 'schema').glob('*.schema.json')), ids=lambda p: p.name)
def test_schema_ids_use_the_ohf_namespace(path):
    schema = load(path)
    assert schema['$id'].startswith('ohf:') and schema['$id'].endswith('@1')
