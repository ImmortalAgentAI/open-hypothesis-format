"""Upgrade the frozen rapa flagship (content_hash 473ca95e…) to an OHF 1.1 example card.

Usage: upgrade.py INPUT_DIR OUT_CARD AT CONVERTER_HASH. INPUT_DIR holds the base card, arena-biodb's
values and their search log. Every wording the upgrade adds is a verbatim substring of the line's quote,
study_type or study_system; the script asserts it. The rules are in UPGRADE.md next to this file.
"""
import copy, hashlib, json, sys
from pathlib import Path

OHF = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(OHF))
from tools.content_hash import content_hash  # noqa: E402

INPUT, OUT_CARD, AT, CONVERTER_HASH = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3], sys.argv[4]
card = json.loads((INPUT / 'intermittent-rapamycin-mtorc2.json').read_text())
assert card['content_hash'] == 'sha256:473ca95e5dd7ad4efa2ccdc09dac51d25b970542ec9362f741f1076d9f917db5'
values = json.loads((INPUT / 'rapa-1.1-values.json').read_text())
assert values['card']['content_hash'] == card['content_hash']
log = {json.loads(l)['call_id']: json.loads(l) for l in (INPUT / 'search-log.jsonl').read_text().splitlines() if l}


def pin(name):
    return 'sha256:' + hashlib.sha256((OHF / 'vocabularies' / name).read_bytes()).hexdigest()


card['standard_version'] = '1.1'
card['vocabularies'].update(
    profiles={'id': 'ohf:profiles@2', 'sha256': pin('profiles-2.json')},
    terms={'id': 'ohf:terms@1', 'sha256': pin('terms-1.json')},
    hallmarks={'id': 'ohf:hallmarks@1', 'sha256': pin('hallmarks-1.json')})
added = card['added']
L = added['layers']
sources = added['sources']


def call_source(call_id, kind):
    """A sources entry for one arena-biodb call, keyed by the call id."""
    key = f'biodb_{call_id}'
    entry = log[call_id]
    sources.setdefault(key, {
        'source': entry['responses'][-1]['url'] if entry.get('responses') else entry['ask'].get('source', ''),
        'locator': f"{kind}: {entry['ask'].get('id')}",
        'accessed_at': entry['finished_at'],
        'tool': f"arena-biodb biodb.py ({values['kit']['commit']}), call {call_id}"})
    return key


# Endpoint of each line: (verbatim wording, term). Lines left out state no single endpoint.
ENDPOINTS = {
    'e_ac_glucose': ('glucose tolerance', 'physiological'),
    'e_ac_mtorc2_sparing': ('AKT S473 phosphorylation', 'molecular'),
    'e_ac_not_continuous': ('mTORC1', 'molecular'),
    'e_ac_d5_persistence': ('phosphorylation of S6', 'molecular'),
    'e_ac_d5_adipose': ('S6 phosphorylation', 'molecular'),
    'e_ac_mtorc2_lifespan': ('survival', 'lifespan'),
    'e_ac_pyruvate': ('pyruvate tolerance test', 'physiological'),
    'e_ac_tcells': ('T cells', 'molecular'),
    'e_ac_testes': ('testes weight', 'physiological'),
    'e_liver_mtorc2': ('glucose intolerance', 'physiological'),
    'e_mtorc2_models': ('cardiac function', 'function'),
    'e_mtorc2_immune': ('immunosuppressive effects', 'adverse_event'),
    'e_intermittent_longevity': ('longevity', 'lifespan'),
    'e_dl001': ('glucose intolerance, dyslipidemia, and immune disruption', 'adverse_event'),
    'e_diets': ('lifespan', 'lifespan'),
    'e_muscle_mtorc1_ko': ('muscle function', 'function'),
    'e_pearl_lean': ('lean mass', 'physiological'),
    'e_resilience': ('cold tolerance', 'physiological'),
    'e_wound_fracture': ('wound healing', 'function'),
    'e_human_infection_risk': ('risk of infection', 'disease'),
    'e_offlabel_infections': ('self-reported infections', 'disease'),
    'e_queiroz_glucose': ('glucose metabolism', 'physiological'),
    'e_rapaex_adverse': ('incidence rate of AEs', 'adverse_event'),
    'e_exercise_trial': ('chair-stand repetitions', 'function'),
    'e_daily_trial_metabolic': ('glycated hemoglobin (A1C)', 'biomarker'),
    'e_pearl_safety': ('adverse events (AEs)', 'adverse_event'),
    'e_johnson': ('skin/soft tissue infections, lipid abnormalities, glucose elevations', 'adverse_event'),
    'e_offlabel_few_adverse': ('adverse events', 'adverse_event'),
    'e_diet_no_side_effects': ('metabolic and immune side-effects', 'adverse_event'),
    'e_osteo_akt': ('osteoarthritis pathology', 'disease'),
    'e_pearl_hba1c': ('Hemoglobin A1C', 'biomarker'),
    'e_itp_schedules': ('median and 90th percentile lifespan', 'lifespan'),
    'e_itp_low_dose': ('lifespan', 'lifespan'),
    'e_celegans_mtorc2': ('longevity', 'lifespan'),
    'e_persistence': ('expression of electron transport chain complex components', 'molecular'),
    'e_mannick_schedules': ('well tolerated', 'adverse_event'),
    'e_infections_down': ('rate of total infections', 'disease'),
    'e_muscle_ok': ('muscle mass', 'physiological'),
    'e_bg_lifespan': ('median lifespan', 'lifespan'),
    'e_bg_glucose': ('glucose tolerance', 'physiological'),
    'e_pearl_primary': ('visceral adiposity', 'physiological'),
    'e_oa_mtorc2_intact': ('OA severity', 'disease'),
    'e_blago_pseudodiabetes': ('glucose intolerance', 'physiological'),
    'e_blago_insulin_production': ('insulin production', 'physiological'),
}
MARKER = {'biomarker', 'physiological', 'molecular'}
CLINICAL = {'lifespan', 'mortality', 'function', 'disease', 'adverse_event'}
# Who in the sample the result is about, as the quote says it.
SAMPLES = {
    'e_pearl_hba1c': {'population': 'subgroup', 'subgroup': 'males in the 5 mg cohort',
                      'outcome': 'not_stated', 'analysis': 'not_stated'},
    'e_pearl_lean': {'population': 'subgroup', 'subgroup': 'women', 'outcome': 'not_stated', 'analysis': 'not_stated'},
    'e_pearl_primary': {'population': 'whole_sample', 'outcome': 'primary', 'analysis': 'not_stated'},
}
# A result the quote reports, word for word, with what the quote says of it.
ESTIMATES = {
    'e_pearl_hba1c': {'reported': 'md = 0.059 (95% CI = 0.006–0.112), p = 0.024', 'measure': 'md',
                      'contrast': 'not_stated', 'scale': 'not_stated'},
    'e_rapaex_adverse': {'reported': '57% higher incidence rate of AEs', 'measure': 'incidence rate',
                         'contrast': 'not_stated', 'scale': 'not_stated'},
    'e_daily_trial_metabolic': {'reported': 'small increases in glycated hemoglobin (A1C) (within-group p = 0.03) and a '
                                            '40% increase in triglyceride levels (within-group p = 0.05)',
                                'measure': 'not_stated', 'contrast': 'within-group', 'scale': 'not_stated'},
    'e_itp_low_dose': {'reported': 'significant lifespan extension (16%, P = 0.02) at UM', 'measure': 'lifespan extension',
                       'contrast': 'not_stated', 'scale': 'not_stated'},
    'e_bg_lifespan': {'reported': 'increases in median lifespan, of 18% and 28% respectively', 'measure': 'median lifespan',
                      'contrast': 'not_stated', 'scale': 'not_stated'},
}
# Conditions the quote names: (member path, verbatim wording).
CONDITIONS = {
    'e_pearl_lean': [('intervention.agent', 'compound rapamycin'), ('intervention.dose', '10 mg')],
    'e_pearl_hba1c': [('intervention.dose', '5 mg')],
    'e_itp_schedules': [('system.age_at_start', '20 months of age')],
    'e_itp_low_dose': [('intervention.agent', 'Rapamycin'), ('intervention.dose', '4.7 ppm')],
    'e_mannick_schedules': [('intervention.agent', 'everolimus'),
                            ('intervention.dose', '0.5 mg everolimus once daily or 5 mg everolimus once weekly')],
}

