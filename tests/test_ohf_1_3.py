"""OHF 1.3: each new rule accepts a card that follows it and rejects a mutation that breaks it.

The released 1.1 example cards, made 1.2 cards by `as_1_2`, are the base: `as_1_3` gives the same
card as an OHF 1.3 card. A 1.3 card follows every rule of 1.2.
"""
import copy
import hashlib

import pytest

from tests.test_ohf_1_2 import PETO, RAPA, as_1_2, gap_codes, public_domain, record
from tools.check_refs import check as check_refs, release_context
from tools.content_hash import content_hash
from tools.strict_json import load
from tools.validate import validation_errors
from tests.test_ohf_1_2 import ROOT, SCHEMA

# The release context of a released 1.3.0, injected so that the tests do not depend on the
# CHANGELOG and VERSION of the checkout before the release commit.
RELEASED = {'known': ['1.3.0', '1.2.0', '1.1.4'], 'current': '1.3.0'}
COMMIT = 'b8101eb95be080898d8957689cdeb929466c7e12'


def as_1_3(card):
    card = as_1_2(card)
    card['standard_version'] = '1.3'
    return card


def codes(card, kind='errors', release=RELEASED, licences=None):
    return {issue['code'] for issue in check_refs(card, release=release, licences=licences)[kind]}


def schema_rejects(card):
    return bool(validation_errors(SCHEMA, card))


def with_release(card, version='1.3.0', commit=None):
    card = copy.deepcopy(card)
    card['added']['by']['standard_release'] = {'version': version, **({'commit': commit} if commit else {})}
    return card


@pytest.mark.parametrize('card', [RAPA, PETO], ids=['rapa', 'peto'])
def test_1_2_cards_as_1_3_cards_are_valid(card):
    card = as_1_3(card)
    assert not validation_errors(SCHEMA, card)
    result = check_refs(card, release=RELEASED)
    assert result['valid'], result['errors']


# ------------------------------------------------------------------ N2: the release the card was built against

@pytest.mark.parametrize('commit', [None, COMMIT], ids=['version', 'version_and_commit'])
def test_a_stated_release_is_valid(commit):  # P2
    card = with_release(as_1_3(PETO), commit=commit)
    assert not validation_errors(SCHEMA, card)
    assert not codes(card) & {'REF_RELEASE_VERSION', 'REF_RELEASE_UNKNOWN'}


def test_a_card_without_a_release_needs_nothing():
    card = as_1_3(PETO)
    assert 'standard_release' not in card['added']['by']
    assert not validation_errors(SCHEMA, card) and not codes(card)


def test_a_1_2_card_states_no_release():  # M2a
    card = as_1_2(PETO)
    assert not validation_errors(SCHEMA, card)
    card['added']['by']['standard_release'] = {'version': '1.2.0'}
    assert schema_rejects(card)


def test_the_release_is_of_the_cards_minor_version():  # M2b
    card = with_release(as_1_3(PETO), '1.2.0')
    assert not validation_errors(SCHEMA, card)
    assert 'REF_RELEASE_VERSION' in codes(card)


def test_an_unknown_release_is_reported():  # M2c: not among the known releases, older than the current one
    release = {'known': ['1.3.0', '1.3.2'], 'current': '1.3.2'}
    assert 'REF_RELEASE_UNKNOWN' not in codes(with_release(as_1_3(PETO), '1.3.2'), release=release)
    assert 'REF_RELEASE_UNKNOWN' in codes(with_release(as_1_3(PETO), '1.3.1'), release=release)


def test_a_release_newer_than_the_tool_is_reported():  # M2d: known, but later than the current one
    release = {'known': ['1.3.0', '1.3.1'], 'current': '1.3.0'}
    assert 'REF_RELEASE_UNKNOWN' not in codes(with_release(as_1_3(PETO), '1.3.0'), release=release)
    assert 'REF_RELEASE_UNKNOWN' in codes(with_release(as_1_3(PETO), '1.3.1'), release=release)


@pytest.mark.parametrize('release', [{'version': '1.3'}, {'version': '1.3.0', 'commit': 'b8101eb'},
                                     {'version': '01.3.0'}, {'commit': COMMIT}, {'version': '1.3.0', 'tag': 'v1.3.0'},
                                     {'version': '1.3.0\n'}, {'version': '1.3.0', 'commit': COMMIT + '\n'}],
                         ids=['short_version', 'short_commit', 'leading_zero', 'no_version', 'unknown_member',
                              'version_with_final_lf', 'commit_with_final_lf'])
