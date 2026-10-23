"""Entailment ledgers: each published ledger binds its card's verdicts to the checked text, and
the ledger checker reports a value, verdict or note that differs from the checks recorded."""
import copy
import subprocess
import sys
from pathlib import Path

import pytest

from tools import check_ledger
from tools.content_hash import content_hash
from tools.strict_json import load

ROOT = Path(__file__).resolve().parents[1]
CARDS = sorted((ROOT / 'examples/cards').glob('*.json'))
LEDGERS = sorted((ROOT / 'examples/ledgers').glob('*.json'))
# Converted before ledgers were kept: its records name no checked text.
# OHF 1.1 cards: check_ledger expects a record for every sourced value and rebuilds a value without
# its closed term, so it does not apply yet (an item for 1.2).
WITHOUT_LEDGER = {'muller-sheltering', 'intermittent-rapamycin-mtorc2', 'peto-paradox-mammals'}
# Test only: the src passages of the example card are not in the repository.
PASSAGE = 'passage not in the repository'


def test_every_ledger_has_its_card():
    assert {p.stem for p in LEDGERS} <= {p.stem for p in CARDS}


def test_every_card_has_a_ledger_or_is_listed_without_one():
    assert {p.stem for p in CARDS} - {p.stem for p in LEDGERS} == WITHOUT_LEDGER


@pytest.mark.parametrize('path', LEDGERS, ids=lambda p: p.name)
def test_published_ledgers_pass(path):
    card = load(ROOT / 'examples/cards' / path.name)
    assert check_ledger.check(card, load(path)) == []


def ledger_for(card):
    """A ledger with one check per record of the card, as a merge would write it."""
    ledger = check_ledger.new_ledger(card)
    records = {check_ledger.key_of(r): r for r in card['added']['integrity']['entailment']}
    for item in check_ledger.value_items(card):
        key = check_ledger.key_of(item)
        item = dict(item, source_passage=item.get('source_passage', PASSAGE))
        check_ledger.add_entry(ledger, key, check_ledger.entry(item, records[key]), records[key].get('note'))
    return ledger


def rehashed(card):
    card['content_hash'] = content_hash(card)
    return card


@pytest.fixture
def card():
    return copy.deepcopy(load(ROOT / 'examples/cards/muller-sheltering.json'))


def entails_record(card):
    return next(r for r in card['added']['integrity']['entailment'] if r['verdict'] == 'entails')


def test_ledger_of_the_card_passes(card):
    assert check_ledger.check(card, ledger_for(card)) == []


def test_value_changed_after_the_check_fails(card):
    ledger = ledger_for(card)
    card['added']['layers']['core']['scope']['value'] += ' Changed.'
    rehashed(card)
    errors = check_ledger.check(card, ledger)
    assert any('/added/layers/core/scope|src: the value differs' in e for e in errors)
    assert any('ledger content_hash' in e for e in errors)


def test_verdict_edited_by_hand_fails(card):
    ledger = ledger_for(card)
    record = next(r for r in card['added']['integrity']['entailment'] if r['verdict'] != 'entails')
    record['verdict'] = 'entails'
    record.pop('note')
    ledger['content_hash'] = rehashed(card)['content_hash']
    assert any("verdict 'entails' in the card" in e for e in check_ledger.check(card, ledger))


def test_earlier_no_on_the_same_text_is_shown(card):
    ledger = ledger_for(card)
    record = entails_record(card)
    key = check_ledger.key_of(record)
    earlier = dict(ledger['entries'][key][0], checked_at='2000-01-01T00:00:00Z', verdict='no',
                   note_sha256=check_ledger.note_sha256('Earlier check.'))
    check_ledger.add_entry(ledger, key, earlier, 'Earlier check.')
    errors = check_ledger.check(card, ledger)
    assert any(f"{key}: verdict 'entails' in the card, 'no' in the ledger" in e for e in errors)
    assert any(key in line for line in check_ledger.summary(card, ledger)[0])


def test_record_without_ledger_entry_fails(card):
    ledger = ledger_for(card)
    key = check_ledger.key_of(entails_record(card))
    del ledger['entries'][key]
    assert any(f'{key}: entailment record with no ledger entry' in e for e in check_ledger.check(card, ledger))


def test_ledger_of_another_card_fails(card):
    ledger = ledger_for(card)
    ledger['card_id'] = 'h_other'
    assert any("ledger is for card 'h_other'" in e for e in check_ledger.check(card, ledger))


def test_command_line_exit_codes(card, tmp_path):
    import json
    card_path, ledger_path = tmp_path / 'card.json', tmp_path / 'ledger.json'
    card_path.write_text(json.dumps(card))
    ledger_path.write_text(json.dumps(ledger_for(card)))
    args = [sys.executable, '-I', str(ROOT / 'tools/check_ledger.py'), str(card_path), str(ledger_path)]
    r = subprocess.run(args, capture_output=True, text=True)
    assert r.returncode == 0 and 'LEDGER CHECK PASS' in r.stdout, r.stdout + r.stderr
    ledger_path.unlink()
    r = subprocess.run(args, capture_output=True, text=True)
    assert r.returncode == 1 and 'no entailment ledger' in r.stdout


