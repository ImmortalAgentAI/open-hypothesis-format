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

# The field names that make a pointer a field of each aspect: one segment of the pointer must be one of them.
ASPECT_FIELDS = {
    'endpoint': {'endpoint', 'endpoint_kind', 'endpoint_ref'},
    'population': {'sample', 'sample_size', 'study_system', 'population', 'subgroup'},
    'system': {'system', 'study_system', 'taxon', 'taxon_id'},
}


def issue(code, path, message):
    return {'code': code, 'path': path, 'message': message}


def plain(node):
    """The value with every source wrapper removed."""
    if isinstance(node, dict):
        if 'value' in node and ('src' in node or 'locator' in node):
            return plain(node['value'])
        return {key: plain(item) for key, item in node.items()}
    if isinstance(node, list):
        return [plain(item) for item in node]
    return node


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
                elif not ASPECT_FIELDS[item['aspect']] & set(pointer.split('/')):
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
