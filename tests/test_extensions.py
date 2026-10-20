"""Each extension example validates against its named definition; broken fragments reject."""
from pathlib import Path
from urllib.parse import quote

import pytest
from jsonschema import Draft202012Validator

from tools.strict_dates import format_checker
from tools.strict_json import load

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = load(ROOT / 'schema/scientific-field-extensions.schema.json')
EXAMPLES = load(ROOT / 'tests/fixtures/fragments/scientific-field-extensions.json')['examples']


def validator(definition):
    return Draft202012Validator({**SCHEMA, '$ref': '#/$defs/' + quote(definition, safe='')},
                                format_checker=format_checker())


def test_library_has_no_document_level_constraint():
    # The file is a definition library: an arbitrary document passes at the top level.
    assert not list(Draft202012Validator(SCHEMA).iter_errors({'anything': True}))


@pytest.mark.parametrize('row', EXAMPLES, ids=lambda row: row['id'])
def test_example_fragment_validates(row):
    assert row['definition'] in SCHEMA['$defs']
    validator(row['definition']).validate(row['fragment'])


@pytest.mark.parametrize('row', EXAMPLES, ids=lambda row: row['id'])
def test_fragment_without_provenance_rejects(row):
    fragment = dict(row['fragment'])
    fragment.pop('src', None)
    fragment.pop('locator', None)
    assert list(validator(row['definition']).iter_errors(fragment))
