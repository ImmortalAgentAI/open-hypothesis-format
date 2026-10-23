"""Upgrade the accepted peto card (content_hash 721bbc8f…) to an OHF 1.1 example card.

Usage: upgrade.py INPUT_DIR OUT_CARD AT CONVERTER_HASH. INPUT_DIR holds the base card, the values tool's
output (biodb.py) and its search log, and the Europe PMC records of the independence keys. Every wording
the upgrade adds is a verbatim substring of the line's quote, study_type or study_system; the script asserts
it. The rules are in UPGRADE.md next to this file.
"""
import copy, hashlib, json, re, sys
from pathlib import Path

OHF = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(OHF))
from tools.check_refs import RESULT_NUMBER  # noqa: E402
from tools.content_hash import content_hash  # noqa: E402

INPUT, OUT_CARD, AT, CONVERTER_HASH = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3], sys.argv[4]
card = json.loads((INPUT / 'peto-paradox-mammals.json').read_text())
assert card['content_hash'] == 'sha256:721bbc8f5e8979b4453d71b7f7cbd479c7ef990aea740480b8f7c6114e21769c'
# The values were made for the version before the base's revision of wording (b0437424…). That revision
# changed prose only: everything the values and this upgrade read is identical in both.
previous = json.loads((INPUT / 'peto-paradox-mammals-b0437424.json').read_text())
assert previous['content_hash'] == 'sha256:b04374244b572b21b624e0db366a2d50a542a6d63f9f567f323ab16d4de81744'
for path in (('layers', 'evidence', 'lines'), ('layers', 'core', 'atoms'), ('layers', 'core', 'alternative_explanations'),
             ('integrity',), ('sources',)):
    a, b = previous['added'], card['added']
    for key in path:
        a, b = a[key], b[key]
    assert a == b, path
values = json.loads((INPUT / 'peto-1.1-values.json').read_text())
assert values['card']['content_hash'] == previous['content_hash']
log = {json.loads(l)['call_id']: json.loads(l) for l in (INPUT / 'search-log.jsonl').read_text().splitlines() if l}


def pin(name):
    return 'sha256:' + hashlib.sha256((OHF / 'vocabularies' / name).read_bytes()).hexdigest()


card['standard_version'] = '1.1'
card['vocabularies']['terms'] = {'id': 'ohf:terms@1', 'sha256': pin('terms-1.json')}
added = card['added']
L = added['layers']
sources = added['sources']


def call_source(call_id, kind):
    """A sources entry for one call of the values tool, keyed by the call id."""
    key = f'biodb_{call_id}'
    entry = log[call_id]
    sources.setdefault(key, {
        'source': entry['responses'][-1]['url'] if entry.get('responses') else entry['ask'].get('source', ''),
        'locator': f"{kind}: {entry['ask'].get('id')}",
        'accessed_at': entry['finished_at'],
        'tool': f"values tool biodb.py (commit {values['kit']['commit']}), call {call_id}"})
    return key


