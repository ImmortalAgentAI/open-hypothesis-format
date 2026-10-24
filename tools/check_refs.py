"""Check the internal references of an OHF card and report which predictions are comparable.

A prediction is comparable when, across both zones, it states its system, endpoint,
form and epistemic status, and a direction when its form is a directional contrast.

Identifiers are unique within their namespace and zone; the same identifier in the
author and added zones names one record seen from both zones. Each reference field
names what its vocabulary in the field reference says: an identifier must name a
record of the right namespace, and a card pointer must resolve to a filled value and,
for a typed field, to a record of the right kind. `REFERENCES` holds the typed fields
and `OPEN_REFERENCES` the fields that may name any card value; any other card pointer
in the layers must resolve. A versioned proposition, written `h_<id>@<version>` as in
`identity.supersedes[]`, and an external, artifact or unavailable reference are listed
under `external`, not fetched. The table in `spec/references.md` lists every field.

Every `src` in the added zone names a record of `added.sources`. Author-zone values
carry a `locator` into the text of `author.source`; OHF 1.0 defines no locator syntax,
so locators are not resolved.

The card is also checked for the rules that JSON Schema cannot express: every
author-zone atom is classified by an added-zone atom with the same id; a refetched
source matches, or for a mismatch differs from, `author.source.source_text_sha256`;
each entailment record names a sourced added-zone value once per basis, and its
checker is not the pass that wrote the added zone; the counts of `author.generation`
agree; an entailment record is not older than the access time of the source record
its value names or than the nearest assessment of that value; and no added-zone
assessment is later than `added.at`. A card whose kind is mechanism while every atom
only states existence, distribution or association gets a warning. In an OHF 1.1 card, an
evidence line whose quote reports a result in numbers has a result estimate quoting those
words, or a gap that says why not; a dose or an age in the quote that the line does not
record gets a warning (`check_quotes`); a declared `human_proximity` follows from the line's
taxon and endpoint kind where the pinned taxon table allows it (`check_proximity`). In an OHF 1.2 card,
each entailment record follows the check of the value it names, from the field catalogue: a passage
record names a value checked against its passage, a resolution record a value checked against an
external record, bound to the response and the key it looked up; a value checked by resolution
without a record gets a warning (`check_integrity`); the relation of an atom triple has the label
of that predicate in the pinned vocabulary (`check_predicates`); an atom scope with the text of the
card scope gets a warning, because an atom scope only narrows it (`check_atom_scope`). The completeness
level is computed by `check_completeness.py` and compared with the declared one.
It assumes a card that already passes `tools/validate.py`.
"""
import argparse
import datetime
import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

import check_completeness  # noqa: E402
from check_gaps import filled, resolve_pointer, unwrap  # noqa: E402
from check_ledger import check_class, checks_classes, logical_path, own_versions  # noqa: E402
from strict_json import load  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
ZONES = ('author', 'added')
COMPARABLE = ('system', 'endpoint', 'form', 'epistemic_status')
VERSIONED = re.compile(r'h_[a-z0-9-]+@[1-9][0-9]*')
# Numbers in an evidence line's quote (OHF 1.1): a reported result, a dose, an age.
RESULT_NUMBER = re.compile(r'\d(?:[.,]\d+)?\s?%|\b[pP]\s?[<=>≤≥]\s?0?[.,]\d|\b\d{2}\s?%\s?CI\b|\bCI\b|\d\s?-?fold\b'
                           r'|\b(?:HR|OR|RR|IRR|SMD)\s?[=:(]|η\s?p?2|\bmd\s?=|\bβ\s?=|\br\s?=\s?-?0?[.,]\d')
DOSE_NUMBER = re.compile(r'\d(?:[.,]\d+)?\s?(?:mg/kg|mg|µg|μg|ppm|[µμnm]M|IU)\b')
AGE_NUMBER = re.compile(r'\b\d+\s?(?:days?|weeks?|months?|years?)\s+(?:of\s+age|old)\b'
                        r'|\b(?:starting|beginning|started|from)\s+at\s+\d+\s?(?:days?|weeks?|months?|years?)\b')

