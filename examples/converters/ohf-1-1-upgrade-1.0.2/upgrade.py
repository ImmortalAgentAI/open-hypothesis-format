"""Upgrade the accepted rapa card (content_hash 0ec01fd8…) to an OHF 1.1 example card.

Usage: upgrade.py INPUT_DIR OUT_CARD AT CONVERTER_HASH. INPUT_DIR holds the base card, the values
tool's output (biodb.py) and its search log. Every wording the upgrade adds is a verbatim substring of the line's quote,
study_type or study_system; the script asserts it. The rules are in UPGRADE.md next to this file.
"""
import copy, hashlib, json, sys
from pathlib import Path

OHF = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(OHF))
from tools.content_hash import content_hash  # noqa: E402

INPUT, OUT_CARD, AT, CONVERTER_HASH = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3], sys.argv[4]
card = json.loads((INPUT / 'intermittent-rapamycin-mtorc2.json').read_text())
assert card['content_hash'] == 'sha256:0ec01fd8f42074a160351634c41a80e49477ae2e9c981812c69c1203a58c98b1'
# The values were made for version 2 of the card (473ca95e…). Version 8 differs from it in the wording of
# gap reasons and of the first proposal: everything the values and this upgrade read is identical.
previous = json.loads((INPUT / 'intermittent-rapamycin-mtorc2-473ca95e.json').read_text())
assert previous['content_hash'] == 'sha256:473ca95e5dd7ad4efa2ccdc09dac51d25b970542ec9362f741f1076d9f917db5'
same = lambda added: {k: v for k, v in added.items() if k not in ('gaps', 'layers')}  # noqa: E731
assert same(previous['added']) == same(card['added'])
assert {k: v for k, v in previous['added']['layers'].items() if k != 'core'} == \
    {k: v for k, v in card['added']['layers'].items() if k != 'core'}
assert {k: v for k, v in previous['added']['layers']['core'].items() if k != 'first_proposed'} == \
    {k: v for k, v in card['added']['layers']['core'].items() if k != 'first_proposed'}
assert [{k: v for k, v in g.items() if k != 'reason'} for g in previous['added']['gaps']] == \
    [{k: v for k, v in g.items() if k != 'reason'} for g in card['added']['gaps']]
assert previous['author'] == card['author']
values = json.loads((INPUT / 'rapa-1.1-values.json').read_text())
assert values['card']['content_hash'] == previous['content_hash']
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
    # The estimate is the result at one site in males; the pooled male result in the same quote is null.
    'e_itp_low_dose': {'population': 'subgroup', 'subgroup': 'males at UM', 'outcome': 'not_stated',
                       'analysis': 'not_stated'},
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

# Atoms: the typed reading of the one atom that states rapamycin's direct action, and the chain of the
# hypothesis as its general atom states it (category: consistency with the card's own atoms).
atoms_by_id = {a['id']: a for a in L['core']['atoms']}
acute = atoms_by_id['a_acute_chronic']
assert 'Rapamycin acutely inhibits mTORC1' in acute['statement']['value']
acute['triple'] = {'value': {'subject': {'id': 'CHEBI:9168', 'label': 'sirolimus'},
                             'relation': {'id': 'RO:0002212', 'label': 'negatively regulates'},
                             'object': {'id': 'GO:0031931', 'label': 'TORC1 complex'}},
                   'src': acute['statement']['src']}
REQUIRES = {'a_intermittent_selective': ['a_acute_chronic'],
            'a_fewer_side_effects': ['a_side_mtorc2', 'a_intermittent_selective'],
            'a_less_immunosuppressive': ['a_intermittent_selective'],
            'a_general': ['a_intermittent_selective', 'a_side_mtorc2', 'a_mtorc1_sufficient']}
for ident, required in REQUIRES.items():
    atoms_by_id[ident]['requires'] = {'value': required, 'src': atoms_by_id[ident]['statement']['src']}

# Alternatives get identifiers, so lines and excluded records can name them.
for alt, ident in zip(L['core']['alternative_explanations']['value'],
                      ('alt_tcell_mtorc1_or_mtorc2', 'alt_cr_mimetic', 'alt_broad_mtorc1')):
    alt['id'] = ident

# The ITP: Miller et al. 2014 p[5] names the programme and its three institutions.
sources['itp_programme'] = {**sources['itp_low_dose'], 'locator': 'XML .//p[5] (1-based document order)'}
itp = next(l for l in lines if l['id'] == 'e_itp_low_dose')
itp['multi_site_program'] = {'value': {'program': 'Interventions Testing Program (ITP)', 'sites': 3},
                             'src': 'itp_programme'}

# What the review says and the card does not carry, with the reason the base card's report gives.
L['evidence']['excluded'] = [{
    'id': 'x_celegans_review_clause',
    'target_ref': {'kind': 'card', 'pointer': '/added/layers/core/atoms/4'},
    'reason': 'other',
    'note': 'Reference 65 of this sentence is PMC4172656, which the card reads at first hand as e_celegans_mtorc2; '
            'a line quoting the review would put one work on both sides of one atom.',
    'quote': 'inhibition of mTORC2 also negatively impacts survival in C. elegans [65, 66]',
    'record': 'PMC13355979 p[23]', 'src': 'side_mtorc2'}]
