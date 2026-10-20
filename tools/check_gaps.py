"""Check the gap records of a card against the gap policy and field classes.

The check is structural. It checks the gaps a card lists; it does not show that every
missing applicable field is listed. It confirms what the card itself shows; a condition
that needs a human reading of the source is listed under `review_required`, never passed
silently. It does not resolve query records or source artifacts. It assumes a card that already passes
`tools/validate.py` and does not replace schema validation.

A field of a domain profile the card does not select is absent and needs no gap; a gap
for it is an error.
"""
import argparse
import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from strict_json import load  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SEARCH_DISPOSITIONS = {'searched_not_found', 'budget_exhausted'}


def issue(code, path, message):
    return {'code': code, 'path': path, 'message': message}


def unwrap(value):
    return value['value'] if isinstance(value, dict) and 'value' in value else value


def filled(value):
    return value is not None and (not isinstance(value, (str, list, dict)) or bool(value))


def values(card, path, zones=('author', 'added')):
    """Return every value at a logical or concrete path, looking through source wrappers."""
    if path.startswith('identity.'):
        nodes = [card]
    else:
        nodes = [card.get(zone, {}).get('layers', {}) for zone in zones]
    parent_exists = False
    parts = path.split('.')
    for position, part in enumerate(parts):
        match = re.fullmatch(r'([A-Za-z_][A-Za-z_0-9]*)(?:\[([0-9]*)\])?', part)
        if match is None:
            return [], False
        key, index = match.groups()
        found = []
        for node in nodes:
            node = unwrap(node)
            if not isinstance(node, dict):
                continue
            if position == len(parts) - 1:
                parent_exists = True
            if key not in node:
                continue
            value = unwrap(node[key])
            if index is None:
                found.append(value)
            elif isinstance(value, list):
                if index == '':
                    found.extend(value)
                elif int(index) < len(value):
                    found.append(value[int(index)])
        nodes = found
    return nodes, parent_exists


def resolve_pointer(card, pointer):
    node = card
    for token in pointer.split('/')[1:]:
        token = token.replace('~1', '/').replace('~0', '~')
        if isinstance(node, list) and token.isdigit() and int(token) < len(node):
            node = node[int(token)]
        elif isinstance(node, dict) and token in node:
            node = node[token]
        else:
            raise KeyError(pointer)
    return node


def catalogue_row(path, rows):
    """Match a gap path to its catalogue path; component paths inherit their parent row."""
    logical = re.sub(r'\[[0-9]+\]', '[]', path)
    candidate = logical
    while candidate:
        if candidate in rows:
            return rows[candidate], candidate != logical
        cut = max(candidate.rfind('.'), candidate.rfind('['))
        candidate = candidate[:cut] if cut > 0 else ''
    return None, False


def check_condition(card, gap, condition):
    """Return (errors, review notes) for one N/A scope condition."""
    path = gap['path']
    if condition is None:
        return [], ['No machine-checkable condition: a reviewer must confirm inapplicability from the source.']
    kind = condition['id']
    if kind == 'source_verified_human_author':
        stated = card.get('author', {}).get('layers', {}).get('provenance', {}).get('author_type')
        if not (isinstance(stated, dict) and stated.get('value') == condition['expected_value']
                and stated.get('locator')):
            return [issue('GAP_SCOPE_CONDITION', path, 'author_type must be an author-zone "human" value with a locator')], []
        return [], ['A reviewer must confirm that the locator substantiates human authorship.']
    if kind == 'no_translation_with_original_language':
        errors = []
        if not filled(card.get('author', {}).get('source', {}).get('language')):
            errors.append(issue('GAP_SCOPE_CONDITION', path, 'author.source.language must be present'))
        if any(filled(v) for v in values(card, 'provenance.translation')[0]):
            errors.append(issue('GAP_SCOPE_CONDITION', path, 'A translation is recorded'))
        return errors, []
    return [issue('GAP_POLICY_INVALID', path, f'Unknown condition {kind}')], []


