"""Check the standard catalogue, mapping, schema and rendered table together."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def schema_paths(node, prefix='', *, definitions=None, stack=(), include_constraints=False):
    from urllib.parse import unquote

    if isinstance(node, bool):
        return set()
    definitions = definitions if definitions is not None else node.get('$defs', {})
    result = set()
    if '$ref' in node:
        ref = node['$ref']
        if not ref.startswith('#/$defs/'):
            raise ValueError(f'Unsupported mapping schema reference: {ref}')
        name = unquote(ref[len('#/$defs/'):])
        if name in stack or name not in definitions:
            raise ValueError(f'Unresolved or recursive mapping schema reference: {ref}')
        result.update(schema_paths(definitions[name], prefix,
                                   definitions=definitions, stack=stack + (name,),
                                   include_constraints=include_constraints))
    for key, child in node.get('properties', {}).items():
        path = f'{prefix}.{key}' if prefix else key
        result.add(path)
        result.update(schema_paths(child, path, definitions=definitions, stack=stack,
                                   include_constraints=include_constraints))
    if 'items' in node:
        result.add(prefix + '[]')
        result.update(schema_paths(node['items'], prefix + '[]',
                                   definitions=definitions, stack=stack,
                                   include_constraints=include_constraints))
    for option in ('anyOf', 'oneOf', 'allOf'):
        for child in node.get(option, []):
            result.update(schema_paths(child, prefix, definitions=definitions, stack=stack,
                                   include_constraints=include_constraints))
    for option in (('if', 'then', 'else', 'not') if include_constraints
                   else ('then', 'else')):
        if option in node:
            result.update(schema_paths(node[option], prefix,
                                       definitions=definitions, stack=stack,
                                   include_constraints=include_constraints))
    for child in node.get('dependentSchemas', {}).values():
        result.update(schema_paths(child, prefix, definitions=definitions, stack=stack,
                                   include_constraints=include_constraints))
    for option in ('contains', 'additionalItems', 'unevaluatedItems'):
        if option in node:
            result.update(schema_paths(node[option], prefix + '[]',
                                       definitions=definitions, stack=stack,
                                   include_constraints=include_constraints))
    for child in node.get('prefixItems', []):
        result.update(schema_paths(child, prefix + '[]',
                                   definitions=definitions, stack=stack,
                                   include_constraints=include_constraints))
    dynamic = list(node.get('patternProperties', {}).values())
    dynamic.extend(node[key] for key in ('additionalProperties', 'unevaluatedProperties')
                   if isinstance(node.get(key), dict))
    for child in dynamic:
        result.update(schema_paths(child, prefix + '.*',
                                   definitions=definitions, stack=stack,
                                   include_constraints=include_constraints))
    return result


def check(root=ROOT):
    catalogue = json.loads((root / 'spec/field-catalogue.json').read_text())['fields']
    mapping = json.loads((root / 'spec/mapping.json').read_text())
    rows = mapping['mappings']
    expected = [field['path'] for field in catalogue]
    actual = [row['catalogue_path'] for row in rows]
    if len(set(expected)) != len(expected) or len(set(actual)) != len(actual):
        raise ValueError('Duplicate catalogue or mapping paths')
    if not expected or set(actual) != set(expected):
        raise ValueError('Mapping must cover every catalogue path exactly')
    schema = json.loads((root / 'schema/hypothesis-1.schema.json').read_text())
    zones = {field['path']: field.get('zones', ['author', 'added']) for field in catalogue}
    markdown = (root / 'spec/mapping.md').read_text()
    for row in rows:
        if not row['card_paths'] and not row.get('extension'):
            raise ValueError(f"Missing extension reason: {row['catalogue_path']}")
        if f"| `{row['catalogue_path']}` |" not in markdown:
            raise ValueError(f"Mapping table missing {row['catalogue_path']}")
    paths = schema_paths(schema)
    for row in rows:
        for target in row['card_paths']:
            if target not in paths:
                raise ValueError(f'Mapping target absent from the card schema: {target}')
    check_reverse(root, schema, schema, rows, mapping, zones)
    errors = check_classes(catalogue, schema)
    if errors:
        raise ValueError('; '.join(errors))
    return len(rows)


CHECKS = {'passage', 'resolution', 'card'}


def check_classes(catalogue, schema):
    """Every catalogue row says how its added value is checked (OHF 1.2): one check, or one for each
    member of the value, in which case the members are exactly those the schema gives the value."""
    errors = []
    paths = schema_paths(schema)
    for row in catalogue:
        check = row.get('check')
        if isinstance(check, str) and check in CHECKS:
            continue
        if not isinstance(check, dict) or not check or not set(check.values()) <= CHECKS:
            errors.append(f"Catalogue row {row['path']} has no check of {sorted(CHECKS)}")
            continue
        prefix = f"added.layers.{row['path']}.value."
        members = {p[len(prefix):] for p in paths if p.startswith(prefix) and '.' not in p[len(prefix):]}
        if set(check) != members:
            errors.append(f"Catalogue row {row['path']}: the checks name {sorted(check)}, the schema {sorted(members)}")
    return errors



def sourced_scientific_paths(node, prefix, definitions):
    """Conservatively combine declarations, including ref siblings and conditions.

    This classifies declared storage, rather than selecting a branch for one
    instance. Dynamic source locations retain a wildcard and cannot silently
    match a fixed catalogue path. A sourced payload owns its declared compound
    representation; its metadata and payload are not new catalogue fields.
    """
    paths = schema_paths(node, prefix, definitions=definitions,
                         include_constraints=True)
    candidates = {path.removesuffix('.value') for path in paths
                  if path.endswith('.value')
                  and ({path.removesuffix('.value') + '.src',
                        path.removesuffix('.value') + '.locator'} & paths)}
    for path in sorted(candidates):
        if not any(path.startswith(parent + '.') or path.startswith(parent + '[]')
                   for parent in candidates if parent != path):
            yield path


def check_reverse(root, schema, branch, rows, mapping, zones=None):
    """Audit explicit placement in both directions; scientific support is separate."""
    deferred = {'identity.question_refs[]'}
    deferred.update('identity.assertions[].' + key
                    for key in ('id', 'text', 'agent_ref', 'asserted_at', 'stance', 'confidence'))
    deferred.update('pair.' + key for key in (
        'discriminability', 'diagnosticity_matrix', 'assumptions', 'context_ref'))
    external = {
        'pair.relation': ('schema/hypothesis-relations-1.schema.json', 'ohf:hypothesis-relations@1', 'edges[].type'),
        'pair.hypothesis_refs': ('schema/pair-brief-1.schema.json', 'ohf:pair-brief@1', 'hypothesis_refs[]'),
        'pair.decisive_test': ('schema/pair-brief-1.schema.json', 'ohf:pair-brief@1', 'decisive_test'),
    }
    direct_targets = set()
    for row in rows:
        path = row['catalogue_path']
        kind = row.get('coverage')
        if path in deferred:
            if kind != 'deferred' or row['card_paths'] or not row.get('extension'):
                raise ValueError(f'Deferred field cannot claim direct coverage: {path}')
        elif path in external:
            if kind != 'external' or row['card_paths']:
                raise ValueError(f'Pair field must distinguish in-card and detached storage: {path}')
            schema_file, contract, target = external[path]
            expected = [{'schema_file': schema_file, 'contract': contract, 'paths': [target]}]
            if row.get('external_paths') != expected:
                raise ValueError(f'Missing detached target: {path}')
            if target not in schema_paths(json.loads((root / schema_file).read_text())):
                raise ValueError(f'Detached target absent from schema: {path}')
        else:
            if kind != 'direct' or row.get('extension') or row.get('external_paths'):
                raise ValueError(f'Unexpected direct-field coverage declaration: {path}')
            normalized = {target.replace('.value[]', '[]') for target in row['card_paths']}
            expected = ({path} if path.startswith('identity.') else {
                zone + '.layers.' + path for zone in (zones or {}).get(path, ('author', 'added'))})
            if normalized != expected:
                raise ValueError(f'Semantically different storage path: {path}')
            direct_targets.update(target.removesuffix(".value[]")
                                  for target in row["card_paths"])
    expected_components = {
        f'{zone}.layers.predictions[].intermediate_tests[].{key}'
        for zone in ('author', 'added') for key in ('h0', 'h1', 'test', 'status')}
    supplemental = mapping.get('supplemental_fields', [])
    component_paths = [item.get('card_path') for item in supplemental]
    if (len(set(component_paths)) != len(component_paths)
            or set(component_paths) != expected_components
            or any(item.get('kind') != 'test_record_component'
                   or item.get('logical_parent') != 'predictions[].intermediate_tests[]'
                   or not isinstance(item.get('meaning'), str) or not item['meaning'].strip()
                   for item in supplemental)):
        raise ValueError('Intermediate-test component coverage is incomplete or ambiguous')
    wrappers = set()
    for zone in ('author', 'added'):
        layers = branch['properties'][zone]['properties']['layers']
        wrappers.update(sourced_scientific_paths(layers, zone + '.layers', schema['$defs']))
    missing = wrappers - direct_targets - expected_components
    if missing:
        raise ValueError('Unmapped sourced scientific values: ' + ', '.join(sorted(missing)))
    all_paths = schema_paths(branch, definitions=schema['$defs'])
    if not expected_components <= all_paths:
        raise ValueError('Declared test components absent from schema')
    return {'direct_fields': len(rows) - len(deferred) - len(external),
            'deferred_fields': len(deferred), 'external_fields': len(external),
            'sourced_scientific_locations': len(wrappers),
            'supplemental_component_locations': len(expected_components)}


if __name__ == '__main__':
    print(f'Standard mapping: {check()} paths checked')
