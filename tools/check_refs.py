"""Check the internal references of an OHF card and report which predictions are comparable.

A prediction is comparable when, across both zones, it states its system, endpoint,
form and epistemic status, and a direction when its form is a directional contrast.

Atom and prediction identifiers must name an atom or prediction of the card. Card
pointers must resolve; a known result must be an evidence line and an alternative
must be an item of `core.alternative_explanations`. External references are listed,
not fetched. It assumes a card that already passes `tools/validate.py`.

The card is also checked for the rules that JSON Schema cannot express: every
author-zone atom is classified by an added-zone atom with the same id; a refetched
source matches, or for a mismatch differs from, `author.source.source_text_sha256`;
each entailment record names a sourced added-zone value once per basis, and its
checker is not the pass that wrote the added zone. A card whose kind is mechanism
while every atom only states existence, distribution or association gets a warning.
"""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from check_gaps import filled, resolve_pointer, unwrap  # noqa: E402
from strict_json import load  # noqa: E402

ZONES = ('author', 'added')
ITEM_LISTS = ('explains', 'reinterprets', 'opens')
COMPARABLE = ('system', 'endpoint', 'form', 'epistemic_status')


def issue(code, path, message):
    return {'code': code, 'path': path, 'message': message}


def layers(card, zone):
    return card.get(zone, {}).get('layers', {})


def identifiers(card, key, errors):
    """Identifiers of core.atoms[] or predictions[] across both zones.

    An identifier is unique within its zone. The same identifier in the author
    and added zones names one record seen from both zones.
    """
    found = set()
    for zone in ZONES:
        records = layers(card, zone).get('core', {}).get('atoms', []) if key == 'atoms' \
            else layers(card, zone).get('predictions', [])
        seen = set()
        for i, record in enumerate(unwrap(records) or []):
            value = unwrap(record.get('id')) if isinstance(record, dict) else None
            if not isinstance(value, str):
                continue
            if value in seen:
                path = f'{zone}.core.atoms[{i}]' if key == 'atoms' else f'{zone}.predictions[{i}]'
                errors.append(issue('REF_DUPLICATE_ID', path, f'Duplicate id {value!r} in the {zone} zone'))
            seen.add(value)
            found.add(value)
    return found


def pointer_target(card, reference, path, prefixes, errors, external):
    """Resolve one reference; card pointers must start with one of `prefixes`."""
    if not isinstance(reference, dict):
        return
    if reference.get('kind') != 'card':
        external.append({'path': path, 'reference': reference})
        return
    target = reference.get('pointer', '')
    try:
        node = resolve_pointer(card, target)
    except KeyError:
        errors.append(issue('REF_UNRESOLVED', path, f'Card pointer does not resolve: {target}'))
        return
    if prefixes and not any(_under(target, prefix) for prefix in prefixes):
        errors.append(issue('REF_WRONG_TARGET', path, f'Pointer must name {" or ".join(prefixes)}'))
    elif not filled(unwrap(node)):
        errors.append(issue('REF_UNRESOLVED', path, f'Card pointer names an empty value: {target}'))


def _under(pointer, pattern):
    """Match a pointer against a pattern in which `*` stands for one array index."""
    parts, wanted = pointer.split('/'), pattern.split('/')
    return len(parts) == len(wanted) and all(
        w == p or (w == '*' and p.isdigit()) for w, p in zip(wanted, parts))


def evidence_lines():
    return [f'/{zone}/layers/evidence/lines/*' for zone in ZONES]


def alternatives():
    return [f'/{zone}/layers/core/alternative_explanations/value/*' for zone in ZONES]


def check_ids(values, known, path, kind, errors):
    for value in values or []:
        if value not in known:
            errors.append(issue('REF_UNKNOWN_ID', path, f'No {kind} with id {value!r}'))


