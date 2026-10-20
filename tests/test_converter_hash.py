"""Converter pins: the hash of a rules directory reproduces from its files alone."""
import copy
import hashlib
from pathlib import Path

from tools import converter_hash
from tools.strict_json import load

ROOT = Path(__file__).resolve().parents[1]
CARD = load(ROOT / 'examples/cards/muller-sheltering.json')


def sha(data):
    return 'sha256:' + hashlib.sha256(data).hexdigest()


def rules(root):
    (root / 'references').mkdir(parents=True)
    (root / 'scripts').mkdir()
    (root / 'SKILL.md').write_text('skill\n')
    (root / 'references/rules.md').write_text('rules\n')
    (root / 'scripts/build.py').write_text('print(1)\n')
    return root


def test_hash_is_the_sorted_listing_of_relative_paths(tmp_path):
    root = rules(tmp_path / 'r')
    listing = ''.join(f'{p} {sha((root / p).read_bytes())}\n'
                      for p in ('SKILL.md', 'references/rules.md', 'scripts/build.py'))
    assert converter_hash.converter_hash(root) == sha(listing.encode())


def test_hash_does_not_depend_on_where_the_directory_is(tmp_path):
    assert converter_hash.converter_hash(rules(tmp_path / 'a')) == converter_hash.converter_hash(rules(tmp_path / 'b' / 'c'))


def test_changed_byte_or_renamed_file_changes_the_hash(tmp_path):
    root = rules(tmp_path / 'r')
    before = converter_hash.converter_hash(root)
    (root / 'scripts/build.py').write_text('print(2)\n')
    changed = converter_hash.converter_hash(root)
    (root / 'scripts/build.py').rename(root / 'scripts/make.py')
    assert len({before, changed, converter_hash.converter_hash(root)}) == 3


def test_card_without_rules_in_the_repository_fails():
    card = copy.deepcopy(CARD)
    card['added']['by'].update(converter='ohf-extractor', converter_version='0.0.0')
    [error] = converter_hash.pin_errors(card)
    assert 'no rules in examples/converters/ohf-extractor-0.0.0' in error


def test_pin_of_rules_kept_in_the_repository(tmp_path, monkeypatch):
    monkeypatch.setattr(converter_hash, 'CONVERTERS', tmp_path)
    rules(tmp_path / 'ohf-extractor-1.0.0')
    card = copy.deepcopy(CARD)
    card['added']['by'].update(converter='ohf-extractor', converter_version='1.0.0',
                               converter_hash=converter_hash.converter_hash(tmp_path / 'ohf-extractor-1.0.0'))
    assert converter_hash.pin_errors(card) == []
    card['added']['by']['converter_hash'] = sha(b'other')
    assert converter_hash.pin_errors(card)


def test_name_or_version_outside_the_allowed_characters_fails():
    for name, version in (('ohf-extractor', '../1.0'), ('ohf/extractor', '1.0'), ('ohf-extractor', '1.0\n'),
                          ('OHF', '1.0'), ('ohf-extractor', 1)):
        card = copy.deepcopy(CARD)
        card['added']['by'].update(converter=name, converter_version=version)
        [error] = converter_hash.pin_errors(card)
        assert 'may hold only [a-z0-9.-]' in error, (name, version)


def test_symbolic_link_in_the_rules_fails(tmp_path, monkeypatch):
    monkeypatch.setattr(converter_hash, 'CONVERTERS', tmp_path / 'converters')
    outside = rules(tmp_path / 'outside')
    root = rules(tmp_path / 'converters' / 'ohf-extractor-1.0.0')
    (root / 'scripts' / 'linked.py').symlink_to(outside / 'scripts' / 'build.py')
    card = copy.deepcopy(CARD)
    card['added']['by'].update(converter='ohf-extractor', converter_version='1.0.0')
    [error] = converter_hash.pin_errors(card)
    assert 'a symbolic link in the rules directory' in error
    (tmp_path / 'converters' / 'ohf-extractor-2.0.0').symlink_to(outside, target_is_directory=True)
    card['added']['by']['converter_version'] = '2.0.0'
    [error] = converter_hash.pin_errors(card)
    assert 'the rules directory is a symbolic link' in error