assert atoms_by_id['a_mtorc2_negative'] is L['core']['atoms'][4]

# Four works the base card names against it that may not be quoted: a line each, with the quote withheld,
# a paraphrase and the sentence of the PubMed abstract that entails it.
import re as _re
import xml.etree.ElementTree as ET


def abstract(pmid):
    root = ET.parse(INPUT / 'pubmed' / f'{pmid}.xml').getroot()
    return ' '.join(_re.sub(r'\s+', ' ', ''.join(a.itertext())).strip() for a in root.iter('AbstractText'))


WITHHELD = [
    ('e_withheld_strains', '31276577', 'a_liver_mtorc2', 'disputes', 'licence_unknown', 'nine inbred strains of mice',
     'mice', 'NCBITaxon:10090', 'systemic insulin sensitivity', 'physiological',
     'Across all strains, rapamycin significantly delayed glucose clearance after challenge. However, rapamycin '
     'showed no main effect on systemic insulin sensitivity.',
     'Across the strains surveyed, rapamycin delayed glucose clearance but had no main effect on systemic insulin '
     'sensitivity.'),
    ('e_withheld_bone', '34389472', 'a_fewer_side_effects', 'disputes', 'no_open_text',
     'female wild-type (ICR) and Nrf2-/- mice', 'mice', 'NCBITaxon:10090', 'bone mineral density', 'physiological',
     'Rapamycin (4 mg/kg bodyweight) was administered by intraperitoneal injection every other day for 12 weeks. '
     'Mice treated with rapamycin exhibited lower femur bone mineral content, bone mineral density, and bone volume '
     'compared to vehicle-treated mice.',
     'Rapamycin injected every other day for 12 weeks lowered femur bone mineral content, bone mineral density and '
     'bone volume in mice, compared with vehicle.'),
    ('e_withheld_phase1', '40394335', 'a_humans_few_adverse', 'neutral', 'nc_nd',
     'people 55-85 years old with mild cognitive impairment or early-stage dementia', 'people', 'NCBITaxon:9606',
     'adverse events', 'adverse_event',
     'After treatment, we find that twenty, mostly mild adverse events occur, systolic blood pressure and '
     'hemoglobin A1c increase, multiple erythrocyte parameters decrease, and there are no significant cognitive '
     'changes.',
     'In ten people given rapamycin 1 mg a day for eight weeks, twenty mostly mild adverse events occurred, '
     'systolic blood pressure and hemoglobin A1c rose, and CSF phosphorylated tau-181, glial fibrillary acidic '
     'protein and neurofilament light and several plasma inflammatory markers increased significantly.'),
]
# How far each line is from the atom it targets. The independent check found that no abstract names the
# targeted atom's mechanism or schedule (target_ref: 0 of 4 entails); the line for HET3 mice (23648089), whose
# verdict was no, is dropped, and the other three state the distance here.
INDIRECTNESS = {
    # Systemic glucose clearance and insulin sensitivity, not hepatic insulin resistance or mTORC2.
    'e_withheld_strains': {'system': 'none', 'endpoint': 'serious', 'intervention': 'none', 'comparison': 'none'},
    # Injection every other day against vehicle, not intermittent against continuous dosing.
    'e_withheld_bone': {'system': 'none', 'endpoint': 'none', 'intervention': 'some', 'comparison': 'serious'},
    # Continuous daily dosing (1 mg/day for eight weeks), not intermittent; before and after, no control group.
    'e_withheld_phase1': {'system': 'none', 'endpoint': 'none', 'intervention': 'serious', 'comparison': 'some'},
}
DELTA_VERDICTS = 'sha256:9d0121dd99b49a2007fd8cf98a42fd11d06cdbee1f1e3155041127517498ce19'
INDIRECTNESS_AT = (INPUT / 'verdicts' / 'RAPA-1.1-DELTA-VERDICTS-20261022.json.checked_at').read_text().strip()
assert 'sha256:' + hashlib.sha256((INPUT / 'verdicts' / 'RAPA-1.1-DELTA-VERDICTS-20261022.json').read_bytes()).hexdigest() \
    == DELTA_VERDICTS