def test_a_malformed_release_is_rejected(release):  # M2e
    card = as_1_3(PETO)
    card['added']['by']['standard_release'] = release
    assert schema_rejects(card)


def test_the_default_release_context_is_the_tools_own():
    context = release_context()
    assert context['current'] == (ROOT / 'VERSION').read_text().strip()
    assert context['current'] in context['known']
    assert '1.1.4' in context['known'] and '1.2.0' in context['known']


# ------------------------------------------------------------------ N3: the licence ids that OHF defines

LICENCE_REFS = load(ROOT / 'vocabularies/licence-refs-1.json')
NOT_STATED = 'LicenseRef-CC-BY-version-not-stated'
LICENCE = 'author.source.license'
LICENCE_CODES = {'REF_LICENCE_REF_UNKNOWN', 'REF_LICENCE_REF_RELEASE', 'REF_LICENCE_FORM'}


def licence_refs_pin(data=None):
    data = data if data is not None else (ROOT / 'vocabularies/licence-refs-1.json').read_bytes()
    return 'sha256:' + hashlib.sha256(data).hexdigest()


def with_licence(card, licence, pin=True):
    card = copy.deepcopy(card)
    card['author']['source']['license'] = licence
    if pin:
        card['vocabularies']['licence_refs'] = {'id': 'ohf:licence-refs@1', 'sha256': licence_refs_pin()}
    return card


def with_row(since, licence='LicenseRef-fixture-row'):
    """The published vocabulary with one fixture row. The published file has none."""
    licences = copy.deepcopy(LICENCE_REFS)
    licences['licence_refs'].append({'id': licence, 'since': since, 'meaning': 'A fixture row of the tests.'})
    return licences


def licence_codes(card, licences=None):
    result = check_refs(card, release=RELEASED, licences=licences)
    return ({i['code'] for i in result['errors']} & LICENCE_CODES, {i['code'] for i in result['warnings']} & LICENCE_CODES)


@pytest.mark.parametrize('card', [with_licence(as_1_3(PETO), NOT_STATED),
                                  with_release(with_licence(as_1_3(PETO), NOT_STATED), '1.3.0'),
                                  with_licence(as_1_3(public_domain()), 'LicenseRef-public-domain-term'),
                                  with_licence(as_1_3(PETO), 'CC-BY-4.0', pin=False)],
                         ids=['not_stated', 'not_stated_with_release', 'public_domain_term', 'spdx_without_pin'])
def test_a_defined_licence_id_is_valid(card):  # P3: each id at and after its since
    assert not validation_errors(SCHEMA, card)
    result = check_refs(card, release=RELEASED)
    assert result['valid'], result['errors']
    assert licence_codes(card) == (set(), set())


@pytest.mark.parametrize('licence', ['LicenseRef-CC-BY-4.0', 'LicenseRef-public-domain', 'licenseref-cc-by-version-not-stated'])
def test_an_unknown_licence_id_is_an_error_in_1_3_and_a_warning_before(licence):  # M3a
    card = with_licence(as_1_3(PETO), licence)
    assert not validation_errors(SCHEMA, card)
    assert licence_codes(card) == ({'REF_LICENCE_REF_UNKNOWN'}, set())
    card = with_licence(as_1_2(PETO), licence, pin=False)
    assert not validation_errors(SCHEMA, card)
    assert check_refs(card, release=RELEASED)['valid']
    assert licence_codes(card) == (set(), {'REF_LICENCE_REF_UNKNOWN'})


def test_a_later_patch_is_reported_against_the_stated_release():  # M3b
    card = with_release(with_licence(as_1_3(PETO), 'LicenseRef-fixture-row'), '1.3.0')
    assert licence_codes(card, with_row('1.3.1')) == ({'REF_LICENCE_REF_RELEASE'}, set())
    assert licence_codes(card, with_row('1.3.0')) == (set(), set())
    # Without the stated release the patch is not known, and only the minor line is checked.
    del card['added']['by']['standard_release']
    assert licence_codes(card, with_row('1.3.1')) == (set(), set())
    # Without the fixture row the id is unknown, so the finding above comes from the row's since.
    assert licence_codes(card, LICENCE_REFS) == ({'REF_LICENCE_REF_UNKNOWN'}, set())