# Identifier namespaces: the record list that holds the identifiers.
NAMESPACES = {
    'atom': 'core.atoms[]',
    'prediction': 'predictions[]',
    'evidence line': 'evidence.lines[]',
    'mechanism entity': 'mechanism.entities[]',
    'mechanism step': 'mechanism.steps[]',
    'assumption': 'core.assumptions[]',
    'uncertainty': 'core.uncertainties[]',
    'explained observation': 'core.explains[]',
    'reinterpretation': 'core.reinterprets[]',
    'opened question': 'core.opens[]',
    'alternative': 'core.alternative_explanations[]',
    'excluded record': 'evidence.excluded[]',
}
# The card pointer of one record of each kind a typed reference can name; `*` is an array index.
POINTERS = {
    'atom': 'core/atoms/*',
    'prediction': 'predictions/*',
    'evidence line': 'evidence/lines/*',
    'mechanism entity': 'mechanism/entities/*',
    'mechanism step': 'mechanism/steps/*',
    'alternative': 'core/alternative_explanations/value/*',
    'proposition': 'core/statement',
    'experiment plan': 'appendix/experiment_plan',
}
# Typed reference fields: the kinds they may name and the forms they may take.
# Forms: `id` an identifier, `pointer` a card pointer, `version` a versioned proposition,
# `external` an external, artifact or unavailable reference, `text` a free label, `null` a root.
REFERENCES = {
    'core.atoms[].parent_ref': (('atom',), {'id', 'pointer', 'version', 'external', 'null'}),
    'core.explains[].atom_refs[]': (('atom',), {'id'}),
    'core.atoms[].requires[]': (('atom',), {'id'}),
    'core.atoms[].contradicts[]': (('atom',), {'id'}),
    'core.atoms[].triple.subject.entity_ref': (('mechanism entity',), {'id'}),
    'core.atoms[].triple.object.entity_ref': (('mechanism entity',), {'id'}),
    'core.explains[].prediction_refs[]': (('prediction',), {'id'}),
    'core.reinterprets[].atom_refs[]': (('atom',), {'id'}),
    'core.opens[].atom_refs[]': (('atom',), {'id'}),
    'core.alternative_explanations[].distinguishing_prediction_refs[]': (('prediction',), {'pointer', 'external'}),
    'mechanism.steps[].subject_ref': (('mechanism entity',), {'id', 'pointer'}),
    'mechanism.steps[].object_ref': (('mechanism entity',), {'id', 'pointer'}),
    'mechanism.steps[].evidence_refs[]': (('evidence line',), {'id', 'pointer'}),
    'mechanism.molecular_targets[].entity_ref': (('mechanism entity',), {'id'}),
    'predictions[].derives_from_atom_refs[]': (('atom',), {'id'}),
    'predictions[].known_result_ref': (('evidence line',), {'pointer', 'external'}),
    'predictions[].also_expected_under[].ref': (('alternative',), {'pointer', 'external'}),
    'predictions[].test_plan_ref': (('experiment plan',), {'pointer', 'external', 'text'}),
    'evidence.lines[].target_ref': (('atom', 'prediction', 'mechanism step', 'alternative', 'proposition'),
                                    {'id', 'pointer', 'version', 'external'}),
    'evidence.lines[].items[].line_id': (('evidence line',), {'id'}),
    'evidence.excluded[].target_ref': (('atom', 'prediction', 'mechanism step', 'alternative', 'proposition'),
                                       {'id', 'pointer', 'version', 'external'}),
    'profile.dose_response.endpoint_ref': (('prediction',), {'id', 'pointer', 'version', 'external'}),
    'profile.aging_hallmarks[].atom_refs[]': (('atom',), {'id'}),
}
# Lists whose elements may carry their own `src` from OHF 1.1; such an element is a sourced value.
ELEMENT_SOURCED = tuple(f'/added/layers/core/{name}/value/*'
                        for name in ('alternative_explanations', 'uncertainties', 'opens', 'explains')
                        ) + ('/added/layers/evidence/excluded/*',)
# Reference fields whose vocabulary names no namespace: a card pointer must resolve.
OPEN_REFERENCES = (
    'core.explains[].observation_ref', 'core.explains[].rival_ref', 'core.reinterprets[].finding_ref',
    'core.uncertainties[].target_ref', 'core.uncertainties[].resolution_test_ref',
    'core.alternative_explanations[].claim_or_ref.ref', 'core.alternative_explanations[].shared_observation_refs[]',
    'core.first_proposed.source_ref', 'core.testability.cheapest_test.ref', 'core.novelty_assessment.prior_claim_refs[]',
    'core.potential_benefit.target_refs[]', 'predictions[].resolution.resolves_by.event_ref',
    'evidence.lines[].risk_of_bias.tool_ref', 'evidence.references[].access_context.alternate_source_refs[]',
    'provenance.inspiration_refs[]', 'profile.harm',
)


def issue(code, path, message):
    return {'code': code, 'path': path, 'message': message}


def layers(card, zone):
    return card.get(zone, {}).get('layers', {})


def sourced(node):
    """True for a source wrapper: a value with its `src` or `locator`."""
    return isinstance(node, dict) and 'value' in node and ('src' in node or 'locator' in node)


