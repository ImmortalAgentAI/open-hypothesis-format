"""The list of related standards agrees with the catalogue and its Markdown form is current."""
from pathlib import Path

from tools.build_related_standards import RELATION, render
from tools.strict_json import load

ROOT = Path(__file__).resolve().parents[1]
DATA = load(ROOT / 'spec/related-standards.json')
CATALOGUE = load(ROOT / 'spec/field-catalogue.json')


def test_markdown_is_current():
    assert (ROOT / 'spec/related-standards.md').read_text() == render(DATA)


def test_every_catalogue_basis_is_listed():
    named = {path for entry in DATA['standards'] for path in entry['catalogue_paths']}
    expected = {field['path'] for field in CATALOGUE['fields'] if field['basis'] != 'ohf'}
    assert named == expected


def test_entries_are_complete():
    for entry in DATA['standards']:
        assert entry['relation'] in RELATION
        assert entry['urls'] and all(url.startswith('https://') for url in entry['urls'])
        assert entry['version'] and entry['scope'] and entry['difference']
        assert entry['license']['source']