TAXON_SOURCE = {'NCBITaxon:10090': 'biodb_5c456c648524', 'NCBITaxon:9606': 'biodb_1272a10cf166'}
for (ident, pmid, target, direction, reason, study_system, words, taxon_id, endpoint, term,
     abstract_quote, paraphrase) in WITHHELD:
    text = abstract(pmid)
    assert abstract_quote in text and study_system in text and endpoint in abstract_quote, ident
    key = f'pubmed_{pmid}'
    sources[key] = {'source': f'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pmid}&retmode=xml',
                    'locator': 'PubMed record, abstract',
                    'accessed_at': (INPUT / 'pubmed' / f'{pmid}.retrieved').read_text().strip(),
                    'tool': 'PubMed E-utilities, read by the OHF 1.1 upgrade'}
    human = taxon_id == 'NCBITaxon:9606'
    lines.append({
        'id': ident, 'target_ref': {'value': target, 'src': key}, 'direction': {'value': direction, 'src': key},
        'quote_withheld': {'value': {'reason': reason, 'locator': 'abstract',
                                     'record_ref': {'scheme': 'pmid', 'id': pmid},
                                     'paraphrase': paraphrase, 'abstract_quote': abstract_quote}, 'src': key},
        'study_system': {'value': study_system, 'src': key},
        'system': {'taxon': {'value': words, 'src': key}, 'taxon_id': {'value': taxon_id, 'src': TAXON_SOURCE[taxon_id]}},
        'endpoint_kind': {'value': endpoint, 'src': key, 'term': term},
        'human_proximity': {'value': ('human_clinical' if term in CLINICAL else 'human_marker') if human else 'mammal',
                            'src': TAXON_SOURCE[taxon_id]},
        'src': key})
    lines[-1]['indirectness'] = {'value': INDIRECTNESS[ident], 'src': key, 'assessment': {
        'assessor': 'ohf-1-1-upgrade 1.0.2', 'assessed_at': INDIRECTNESS_AT,
        'evidence_ref': {'kind': 'artifact', 'sha256': DELTA_VERDICTS}}}
    added['gaps'].append({**copy.deepcopy(whole), 'path': f'evidence.lines[{len(lines) - 1}].result_estimate',
                          'reason': 'The quote is withheld; the result is carried by the paraphrase, which gives no figure.'})

# Verdicts of the independent entailment check (an independent reader), one file per batch in INPUT/verdicts with its
# time in a sidecar. A verdict is written only where its pointer resolves; the checker is the base card's.
checker = added['integrity']['entailment'][0]['checker']
base = json.loads((INPUT / 'intermittent-rapamycin-mtorc2.json').read_text())


def resolve(document, pointer):
    node = document
    for token in pointer.split('/')[1:]:
        node = node[int(token)] if isinstance(node, list) else node[token]
    return node


def content(node):
    """The value a paragraph check judged: identifiers given to list elements are not part of it."""
    if isinstance(node, dict):
        return {k: content(v) for k, v in node.items() if k != 'id' or 'claim_or_ref' not in node}
    if isinstance(node, list):
        return [content(v) for v in node]
    return node


# A base record whose checked content the upgrade changed no longer holds; it is dropped until checked again.
added['integrity']['entailment'] = [r for r in added['integrity']['entailment']
                                    if content(resolve(base, r['pointer'])) == content(resolve(card, r['pointer']))]
# The delta was checked on the card in which the HET3 line was line 53; it is dropped, so later lines move up.
MOVED = {'/added/layers/evidence/lines/53': None, '/added/layers/evidence/lines/54': '/added/layers/evidence/lines/53',
         '/added/layers/evidence/lines/55': '/added/layers/evidence/lines/54'}
# Values changed after their check: the paraphrase of the phase 1 trial now names the biomarker rises.
CHANGED = {'/added/layers/evidence/lines/54/quote_withheld'}


def moved(pointer):
    for old, new in MOVED.items():
        if pointer.startswith(old + '/'):
            return new and new + pointer[len(old):]
    return pointer


for path in sorted((INPUT / 'verdicts').glob('*.json')) if (INPUT / 'verdicts').is_dir() else []:
    checked_at = Path(f'{path}.checked_at').read_text().strip()
    delta = path.name.startswith('RAPA-1.1-DELTA')
    for verdict in json.loads(path.read_text()):
        pointer = moved(verdict['pointer']) if delta else verdict['pointer']
        if pointer is None or pointer in CHANGED:
            continue
        node = resolve(card, pointer)
        # A record names a sourced value; the target of a withheld line is one. The quote of an excluded record
        # is checked by containment; that verdict stays in the verdict file.
        if not (isinstance(node, dict) and 'value' in node and 'src' in node):
            continue
        verdict = {**verdict, 'pointer': pointer}
        record = {'pointer': verdict['pointer'], 'basis': verdict['basis'], 'verdict': verdict['verdict'],
                  'checker': dict(checker), 'checked_at': checked_at}
        if verdict.get('note'):
            record['note'] = verdict['note']
        added['integrity']['entailment'].append(record)

# This version's requests: every response of the values tool's calls and the four PubMed records.
added['budget']['http_requests'] += sum(len(entry.get('responses') or []) for entry in log.values()) + len(WITHHELD)

identity = card['identity']
identity['supersedes'] = [f"{identity['proposition_id']}@{card['version']}"]
card['version'] += 1
identity['version'] = card['version']
added['by'] = {'converter': 'ohf-1-1-upgrade', 'converter_version': '1.0.2',
               'converter_hash': CONVERTER_HASH,
               'model': 'claude-opus-5-5'}
added['at'] = AT
card['content_hash'] = content_hash(card)
OUT_CARD.write_text(json.dumps(card, indent=2, ensure_ascii=False) + '\n')
print(card['content_hash'], sum('endpoint_kind' in l for l in lines), sum('human_proximity' in l for l in lines),
      sum('taxon_id' in l.get('system', {}) for l in lines))