def walk(node, logical, path):
    """Yield (logical path, card path, node) for a node and everything in it, looking through wrappers."""
    yield logical, path, node
    value = node['value'] if sourced(node) else node
    if isinstance(value, dict):
        for key, item in value.items():
            yield from walk(item, f'{logical}.{key}', f'{path}.{key}')
    elif isinstance(value, list):
        for i, item in enumerate(value):
            yield from walk(item, f'{logical}[]', f'{path}[{i}]')


def zone_nodes(card, zone):
    for layer, content in layers(card, zone).items():
        yield from walk(content, layer, f'{zone}.{layer}')


def identifiers(card, errors):
    """Identifiers of each namespace across both zones.

    An identifier is unique within its namespace and zone. The same identifier in the
    author and added zones names one record seen from both zones.
    """
    found = {kind: set() for kind in NAMESPACES}
    for zone in ZONES:
        seen = {kind: set() for kind in NAMESPACES}
        for logical, path, node in zone_nodes(card, zone):
            for kind, records in NAMESPACES.items():
                value = unwrap(node)
                if logical != f'{records}.id' or not isinstance(value, str):
                    continue
                if value in seen[kind]:
                    errors.append(issue('REF_DUPLICATE_ID', path.removesuffix('.id'),
                                        f'Duplicate {kind} id {value!r} in the {zone} zone'))
                seen[kind].add(value)
                found[kind].add(value)
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


def patterns(kinds):
    return [f'/{zone}/layers/{POINTERS[kind]}' for kind in kinds for zone in ZONES]


def typed_reference(card, value, path, kinds, forms, ids, errors, external):
    """Check one value of a typed reference field."""
    wanted = ' or '.join(kinds)
    if value is None and 'null' in forms:
        return
    if isinstance(value, dict) and value.get('kind') == 'card':
        if 'pointer' in forms:
            pointer_target(card, value, path, patterns(kinds), errors, external)
        else:
            errors.append(issue('REF_WRONG_TARGET', path, f'Must be the identifier of a {wanted}'))
        return
    if isinstance(value, dict):
        if 'external' in forms:
            external.append({'path': path, 'reference': value})
        else:
            errors.append(issue('REF_WRONG_TARGET', path, f'Must name a {wanted} of this card'))
        return
    if not isinstance(value, str):
        return
    if 'version' in forms and VERSIONED.fullmatch(value):
        if value not in own_versions(card):
            external.append({'path': path, 'reference': value})
        return
    if 'id' not in forms:
        if 'text' not in forms:
            errors.append(issue('REF_WRONG_TARGET', path, f'Must be a card pointer to a {wanted}'))
        return
    named = [kind for kind in kinds if value in ids.get(kind, ())]
    if len(named) > 1:
        errors.append(issue('REF_WRONG_TARGET', path, f'{value!r} names records of more than one kind: '
                            + ', '.join(named)))
    elif not named:
        other = [kind for kind, known in ids.items() if value in known]
        if other:
            errors.append(issue('REF_WRONG_TARGET', path, f'{value!r} names a {other[0]}, not a {wanted}'))
        else:
            errors.append(issue('REF_UNKNOWN_ID', path, f'No {wanted} with id {value!r}'))


def check_references(card, ids, errors, external):
    for zone in ZONES:
        for logical, path, node in zone_nodes(card, zone):
            value = unwrap(node) if sourced(node) else node
            if logical in REFERENCES:
                typed_reference(card, value, path, *REFERENCES[logical], ids, errors, external)
            elif logical in OPEN_REFERENCES:
                pointer_target(card, value, path, (), errors, external)
            elif isinstance(value, dict) and value.get('kind') == 'card' and 'pointer' in value:
                pointer_target(card, value, path, (), errors, [])
    search = card.get('added', {}).get('challenge_search') or {}
    for i, reference in enumerate(search.get('evidence_refs', [])):
        pointer_target(card, reference, f'added.challenge_search.evidence_refs[{i}]',
                       patterns(('evidence line',)), errors, external)
    check_parents(card, errors)


def check_parents(card, errors):
    """An atom is not its own ancestor."""
    parents = {}
    for zone in ZONES:
        atoms = layers(card, zone).get('core', {}).get('atoms', [])
        for i, atom in enumerate(atoms if isinstance(atoms, list) else []):
            ident, parent = unwrap(atom.get('id')), unwrap(atom.get('parent_ref'))
            if isinstance(parent, dict) and parent.get('kind') == 'card':
                try:
                    parent = unwrap(unwrap(resolve_pointer(card, parent.get('pointer', ''))).get('id'))
                except (KeyError, AttributeError):
                    parent = None
            if isinstance(ident, str) and isinstance(parent, str):
                parents[ident] = (parent, f'{zone}.core.atoms[{i}].parent_ref')
    for start in sorted(parents):
        seen, current = {start}, parents[start][0]
        while current in parents and current not in seen:
            seen.add(current)
            current = parents[current][0]
        if current == start:
            errors.append(issue('REF_WRONG_TARGET', parents[start][1], f'Atom {start!r} is its own ancestor'))


