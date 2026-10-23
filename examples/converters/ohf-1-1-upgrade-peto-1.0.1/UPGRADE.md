# How the accepted OHF 1.0 Peto card is upgraded to an OHF 1.1 example

The upgrade adds OHF 1.1 values to a frozen, accepted OHF 1.0 card. It changes no value the card already has, except those listed in rule 2. It was done by a language model with the script `upgrade.py` in this directory. The base card, the values, the search log and the Europe PMC records are inputs named by hash. They are not in this repository.

## Inputs of `peto-paradox-mammals`, version 9

- **Base card**: `h_peto-paradox-mammals` version 8, `content_hash` `sha256:db738db37ab9b38f75c10735361acfb049630bc5160650f637d4fb51fa5f48a9` (file `sha256:3f66e53ead6db5971b2c7b2f67eaa15f641eb96c969d8335f74fcaa3338a7333`), produced by ohf-extractor 0.8.17. It differs from version 2 (`sha256:b04374244b572b21b624e0db366a2d50a542a6d63f9f567f323ab16d4de81744`) only in wording. Version 2 is also an input: the values were made for it, and the script asserts that the lines, atoms, alternatives, entailment records and sources are identical in both versions.
- **Ledger of the base card**: 313 entailment records.
- **Values**: the values tool `biodb.py`, run 1, kit commit eaf6f4c, `sha256:9dc773b012555c7e…`, with its search log. The values cover the organism word of each line, its NCBI taxon where the word names one species, and the rung from the NCBI lineage. They name no intervention and no hallmark, because the card's domain profile is `none`.
- **Europe PMC records** of the three DOIs used as independence keys, each with its retrieval time.

## Rules

1. **Version and pins.** `standard_version` becomes `1.1` and the card pins `ohf:terms@1`. The profile stays `none`, so the card keeps `ohf:profiles@1` and has no hallmarks. The card version goes up by one to 9, `identity.version` is set to it, and the base card version is in `supersedes`.
2. **Changed values.** These values of the base card change:
   - `added.by` names this upgrade and the model that wrote its rules; `added.at` is the time of the run.
   - The whole-list gap `evidence.lines[].result_estimate` is replaced (rule 6).
   - `added.budget.http_requests` adds this version's requests: every response of the values tool's calls and the three Europe PMC records. The run makes no model call, so `model_calls` is unchanged; the model calls spent writing the rules were not counted.
   - The 17 lines of the three keyed groups gain a `key` in `independence_group` (rule 8). Their 17 base entailment records checked the group label against a paragraph and no longer describe the value, so they are dropped. A group's key is decided by resolution, not by a paragraph.
   - `added.produced_by` still names ohf-extractor 0.8.17, which produced the rest. The other `integrity.entailment` records of the base card are kept as they are: no value they name has changed. An identifier given to an alternative is not content a paragraph supports, so the record on the alternatives stands.
3. **System of a line.**
   - `system.taxon` is the organism word of the line's own `study_system`, checked as a substring, with the `study_system`'s `src`.
   - `system.taxon_id` is the NCBI Taxonomy answer to that word, with a sources entry for that call. A word that names a clade (mammals, Carnivora, ruminants) or several species gets no `taxon_id`. Only the human line has one.
4. **Endpoint kind.**
   - `endpoint_kind.value` is a verbatim substring of the line's quote or `study_type`; the script asserts this.
   - `term` is the converter's reading against `ohf:terms@1`. Cancer mortality risk is `mortality`. Cancer detected, its prevalence or incidence, and neoplasia are `disease`. The somatic mutation rate is `molecular`.
   - Three lines give no single endpoint and get none: the elephant TP53 line, which states both a gene copy number and a cancer prevalence, and the two arguments about method and interpretation.
5. **Rung.**
   - For a non-human taxon, `human_proximity` is the rung from the NCBI lineage, as the values give it. For the human line it is `human_clinical`, by its endpoint kind.
   - A clade has no `taxon_id`, so the rung cannot be derived from the card, and `tools/check_refs.py` reports `REF_PROXIMITY_NOT_DERIVED` for it. The warning is expected. The rung stands on the values tool's lineage call, which is the line's source record for it.
   - A line whose organisms span classes (amphibians, reptiles, birds and mammals), or with no organism word, gets no rung.
6. **Result estimate.**
   - Where a quote reports a result in numbers, as `tools/check_refs.py` defines it, `result_estimate` gives the reported text verbatim. It gives the measure, contrast and scale as the passage states them, or `not_stated`. The script asserts that the lines with an estimate are exactly the lines whose quote reports a result in numbers.
   - The other lines get one gap each, saying that the passage states the result in words.
7. **Sample size.** `sample_size` is set where the quote states the number of species the result rests on: 191 for the cancer mortality risk across species, 16 for the somatic mutation rate.
8. **Independence keys.** A group whose label names one work that holds its own data gets that work's DOI as its key, on every line of the group. These groups are the ZIMS data of Vincze et al. 2022, the elephant TP53 copies of Sulak et al. 2016 and the somatic mutation rates of Cagan et al. 2022. The script asserts that Europe PMC resolves each DOI to one record. The two reanalysis lines of Dujon et al. already carry the Vincze group, because they reuse its data, so they carry its key. Some groups get no key: groups named for several cited studies; Butler et al. 2025 and Compton et al. 2026, which analyse data compiled from earlier work whose first appearance this upgrade did not establish; and Lynch et al. 2025 and the spandrel paper, which are arguments.
9. **Atoms and alternatives.**
   - `requires` records what an atom's own statement rests on. The pathogen reading rests on the diet result. The co-evolution reading ("The results suggest") rests on the body-mass and life-expectancy results.
   - The five alternatives get identifiers. The target of an accepted line is not changed, so no line targets an alternative.
10. **Entailment.** The verdicts of the independent check (an independent reader, prompt `ENTAILMENT-PROMPT.md`, sha256 46716d7b…) are written to `integrity.entailment` with the time they were delivered, including `partial` and `no` verdicts and their notes. A verdict is written only for a sourced value. Values the check has not yet returned carry no record. Three values were corrected after the first batch, because the check found that they dropped a scope or added a qualifier that the passage does not give. The endpoint kind of the frequency line is now the passage's own `CMR`. The estimates on the managed-population burden and on the viral fraction in humans now begin with the passage's "In some species" and "in humans it was estimated that". Their first verdicts are not written; the verdicts of the recheck are.

`added.by.converter_hash` is the hash of this directory, computed by `tools/converter_hash.py`.