by_line = {v['line']: v for v in values['lines']}
lines = L['evidence']['lines']
assert [l['id'] for l in lines] == [v['line'] for v in values['lines']]
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
    if line['id'] in SAMPLES:
        line['sample'] = {'value': SAMPLES[line['id']], 'src': src}
    for member, wording in CONDITIONS.get(line['id'], []):
        assert wording in line['quote'], (line['id'], wording)
        group, field = member.split('.')
        line.setdefault(group, {})[field] = {'value': wording, 'src': src}
    if line['id'] in ESTIMATES:
        assert ESTIMATES[line['id']]['reported'] in line['quote']
        line['result_estimate'] = {'value': ESTIMATES[line['id']], 'src': src}

# OHF 1.1 asks for an estimate wherever a quote reports a result in numbers, with not_stated where the
# source is silent; the lines with one leave the whole-list gap, and the others keep it one by one.
whole = next(g for g in added['gaps'] if g['path'] == 'evidence.lines[].result_estimate')
added['gaps'].remove(whole)
for i, line in enumerate(lines):
    if 'result_estimate' not in line:
        added['gaps'].append({**copy.deepcopy(whole), 'path': f'evidence.lines[{i}].result_estimate',
                              'reason': 'The passage states the result in words, with no figure to record.'})

ROUTES = {'intraperitoneal injection': 'intraperitoneal', 'intraperitoneal (IP)': 'intraperitoneal'}
for prediction in L['predictions']:
    route = prediction.get('intervention', {}).get('route')
    if route:
        route['term'] = ROUTES[route['value']]

hallmarks = [h for h in values['aging_hallmarks'] if h.get('atom_refs_hint')]
atoms = {a['id'] for a in L['core']['atoms']}
key = None
for h in hallmarks:
    assert set(h['atom_refs_hint']) <= atoms
    key = call_source(h['hints'][0]['call_id'], 'hallmarks of aging')
L['profile']['domain'] = 'ohf:aging@1'
L['profile']['aging_hallmarks'] = {
    'value': [{'hallmark': h['hallmark'], 'atom_refs': h['atom_refs_hint']} for h in hallmarks], 'src': key}

identity = card['identity']
identity['supersedes'] = [f"{identity['proposition_id']}@{identity['version']}"]
identity['version'] += 1
card['version'] = identity['version']
added['by'] = {'converter': 'ohf-1-1-upgrade', 'converter_version': '1.0.0',
               'converter_hash': CONVERTER_HASH,
               'model': 'claude-opus-5-5'}
added['at'] = AT
card['content_hash'] = content_hash(card)
OUT_CARD.write_text(json.dumps(card, indent=2, ensure_ascii=False) + '\n')
print(card['content_hash'], sum('endpoint_kind' in l for l in lines), sum('human_proximity' in l for l in lines),
      sum('taxon_id' in l.get('system', {}) for l in lines))
