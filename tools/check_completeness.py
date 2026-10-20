"""Compute the completeness level of an OHF card from the conditions of each level.

The conditions are those of the specification, section Completeness:

- accepted: `added.source_verification.status` is `refetched_match` with the stored
  hash; `author.source` gives a citation, a URL and the SHA-256 of the source text;
  it gives a licence and its basis; and the provenance of the record is present:
  `author.generator`, `added.by` and `added.produced_by`.
- comparable: accepted, and at least one comparable prediction.
- full: comparable, and a typed mechanism step (a step with `subject_ref`,
  `relation` and `object_ref`, across both zones), claim atoms and evidence on both
  sides. Evidence is on both sides when a line supports and a line disputes.
  Without a disputing line, the search for one is recorded by `added.challenge_search`
  with the outcome `not_found` and its query identifiers; OHF 1.0 has no gap path
  for a missing disputing line, so no gap stands for that search.
  `added.challenge_search` is optional; when it is recorded with the outcome `found`,
  it names a disputing line.

The level is computed from the card's own records; the tools fetch nothing. The
condition on source bytes relies on the source verification the card records
(`added.source_verification`), which these tools do not repeat: they neither refetch
the source nor compare the author-zone values with it.

Each condition is met, unmet or for manual review. A source that was not refetched,
or whose refetched bytes differ, cannot show by machine that the author's assertion
was checked against the source bytes; nor can a search that stopped early show that
no disputing evidence exists. The computed level is the highest level whose
conditions, and those of every lower level, are all met.

A declared level above the levels that manual review could still confirm is an
error; a declared level below the computed level is a warning. `missing_for_next`
is derived for the level after the declared one, or after the highest level that
manual review could confirm when the declared level is overstated. Each derived
condition must be named by an item of the declared `missing_for_next`: an item
names a condition when it contains the condition's key, ignoring case; the match is
by substring, so an item that uses a different word (for example "license") does not
name the condition, and any item that mentions a key names it. An item
that names no unmet or manual-review condition up to that level is extra. A
missing or extra item is a warning. The keys are the first member of each entry
of `CONDITIONS`.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from check_gaps import filled, unwrap  # noqa: E402

LEVELS = ('accepted', 'comparable', 'full')
ZONES = ('author', 'added')
CONDITIONS = {
    'accepted': [
        ('source bytes', 'The author assertions are checked against the source bytes.'),
        ('source record', 'A source record: author.source with citation, URL and source text SHA-256.'),
        ('licence', 'A licence: author.source.license and rights_basis.'),
        ('provenance', 'Provenance: author.generator, added.by and added.produced_by.'),
    ],
    'comparable': [
        ('comparable prediction', 'A comparable prediction: system, endpoint, form and epistemic status, '
                                  'and a direction for a directional contrast.'),
    ],
    'full': [
        ('typed mechanism step', 'A typed mechanism step: subject_ref, relation and object_ref.'),
        ('claim atom', 'Claim atoms in core.atoms[].'),
        ('both sides', 'Evidence on both sides: a supporting and a disputing evidence line, '
                       'or a recorded search for disputing evidence.'),
        ('challenge search', 'A challenge search with the outcome found names a disputing evidence line.'),
    ],
}


def issue(code, path, message):
    return {'code': code, 'path': path, 'message': message}


def layers(card, zone):
    return card.get(zone, {}).get('layers', {})


def source_bytes(card):
    verification = card.get('added', {}).get('source_verification', {})
    status = verification.get('status')
    stored = card.get('author', {}).get('source', {}).get('source_text_sha256')
    if status == 'refetched_match':
        if verification.get('sha256') == stored:
            return 'met', 'added.source_verification records a refetch whose hash matches author.source.source_text_sha256.'
        return 'unmet', 'added.source_verification records refetched_match, but its hash differs from the stored one.'
    if status == 'refetched_mismatch':
        return 'manual', 'The refetched source differs from the stored one; a reviewer must check the assertions.'
    if status == 'not_refetchable':
        return 'manual', f"The source was not refetched: {verification.get('reason', 'no reason given')}"
    return 'unmet', 'added.source_verification has no status.'


def present(record, keys, name):
    missing = [key for key in keys if not filled((record or {}).get(key))]
    if missing:
        return 'unmet', f'{name} lacks {", ".join(missing)}.'
    return 'met', f'{name} is present.'


def provenance(card):
    added = card.get('added', {})
    missing = [name for name, value in (('author.generator', card.get('author', {}).get('generator')),
                                        ('added.by', added.get('by')),
                                        ('added.produced_by', added.get('produced_by'))) if not filled(value)]
    if missing:
        return 'unmet', f'Missing {", ".join(missing)}.'
    return 'met', 'author.generator, added.by and added.produced_by are present.'


def comparable_prediction(comparable, not_comparable):
    if comparable:
        return 'met', f'Comparable: {", ".join(map(str, comparable))}.'
    if not_comparable:
        return 'unmet', 'No prediction is comparable: ' + '; '.join(
            f"{entry['id']} lacks {', '.join(entry['missing'])}" for entry in not_comparable) + '.'
    return 'unmet', 'The card has no prediction.'


def typed_step(card):
    merged = {}
    for zone in ZONES:
        for i, step in enumerate(unwrap(layers(card, zone).get('mechanism', {}).get('steps')) or []):
            if not isinstance(step, dict):
                continue
            key = unwrap(step.get('id'))
            record = merged.setdefault(key if isinstance(key, str) else (zone, i), {})
            record.update({name: value for name, value in step.items() if filled(unwrap(value))})
    if any(all(name in step for name in ('subject_ref', 'relation', 'object_ref')) for step in merged.values()):
        return 'met', 'A mechanism step has a subject, a relation and an object.'
    if merged:
        return 'unmet', 'No mechanism step has all of subject_ref, relation and object_ref.'
    return 'unmet', 'The card has no mechanism step.'


def claim_atoms(card):
    if any(unwrap(layers(card, zone).get('core', {}).get('atoms')) for zone in ZONES):
        return 'met', 'The card has claim atoms.'
    return 'unmet', 'The card has no claim atoms.'


def evidence_lines(card):
    """Yield (card pointer, direction) for every evidence line of both zones."""
    for zone in ZONES:
        for i, line in enumerate(unwrap(layers(card, zone).get('evidence', {}).get('lines')) or []):
            if isinstance(line, dict):
                yield f'/{zone}/layers/evidence/lines/{i}', unwrap(line.get('direction'))


def both_sides(card):
    directions = {direction for _, direction in evidence_lines(card)}
    search = card.get('added', {}).get('challenge_search') or {}
    if 'supports' not in directions:
        return 'unmet', 'No evidence line supports the hypothesis.'
    if 'disputes' in directions:
        return 'met', 'Evidence lines support and dispute the hypothesis.'
    if search.get('outcome') == 'not_found' and search.get('query_ids'):
        return 'met', 'No line disputes the hypothesis, and added.challenge_search records the search with its queries.'
    if search.get('outcome') == 'incomplete':
        return 'manual', 'No line disputes the hypothesis, and the recorded search stopped before it was complete.'
    return 'unmet', 'No line disputes the hypothesis, and added.challenge_search records no completed search for one.'


def challenge_search(card):
    search = card.get('added', {}).get('challenge_search')
    if not search:
        return 'met', 'No challenge search is recorded; it is optional.'
    if search.get('outcome') == 'found':
        disputing = {pointer for pointer, direction in evidence_lines(card) if direction == 'disputes'}
        if not any(ref.get('pointer') in disputing for ref in search.get('evidence_refs', [])):
            return 'unmet', 'The challenge search found evidence but names no disputing evidence line.'
    return 'met', f"The challenge search is recorded with the outcome {search.get('outcome')}."


def evaluate(card, comparable, not_comparable):
    """Return {level: [(key, text, status, reason)]} for the conditions of each level."""
    source = card.get('author', {}).get('source')
    results = {
        'source bytes': source_bytes(card),
        'source record': present(source, ('citation', 'url', 'source_text_sha256'), 'author.source'),
        'licence': present(source, ('license', 'rights_basis'), 'author.source'),
        'provenance': provenance(card),
        'comparable prediction': comparable_prediction(comparable, not_comparable),
        'typed mechanism step': typed_step(card),
        'claim atom': claim_atoms(card),
        'both sides': both_sides(card),
        'challenge search': challenge_search(card),
    }
    return {level: [(key, text, *results[key]) for key, text in CONDITIONS[level]] for level in LEVELS}


def highest(conditions, allowed):
    """Index of the highest level whose conditions, and those of lower levels, all have an allowed status."""
    reached = -1
    for index, level in enumerate(LEVELS):
        if not all(status in allowed for _, _, status, _ in conditions[level]):
            break
        reached = index
    return reached


def check(card, comparable, not_comparable, errors, warnings):
    """Compare the declared completeness with the computed one; return the completeness report."""
    declared_record = card.get('added', {}).get('completeness', {})
    declared = LEVELS.index(declared_record['level']) if declared_record.get('level') in LEVELS else -1
    conditions = evaluate(card, comparable, not_comparable)
    computed = highest(conditions, {'met'})
    attainable = highest(conditions, {'met', 'manual'})

    def entries(statuses, top):
        return [{'level': level, 'condition': text, 'reason': reason}
                for level in LEVELS[:top + 1] for _, text, status, reason in conditions[level]
                if status in statuses]

    if declared > attainable:
        unmet = entries({'unmet'}, declared)
        errors.append(issue('REF_COMPLETENESS_OVERSTATED', 'added.completeness.level',
                            f"Declared {LEVELS[declared]}, but: " + ' '.join(e['reason'] for e in unmet)))
    elif declared < computed:
        warnings.append(issue('REF_COMPLETENESS_UNDERSTATED', 'added.completeness.level',
                              f'Declared {LEVELS[declared]}, but the conditions of {LEVELS[computed]} are met'))
    base = min(declared, attainable)
    following = base + 1
    derived = [] if following >= len(LEVELS) else [
        (key, text) for key, text, status, _ in conditions[LEVELS[following]] if status == 'unmet']
    named = {key for level in LEVELS[:following + 1] for key, _, status, _ in conditions[level]
             if status != 'met'}
    stated = [item.lower() for item in declared_record.get('missing_for_next', [])]
    for key, text in derived:
        if not any(key in item for item in stated):
            warnings.append(issue('REF_MISSING_FOR_NEXT', 'added.completeness.missing_for_next',
                                  f'The next level still needs, and missing_for_next does not name: {text}'))
    for item in declared_record.get('missing_for_next', []):
        if not any(key in item.lower() for key in named):
            warnings.append(issue('REF_MISSING_FOR_NEXT', 'added.completeness.missing_for_next',
                                  f'The item names no condition the next level still needs: {item}'))
    return {
        'declared': LEVELS[declared] if declared >= 0 else None,
        'computed': LEVELS[computed] if computed >= 0 else None,
        'unmet': entries({'unmet'}, len(LEVELS) - 1),
        'manual_review_required': entries({'manual'}, len(LEVELS) - 1),
        'missing_for_next': [text for _, text in derived],
    }
