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
WITHOUT_LEDGER = {'muller-sheltering'}
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
