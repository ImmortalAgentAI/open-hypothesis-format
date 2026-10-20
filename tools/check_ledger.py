"""Check that a card's entailment records are bound to the text that was checked.

Usage: check_ledger.py CARD LEDGER [WORKDIR]

The card schema allows no extra members in added.integrity.entailment[], so the binding lives
in a ledger file next to the card (examples/ledgers/<slug>.json in the OHF repository,
WORKDIR/entailment-ledger.json during a conversion):

  {"format": "ohf-entailment-ledger/2", "canonicalisation": "...", "card_id": ..., "content_hash": ...,
   "entries": {"<pointer>|<basis>": [{"value_sha256", "passage_sha256", "checked_at", "verdict",
                                      "note_sha256"?}, ...]},
   "notes": {"<note_sha256>": "<note text>"}}

value_sha256 is the SHA-256 of the value exactly as the checker saw it, in canonical JSON
(CANONICALISATION below); passage_sha256 is the SHA-256 of the passage text the checker saw.
Each key holds the whole history of its checks, in time order: entries are only appended.
Format /1 (one entry per key) is read as lists of one.

The active checks of a key are those of the card's current value and passage. The card's
record must show the worst active verdict (no < partial < entails), and on a tie the earliest
such check that is not older than the latest assessment the value carries (else the earliest),
with its time and note. A key whose active checks disagree is DISPUTED: printed
as information, not a failure. A later 'entails' on the same text never hides an earlier 'no'.
Limit: without WORKDIR the passage of a src item is not known, and it is taken to be the passage
of the check the record shows. A check of the same value against another passage (one made
after the src was changed) is then not told apart from a check of the current passage, so a
later 'entails' with another passage hash can stand in for an earlier 'no'. With WORKDIR the
passage is read from the source and only its own checks count.

Without WORKDIR the check needs only the card and the ledger: it rebuilds every checked value
from the card, with the same rules as entailment.build, and fails on a missing or mismatched
entry, a record that shows a better verdict than the worst active check or that no active check
backs, a sourced value with no record, and a ledger made for another card or another
content_hash. The passage of a basis_quote item is the quotation in the card, so its hash is
checked too. The passage of a src item is a paragraph of a source document: with WORKDIR, those
passages are read from the downloaded sources (this needs the ohf-extractor readers next to
this file) and their hashes are checked as well. Without WORKDIR, passage binding of src items
is not checked, and the passage is taken to be the one the record's own check names; the
SHA-256 of each source document is in the card.

Runs on the standard library plus tools/content_hash.py of the OHF repository.
Exit 0 only when every check passes.
"""
import hashlib
import json
import os
import re
import sys
from pathlib import Path

FORMAT = 'ohf-entailment-ledger/2'
FORMATS = ('ohf-entailment-ledger/1', FORMAT)  # /1 is read as lists of one
CANONICALISATION = ('value_sha256: SHA-256 of the UTF-8 bytes of json.dumps(value, ensure_ascii=False, '
                    "sort_keys=True, separators=(',', ':')), value as given to the checker; "
                    'passage_sha256: SHA-256 of the UTF-8 bytes of the passage text as given to the checker; '
                    'note_sha256: SHA-256 of the UTF-8 bytes of the note; '
                    'all written "sha256:<hex>"; entries keyed "<pointer>|<basis>", each a list of checks in time order')
LEDGER_NAME = 'entailment-ledger.json'

# ------------------------------------------------------------------ the item-building rules
# entailment.py imports these, so the checker input and this check cannot drift apart.

# Fields recorded from article metadata, and evidence lines checked by exact quotation.
SKIP_PREFIXES = ('/added/layers/provenance/',)
LINE_FIELDS = ('direction', 'study_type', 'study_system')
LINE_FIELD = re.compile(r'^/added/layers/evidence/lines/(\d+)/(direction|study_type|study_system|indirectness)$')
# Judged against the target: "supports" needs an object. Indirectness is sent alone: with
# the target added, the checker read the target as a claim the passage must support.
WITH_TARGET = ('direction',)


def skip(pointer, node):
    if pointer.startswith(SKIP_PREFIXES) or pointer == '/added/layers/core/first_proposed':
        return True
    return 'value' not in node  # an evidence line object: its fields are checked one by one


