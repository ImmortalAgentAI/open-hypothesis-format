# OHF specification

A hypothesis card keeps what its author said apart from what was added later. Both zones, `author` and `added`, use the same scientific layers: claim core, mechanism, predictions, evidence, provenance, profile and appendix. Layer 0, identity and versions, applies to the whole card. The pair-level record describes two cards together and is stored outside them.

Every card states `"standard_version": "1.0"`, the version of the card format; any other value is rejected. A release that does not change the format keeps this value. The terms used here are defined in the [glossary](glossary.md).

## Files

| File | Contents |
| --- | --- |
| [glossary.md](glossary.md) | Definitions of the terms OHF uses |
| [field-catalogue.json](field-catalogue.json) | All 180 logical paths, with definition, logical type, vocabulary, conceptual basis and field class |
| [fields.md](fields.md) | Field reference with an example for every path, generated from [field-reference.json](field-reference.json) |
| [logical-types.md](logical-types.md) | How logical types are represented |
| [references.md](references.md) | The identifier namespaces of a card and what each reference field must name |
| [related-standards.md](related-standards.md), [related-standards.json](related-standards.json) | The standards and models OHF fields draw on, with version, licence and relation to OHF |
| [mapping.md](mapping.md), [mapping.json](mapping.json) | Where each logical path is stored in a card, or why it is not |
| [gap-path-policy.json](gap-path-policy.json) | For each path, whether a gap may call the field not applicable |
| [`profiles-1.json`](../vocabularies/profiles-1.json) | The domain profiles a card can select, with their paths |
| [`heuristics-1.json`](../vocabularies/heuristics-1.json) | The heuristic principles `provenance.heuristic_principle[]` may name |

## Logical paths and storage

Logical paths describe scientific concepts. Their serialization in a card adds provenance wrappers: an author value has a source `locator`, and an added value has a `src` that points to a source record. The [mapping](mapping.md) gives the card path for each logical path.

Where the schema restricts a value to a fixed list, the restriction applies in both zones. The exceptions are restricted only in the added zone: `core.kind`, `core.atoms[].operator` and `mechanism.steps[].sign`. Their author-zone value is a passage of the source as written. Other fixed-list fields, such as `core.atoms[].modality` and the assessments, exist only in the added zone.

Some catalogue paths are not stored in an individual card:

- question references and the assertion registry are deferred extensions;
- the pair relation is stored in a separate artifact, described by [`hypothesis-relations-1.schema.json`](../schema/hypothesis-relations-1.schema.json); a card holds no relations;
- the hypothesis references and the decisive test of a pair are stored in a [pair brief](../schema/pair-brief-1.schema.json) for one pair of card versions;
- the other pair-level fields (discriminability, diagnosticity matrix, assumptions, comparison context) are deferred extensions.

Matching a field path does not prove source support or completeness.

## Gaps

A missing field stays missing and is listed in `added.gaps`. A gap does not invent a value.

Each gap names its exact catalogue path, a disposition, a reason, and the search queries and inspected artifacts behind it.

The disposition says why the value is missing:

