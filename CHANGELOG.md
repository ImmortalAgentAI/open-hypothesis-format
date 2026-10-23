# Changelog

## Unreleased

The card format, the schemas and the vocabularies are unchanged.

- The rapa example no longer names the base card's internal review rounds in the reason of its `evidence.selection_record` gap. The converter is now `ohf-1-1-upgrade` 1.0.1 (`examples/converters/ohf-1-1-upgrade-1.0.1/`); the card is rebuilt, so its `content_hash` changed.

## 1.1.0 (2026-10-23)

A minor version: every new member is optional, a 1.0 card stays valid and is checked by the 1.0 rules, and a 1.0 card may not carry a member introduced in 1.1 or name one in a gap. The 36 new catalogue paths are marked `since: "1.1"`. The rules are listed in [spec/README.md, section OHF 1.1](spec/README.md#ohf-11). The standard still holds no verdict on a claim.

- **Closed vocabularies.** `vocabularies/terms-1.json` (`ohf:terms@1`, pinned by sha256): route, control type, endpoint kind, human proximity, exclusion reason, and a taxon table. A recorded route or endpoint kind in the added zone carries the closed `term`. `endpoint_kind` is redefined from free text to a term of this list. `predictions[].control_type` is a list of terms in which `none` and `not_stated` stand alone.
- **Conditions of an evidence line**: system with `taxon_id`, intervention, `sample_size`, `multi_site_program`. The intervention of a line is not gated by the domain profile, a deliberate departure from the 1.0 rule for predictions: it describes the study, not the claim. `REF_CONDITION_IN_QUOTE` (warning).
- **Sample and result estimate** of a line; an estimate must appear in the quote (`REF_ESTIMATE_IN_QUOTE`, `REF_ESTIMATE_NOT_QUOTED`, errors).
- **A line may target an alternative**: an element of `core.alternative_explanations` may have an `id`, and a line or an excluded record may target it. Elements of `alternative_explanations`, `uncertainties`, `opens` and `explains` may carry their own `src` or `locator`.
- **Typed triple on an atom** (RO or Biolink relation, CURIE or entity reference as subject and object, Biolink qualifiers) and **links between atoms** (`requires`, `contradicts`; `REF_ATOM_LINK`).
- **Excluded evidence**: `evidence.excluded[]` with a closed reason and at least one of `artifact` and `record`.
- **Proximity to humans**: `human_proximity` on a line, derived from taxon and endpoint kind (`REF_PROXIMITY_MISMATCH` error, `REF_PROXIMITY_NOT_DERIVED` warning). A human line with no marker or clinical endpoint kind has no derived rung; a taxon row given with `--taxa` can give warnings, never errors.
- **Known result**: `core.novelty_assessment.status` may be `known_result`, with prior claims, search scope and date, and without `new_content`. This is the one relaxation of 1.1: in 1.0 every novelty assessment requires `new_content`.
- **Aging profile** `ohf:aging@1` (`vocabularies/profiles-2.json`, `ohf:profiles@2`; hallmarks in `vocabularies/hallmarks-1.json`, `ohf:hallmarks@1`): a superset of the intervention profile with `profile.aging_hallmarks`. It does not require `intervention_type`. 1.0 cards keep `ohf:profiles@1`.
- **Gaps for empty lists**: a gap may name a whole list that is empty, such as `core.assumptions`; 1.0 forbids these paths.
- **Independence key** on a line (`REF_INDEPENDENCE_KEY`): one label, one key, on every line of the group; a DOI compared without case; **generator prompt and generation time** in `author.generator` (`prompt`, `generated_at`).
- **Withheld quote**: `evidence.lines[].quote_withheld` for a source whose licence forbids quoting (reason, locator, record, paraphrase and abstract quote, all required). A line has a quote or a withheld quote, not both; a disputing line that is only withheld does not meet `full`.
- **Scope of an edge**: `scope_differs[]` on an edge of the relations schema, with the new `tools/check_relations.py` (`REL_CARD_MISSING`, `REL_POINTER_UNRESOLVED`, `REL_SCOPE_FIELD`, `REL_SCOPE_SAME`).
- **Examples**: `examples/cards/intermittent-rapamycin-mtorc2.json` is a 1.1 card built by the converter `examples/converters/ohf-1-1-upgrade-1.0.0/` from an accepted 1.0 card and recorded inputs. An independent reader checked its new quoted and paraphrased values, endpoint kinds, conditions, estimates and the targets of its withheld-quote lines against their passages; taxon identifiers, proximity rungs, hallmarks, the atom triple, `requires` links and the excluded record are checked by the schema and `tools/check_refs.py`, not by that reader. `tests/fixtures/ex1-rapamycin-1.1.json` is a fixture, not a published example.
- `tools/check_relations.py` runs in CI.
- Every new rule has a mutation test that must fail.

Known limits of 1.1:

- `tools/check_ledger.py` does not apply to the 1.1 example: it expects a ledger record for every sourced value and rebuilds the value without `term`. Left for 1.2.
- The base card of the rapa example has one pending check of its latest corrections; `examples/index.json` records the base hash, and if that check changes the base card the example is rebuilt.
- In the rapa example no `target_ref` of a withheld-quote line is entailed by its abstract: three are `partial` and recorded, and the line whose target got `no` was not carried. The choice of a target is a reading of the card more than of a paragraph; a later version may decide it by resolution against the card.
- `quote_withheld` was checked as a whole value. Its `reason` and `record_ref` are facts about the record, not the content of a paragraph, so they should be decided by resolution and the rest checked member by member. Left for 1.2.

### Also in 1.1.0: example tools

- `tools/converter_hash.py` checks an example card's `added.by.converter_hash` against conversion rules kept in the repository: `examples/cards/CONVERSION.md` for `ohf-example-conversion`, else `examples/converters/<converter>-<version>/`. The pin is the hash of a listing of relative paths and file hashes, so it reproduces from the repository alone.
- `tools/check_ledger.py` checks an example card's entailment records against its ledger, `examples/ledgers/<slug>.json`: each record shows the worst recorded check of its current value and passage. CI runs both checks.
- An example card may quote a source under CC BY 3.0 as well as CC BY 4.0.

## 1.0.1

The card format, the schemas and the vocabularies are unchanged; cards valid under 1.0.0 stay schema-valid. The reference checker is stricter, so a card that passed it under 1.0.0 can now fail it.

- `tools/check_refs.py` checks every `src` in the added zone against `added.sources` (`REF_SOURCE_UNKNOWN`, `REF_SOURCES_EMPTY`).
- Identifiers are unique per namespace, and each reference field names a record of the kind it allows. The namespaces and fields are listed in the new [`spec/references.md`](spec/references.md).
- `author.generation` counts must agree (`REF_GENERATION_INCONSISTENT`). Entailment checks and assessments must be in time order (`REF_TIME_ORDER`).
- The completeness level is computed by the new `tools/check_completeness.py`. A declared level above the computed one is an error (`REF_COMPLETENESS_OVERSTATED`); a lower one, or a `missing_for_next` that does not match, is a warning.
- Correction: `full` without a disputing line needs `added.challenge_search` with the outcome `not_found` and its query identifiers. The 1.0.0 text named a gap for this search, but the gap catalogue has no path for a missing disputing line.
- The example card declares its computed level, `comparable`, with a derived `missing_for_next`.
- spec/README.md states how a card written without a generation tool fills the required process members: null generation members, `model: "none"`, zero model calls; each means not applicable. The fixture `fx_nine` follows it and reaches `accepted`. Regression tests cover each new rule.
- README: the gap checker checks only the gaps a card lists; Python 3.11 or later is required and 3.12 is tested; `.github/` is under the MIT licence.

## 1.0.0

- Initial public release.