def target_statement(card, line):
    """What the line bears on: an atom's statement, or a prediction's population,
    endpoint and direction."""
    layers = card['added']['layers']
    ref = line.get('target_ref')
    val = lambda n: n.get('value') if isinstance(n, dict) else n  # noqa: E731
    for a in layers['core'].get('atoms', []):
        if a['id'] == ref:
            return val(a.get('statement'))
    for pr in layers.get('predictions', []):
        if pr['id'] == ref:
            return {k: val(pr[k]) for k in ('population', 'endpoint', 'direction') if k in pr}
    raise ValueError(f'evidence line {line.get("id")}: target_ref {ref!r} is neither an atom nor a prediction')


def checked_value(card, pointer, node):
    """The value the checker judges. An evidence line's direction is given with what its
    target states, so that "supports" has an object."""
    m = LINE_FIELD.match(pointer)
    if m and m.group(2) in WITH_TARGET:
        line = card['added']['layers']['evidence']['lines'][int(m.group(1))]
        return {'direction': node['value'], 'target_statement': target_statement(card, line)}
    return node.get('value')


def sourced(card):
    """(pointer, node) of every added value that names a src and goes to the checker."""
    out = []

    def walk(o, p):
        if isinstance(o, dict):
            if 'src' in o and not skip(p, o):
                out.append((p, o))
            for k, v in o.items():
                walk(v, f'{p}/{k}')
        elif isinstance(o, list):
            for i, v in enumerate(o):
                walk(v, f'{p}/{i}')
    walk(card['added']['layers'], '/added/layers')
    return out


def value_items(card):
    """The checker items without their src passages: dicts with pointer, basis, value, and
    either 'src' (the passage is a paragraph of a source) or 'source_passage' (a basis_quote)."""
    items = []
    for p, node in sourced(card):
        value = checked_value(card, p, node)
        items.append({'pointer': p, 'basis': 'src', 'value': value, 'src': node['src']})
        if 'basis_quote' in node:
            items.append({'pointer': p, 'basis': 'basis_quote', 'value': value, 'source_passage': node['basis_quote']})
    return items


# ------------------------------------------------------------------ hashes and the ledger

def _sha(data):
    return 'sha256:' + hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')


def value_sha256(value):
    return _sha(canonical(value))


def passage_sha256(passage):
    return _sha(passage.encode('utf-8'))


def note_sha256(note):
    return _sha(note.encode('utf-8'))


def key_of(x):
    return f"{x['pointer']}|{x['basis']}"


# Worst first: a record shows the worst verdict among the checks of the same text.
RANK = {'no': 0, 'partial': 1, 'entails': 2}


def entry(item, record):
    """The ledger entry for a checker item (with its source_passage) and its record."""
    e = {'value_sha256': value_sha256(item['value']), 'passage_sha256': passage_sha256(item['source_passage']),
         'checked_at': record['checked_at'], 'verdict': record['verdict']}
    if record.get('note'):
        e['note_sha256'] = note_sha256(record['note'])
    return e


def new_ledger(card, entries=None, notes=None):
    return {'format': FORMAT, 'canonicalisation': CANONICALISATION, 'card_id': card['id'],
            'content_hash': card.get('content_hash'), 'entries': entries or {}, 'notes': notes or {}}


def upgrade(ledger):
    """A ledger in format /2: format /1 entries become lists of one. None stays None."""
    if ledger is None or ledger.get('format') not in FORMATS:
        return ledger
    out = dict(ledger)
    entries = ledger.get('entries') or {}
    out['entries'] = {k: (list(v) if isinstance(v, list) else [v]) for k, v in entries.items()}
    out['notes'] = dict(ledger.get('notes') or {})
    out['format'] = FORMAT
    out['canonicalisation'] = CANONICALISATION
    return out


def add_entry(ledger, key, e, note=None):
    """Append a check to the history of `key`, in time order, unless an identical entry is
    there. No entry is ever removed or rewritten. Returns True when it was added."""
    history = ledger['entries'].setdefault(key, [])
    if note:
        ledger['notes'][note_sha256(note)] = note
    if e in history:
        return False
    history.append(e)
    history.sort(key=lambda x: x['checked_at'])  # stable: equal times keep their order
    return True


def active(history, value_sha, passage_sha=None):
    """The checks of the value as it now stands (and of its passage, when that is known)."""
    return [e for e in history if e['value_sha256'] == value_sha
            and (passage_sha is None or e['passage_sha256'] == passage_sha)]


def choose(entries, not_before=None):
    """The check a record shows: the worst verdict; on a tie, the earliest check of that
    verdict that is not older than `not_before` (the latest assessment the value carries),
    else the earliest. The tie-break never changes the verdict shown; it keeps a record from
    predating its assessment when a later check of the same verdict exists."""
    if not entries:
        return None
    worst = min(RANK[e['verdict']] for e in entries)
    tied = sorted((e for e in entries if RANK[e['verdict']] == worst), key=lambda e: e['checked_at'])
    if not_before:
        later = [e for e in tied if e['checked_at'] >= not_before]
        if later:
            return later[0]
    return tied[0]


