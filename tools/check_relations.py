"""Check a relations file against the cards it names.

The schema checks the form of the file. This check needs the cards: each end of an edge must name a
card given by `id`, `version` and `content_hash`, and a `pointer` on an end must resolve in that card.
From OHF 1.1 an edge may list `scope_differs`: the endpoint, population or system on which the two
cards differ. Each item names the field of the source card and of the target card. Both fields must
resolve, both must be fields of that aspect, and their values must differ once source wrappers are
removed; an edge cannot claim a difference the cards do not show.

Error codes: REL_CARD_MISSING, REL_POINTER_UNRESOLVED, REL_SCOPE_FIELD, REL_SCOPE_SAME.
"""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from strict_json import load  # noqa: E402
from check_gaps import resolve_pointer  # noqa: E402

# Scientific field boundaries, relative to either zone's layers. Nested system
# members and sourced values are allowed, but metadata cannot supply the aspect.
ASPECT_FIELDS = {
    'endpoint': {'endpoint', 'endpoint_kind', 'endpoint_ref'},
    'population': {'sample', 'sample_size', 'study_system', 'population', 'subgroup'},
    'system': {'system', 'study_system', 'taxon', 'taxon_id'},
}
SCOPE_CONTEXTS = {
    ('predictions', '*'): {'endpoint', 'endpoint_kind', 'population', 'system'},
    ('evidence', 'lines', '*'): {
        'endpoint_kind', 'sample', 'sample_size', 'study_system', 'system'},
    ('profile', 'dose_response'): {'endpoint_ref'},
}
SCOPE_METADATA = {'src', 'locator', 'assessment', 'assessment_status',
                  'provenance', 'basis_quote', 'paraphrase', 'confidence'}


def issue(code, path, message):
    return {'code': code, 'path': path, 'message': message}


def plain(node):
    """Scientific value, without source wrappers or provenance/assessment data."""
    if isinstance(node, dict):
        if 'value' in node and ('src' in node or 'locator' in node):
            return plain(node['value'])
        return {key: plain(item) for key, item in node.items() if key not in SCOPE_METADATA}
    if isinstance(node, list):
        return [plain(item) for item in node]
    return node


def scientific_scope_field(card, pointer, aspect):
    """Accept an actual scope field or its value descendants, never metadata."""
    parts = [part.replace('~1', '/').replace('~0', '~') for part in pointer.split('/')[1:]]
    if len(parts) < 4 or parts[0] not in ('author', 'added') or parts[1] != 'layers':
        return False
    logical = parts[2:]
    for context, fields in SCOPE_CONTEXTS.items():
        size = len(context)
        if len(logical) <= size or any(
                not actual.isdigit() if expected == '*' else actual != expected
                for actual, expected in zip(logical, context)):
            continue
        if logical[size] not in fields & ASPECT_FIELDS[aspect]:
            continue
        node = card
        for token in parts:
            if token in SCOPE_METADATA:
                return False
            if isinstance(node, dict) and 'value' in node and ('src' in node or 'locator' in node):
                if token != 'value':
                    return False
            node = node[int(token)] if isinstance(node, list) else node[token]
        return True
    return False


def resolve(card, pointer):
    try:
        return True, resolve_pointer(card, pointer)
    except (KeyError, IndexError, TypeError, ValueError):
        return False, None


def check(relations, cards):
    """Errors of a relations file given the cards it names, each card a parsed document."""
    index = {(card['id'], card['version'], card['content_hash']): card for card in cards}
    errors = []
    for i, edge in enumerate(relations.get('edges', [])):
        ends = {}
        for end in ('source', 'target'):
            ref = edge[end]
            card = index.get((ref['id'], ref['version'], ref['content_hash']))
            if card is None:
                errors.append(issue('REL_CARD_MISSING', f'edges[{i}].{end}',
                                    f"No card {ref['id']} version {ref['version']} with that content_hash was given"))
                continue
            ends[end] = card
            if 'pointer' in ref and not resolve(card, ref['pointer'])[0]:
                errors.append(issue('REL_POINTER_UNRESOLVED', f'edges[{i}].{end}.pointer', ref['pointer']))
        if len(ends) < 2:
            continue
        for j, item in enumerate(edge.get('scope_differs', [])):
            path = f'edges[{i}].scope_differs[{j}]'
            values = []
            for end in ('source', 'target'):
                pointer = item[f'{end}_pointer']
                found, value = resolve(ends[end], pointer)
                if not found:
                    errors.append(issue('REL_POINTER_UNRESOLVED', f'{path}.{end}_pointer', pointer))
                elif not scientific_scope_field(ends[end], pointer, item['aspect']):
                    errors.append(issue('REL_SCOPE_FIELD', f'{path}.{end}_pointer',
                                        f"{pointer} is not a field of the {item['aspect']}"))
                else:
                    values.append(plain(value))
            if len(values) == 2 and values[0] == values[1]:
                errors.append(issue('REL_SCOPE_SAME', path,
                                    f"The two cards give the same {item['aspect']}; the edge cannot claim it differs"))
    return {'valid': not errors, 'errors': errors}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('relations', type=Path)
    parser.add_argument('cards', type=Path, nargs='+')
    args = parser.parse_args()
    result = check(load(args.relations), [load(path) for path in args.cards])
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result['valid'] else 1


if __name__ == '__main__':
    sys.exit(main())