def check_atom_links(card, errors):
    """An atom neither requires nor contradicts itself, and requires has no cycle (OHF 1.1)."""
    atoms = layers(card, 'added').get('core', {}).get('atoms', [])
    requires = {}
    for i, atom in enumerate(atoms):
        ident = unwrap(atom.get('id'))
        for name in ('requires', 'contradicts'):
            linked = unwrap(atom.get(name)) or []
            if ident in linked:
                errors.append(issue('REF_ATOM_LINK', f'added.core.atoms[{i}].{name}', f'An atom cannot {name[:-1]} itself'))
        requires[ident] = [ref for ref in unwrap(atom.get('requires')) or [] if ref != ident]
    state = {}

    def visit(ident, trail):
        if state.get(ident) == 'done':
            return
        if state.get(ident) == 'open':
            errors.append(issue('REF_ATOM_LINK', 'added.core.atoms', 'requires forms a cycle: '
                                + ' -> '.join(trail[trail.index(ident):] + [ident])))
            return
        state[ident] = 'open'
        for target in requires.get(ident, []):
            if target in requires:
                visit(target, trail + [ident])
        state[ident] = 'done'

    for ident in requires:
        visit(ident, [])


def check_independence(card, errors):
    """One independence group, one key: a label names one data origin and an origin one label (OHF 1.1).

    Once one line of a group gives a key, every line of the group gives it. A DOI is compared without case."""
    labels, keys, lines = {}, {}, layers(card, 'added').get('evidence', {}).get('lines', [])
    for i, line in enumerate(lines):
        group = line.get('independence_group')
        if not (isinstance(group, dict) and isinstance(group.get('key'), dict)):
            continue
        scheme, ident = group['key'].get('scheme'), group['key'].get('id')
        label, key = group.get('value'), (scheme, ident.lower() if scheme == 'doi' and isinstance(ident, str) else ident)
        path = f'evidence.lines[{i}].independence_group'
        if labels.setdefault(label, key) != key:
            errors.append(issue('REF_INDEPENDENCE_KEY', path, f'group {label!r} has two keys'))
        if keys.setdefault(key, label) != label:
            errors.append(issue('REF_INDEPENDENCE_KEY', path, f'key {key[0]} {key[1]} has two groups: '
                                f'{keys[key]!r} and {label!r}'))
    for i, line in enumerate(lines):
        group = line.get('independence_group')
        if isinstance(group, dict) and 'key' not in group and group.get('value') in labels:
            errors.append(issue('REF_INDEPENDENCE_KEY', f'evidence.lines[{i}].independence_group',
                                f'group {group["value"]!r} has a key on another line and none here'))


def check_sources(card, errors):
    """Every `src` in the added zone names a record of `added.sources`."""
    added = card.get('added', {})
    registry = added.get('sources') or {}
    nodes = [node for member, content in added.items() if member not in ('layers', 'sources')
             for node in walk(content, member, f'added.{member}')]
    nodes += list(zone_nodes(card, 'added'))
    dangling = [(path, node['src']) for _, path, node in nodes
                if isinstance(node, dict) and isinstance(node.get('src'), str) and node['src'] not in registry]
    if dangling and not registry:
        errors.append(issue('REF_SOURCES_EMPTY', 'added.sources',
                            'Added values name source records, but added.sources is empty'))
    for path, name in dangling:
        errors.append(issue('REF_SOURCE_UNKNOWN', path, f'No source record {name!r} in added.sources'))


def check_generation(card, errors):
    """The counts of a generation run agree with each other."""
    generation = card.get('author', {}).get('generation') or {}
    generated, submitted, everything = (generation.get(key) for key in ('generated', 'submitted', 'submits_all'))
    if type(generated) is not int or type(submitted) is not int:
        return
    if submitted > generated:
        message = f'The run submitted {submitted} hypotheses but generated only {generated}'
    elif everything is True and submitted != generated:
        message = 'submits_all is true, so submitted must equal generated'
    elif everything is False and submitted == generated:
        message = 'submits_all is false, but submitted equals generated'
    else:
        return
    errors.append(issue('REF_GENERATION_INCONSISTENT', 'author.generation', message))