def latest_assessment(node):
    """The latest assessed_at inside a value node, or None."""
    times = []

    def walk(o):
        if isinstance(o, dict):
            if isinstance(o.get('assessed_at'), str):
                times.append(o['assessed_at'])
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(node)
    return max(times) if times else None


def unknown_verdicts(ledger):
    """Keys with an entry whose verdict is not one of RANK."""
    return {k for k, history in ledger['entries'].items() for e in history if e.get('verdict') not in RANK}


def disputed(entries):
    return len({e['verdict'] for e in entries}) > 1


def _kit_repo(here):
    """ohfkit.REPO when this file sits in the ohf-extractor scripts/, else None."""
    if not (here / 'ohfkit.py').exists():
        return None
    if str(here) not in sys.path:
        sys.path.insert(0, str(here))
    import ohfkit
    return ohfkit.REPO


def _content_hash():
    """tools/content_hash.content_hash of the OHF repository: found next to this file when it
    sits in the repository's tools/, else through OHF_REPO, else the repository the kit names."""
    here = Path(__file__).resolve().parent
    for root in (here.parent, os.environ.get('OHF_REPO'), _kit_repo(here)):
        if root and (Path(root) / 'tools' / 'content_hash.py').exists():
            if str(root) not in sys.path:
                sys.path.insert(0, str(root))
            from tools.content_hash import content_hash
            return content_hash
    raise RuntimeError('tools/content_hash.py not found: run from the OHF repository or set OHF_REPO')


def _active_for(key, item, record, history, passages):
    """(active entries, error) for a card record. Without the src passage (no WORKDIR), the
    passage is taken to be the one the record's own entry was checked against."""
    vsha = value_sha256(item['value'])
    by_value = active(history, vsha)
    if not by_value:
        return [], (f'{key}: the value differs from the value that was checked (it changed after the '
                    'entailment pass: re-run the pass on it and merge)')
    passage = item.get('source_passage', (passages or {}).get(key))
    if passage is not None:
        act = active(by_value, vsha, passage_sha256(passage))
        if not act:
            return [], (f'{key}: the passage differs from the passage that was checked (src or quotation '
                        'changed after the entailment pass: re-run the pass on it and merge)')
        return act, None
    own = [e for e in by_value if record and e['checked_at'] == record['checked_at']
           and e['verdict'] == record['verdict']]
    return (active(by_value, vsha, own[0]['passage_sha256']) if own else by_value), None