# Endpoint of each line: (verbatim wording, term). Lines left out state no single endpoint.
ENDPOINTS = {
    'e_body_mass': ('cancer mortality risk', 'mortality'),
    'e_life_expectancy': ('cancer mortality risk', 'mortality'),
    'e_mammal_prey': ('cancer mortality risk', 'mortality'),
    'e_animal_diet_null': ('cancer mortality risk', 'mortality'),
    'e_biomagnification_null': ('cancer mortality risk', 'mortality'),
    'e_frequency': ('CMR', 'mortality'),
    'e_phylogenetic_signal': ('cancer mortality risk', 'mortality'),
    'e_artiodactyla_large': ('cancer mortality risk', 'mortality'),
    'e_sex_bias_null': ('sex-specific cancer mortality risk', 'mortality'),
    'e_detection_sampling': ('the probability of detecting cancer', 'disease'),
    'e_two_zero_species': ('no cancer was detected', 'disease'),
    'e_ruminants': ('cancer mortality risk', 'mortality'),
    'e_burden': ('dying of cancer-related pathologies', 'mortality'),
    'e_within_species': ('develop cancer', 'disease'),
    'e_viral_fraction_humans': ('cancers are of viral origin', 'disease'),
    'e_butler_size': ('prevalence of malignancy', 'disease'),
    'e_butler_longevity': ('malignancy', 'disease'),
    'e_butler_rate': ('neoplasia and malignancy', 'disease'),
    'e_compton_prior': ('neoplasms and cancers', 'disease'),
    'e_compton_rate_null': ('malignancy or benign tumor prevalence', 'disease'),
    'e_dujon_reanalysis': ('cancer mortality incidence', 'mortality'),
    'e_dujon_longevity': ('cancer mortality', 'mortality'),
    'e_dujon_diet': ('cancer risk', 'disease'),
    'e_mutation_rate': ('somatic mutation rate', 'molecular'),
}
MARKER = {'biomarker', 'physiological', 'molecular'}
CLINICAL = {'lifespan', 'mortality', 'function', 'disease', 'adverse_event'}
# A result the quote reports, word for word, with what the quote says of it.
ESTIMATES = {
    'e_body_mass': {'reported': 'a 2.8–2.9% decrease in cancer risk for a doubling of the body weight',
                    'measure': 'decrease in cancer risk', 'contrast': 'a doubling of the body weight',
                    'scale': 'not_stated'},
    'e_life_expectancy': {'reported': 'a 24.7–25.2% increase in cancer risk for a doubling of the adult life expectancy',
                          'measure': 'increase in cancer risk', 'contrast': 'a doubling of the adult life expectancy',
                          'scale': 'not_stated'},
    'e_frequency': {'reported': 'ranging from 0% (in 47 species out of 191) to 57.14% in the kowari (Dasyuroides byrnei)',
                    'measure': 'CMR', 'contrast': 'not_stated', 'scale': 'not_stated'},
    'e_phylogenetic_signal': {'reported': 'CMR: n = 191, λ = 0.87, P < 0.0001; ICM: n = 172, λ = 0.69, P < 0.0001',
                              'measure': 'phylogenetic signal', 'contrast': 'not_stated', 'scale': 'not_stated'},
    'e_sex_bias_null': {'reported': 'CMR: t = 0.52, df = 33, P = 0.6061; ICM: t = −0.6815, df = 27, P = 0.5014',
                        'measure': 'phylogenetic paired t-tests', 'contrast': 'Pairwise comparison between sexes',
                        'scale': 'not_stated'},
    'e_burden': {'reported': 'In some species more than 20–40% of the managed adult population die of cancer-related '
                             'pathologies',
                 'measure': 'not_stated', 'contrast': 'not_stated', 'scale': 'not_stated'},
    'e_viral_fraction_humans': {'reported': 'in humans it was estimated that 10–20% of all cancers are of viral origin',
                                'measure': 'not_stated', 'contrast': 'not_stated', 'scale': 'not_stated'},
}
# The number of species a line's result rests on, where the quote states it.
SAMPLE_SIZES = {'e_frequency': ('191', 191), 'e_mutation_rate': ('16 mammalian species', 16)}

by_line = {v['id']: v for v in values['lines']}
lines = L['evidence']['lines']
assert [l['id'] for l in lines] == [v['id'] for v in values['lines']]
for i, line in enumerate(lines):
    v = by_line[line['id']]
    assert v['pointer'] == f'/added/layers/evidence/lines/{i}'
    src = line['src']
    text = line['quote'] + ' ' + line['study_type']['value']
    calls = v.get('call_id') or []
    calls = calls if isinstance(calls, list) else [calls]
    taxon_src = call_source(calls[0], 'NCBI Taxonomy') if calls else None
    if v.get('words'):
        assert v['words'] in line['study_system']['value']
        system = {'taxon': {'value': v['words'], 'src': line['study_system']['src']}}
        if v.get('taxon_id'):
            system['taxon_id'] = {'value': v['taxon_id'], 'src': taxon_src}
        line['system'] = system
    if line['id'] in ENDPOINTS:
        wording, term = ENDPOINTS[line['id']]
        assert wording in text, (line['id'], wording)
        line['endpoint_kind'] = {'value': wording, 'src': src, 'term': term}
    rung = v.get('human_proximity')
    if v.get('rung') == 'human' and line['id'] in ENDPOINTS:
        term = ENDPOINTS[line['id']][1]
        rung = 'human_marker' if term in MARKER else 'human_clinical' if term in CLINICAL else None
    if rung:
        line['human_proximity'] = {'value': rung, 'src': taxon_src}
    if line['id'] in SAMPLE_SIZES:
        wording, size = SAMPLE_SIZES[line['id']]
        assert wording in line['quote'], (line['id'], wording)
        line['sample_size'] = {'value': size, 'src': src}
    if line['id'] in ESTIMATES:
        assert ESTIMATES[line['id']]['reported'] in line['quote'], line['id']
        line['result_estimate'] = {'value': ESTIMATES[line['id']], 'src': src}
    assert ('result_estimate' in line) == bool(RESULT_NUMBER.search(line['quote'])), line['id']

# OHF 1.1 asks for an estimate wherever a quote reports a result in numbers; the lines with one leave the
# whole-list gap, and the others keep it one by one with the reason that fits them.
whole = next(g for g in added['gaps'] if g['path'] == 'evidence.lines[].result_estimate')
added['gaps'].remove(whole)
for i, line in enumerate(lines):
    if 'result_estimate' not in line:
        added['gaps'].append({**copy.deepcopy(whole), 'path': f'evidence.lines[{i}].result_estimate',
                              'reason': 'The passage states the result in words, with no figure to record.'})