def moment(text):
    """Parse an RFC 3339 timestamp; None when it is not one or has no offset."""
    try:
        parsed = datetime.datetime.fromisoformat(text.replace('t', 'T').replace('z', 'Z').replace('Z', '+00:00'))
    except (AttributeError, TypeError, ValueError):
        return None
    return parsed if parsed.tzinfo is not None else None


def nearest_assessment(card, pointer):
    """The assessment at a pointer or at its nearest ancestor, or None."""
    tokens = pointer.split('/')[1:]
    for end in range(len(tokens), 0, -1):
        try:
            node = resolve_pointer(card, '/' + '/'.join(tokens[:end]))
        except KeyError:
            continue
        if isinstance(node, dict) and isinstance(node.get('assessment'), dict):
            return node['assessment']
    return None


def check_times(card, errors):
    """No added-zone assessment is later than `added.at`; a generation is not later than its submission."""
    generator = card.get('author', {}).get('generator', {})
    generated, submitted = moment(generator.get('generated_at')), moment(card.get('author', {}).get('submitted_at'))
    if generated and submitted and generated > submitted:
        errors.append(issue('REF_TIME_ORDER', 'author.generator.generated_at',
                            'generated_at is later than author.submitted_at'))
    written = moment(card.get('added', {}).get('at'))
    for _, path, node in zone_nodes(card, 'added'):
        if not (isinstance(node, dict) and isinstance(node.get('assessment'), dict)):
            continue
        assessed = moment(node['assessment'].get('assessed_at'))
        if written and assessed and assessed > written:
            errors.append(issue('REF_TIME_ORDER', f'{path}.assessment',
                                'assessed_at is later than added.at, when the added zone was written'))


def gap_dispositions(card, index, member):
    """Dispositions of the gaps that cover member of evidence line index."""
    paths = {f'evidence.lines[].{member}', f'evidence.lines[{index}].{member}'}
    return [gap.get('disposition') for gap in card.get('added', {}).get('gaps', []) if gap.get('path') in paths]


# Rung of an evidence line's system (OHF 1.1): human endpoints by kind; other taxa by the pinned table.
HUMAN_MARKER = {'biomarker', 'physiological', 'molecular'}
HUMAN_CLINICAL = {'lifespan', 'mortality', 'function', 'disease', 'adverse_event'}
STATED_ONLY = {'in_vitro', 'ex_vivo'}


def derived_proximity(line, taxa):
    """The rungs a line may declare, from its taxon and endpoint kind; None when they cannot be derived."""
    system = line.get('system') if isinstance(line.get('system'), dict) else {}
    taxon = taxa.get(unwrap(system.get('taxon_id')))
    if taxon is None:
        return None
    if taxon != 'human':
        return {taxon} | STATED_ONLY
    kind = line.get('endpoint_kind') if isinstance(line.get('endpoint_kind'), dict) else {}
    term = kind.get('term')
    if term in HUMAN_MARKER:
        return {'human_marker'} | STATED_ONLY
    if term in HUMAN_CLINICAL:
        return {'human_clinical'} | STATED_ONLY
    # Behaviour, another kind or no endpoint kind: the human rung is not determined.
    return None


def check_proximity(card, errors, warnings, taxa=None, terms=None):
    """A declared human_proximity agrees with the rung its taxon and endpoint kind give.

    `taxa` is an optional list of further rows of the form of the pinned table, such as a
    converter's taxa.json; a row adds a taxon the pinned table lacks and never overrides one.
    A row whose proximity is null names a taxon that has no rung, such as one outside the animals.
    Only the pinned table can make a card invalid: a mismatch with a given row is a warning.
    """
    terms = terms if terms is not None else load(ROOT / 'vocabularies/terms-1.json')
    table = {row['id']: row['proximity'] for row in terms['taxa']}
    for row in taxa or []:
        table.setdefault(row['id'], row.get('proximity'))
    known = {ident: rung for ident, rung in table.items() if rung is not None}
    for index, line in enumerate(layers(card, 'added').get('evidence', {}).get('lines', [])):
        declared = unwrap(line.get('human_proximity'))
        if declared is None:
            continue
        path = f'evidence.lines[{index}].human_proximity'
        allowed = derived_proximity(line, known)
        if allowed is None:
            if declared not in STATED_ONLY:
                warnings.append(issue('REF_PROXIMITY_NOT_DERIVED', path,
                                      'the taxon has no rung in the pinned table or the given taxa'))
        elif declared not in allowed:
            pinned = derived_proximity(line, {row['id']: row['proximity'] for row in terms['taxa']}) is not None
            (errors if pinned else warnings).append(issue('REF_PROXIMITY_MISMATCH', path,
                                f'{declared} does not follow from the taxon and endpoint kind: '
                                + ' or '.join(sorted(allowed - STATED_ONLY))))


