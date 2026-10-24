"""OHF 1.3: each new rule accepts a card that follows it and rejects a mutation that breaks it.

The released 1.1 example cards, made 1.2 cards by `as_1_2`, are the base: `as_1_3` gives the same
card as an OHF 1.3 card. A 1.3 card follows every rule of 1.2.
"""
import copy

import pytest

from tests.test_ohf_1_2 import PETO, RAPA, as_1_2
from tools.check_refs import check as check_refs, release_context
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


def codes(card, kind='errors', release=RELEASED):
    return {issue['code'] for issue in check_refs(card, release=release)[kind]}


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
                                     {'version': '01.3.0'}, {'commit': COMMIT}, {'version': '1.3.0', 'tag': 'v1.3.0'}],
                         ids=['short_version', 'short_commit', 'leading_zero', 'no_version', 'unknown_member'])
def test_a_malformed_release_is_rejected(release):  # M2e
    card = as_1_3(PETO)
    card['added']['by']['standard_release'] = release
    assert schema_rejects(card)


def test_the_default_release_context_is_the_tools_own():
    context = release_context()
    assert context['current'] == (ROOT / 'VERSION').read_text().strip()
    assert context['current'] in context['known']
    assert '1.1.4' in context['known'] and '1.2.0' in context['known']