def check(card, ledger, passages=None):
    """Errors, each with how to fix it. `passages` maps "<pointer>|src" to the passage text
    read from the source documents; without it, src passages are not checked."""
    errors = []
    if ledger is None:
        return [f'no entailment ledger (merge writes WORKDIR/{LEDGER_NAME}; re-run the entailment pass '
                'and merge, or carry from the previous card)']
    if ledger.get('format') not in FORMATS:
        return [f'ledger format {ledger.get("format")!r} is not one of {FORMATS} (write it with entailment.py merge)']
    led = upgrade(ledger)
    if led.get('card_id') != card.get('id'):
        errors.append(f'ledger is for card {led.get("card_id")!r}, not {card.get("id")!r} (use the ledger of this card)')
    actual = _content_hash()(card)
    if card.get('content_hash') != actual:
        errors.append(f'card content_hash {card.get("content_hash")} is not its hash {actual} (the card changed '
                      'after it was hashed: rebuild, then carry and merge)')
    elif led.get('content_hash') != actual:
        errors.append(f'ledger content_hash {led.get("content_hash")} is not the card\'s {actual} (the card '
                      'changed after the last merge or carry: carry, re-check what changed, merge)')
    entries, notes = led['entries'], led['notes']
    bad = unknown_verdicts(led)
    for k in sorted(bad):
        errors.append(f'{k}: ledger entry with a verdict not in {sorted(RANK)} (the ledger was not written '
                      'by entailment.py merge: rebuild it from the checker outputs)')
    nodes = dict(sourced(card))
    items = {key_of(x): x for x in value_items(card)}
    records = {key_of(r): r for r in card['added']['integrity']['entailment']}
    for k in items.keys() - records.keys():
        p, b = k.rsplit('|', 1)
        errors.append(f'{p} ({b}): no entailment record (run the entailment pass on it)')
    for k in records.keys() - items.keys():
        p, b = k.rsplit('|', 1)
        errors.append(f'{p} ({b}): record for a value that is not sourced (remove the record)')
    for k, r in records.items():
        history = entries.get(k) or []
        if k in bad:
            continue
        if not history:
            errors.append(f'{k}: entailment record with no ledger entry (its checked text is unknown: '
                          're-run the entailment pass on it and merge)')
            continue
        x = items.get(k)
        if x is None:
            continue
        act, err = _active_for(k, x, r, history, passages)
        if err:
            errors.append(err)
            continue
        worst = choose(act, latest_assessment(nodes[x['pointer']]))
        if RANK.get(r['verdict'], -1) > RANK[worst['verdict']]:
            errors.append(f"{k}: verdict {r['verdict']!r} in the card, {worst['verdict']!r} in the ledger is the "
                          f"worst check of this text, at {worst['checked_at']} (never edit a verdict by hand; "
                          'a later check does not hide an earlier one: entailment.py merge writes the record)')
            continue
        if not any(e['verdict'] == r['verdict'] and e['checked_at'] == r['checked_at'] for e in act):
            errors.append(f"{k}: no ledger entry for this text backs the record ({r['verdict']!r} checked at "
                          f"{r['checked_at']}): the record does not come from a merge of this ledger")
            continue
        if (r['verdict'], r['checked_at']) != (worst['verdict'], worst['checked_at']):
            errors.append(f"{k}: the record shows the check at {r['checked_at']}, but the rule shows the worst "
                          f"verdict, earliest on a tie (not older than its assessment): {worst['verdict']!r} at "
                          f"{worst['checked_at']} (merge or restore writes the record)")
            continue
        if 'note_sha256' in worst:
            if r.get('note') is None or note_sha256(r['note']) != worst['note_sha256']:
                errors.append(f'{k}: the note in the card is not the note of the check it shows (never edit a '
                              'note by hand)')
            elif worst['note_sha256'] not in notes:
                errors.append(f'{k}: the ledger has no text for note {worst["note_sha256"]}')
    return errors


def summary(card, ledger, passages=None):
    """(disputed keys, number of history entries, number of keys only in the history).
    A key is disputed when the checks of its current text disagree; that is information."""
    led = upgrade(ledger)
    if not led or led.get('format') != FORMAT:
        return [], 0, 0
    items = {key_of(x): x for x in value_items(card)}
    records = {key_of(r): r for r in card['added']['integrity']['entailment']}
    nodes = dict(sourced(card))
    out = []
    bad = unknown_verdicts(led)
    for k, history in led['entries'].items():
        if k in items and k not in bad:
            act, err = _active_for(k, items[k], records.get(k), history, passages)
            if not err and disputed(act):
                worst = choose(act, latest_assessment(nodes[items[k]['pointer']]))
                out.append(f"{k}: {', '.join(e['verdict'] + ' ' + e['checked_at'] for e in act)}; shown: "
                           f"{worst['verdict']} {worst['checked_at']}")
    n = sum(len(v) for v in led['entries'].values())
    return sorted(out), n, len(led['entries'].keys() - items.keys())


def source_passages(card, workdir):
    """Passages of the src items, read from the downloaded sources with the ohf-extractor readers."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    try:
        import entailment
    except ImportError as e:
        raise RuntimeError(f'passage binding needs the ohf-extractor readers (entailment.py next to this file): {e}')
    docs = entailment.docs_for(card, workdir)
    return {key_of(x): x['source_passage'] for x in entailment.build(card, docs) if x['basis'] == 'src'}


def load(path):
    path = Path(path)
    return json.loads(path.read_text()) if path.exists() else None


def print_summary(card, ledger, passages=None):
    keys, n, only = summary(card, ledger, passages)
    for line in keys:
        print('DISPUTED', line)
    print(f'LEDGER HISTORY {n} entries, {len(keys)} disputed keys, {only} keys only in the history')


def main(argv):
    if len(argv) not in (2, 3):
        sys.exit(__doc__)
    card = json.loads(Path(argv[0]).read_text())
    ledger = load(argv[1])
    passages = source_passages(card, argv[2]) if len(argv) == 3 else None
    errors = check(card, ledger, passages)
    for e in errors:
        print('FAIL', e)
    if ledger is not None and ledger.get('format') in FORMATS:
        print_summary(card, ledger, passages)
    scope = 'values, verdicts and passages' if passages is not None else 'values and verdicts (src passages not checked)'
    print('LEDGER CHECK', 'FAIL' if errors else 'PASS', len(errors), f'[{scope}]')
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