def check_predicates(card, errors, predicates=None):
    """OHF 1.2: the label of an atom triple's relation is the label of that predicate in the pinned
    vocabulary (the schema closes the id)."""
    if card.get('standard_version') in ('1.0', '1.1'):
        return
    predicates = predicates if predicates is not None else load(ROOT / 'vocabularies/predicates-1.json')
    labels = {row['id']: row['label'] for row in predicates['predicates']}
    for i, atom in enumerate(layers(card, 'added').get('core', {}).get('atoms', [])):
        relation = (unwrap(atom.get('triple')) or {}).get('relation') or {}
        if relation.get('id') in labels and relation.get('label') != labels[relation['id']]:
            errors.append(issue('REF_PREDICATE_LABEL', f'added.core.atoms[{i}].triple.relation.label',
                                f"The label of {relation['id']} is {labels[relation['id']]!r}"))


def check_atom_scope(card, warnings):
    """OHF 1.2: an atom scope narrows the scope of the card. Whether it does is read in the passage;
    an atom scope with the same text as the card scope narrows nothing."""
    if card.get('standard_version') in ('1.0', '1.1'):
        return
    same = lambda text: ' '.join(str(text).split()).casefold()
    card_scopes = {same(unwrap(layers(card, zone).get('core', {}).get('scope')))
                   for zone in ZONES if layers(card, zone).get('core', {}).get('scope') is not None}
    for i, atom in enumerate(layers(card, 'added').get('core', {}).get('atoms', [])):
        if 'scope' in atom and same(unwrap(atom['scope'])) in card_scopes:
            warnings.append(issue('REF_ATOM_SCOPE_SAME', f'added.core.atoms[{i}].scope',
                                  'The atom scope repeats the scope of the card; leave it out'))


def check_quotes(card, errors, warnings):
    """OHF 1.1: what a line's quote reports in numbers is also in the line's fields, or a gap says why not.

    A result number (a percentage, a p value, a confidence interval, an effect measure) needs a
    result estimate or a gap whose disposition is not not_supplied: the estimate can say not_stated
    for a measure, contrast or scale the source does not give, so not supplying it is no longer a
    reason. The reported words of the estimate are in the quote. A dose or an age in the quote
    without the matching condition or a gap is a warning, because the pattern is a heuristic.
    """
    if card.get('standard_version') not in ('1.1', '1.2'):
        return
    for index, line in enumerate(layers(card, 'added').get('evidence', {}).get('lines', [])):
        quote = unwrap(line.get('quote'))
        if not isinstance(quote, str):
            continue
        path = f'evidence.lines[{index}]'
        estimate = unwrap(line.get('result_estimate'))
        if isinstance(estimate, dict):
            if ' '.join(estimate.get('reported', '').split()) not in ' '.join(quote.split()):
                errors.append(issue('REF_ESTIMATE_NOT_QUOTED', f'{path}.result_estimate',
                                    'the reported words of the estimate are not in the quote'))
        elif RESULT_NUMBER.search(quote) and not [d for d in gap_dispositions(card, index, 'result_estimate')
                                                  if d != 'not_supplied']:
            errors.append(issue('REF_ESTIMATE_IN_QUOTE', f'{path}.result_estimate',
                                'the quote reports a result in numbers; give a result estimate, with not_stated '
                                'where the source does not say, or a gap that says why it cannot be given'))
        for pattern, member, holder in ((DOSE_NUMBER, 'dose', 'intervention'), (AGE_NUMBER, 'age_at_start', 'system')):
            stated = isinstance(line.get(holder), dict) and filled(unwrap(line[holder].get(member)))
            if pattern.search(quote) and not stated and not gap_dispositions(card, index, f'{holder}.{member}'):
                warnings.append(issue('REF_CONDITION_IN_QUOTE', f'{path}.{holder}.{member}',
                                      f'the quote names a {member.replace("_", " ")} the line does not record'))