def test_a_later_minor_line_is_reported_without_a_stated_release():  # M3c
    card = with_licence(as_1_2(PETO), 'LicenseRef-fixture-row', pin=False)
    assert licence_codes(card, with_row('1.3.0')) == (set(), {'REF_LICENCE_REF_RELEASE'})
    assert licence_codes(card, with_row('1.2.0')) == (set(), set())
    assert licence_codes(card, LICENCE_REFS) == (set(), {'REF_LICENCE_REF_UNKNOWN'})
    card = with_licence(as_1_3(PETO), 'LicenseRef-fixture-row')
    assert licence_codes(card, with_row('1.4.0')) == ({'REF_LICENCE_REF_RELEASE'}, set())
    assert licence_codes(card, with_row('1.3.9')) == (set(), set())
    assert licence_codes(card, LICENCE_REFS) == ({'REF_LICENCE_REF_UNKNOWN'}, set())


@pytest.mark.parametrize('licence', ['CC BY', 'CC BY 2.5', 'CC-BY-2.5 ', 'Creative Commons Attribution', 'CC-BY-4.0\n'])
def test_a_licence_that_is_no_id_gets_a_warning(licence):  # M3d
    for card in (as_1_3(PETO), as_1_2(PETO)):
        card = with_licence(card, licence, pin=False)
        assert not validation_errors(SCHEMA, card)
        assert licence_codes(card) == (set(), {'REF_LICENCE_FORM'})


@pytest.mark.parametrize('licence', [NOT_STATED, 'LicenseRef-CC-BY-4.0', 'licenseref-cc-by-version-not-stated'])
def test_a_1_3_licence_id_needs_the_pin(licence):  # M3e
    card = with_licence(as_1_3(PETO), licence)
    assert not validation_errors(SCHEMA, card)
    del card['vocabularies']['licence_refs']
    assert schema_rejects(card)


def test_a_changed_licence_vocabulary_breaks_the_pin():
    data = bytearray((ROOT / 'vocabularies/licence-refs-1.json').read_bytes())
    data[data.index(b'1.1.4')] = ord('2')
    card = with_licence(as_1_3(PETO), NOT_STATED)
    card['vocabularies']['licence_refs']['sha256'] = licence_refs_pin(bytes(data))
    assert schema_rejects(card)


def test_a_1_2_card_does_not_pin_the_licence_vocabulary():
    card = as_1_2(PETO)
    card['vocabularies']['licence_refs'] = {'id': 'ohf:licence-refs@1', 'sha256': licence_refs_pin()}
    assert schema_rejects(card)


def test_a_released_1_0_card_with_a_later_licence_id_stays_valid():  # P3-legacy
    card = load(ROOT / 'examples/cards/muller-sheltering.json')
    assert card['standard_version'] == '1.0'
    card['author']['source']['license'] = NOT_STATED
    card['content_hash'] = content_hash(card)
    assert not validation_errors(SCHEMA, card)
    result = check_refs(card)
    assert result['valid'], result['errors']
    assert licence_codes(card) == (set(), {'REF_LICENCE_REF_RELEASE'})


def test_the_published_licence_vocabulary():
    """The real file: its pin is the schema's, it has no fixture rows, and each id is defined from a
    release of the CHANGELOG."""
    pin = SCHEMA['properties']['vocabularies']['properties']['licence_refs']['properties']['sha256']['const']
    assert pin == licence_refs_pin()
    assert LICENCE_REFS['schema'] == 'ohf:licence-refs@1'
    assert {row['id']: row['since'] for row in LICENCE_REFS['licence_refs']} == {
        NOT_STATED: '1.1.4', 'LicenseRef-public-domain-term': '1.2.0'}
    assert all(row['since'] in release_context()['known'] for row in LICENCE_REFS['licence_refs'])
    card = with_licence(as_1_3(PETO), 'LicenseRef-fixture-row')
    assert {i['code'] for i in check_refs(card, release=RELEASED)['errors']} >= {'REF_LICENCE_REF_UNKNOWN'}


# ------------------------------------------------------------------ N1: the names the source gives the hypothesis

# Fixture names on the Peto card: the format checks their form, not their wording against the source.
NAMED = 'the Diet Hypothesis of Cancer Mortality'
OTHER = 'mammal-prey cancer hypothesis'
SRC = PETO['added']['layers']['core']['scope']['src']
LOCATOR = PETO['author']['layers']['core']['statement']['locator']


def with_names(card, added=(NAMED, OTHER), author=(NAMED,)):
    card = copy.deepcopy(card)
    card['added']['layers']['core']['names'] = [{'value': name, 'src': SRC} for name in added]
    card['author']['layers']['core']['names'] = [{'value': name, 'locator': LOCATOR} for name in author]
    return card


