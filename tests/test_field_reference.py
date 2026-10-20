"""A catalogue change must invalidate the reference until it is regenerated."""
import copy
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('field_reference', ROOT / 'tools/build_field_reference.py')
reference = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reference)


def test_added_catalogue_field_invalidates_reference(tmp_path):
    directory = tmp_path / 'spec'
    directory.mkdir(parents=True)
    catalogue = json.loads((ROOT / 'spec/field-reference.json').read_text())
    output = directory / 'fields.md'
    output.write_text(reference.render(catalogue))
    extra = copy.deepcopy(catalogue['fields'][-1])
    extra['path'] = 'pair.new_scientific_field'
    extra['definition'] = 'An additional scientific concept.'
    catalogue['fields'].append(extra)
    (directory / 'field-reference.json').write_text(json.dumps(catalogue))
    assert reference.check(tmp_path)
    output.write_text(reference.render(catalogue))
    assert not reference.check(tmp_path)
    assert f'all {len(catalogue["fields"])} logical catalogue paths' in output.read_text()
    assert extra['definition'] in output.read_text()


def test_duplicate_paths_are_rejected():
    catalogue = json.loads((ROOT / 'spec/field-reference.json').read_text())
    catalogue['fields'].append(copy.deepcopy(catalogue['fields'][0]))
    with pytest.raises(ValueError, match='unique paths'):
        reference.render(catalogue)