- `not_supplied`: the source does not state the value, and no search was made for it.
- `searched_not_found`: a search was made and found no value; `query_ids` names at least one query.
- `budget_exhausted`: the search stopped when its time or cost budget ran out, before it could find or rule out a value.
- `blocked`: the source, or the part of it that would hold the value, could not be read, for example because access was refused.
- `converter_error`: the conversion failed on this value; the gap says nothing about the source.
- `source_excluded`: the part of the source that would hold the value was left out of the conversion on purpose, for example by its licence or by the conversion scope.
- `unknown_source_scope`: the retained source text does not establish the value, and it is not known whether the full source does.
- `not_applicable_scope` and `not_applicable_contract`: the field does not apply, under the [rules below](#when-not-applicable-is-allowed).

### Field classes

Every catalogue path has a class that says how a missing value is treated.

- **`searchable`** (122 paths). The value can be looked for in sources. A gap records what was searched.
- **`author_only`** (26 paths). Only the author, or for an assessment such as evidence strength, discrimination or indirectness the person who recorded it, can state the value: for example whether an assumption is fundamental or what threshold decides a prediction. Absence means "not declared". The gap disposition is `not_supplied`; `searched_not_found` and `budget_exhausted` are rejected, because a search cannot establish what the author did not declare.
- **`system`** (32 paths). The record itself assigns the value: identifiers, registry links, version history, pair records, the evidence selection record. An empty value, such as no superseded versions, is a valid value and needs no gap. A search is rejected here too.

### When "not applicable" is allowed

The [gap policy](gap-path-policy.json) limits when a gap may say the field is not applicable:

- **162 paths, `never`.** A missing input, an unknown scope, an exhausted budget or a failed search is not scientific inapplicability.
- **13 paths, `contract`.** The path is stored outside the card: the assertion registry, the pair record and the pair relation. The disposition is `not_applicable_contract`.
- **5 paths, `scope`.** The disposition is `not_applicable_scope`, with a `scope_ref` to filled card content, and only under the condition the policy names:
  - `source_verified_human_author` (`provenance.model`). The author-zone `provenance.author_type` is `human` with a locator.
  - `no_translation_with_original_language` (`provenance.translation`). The source language is recorded and no translation is.
  - no machine-checkable condition (3 combination paths). A reviewer decides from the source.

A claim without an intervention does not mark the intervention fields as not applicable. It selects the domain profile `none`, and those fields are absent; see [domain profiles](#domain-profiles).

Validate the card with `tools/validate.py` first, then run `tools/check_gaps.py` to apply these rules; the gap checker does not check schema shape. It reports the checks that only a reviewer can make under `review_required`.

## Card members outside the layers

Besides the layers, a card holds these members. All are required unless marked optional.

| Member | Records |
| --- | --- |
| `schema`, `id`, `version`, `content_hash` | The card schema (`ohf:hypothesis@1`), the card identifier, the card version and the SHA-256 of the card's canonical form. |
| `standard_version` | The version of the card format, `"1.0"`. |
| `identity` | The proposition identifier and version, superseded versions, retractions, duplicate-cluster and representative references, and the lifecycle state. |
| `vocabularies` | The pinned vocabularies, by id and SHA-256: `ohf:heuristics@1` and `ohf:profiles@1`. |
| `facets` | Search labels for the whole card: `topic[]`, `source_class` and, in the domain profile `ohf:intervention-pharmacology@1`, `intervention_type`. |
| `author.source` | The source of the author's assertions: kind, citation, DOI (optional), URL, licence and its basis, language, retrieval time and the SHA-256 of the retrieved text. |
| `author.generator` | Who or what generated the hypothesis: `human`, `ai_system`, `hybrid` or `unknown`, and for a system its name, version and model, each null when unknown. |
| `author.generation` | For a hypothesis from a generation run: the run identifier, how many hypotheses the run generated and submitted, and whether it submitted all of them. Each member is null when unknown or not applicable. A reader can see from it whether the hypothesis was selected from a larger set. |
| `author.submitted_at` | When the hypothesis was submitted as a card. |
| `added.by`, `added.at` | The converter that wrote the added zone, and when. |
| `added.cutoff_date` | The date up to which the converter's knowledge and searches reach, or null when unknown. |
| `added.sources` | The source records that added values point to through `src`: source, locator, access time and tool. |
| `added.budget` | The model calls, HTTP requests and tokens spent on the added zone; token counts may be null. |
| `added.completeness` | The completeness level, the layers present and what the next level still needs. |
| `added.challenge_search` | Optional. The search for evidence against the hypothesis; see [completeness](#completeness). |

## Domain profiles

A card names its domain profile in `added.layers.profile.domain`. [`profiles-1.json`](../vocabularies/profiles-1.json) lists the profiles and their paths.

- `ohf:intervention-pharmacology@1`: claims about the effect of an intervention. It holds 22 paths in two layers: the details of the intervention and the intercurrent events (14 paths, layer 3, predictions), and dose response, combinations and harm (8 paths, layer 6, profile). `facets.intervention_type` is then required.
- `none`: no domain profile. The 22 paths are absent, and they need no gaps; a gap for one of them is rejected.

Layer 6, profile, also holds general fields that every card may use, whatever its domain profile: biomarkers, human testability, transfer scope and the function or process concerned.

## Completeness

Completeness is structural:

- `accepted`: the author's assertion is checked against source bytes, and source, licence and provenance are present.
- `comparable`: `accepted`, plus a prediction that states, across both zones, its system, endpoint, form and epistemic status, and a direction when the form is `directional_contrast`.
- `full`: `comparable`, plus a typed mechanism step, claim atoms, and evidence on both sides. If no disputing evidence is found, the gap records the search queries. `added.challenge_search` records the search for disputing evidence: its queries, the artifacts inspected, the outcome and the evidence lines found.

Completeness says nothing about whether the claim or its reading is correct.

`tools/check_refs.py` computes the level from these conditions and reports, for each condition that is not met, the reason. It reads them as follows:

- The author's assertion is checked against source bytes when `added.source_verification.status` is `refetched_match` with the stored hash. A source that is `not_refetchable` or `refetched_mismatch` cannot show this by machine; the condition goes to `manual_review_required` with the reason.
- The source is `author.source` with its citation, URL and source text SHA-256; the licence is its `license` and `rights_basis`; the provenance is `author.generator`, `added.by` and `added.produced_by`.
- A typed mechanism step has a `subject_ref`, a `relation` and an `object_ref`, across both zones.
- Evidence is on both sides when one evidence line supports and one disputes. Without a disputing line, the search for one is recorded by `added.challenge_search` with the outcome `not_found`, or by an `evidence.lines` gap with the disposition `searched_not_found` and its query identifiers. A search that stopped early, with the outcome `incomplete` or a `budget_exhausted` gap, goes to `manual_review_required`.
- `added.challenge_search` is optional. When it is recorded with the outcome `found`, it names a disputing evidence line.

The computed level is the highest level whose conditions, and those of every lower level, are met. A declared level that a condition at or below it rules out is an error (`REF_COMPLETENESS_OVERSTATED`); a declared level below the computed one is a warning (`REF_COMPLETENESS_UNDERSTATED`). `missing_for_next` must name each condition that the next level still needs; extra or missing items are a warning (`REF_MISSING_FOR_NEXT`). The checker's report gives the conditions in the words it expects.

## Integrity

The added zone records how it was produced and checked. These members describe the record, not the hypothesis, and have no catalogue rows.

| Member | Records |
| --- | --- |
| `added.produced_by` | Who produced the added zone: `independent_pipeline`, `submitter` or `example_converter`, with pipeline name, version and an optional run identifier. |
| `added.source_verification` | Whether the source was downloaded again and compared with `author.source.source_text_sha256`: `refetched_match`, `refetched_mismatch` or `not_refetchable` with a reason. A refetch gives its URL, time and SHA-256. An optional `metadata_check` records a registry lookup, such as Crossref: DOI and title match, and whether a retraction is listed. |
| `added.integrity.entailment[]` | Whether the source supports each added value: a JSON pointer to the value, the basis checked (`src` or `basis_quote`), a verdict (`entails`, `partial` or `no`, the last two with a note), the checker with its version and the SHA-256 of its instructions, and the time. |

Rules:

- `refetched_match` requires the refetched SHA-256 to equal `author.source.source_text_sha256`; `refetched_mismatch` requires it to differ (`REF_SOURCE_MISMATCH`).
- The entailment checker is not the pass that wrote the added zone: its name differs from `added.by.converter` and its instructions from the rules pinned by `added.by.converter_hash` (`REF_CHECKER_NOT_INDEPENDENT`).
- Each entailment pointer resolves to a sourced added-zone value, once per basis.
- Every `src` in the added zone names a record of `added.sources` (`REF_SOURCE_UNKNOWN`); an empty `added.sources` while values name source records is also reported once (`REF_SOURCES_EMPTY`).
- Identifiers are unique within their namespace, and each reference names a record of the kind its field allows (`REF_DUPLICATE_ID`, `REF_UNKNOWN_ID`, `REF_WRONG_TARGET`, `REF_UNRESOLVED`). [references.md](references.md) lists the namespaces and the reference fields.
- `author.generation`: `submitted` is at most `generated`, and `submits_all` is true exactly when the two are equal; a null count is not compared (`REF_GENERATION_INCONSISTENT`).
- An entailment record is not checked before the source record its value names was accessed, nor before the assessment of that value, or of its nearest enclosing value, was made; no added-zone assessment is made after `added.at` (`REF_TIME_ORDER`). Other times, such as a refetch or an entailment check after `added.at`, are independent and are not ordered.
- A value with a `partial` or `no` verdict is not presented as supported by its source. A value without a record has not been checked.
- `metadata_check.retracted: false` means only that the registry listed no retraction at `checked_at`.
- `produced_by` states who produced the record. Which producers a consumer accepts is the consumer's rule.
- Every added-zone atom has a claim type, a role and a modality; an author-zone atom needs an added-zone atom with the same id that carries them (`REF_ATOM_UNCLASSIFIED`).
- The added zone cannot claim novelty (`novelty_assessment.status: claimed`); only the author zone can, or the added zone records a bounded search or an expert review.

A verdict concerns the source passage, not the truth of the claim. For an assessment, such as `predictions[].discrimination`, it asks whether the assessment follows from the cited basis. An assessment without a basis is not recorded; the field is a gap with `not_supplied`. Schema validity, a matching hash and an `entails` verdict together do not show that the claim is true.

`tools/check_refs.py` applies the rules the schema cannot express. It also warns when `core.kind` is `mechanism` but every atom states only existence, distribution or association (`REF_KIND_ATOMS`).

## Relations and pair briefs

These artifacts are separate from cards.

- `ohf:hypothesis-relations@1` ([schema](../schema/hypothesis-relations-1.schema.json)) records typed edges between card versions in a fixed pool: `rival_same_explanandum`, `nested`, `compatible_independent`, `duplicate`, `refines`, `unrelated`. Support and contradiction are evidence relations, not relations between hypotheses, and are not included.
- `ohf:pair-brief@1` ([schema](../schema/pair-brief-1.schema.json)) describes two card versions side by side: their relation, the observations both explain, the observations they expect differently, and a decisive test or a gap saying why none is known. It does not judge which hypothesis is better.

A pair brief repeats the relation of its two card versions. The relations artifact is the record of that relation: if a pair brief and a relations artifact disagree about the same two card versions, the relations artifact holds and the pair brief must be corrected.

Examples are described in [`examples/README.md`](../examples/README.md).