def resealed(card, ledger):
    """The card rehashed after a change, and the ledger written for it, as merge would leave them."""
    ledger['content_hash'] = rehashed(card)['content_hash']
    return check_ledger.check(card, ledger)


def record_of(card, key):
    return next(r for r in card['added']['integrity']['entailment'] if check_ledger.key_of(r) == key)


def test_quotation_changed_after_the_check_fails(card):
    ledger = ledger_for(card)
    node = card['added']['layers']['core']['atoms'][0]['modality']
    node['basis_quote'] += ' Changed.'
    errors = resealed(card, ledger)
    assert any('/added/layers/core/atoms/0/modality|basis_quote: the passage differs' in e for e in errors)


def test_record_that_no_check_backs_fails(card):
    ledger = ledger_for(card)
    record = entails_record(card)
    record['checked_at'] = '2099-01-01T00:00:00Z'
    errors = resealed(card, ledger)
    assert any(f'{check_ledger.key_of(record)}: no ledger entry for this text backs the record' in e for e in errors)


def test_tie_shows_the_earliest_check(card):
    ledger = ledger_for(card)
    key = '/added/layers/core/scope|src'
    [check] = ledger['entries'][key]
    assert not check_ledger.latest_assessment(card['added']['layers']['core']['scope'])
    check_ledger.add_entry(ledger, key, dict(check, checked_at='2000-01-01T00:00:00Z'))
    assert any(f'{key}: the record shows the check at {check["checked_at"]}' in e
               for e in check_ledger.check(card, ledger))


def test_tie_shows_the_earliest_check_not_older_than_the_assessment(card):
    ledger = ledger_for(card)
    key = '/added/layers/evidence/lines/0/indirectness|src'
    [check] = ledger['entries'][key]
    node = card['added']['layers']['evidence']['lines'][0]['indirectness']
    assessed = check_ledger.latest_assessment(node)
    assert check['verdict'] == 'entails' and assessed < check['checked_at']
    older = dict(check, checked_at='2000-01-01T00:00:00Z')
    check_ledger.add_entry(ledger, key, older)
    # The later check is the one after the assessment: the record keeps showing it.
    assert check_ledger.check(card, ledger) == []
    record_of(card, key)['checked_at'] = older['checked_at']
    assert any(f'{key}: the record shows the check at 2000-01-01T00:00:00Z' in e for e in resealed(card, ledger))


def test_note_edited_by_hand_fails(card):
    ledger = ledger_for(card)
    record = next(r for r in card['added']['integrity']['entailment'] if r['verdict'] == 'partial')
    record['note'] += ' Edited.'
    errors = resealed(card, ledger)
    assert any(f'{check_ledger.key_of(record)}: the note in the card is not the note of the check' in e for e in errors)


def test_note_text_missing_from_the_ledger_fails(card):
    ledger = ledger_for(card)
    record = next(r for r in card['added']['integrity']['entailment'] if r['verdict'] == 'partial')
    del ledger['notes'][check_ledger.note_sha256(record['note'])]
    assert any(f'{check_ledger.key_of(record)}: the ledger has no text for note' in e
               for e in check_ledger.check(card, ledger))


def test_record_for_a_value_that_is_not_sourced_fails(card):
    ledger = ledger_for(card)
    record = dict(entails_record(card), pointer='/added/layers/core/scope', basis='basis_quote')
    assert 'basis_quote' not in card['added']['layers']['core']['scope']
    card['added']['integrity']['entailment'].append(record)
    errors = resealed(card, ledger)
    assert any('/added/layers/core/scope (basis_quote): record for a value that is not sourced' in e for e in errors)


def test_sourced_value_without_a_record_fails(card):
    ledger = ledger_for(card)
    records = card['added']['integrity']['entailment']
    record = entails_record(card)
    records.remove(record)
    errors = resealed(card, ledger)
    assert any(f"{record['pointer']} ({record['basis']}): no entailment record" in e for e in errors)


def test_unknown_verdict_in_the_ledger_is_reported(card):
    ledger = ledger_for(card)
    key = check_ledger.key_of(entails_record(card))
    ledger['entries'][key].append(dict(ledger['entries'][key][0], checked_at='2099-01-01T00:00:00Z', verdict='maybe'))
    errors = check_ledger.check(card, ledger)
    assert any(f'{key}: ledger entry with a verdict not in' in e for e in errors)
    assert check_ledger.summary(card, ledger)[1] == sum(len(v) for v in ledger['entries'].values())