# Independence keys: where the data of a group first appeared, for the groups whose label names one work
# that holds its own data. The Europe PMC record of each DOI is an input.
KEYS = {'g_zims_vincze2022': '10.1038/s41586-021-04224-5', 'g_sulak2016': '10.7554/eLife.11994',
        'g_cagan2022': '10.1038/s41586-022-04618-z'}
for doi in KEYS.values():
    record = json.loads((INPUT / 'europepmc' / (doi.replace('/', '_') + '.json')).read_text())
    assert [r['doi'].lower() for r in record['resultList']['result']] == [doi.lower()], doi
for line in lines:
    group = line.get('independence_group')
    if isinstance(group, dict) and group.get('value') in KEYS:
        group['key'] = {'scheme': 'doi', 'id': KEYS[group['value']]}

# Atoms: the chain the card's own statements give (category: consistency with the card's atoms).
atoms_by_id = {a['id']: a for a in L['core']['atoms']}
assert 'consuming other mammals' in atoms_by_id['a_pathogen']['statement']['value']
assert atoms_by_id['a_coevolution']['statement']['value'].startswith('The results suggest')
REQUIRES = {'a_pathogen': ['a_diet'], 'a_coevolution': ['a_body_mass', 'a_life_expectancy']}
for ident, required in REQUIRES.items():
    atoms_by_id[ident]['requires'] = {'value': required, 'src': atoms_by_id[ident]['statement']['src']}

# Alternatives get identifiers, so lines and excluded records can name them.
ALTERNATIVES = ('alt_biomagnification', 'alt_microbiome', 'alt_captivity_physiology', 'alt_housed_diet_bias',
                'alt_fat_fibre_diet')
alternatives = L['core']['alternative_explanations']['value']
assert len(alternatives) == len(ALTERNATIVES)
for alt, ident in zip(alternatives, ALTERNATIVES):
    alt['id'] = ident

# A base record whose checked content the upgrade changed no longer holds and is dropped: the keyed groups.
# An identifier given to an alternative is not content a paragraph supports, so that record stands.
base = json.loads((INPUT / 'peto-paradox-mammals.json').read_text())  # the base as read, before this upgrade


def resolve(document, pointer):
    node = document
    for token in pointer.split('/')[1:]:
        node = node[int(token)] if isinstance(node, list) else node[token]
    return node


def content(node):
    if isinstance(node, dict):
        return {k: content(v) for k, v in node.items() if k != 'id' or 'claim_or_ref' not in node}
    if isinstance(node, list):
        return [content(v) for v in node]
    return node


kept = [r for r in added['integrity']['entailment']
        if content(resolve(base, r['pointer'])) == content(resolve(card, r['pointer']))]
assert len(added['integrity']['entailment']) - len(kept) == 17
added['integrity']['entailment'] = kept

# Verdicts of the independent entailment check, one file per batch in INPUT/verdicts with its time in a
# sidecar. A verdict is written only for a sourced value; the checker is the base card's.
checker = added['integrity']['entailment'][0]['checker']
# Values changed after their check, to keep the scope the passage gives: the verdict on the earlier value is
# not written.
CHANGED = {'/added/layers/evidence/lines/5/endpoint_kind', '/added/layers/evidence/lines/12/result_estimate',
           '/added/layers/evidence/lines/14/result_estimate'}
for path in sorted((INPUT / 'verdicts').glob('*.json')):
    checked_at = Path(f'{path}.checked_at').read_text().strip()
    for verdict in json.loads(path.read_text()):
        if path.name == 'PETO-1.1-VERDICTS-20261023.json' and verdict['pointer'] in CHANGED:
            continue
        node = card
        for token in verdict['pointer'].split('/')[1:]:
            node = node[int(token)] if isinstance(node, list) else node[token]
        if not (isinstance(node, dict) and 'value' in node and 'src' in node):
            continue
        record = {'pointer': verdict['pointer'], 'basis': verdict['basis'], 'verdict': verdict['verdict'],
                  'checker': dict(checker), 'checked_at': checked_at}
        if verdict.get('note'):
            record['note'] = verdict['note']
        added['integrity']['entailment'].append(record)

# This version's requests: every response of the values tool's calls and the three Europe PMC records.
added['budget']['http_requests'] += sum(len(entry.get('responses') or []) for entry in log.values()) + len(KEYS)

identity = card['identity']
identity['supersedes'] = [f"{identity['proposition_id']}@{card['version']}"]
card['version'] += 1
identity['version'] = card['version']
added['by'] = {'converter': 'ohf-1-1-upgrade-peto', 'converter_version': '1.0.0',
               'converter_hash': CONVERTER_HASH, 'model': 'claude-opus-5-5'}
added['at'] = AT
card['content_hash'] = content_hash(card)
OUT_CARD.write_text(json.dumps(card, indent=2, ensure_ascii=False) + '\n')
print(card['content_hash'], sum('endpoint_kind' in l for l in lines), sum('human_proximity' in l for l in lines),
      sum('result_estimate' in l for l in lines), sum('key' in (l.get('independence_group') or {}) for l in lines))