def check(card, taxa=None):
    errors, warnings, external, comparable, not_comparable = [], [], [], [], []
    fields = {}
    if card.get('standard_version') not in ('1.0', '1.1', '1.2'):
        return {'valid': False, 'errors': [issue('REF_STANDARD_VERSION', 'standard_version', 'Only OHF 1.0, 1.1 and 1.2 cards are checked')],
                'warnings': [], 'external': [], 'comparable': [], 'not_comparable': [], 'completeness': None}
    ids = identifiers(card, errors)
    domains = {zone: layers(card, zone).get('profile', {}).get('domain') for zone in ZONES}
    if domains['author'] is not None and domains['author'] != domains['added']:
        errors.append(issue('REF_DOMAIN_MISMATCH', 'profile.domain',
                            'author and added zones select different domain profiles'))
    check_references(card, ids, errors, external)
    check_sources(card, errors)
    check_atom_links(card, errors)
    check_independence(card, errors)
    check_generation(card, errors)
    for zone in ZONES:
        for prediction in layers(card, zone).get('predictions', []):
            merged = fields.setdefault(unwrap(prediction.get('id')), {})
            merged.update({key: unwrap(value) for key, value in prediction.items()
                           if filled(unwrap(value))})
    check_integrity(card, errors, warnings)
    check_times(card, errors)
    check_quotes(card, errors, warnings)
    check_proximity(card, errors, warnings, taxa)
    check_predicates(card, errors)
    check_atom_scope(card, warnings)
    for ident, prediction in fields.items():
        missing = [key for key in COMPARABLE if key not in prediction]
        if prediction.get('form') == 'directional_contrast' and 'direction' not in prediction:
            missing.append('direction')
        if missing:
            not_comparable.append({'id': ident, 'missing': missing})
        else:
            comparable.append(ident)
    completeness = check_completeness.check(card, comparable, not_comparable, errors, warnings)
    return {'valid': not errors, 'errors': errors, 'warnings': warnings, 'external': external,
            'comparable': comparable, 'not_comparable': not_comparable, 'completeness': completeness}


def check_integrity(card, errors, warnings):
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
    verification = card['added']['source_verification']
    stored = card.get('author', {}).get('source', {}).get('source_text_sha256')
    if verification['status'] == 'refetched_match' and verification['sha256'] != stored:
        errors.append(issue('REF_SOURCE_MISMATCH', 'added.source_verification.sha256',
                            'refetched_match needs the refetched bytes to have the stored source hash'))
    if verification['status'] == 'refetched_mismatch' and verification['sha256'] == stored:
        errors.append(issue('REF_SOURCE_MISMATCH', 'added.source_verification.sha256',
                            'refetched_mismatch needs refetched bytes that differ from the stored source'))
    by = card['added']['by']
    sources = card['added'].get('sources') or {}
    classes = checks_classes(card)
    seen, resolved = set(), set()
    for i, record in enumerate(card['added'].get('integrity', {}).get('entailment', [])):
        path = f'added.integrity.entailment[{i}]'
        key = (record['pointer'], record['basis'])
        if key in seen:
            errors.append(issue('REF_DUPLICATE_ID', path, 'One entailment record per pointer and basis'))
        seen.add(key)
        checker = record['checker']
        own = checker.get('tool_sha256') if checker.get('kind') == 'tool' else checker.get('prompt_sha256')
        if checker['name'] == by['converter'] or own == by['converter_hash']:
            errors.append(issue('REF_CHECKER_NOT_INDEPENDENT', path,
                                'The entailment checker must not be the pass that wrote the added zone'))
        try:
            node = resolve_pointer(card, record['pointer'])
        except KeyError:
            errors.append(issue('REF_UNRESOLVED', path, f"Card pointer does not resolve: {record['pointer']}"))
            continue
        if classes:
            how = check_class(card, record['pointer'])
            wanted = 'resolution' if record['basis'] == 'resolution' else 'passage'
            if how != wanted:
                errors.append(issue('REF_BASIS_KIND', path, f"A record with basis {record['basis']!r} names a value "
                                    + (CHECKED[how] if how else 'that is checked member by member')))
                continue
            if wanted == 'resolution':
                resolved.add(record['pointer'])
                check_resolution(card, record, node, path, sources, errors)
                assessment_order(card, record, path, errors)
                continue
            parent = record['pointer'].rsplit('/', 2)
            if not (isinstance(node, dict) and 'src' in node) and parent[1:2] == ['value']:
                node = {'value': node, 'src': unwrap_src(card, parent[0])}
        element = isinstance(node, dict) and 'src' in node and any(
            _under(record['pointer'], pattern) for pattern in ELEMENT_SOURCED)
        if not (isinstance(node, dict) and node.get('src') and 'value' in node or element):
            errors.append(issue('REF_WRONG_TARGET', path, 'An entailment record names a sourced added-zone value'))
            continue
        if record['basis'] == 'basis_quote' and 'basis_quote' not in node:
            errors.append(issue('REF_WRONG_TARGET', path, 'The value has no basis_quote to check'))
        checked = moment(record['checked_at'])
        accessed = moment((sources.get(node['src']) or {}).get('accessed_at'))
        if checked and accessed and checked < accessed:
            errors.append(issue('REF_TIME_ORDER', path,
                                f"checked_at is earlier than the access time of source record {node['src']!r}"))
        assessment_order(card, record, path, errors)
    if classes:
        for pointer in resolution_values(card):
            if pointer not in resolved:
                warnings.append(issue('REF_NOT_RESOLVED', pointer, 'The value is checked against an external record, '
                                      'and no record of that check is in the card'))