def check(card):
    errors, warnings, external, comparable, not_comparable = [], [], [], [], []
    fields = {}
    if card.get('standard_version') != '1.0':
        return {'valid': False, 'errors': [issue('REF_STANDARD_VERSION', 'standard_version', 'Only OHF 1.0 cards are checked')],
                'warnings': [], 'external': [], 'comparable': [], 'not_comparable': []}
    atoms, predictions = identifiers(card, 'atoms', errors), identifiers(card, 'predictions', errors)
    domains = {zone: layers(card, zone).get('profile', {}).get('domain') for zone in ZONES}
    if domains['author'] is not None and domains['author'] != domains['added']:
        errors.append(issue('REF_DOMAIN_MISMATCH', 'profile.domain',
                            'author and added zones select different domain profiles'))
    for zone in ZONES:
        core = layers(card, zone).get('core', {})
        for name in ITEM_LISTS:
            seen = set()
            for i, item in enumerate(unwrap(core.get(name)) or []):
                path = f'{zone}.core.{name}[{i}]'
                if item['id'] in seen:
                    errors.append(issue('REF_DUPLICATE_ID', path, f"Duplicate id {item['id']!r}"))
                seen.add(item['id'])
                check_ids(item.get('atom_refs'), atoms, path, 'atom', errors)
                check_ids(item.get('prediction_refs'), predictions, path, 'prediction', errors)
                for key in ('observation_ref', 'rival_ref', 'finding_ref'):
                    pointer_target(card, item.get(key), f'{path}.{key}', (), errors, external)
        first = unwrap(core.get('first_proposed'))
        if isinstance(first, dict):
            pointer_target(card, first.get('source_ref'), f'{zone}.core.first_proposed.source_ref', (), errors, external)
        test = (unwrap(core.get('testability')) or {}).get('cheapest_test', {})
        if test.get('kind') == 'reference':
            pointer_target(card, test['ref'], f'{zone}.core.testability.cheapest_test', (), errors, external)
        for i, prediction in enumerate(layers(card, zone).get('predictions', [])):
            path = f'{zone}.predictions[{i}]'
            check_ids(unwrap(prediction.get('derives_from_atom_refs')), atoms, path, 'atom', errors)
            pointer_target(card, unwrap(prediction.get('known_result_ref')), f'{path}.known_result_ref',
                           evidence_lines(), errors, external)
            for j, entry in enumerate(unwrap(prediction.get('also_expected_under')) or []):
                if entry.get('kind') == 'alternative':
                    pointer_target(card, entry['ref'], f'{path}.also_expected_under[{j}]',
                                   alternatives(), errors, external)
            merged = fields.setdefault(unwrap(prediction.get('id')), {})
            merged.update({key: unwrap(value) for key, value in prediction.items()
                           if filled(unwrap(value))})
    check_integrity(card, errors, warnings, external)
    for ident, prediction in fields.items():
        missing = [key for key in COMPARABLE if key not in prediction]
        if prediction.get('form') == 'directional_contrast' and 'direction' not in prediction:
            missing.append('direction')
        if missing:
            not_comparable.append({'id': ident, 'missing': missing})
        else:
            comparable.append(ident)
    return {'valid': not errors, 'errors': errors, 'warnings': warnings, 'external': external,
            'comparable': comparable, 'not_comparable': not_comparable}


def check_integrity(card, errors, warnings, external):
    added_atoms = {unwrap(atom.get('id')): atom for atom in layers(card, 'added').get('core', {}).get('atoms', [])}
    for i, atom in enumerate(layers(card, 'author').get('core', {}).get('atoms', [])):
        if unwrap(atom.get('id')) not in added_atoms:
            errors.append(issue('REF_ATOM_UNCLASSIFIED', f'author.core.atoms[{i}]',
                                'An author-zone atom needs an added-zone atom with the same id and its classification'))
    kinds = {unwrap(layers(card, zone).get('core', {}).get('kind')) for zone in ZONES}
    types = {unwrap(atom.get('claim_type')) for atom in added_atoms.values()}
    if 'mechanism' in kinds and types and types <= {'existence', 'distribution', 'association'}:
        warnings.append(issue('REF_KIND_ATOMS', 'core.kind',
                              'core.kind is mechanism, but every atom only states existence, distribution or association'))
    for i, line in enumerate(layers(card, 'added').get('evidence', {}).get('lines', [])):
        tool = unwrap(line.get('risk_of_bias') or {}) or {}
        pointer_target(card, tool.get('tool_ref'), f'added.evidence.lines[{i}].risk_of_bias.tool_ref', (), errors, external)
    verification = card['added']['source_verification']
    stored = card.get('author', {}).get('source', {}).get('source_text_sha256')
    if verification['status'] == 'refetched_match' and verification['sha256'] != stored:
        errors.append(issue('REF_SOURCE_MISMATCH', 'added.source_verification.sha256',
                            'refetched_match needs the refetched bytes to have the stored source hash'))
    if verification['status'] == 'refetched_mismatch' and verification['sha256'] == stored:
        errors.append(issue('REF_SOURCE_MISMATCH', 'added.source_verification.sha256',
                            'refetched_mismatch needs refetched bytes that differ from the stored source'))
    by = card['added']['by']
    seen = set()
    for i, record in enumerate(card['added'].get('integrity', {}).get('entailment', [])):
        path = f'added.integrity.entailment[{i}]'
        key = (record['pointer'], record['basis'])
        if key in seen:
            errors.append(issue('REF_DUPLICATE_ID', path, 'One entailment record per pointer and basis'))
        seen.add(key)
        checker = record['checker']
        if checker['name'] == by['converter'] or checker['prompt_sha256'] == by['converter_hash']:
            errors.append(issue('REF_CHECKER_NOT_INDEPENDENT', path,
                                'The entailment checker must not be the pass that wrote the added zone'))
        try:
            node = resolve_pointer(card, record['pointer'])
        except KeyError:
            errors.append(issue('REF_UNRESOLVED', path, f"Card pointer does not resolve: {record['pointer']}"))
            continue
        if not (isinstance(node, dict) and 'src' in node and 'value' in node):
            errors.append(issue('REF_WRONG_TARGET', path, 'An entailment record names a sourced added-zone value'))
        elif record['basis'] == 'basis_quote' and 'basis_quote' not in node:
            errors.append(issue('REF_WRONG_TARGET', path, 'The value has no basis_quote to check'))


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('cards', type=Path, nargs='+')
    args = parser.parse_args()
    failed = False
    for path in args.cards:
        result = check(load(path))
        print(json.dumps({'card': str(path), **result}, ensure_ascii=False))
        failed |= not result['valid']
    return int(failed)


if __name__ == '__main__':
    raise SystemExit(main())
