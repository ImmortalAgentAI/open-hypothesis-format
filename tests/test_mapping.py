"""Mapping must cover the catalogue and resolve actual schema storage paths."""
import json
from pathlib import Path
import shutil

import pytest

from tools.check_mapping import check, schema_paths

ROOT = Path(__file__).resolve().parents[1]


def test_current_catalogue_targets_resolve():
    count = len(json.loads((ROOT / 'spec/field-catalogue.json').read_text())['fields'])
    assert check(ROOT) == count


@pytest.mark.parametrize('mutation', ['missing_row', 'duplicate_row', 'invented_target'])
def test_invalid_mapping_fails_closed(tmp_path, mutation):
    for name in ['spec/field-catalogue.json', 'spec/mapping.json',
                 'schema/hypothesis-1.schema.json', 'spec/mapping.md']:
        target = tmp_path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)
    path = tmp_path / 'spec/mapping.json'
    data = json.loads(path.read_text())
    if mutation == 'missing_row':
        data['mappings'].pop()
    elif mutation == 'duplicate_row':
        data['mappings'].append(data['mappings'][0])
    else:
        data['mappings'][-1]['card_paths'] = ['added.layers.profile.invented']
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError):
        check(tmp_path)


def test_mapping_reference_must_resolve():
    with pytest.raises(ValueError, match='Unresolved'):
        schema_paths({'$ref': '#/$defs/missing'})


@pytest.mark.parametrize('mutation', [
    'neighbor_field', 'deferred_claim', 'missing_component',
    'new_scientific_value', 'wrong_external_target', 'wrong_brief_target',
])
def test_reverse_mapping_detects_false_coverage(tmp_path, mutation):
    for name in ['spec/field-catalogue.json', 'spec/mapping.json',
                 'schema/hypothesis-1.schema.json', 'spec/mapping.md',
                 'schema/hypothesis-relations-1.schema.json',
                 'schema/pair-brief-1.schema.json']:
        target = tmp_path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)
    mapping_path = tmp_path / 'spec/mapping.json'
    mapping = json.loads(mapping_path.read_text())
    rows = {row['catalogue_path']: row for row in mapping['mappings']}
    if mutation == 'neighbor_field':
        rows['core.statement']['card_paths'] = [
            'author.layers.core.scope', 'added.layers.core.scope']
    elif mutation == 'deferred_claim':
        rows['identity.question_refs[]'].update(
            coverage='direct', card_paths=['author.layers.core.context[]'])
    elif mutation == 'missing_component':
        mapping['supplemental_fields'].pop()
    elif mutation == 'wrong_external_target':
        rows['pair.relation']['external_paths'][0]['paths'] = ['edges[].rationale']
    elif mutation == 'wrong_brief_target':
        rows['pair.decisive_test']['external_paths'][0]['paths'] = ['decisive_test.invented']
    else:
        path = tmp_path / 'schema/hypothesis-1.schema.json'
        schema = json.loads(path.read_text())
        core = schema['properties']['added']['properties']['layers']['properties']['core']
        core['properties']['invented_scientific_field'] = core['properties']['statement']
        path.write_text(json.dumps(schema))
    mapping_path.write_text(json.dumps(mapping))
    with pytest.raises(ValueError):
        check(tmp_path)


@pytest.mark.parametrize('construction', [
    'then', 'else', 'ref_sibling', 'split_declarations',
    'dependent_schema', 'pattern_property', 'contains', 'prefix_items',
])
def test_new_sourced_values_in_schema_applicators_are_not_silent(tmp_path, construction):
    import copy
    from jsonschema import Draft202012Validator

    for name in ['spec/field-catalogue.json', 'spec/mapping.json',
                 'schema/hypothesis-1.schema.json', 'spec/mapping.md',
                 'schema/hypothesis-relations-1.schema.json',
                 'schema/pair-brief-1.schema.json']:
        target = tmp_path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)
    path = tmp_path / 'schema/hypothesis-1.schema.json'
    schema = json.loads(path.read_text())
    core = schema['properties']['added']['properties']['layers']['properties']['core']
    wrapper = copy.deepcopy(core['properties']['statement'])
    core['properties']['unmapped'] = {}
    declaration = {'properties': {'unmapped': wrapper}}
    if construction in ('then', 'else'):
        core.setdefault('allOf', []).append({
            'if': {'required': ['unmapped']}, construction: declaration})
    elif construction == 'ref_sibling':
        schema['$defs']['SyntheticCore'] = copy.deepcopy(core)
        core.clear()
        core.update({'$ref': '#/$defs/SyntheticCore', **declaration})
    elif construction == 'split_declarations':
        core['properties']['unmapped'] = {'properties': {'src': {'type': 'string'}}}
        core.setdefault('allOf', []).append({
            'if': {'required': ['unmapped']},
            'then': {'properties': {'unmapped': {
                'properties': {'value': {'type': 'string'}}}}}})
    elif construction == 'dependent_schema':
        core['dependentSchemas'] = {'statement': declaration}
    elif construction == 'pattern_property':
        core['patternProperties'] = {'^extra_': wrapper}
    else:
        core['properties']['unmapped'] = {'type': 'array',
            ('contains' if construction == 'contains' else 'prefixItems'):
                wrapper if construction == 'contains' else [wrapper]}
    Draft202012Validator.check_schema(schema)
    path.write_text(json.dumps(schema))
    with pytest.raises(ValueError, match='Unmapped sourced scientific'):
        check(tmp_path)


def test_ref_siblings_and_conditionals_contribute_known_paths():
    from tools.check_mapping import sourced_scientific_paths

    definitions = {'Known': {'properties': {'src': {'type': 'string'}}}}
    node = {'$ref': '#/$defs/Known', 'allOf': [
        {'if': {'required': ['src']},
         'then': {'properties': {'value': {'type': 'string'}}}}]}
    assert set(sourced_scientific_paths(node, 'known', definitions)) == {'known'}
    assert {'known.value', 'known.src'} <= schema_paths(
        node, 'known', definitions=definitions)


@pytest.mark.parametrize('constraint', ['not', 'if'])
def test_constraint_only_field_cannot_count_as_positive_storage(tmp_path, constraint):
    from jsonschema import Draft202012Validator

    for name in ['spec/field-catalogue.json', 'spec/mapping.json',
                 'schema/hypothesis-1.schema.json', 'spec/mapping.md',
                 'schema/hypothesis-relations-1.schema.json',
                 'schema/pair-brief-1.schema.json']:
        target = tmp_path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)
    path = tmp_path / 'schema/hypothesis-1.schema.json'
    schema = json.loads(path.read_text())
    core = schema['properties']['added']['properties']['layers']['properties']['core']
    wrapper = core['properties'].pop('statement')
    core[constraint] = {'required': ['statement'], 'properties': {'statement': wrapper}}
    validator = Draft202012Validator({**core, '$defs': schema['$defs']})
    assert not list(validator.iter_errors({}))
    assert list(validator.iter_errors({'statement': {'value': 'Synthetic.', 'src': 's1'}}))
    path.write_text(json.dumps(schema))
    with pytest.raises(ValueError, match='Mapping target absent'):
        check(tmp_path)


def test_negative_constraints_are_separate_from_implementation_paths():
    node = {'not': {'properties': {'forbidden': {
        'properties': {'value': {'type': 'string'}, 'src': {'type': 'string'}}}}}}
    assert not schema_paths(node)
    assert 'forbidden.value' in schema_paths(node, include_constraints=True)