# OHF 1.2: what each check class means, for messages.
CHECKED = {'passage': 'checked against its passage, so its record has basis src or basis_quote',
           'resolution': 'checked against an external record, so its record has basis resolution',
           'card': 'checked against the card by tools/check_refs.py, so no record is written for it'}


def unwrap_src(card, pointer):
    """The src of the source wrapper at `pointer`, or None."""
    try:
        node = resolve_pointer(card, pointer)
    except KeyError:
        return None
    return node.get('src') if isinstance(node, dict) else None


def resolution_key(card, pointer, node):
    """The identifier a resolution of the value at `pointer` looks up, or None when it names none.
    A taxon id, an independence key and a withheld quote's record are looked up as they stand; a
    rung by its line's taxon id; a withheld quote's licence reason by that quote's record."""
    logical = logical_path(card, pointer)
    value = unwrap(node)
    if logical.endswith('.taxon_id'):
        return value
    if logical in ('evidence.lines[].independence_group.key', 'evidence.lines[].quote_withheld.record_ref'):
        return value.get('id') if isinstance(value, dict) else None
    line = pointer.split('/')
    line = resolve_pointer(card, '/'.join(line[:line.index('lines') + 2])) if 'lines' in line else {}
    if logical == 'evidence.lines[].quote_withheld.reason':
        record = (unwrap(line.get('quote_withheld')) or {}).get('record_ref') or {}
        return record.get('id')
    if logical == 'evidence.lines[].human_proximity':
        return unwrap((line.get('system') or {}).get('taxon_id'))
    return None


def assessment_order(card, record, path, errors):
    """A value is checked after it was assessed: checked_at is not earlier than the nearest assessment."""
    checked = moment(record['checked_at'])
    assessed = moment((nearest_assessment(card, record['pointer']) or {}).get('assessed_at'))
    if checked and assessed and checked < assessed:
        errors.append(issue('REF_TIME_ORDER', path, 'checked_at is earlier than the assessment of the value'))


def check_resolution(card, record, node, path, sources, errors):
    """A resolution record names the source record of the response it was checked against, with that
    response's sha256 and the identifier it looked up, which is the one the value names (without case)."""
    against = record['resolved_against']
    source = sources.get(against['source'])
    if source is None:
        errors.append(issue('REF_SOURCE_UNKNOWN', path, f"No source record {against['source']!r} in added.sources"))
        return
    if source.get('sha256') != against['response_sha256']:
        errors.append(issue('REF_RESOLUTION_BINDING', path, f"response_sha256 is not the sha256 of source record "
                            f"{against['source']!r}"))
    wanted = resolution_key(card, record['pointer'], node)
    if wanted is None or str(wanted).casefold() != against['key'].casefold():
        errors.append(issue('REF_RESOLUTION_BINDING', path, f"key {against['key']!r} is not the identifier the value "
                            f"names ({wanted!r})"))
    checked, accessed = moment(record['checked_at']), moment(source.get('accessed_at'))
    if checked and accessed and checked < accessed:
        errors.append(issue('REF_TIME_ORDER', path,
                            f"checked_at is earlier than the access time of source record {against['source']!r}"))


def resolution_values(card):
    """Pointers of the filled added-zone values that are checked against an external record."""
    out = []

    def walk(node, pointer):
        if pointer != '/added/layers':
            how = check_class(card, pointer)
            if how == 'resolution':
                if filled(unwrap(node)):
                    out.append(pointer)
                return
        if isinstance(node, dict):
            for key, value in node.items():
                walk(value, f"{pointer}/{key.replace('~', '~0').replace('/', '~1')}")
        elif isinstance(node, list):
            for i, value in enumerate(node):
                walk(value, f'{pointer}/{i}')
    walk(card['added']['layers'], '/added/layers')
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('cards', type=Path, nargs='+')
    parser.add_argument('--taxa', type=Path, help='further taxon rows for human_proximity, such as taxa.json')
    args = parser.parse_args()
    taxa = load(args.taxa)['taxa'] if args.taxa else None
    failed = False
    for path in args.cards:
        result = check(load(path), taxa)
        print(json.dumps({'card': str(path), **result}, ensure_ascii=False))
        failed |= not result['valid']
    return int(failed)


if __name__ == '__main__':
    raise SystemExit(main())