def name_gap(card, path='core.names'):
    card = copy.deepcopy(card)
    model = next(gap for gap in card['added']['gaps'] if gap['disposition'] == 'not_supplied')
    card['added']['gaps'].append({**copy.deepcopy(model), 'path': path,
                                  'reason': 'The body names the hypothesis; the conversion did not record the name.'})
    return card


def test_names_with_their_passages_are_valid():  # P1
    card = with_names(as_1_3(PETO))
    assert not validation_errors(SCHEMA, card)
    result = check_refs(card, release=RELEASED)
    assert result['valid'], result['errors']


def test_a_card_without_names_needs_no_gap():
    card = as_1_3(PETO)
    assert 'names' not in card['added']['layers']['core']
    assert not validation_errors(SCHEMA, card) and not gap_codes(card) and not codes(card)
    card['added']['layers']['core']['names'] = []
    assert not validation_errors(SCHEMA, card) and not codes(card)


@pytest.mark.parametrize('zone, element', [('added', {'value': NAMED}), ('author', {'value': NAMED}),
                                           ('added', {'value': NAMED, 'src': SRC, 'paraphrase': True}),
                                           ('added', {'value': NAMED, 'locator': LOCATOR}),
                                           ('author', {'value': NAMED, 'src': SRC})],
                         ids=['added_no_src', 'author_no_locator', 'paraphrase', 'added_locator', 'author_src'])
def test_a_name_has_its_own_passage(zone, element):  # M1a: each element its own src or locator, word for word
    card = with_names(as_1_3(PETO))
    card[zone]['layers']['core']['names'][0] = element
    assert schema_rejects(card)


@pytest.mark.parametrize('zone', ['author', 'added'])
def test_a_1_2_card_has_no_names(zone):  # M1b
    card = with_names(as_1_3(PETO))
    card['standard_version'] = '1.2'
    other = 'added' if zone == 'author' else 'author'
    del card[other]['layers']['core']['names']
    assert schema_rejects(card)
    del card[zone]['layers']['core']['names']
    assert not validation_errors(SCHEMA, card)


@pytest.mark.parametrize('path', ['core.names', 'core.names[]', 'core.names[0]'])
def test_a_gap_on_names_is_a_1_3_gap(path):  # M1b: the gap
    card = name_gap(as_1_3(PETO), path)
    assert not validation_errors(SCHEMA, card) and not gap_codes(card)
    card['standard_version'] = '1.2'
    assert schema_rejects(card)
    assert 'GAP_PATH_UNKNOWN' in gap_codes(card)


def test_a_gap_on_a_recorded_name_is_refused():
    assert 'GAP_PATH_POPULATED' in gap_codes(name_gap(with_names(as_1_3(PETO)), 'core.names[0]'))


@pytest.mark.parametrize('value', ['', '   ', '\n'])
def test_a_name_is_not_empty(value):  # M1c
    card = with_names(as_1_3(PETO), added=(value,))
    assert schema_rejects(card)


@pytest.mark.parametrize('again', [NAMED, NAMED.lower(), NAMED.upper(), '  the Diet  Hypothesis of\nCancer Mortality '],
                         ids=['same', 'lower_case', 'upper_case', 'whitespace'])
def test_a_name_is_listed_once(again):  # M1d, with the lead's note (a): letter case does not make another name
    card = with_names(as_1_3(PETO), added=(NAMED, OTHER, again))
    assert not validation_errors(SCHEMA, card)
    assert 'REF_NAME_DUPLICATE' in codes(card)
    assert 'REF_NAME_DUPLICATE' not in codes(with_names(as_1_3(PETO), added=(NAMED, OTHER)))


def test_a_duplicate_is_found_in_the_author_zone_too():
    card = with_names(as_1_3(PETO), author=(NAMED, NAMED.lower()))
    assert 'REF_NAME_DUPLICATE' in codes(card)


def test_the_same_name_in_both_zones_is_no_duplicate():
    assert 'REF_NAME_DUPLICATE' not in codes(with_names(as_1_3(PETO), added=(NAMED,), author=(NAMED,)))


def test_a_name_is_checked_against_its_passage():
    card = with_names(as_1_3(PETO))
    card['added']['integrity']['entailment'].append(record('/added/layers/core/names/1'))
    assert not validation_errors(SCHEMA, card)
    result = check_refs(card, release=RELEASED)
    assert result['valid'], result['errors']
    # A name is checked against a passage, never by resolution.
    card['added']['integrity']['entailment'][-1]['basis'] = 'resolution'
    assert 'REF_BASIS_KIND' in codes(card)
