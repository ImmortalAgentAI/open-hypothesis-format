# How an accepted OHF 1.0 card is upgraded to an OHF 1.1 example

The upgrade adds OHF 1.1 values to a frozen, accepted OHF 1.0 card. It changes no value the card already has, except the two the upgrade must change, listed below. It was done by a language model with the script `upgrade.py` in this directory. The base card, the values and the search log are inputs named by hash. They are not in this repository.

## Inputs of `intermittent-rapamycin-mtorc2`, version 3

- **Base card**: `h_intermittent-rapamycin-mtorc2` version 2, `content_hash` `sha256:473ca95e5dd7ad4efa2ccdc09dac51d25b970542ec9362f741f1076d9f917db5`, converted by ohf-extractor 0.8.17.
  - It is a flagship, accepted subject to one condition that is still open: the acceptor checks that the changes after wave 4 of the critic pass lie only in the post-wave-4 material.
  - If that check changes the base card, this example is rebuilt from the new hash.
- **Ledger of the base card**: `sha256:2c113ef849e8f71a53d6a0e7dc29a2b01f64591fc76b03c19e8e7958cd523168` (file bytes), 535 entailment records.
- **Values**: arena-biodb, run 3, `ohf-extractor:example-values@1`, `sha256:ff90e371248e0f7efbd7e42a5c99c755999d4601b81461c0ec38abb4351b88c3`, kit commit eaf6f4c, with its search log.
  - The values cover the NCBI taxon of each line, the rung for non-human taxa, and hallmark hints with the atoms that name a hint's term.

## Rules

1. **Version and pins.** `standard_version` becomes `1.1`.
   - The card pins `ohf:terms@1`, `ohf:profiles@2` and `ohf:hallmarks@1`.
   - `identity.version` goes up by one, and the base version is in `supersedes`.
2. **Changed values.** Only two values change, and the upgrade must change both.
   - `added.by` names this upgrade, because the upgrade wrote the new values.
   - The whole-list gap `evidence.lines[].result_estimate` is replaced (rule 6).
   - `added.produced_by` still names ohf-extractor 0.8.17, which produced the rest. The `integrity.entailment` records of the base card are kept as they are: no value they name has changed.
3. **System of a line.**
   - `system.taxon` is the organism word of the line's own `study_system`, checked as a substring, with the line's `src`.
   - `system.taxon_id` is the NCBI Taxonomy answer to that word. Its `src` is a sources entry for that call. A word that names a group or several species gets no `taxon_id`.
4. **Endpoint kind.**
   - `endpoint_kind.value` is a verbatim substring of the line's quote or `study_type`. The script asserts this.
   - `term` is the converter's reading against `ohf:terms@1`.
   - A line whose passage gives no single endpoint gets no `endpoint_kind`.
5. **Rung.**
   - For a non-human taxon, `human_proximity` is the rung from the NCBI lineage, as the values give it.
   - For a human, it is `human_marker` or `human_clinical` by the endpoint kind (OHF 1.1 item 6).
   - A line with no rung, or a human line without an endpoint kind, gets none.
6. **Result estimate.**
   - Where a quote reports a result in numbers, `result_estimate` gives the reported text verbatim. It gives the measure, contrast and scale as the passage states them, or `not_stated`.
   - The other lines keep the reason of the base card as one gap per line.
7. **Sample and conditions.**
   - `sample` is set only where the quote names the subgroup or the outcome.
   - A dose, an agent or an age that the quote names is recorded on the line in the quote's words.
8. **Profile.**
   - `profile.domain` becomes `ohf:aging@1`, a superset of the intervention profile.
   - `profile.aging_hallmarks` lists each hallmark whose hints name at least one atom of this card, with those atoms. The hints come from Open Genes. A hallmark with no atom is left out.
9. **Routes.** Each prediction route gets its `term` from its wording.
10. **Atoms and alternatives.**
    - The one atom that states the direct action, `a_acute_chronic`, gets a triple: sirolimus (CHEBI:9168) RO:0002212 *negatively regulates* TORC1 complex (GO:0031931).
    - `requires` records the chain that the general atom states. The selective inhibition rests on the acute and chronic difference. The fewer side effects rest on the mTORC2 cause and the selective inhibition. The general atom rests on both and on mTORC1 sufficiency.
    - The alternatives get identifiers. No passage disputes one, and the target of an accepted line is not changed, so no line targets an alternative.
11. **Multi-site programme.** `e_itp_low_dose` gets the Interventions Testing Program with three sites, from p[5] of the same article, which names both.
12. **Excluded.** The review's C. elegans clause in p[23] is recorded with its reason and is not carried as a line. The base card's report gives that reason: the cited work is already read at first hand.
13. **Withheld quotes.** The four works that the base card names against itself and may not quote each become a line with `quote_withheld`:
    - two with no licence in the record;
    - one CC BY work with no open full text;
    - one CC BY-NC-ND work.
    Each line has the PubMed record, a paraphrase in the added zone, and the abstract sentence that entails the paraphrase. The script asserts that this sentence is in the fetched abstract. The phase 1 trial gave rapamycin daily, so its line is `neutral` on the intermittent atom.
14. **Entailment.** The verdicts of the independent check (ohf-examples, prompt `ENTAILMENT-PROMPT.md`, sha256 46716d7b…) are written to `integrity.entailment` with the time they were delivered, including the `partial` verdict and its note. Values the check has not yet returned carry no record. A record of the base card whose value the upgrade changed is dropped until that value is checked again: the three prediction routes, which gained a term. An identifier given to an alternative is not content a paragraph supports, so the record on the alternatives stands.

`added.by.converter_hash` is the hash of this directory, computed by `tools/converter_hash.py`.