def unselected_paths(card, profiles):
    """Catalogue paths of the domain profiles the card does not select."""
    selected = card.get('added', {}).get('layers', {}).get('profile', {}).get('domain')
    return {path for profile in profiles['profiles'] if profile['id'] != selected
            for path in profile['paths']}


def check(card, policy, catalogue, mapping, profiles=None):
    errors, review = [], []
    if card.get('standard_version') != '1.0':
        return {'valid': False, 'review_required': [], 'errors': [issue(
            'GAP_STANDARD_VERSION', 'standard_version', 'Only OHF 1.0 cards are checked')]}
    profiles = profiles if profiles is not None else load(ROOT / 'vocabularies/profiles-1.json')
    unselected = unselected_paths(card, profiles)
    rows = {row['path']: row for row in catalogue['fields']}
    policies = {row['path']: row for row in policy['fields']}
    detached = {row['catalogue_path'] for row in mapping['mappings']
                if row.get('extension') or row.get('coverage') == 'external'}
    seen = set()
    for gap in card['added']['gaps']:
        path, state = gap['path'], gap['disposition']
        if path in seen:
            errors.append(issue('GAP_PATH_DUPLICATE', path, 'One gap per exact path'))
        seen.add(path)
        row, component = catalogue_row(path, rows)
        if row is None:
            errors.append(issue('GAP_PATH_UNKNOWN', path, 'Path is not a catalogue path or a component of one'))
            continue
        if row['path'] in unselected:
            errors.append(issue('GAP_PROFILE_FIELD', path,
                                'The field belongs to a domain profile this card does not select; it needs no gap'))
            continue
        found, parent_exists = values(card, path)
        if any(filled(v) for v in found):
            errors.append(issue('GAP_PATH_POPULATED', path, 'A populated value cannot also be a gap'))
        if component and not parent_exists:
            errors.append(issue('GAP_COMPONENT_UNBOUND', path, 'A component gap needs its parent record'))
        if state in SEARCH_DISPOSITIONS and row.get('field_class') in ('author_only', 'system'):
            errors.append(issue('GAP_SEARCH_NOT_MEANINGFUL', path,
                                f"{row['field_class']} field: a search cannot establish it; use not_supplied"))
        if state == 'not_applicable_contract':
            if policies.get(row['path'], {}).get('na_allowed') != 'contract' or row['path'] not in detached:
                errors.append(issue('GAP_NA_FORBIDDEN', path, 'Path is not a documented contract extension'))
        if state == 'not_applicable_scope':
            rule = policies.get(row['path'], {})
            if rule.get('na_allowed') != 'scope':
                errors.append(issue('GAP_NA_FORBIDDEN', path, 'Path does not allow scope inapplicability'))
                continue
            ref = gap.get('scope_ref', {})
            pointer = ref.get('pointer', '')
            try:
                if not pointer.startswith(('/author/layers/', '/added/layers/')):
                    raise KeyError(pointer)
                if not filled(unwrap(resolve_pointer(card, pointer))):
                    raise KeyError(pointer)
            except KeyError:
                errors.append(issue('GAP_SCOPE_UNBOUND', path, 'scope_ref must point to filled scientific card content'))
                continue
            found_errors, notes = check_condition(card, gap, rule.get('condition'))
            errors.extend(found_errors)
            review.extend({'path': path, 'check': note} for note in notes)
    return {'valid': not errors, 'errors': errors, 'review_required': review}


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('cards', type=Path, nargs='+')
    args = parser.parse_args()
    policy = load(ROOT / 'spec/gap-path-policy.json')
    catalogue = load(ROOT / 'spec/field-catalogue.json')
    mapping = load(ROOT / 'spec/mapping.json')
    failed = False
    for path in args.cards:
        result = check(load(path), policy, catalogue, mapping)
        print(json.dumps({'card': str(path), **result}, ensure_ascii=False))
        failed |= not result['valid']
    return int(failed)


if __name__ == '__main__':
    raise SystemExit(main())
