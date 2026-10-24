# OHF specification

A hypothesis card keeps what its author said apart from what was added later. Both zones, `author` and `added`, use the same scientific layers: claim core, mechanism, predictions, evidence, provenance, profile and appendix. Layer 0, identity and versions, applies to the whole card. The pair-level record describes two cards together and is stored outside them.

Every card states `standard_version`, the version of the card format: `"1.0"`, `"1.1"`, `"1.2"` or `"1.3"`; any other value is rejected. A release that does not change the format keeps this value. A card of an earlier version stays valid and is checked by the rules of its version, and it may not carry a member introduced in a later one. What each version adds is in [OHF 1.1](#ohf-11), [OHF 1.2](#ohf-12) and [OHF 1.3](#ohf-13). The terms used here are defined in the [glossary](glossary.md).

## Files

| File | Contents |
| --- | --- |
| [glossary.md](glossary.md) | Definitions of the terms OHF uses |
| [field-catalogue.json](field-catalogue.json) | All 219 logical paths, with definition, logical type, vocabulary, conceptual basis and field class |
| [fields.md](fields.md) | Field reference with an example for every path, generated from [field-reference.json](field-reference.json) |
| [logical-types.md](logical-types.md) | How logical types are represented |
| [references.md](references.md) | The identifier namespaces of a card and what each reference field must name |
| [related-standards.md](related-standards.md), [related-standards.json](related-standards.json) | The standards and models OHF fields draw on, with version, licence and relation to OHF |
| [mapping.md](mapping.md), [mapping.json](mapping.json) | Where each logical path is stored in a card, or why it is not |
| [gap-path-policy.json](gap-path-policy.json) | For each path, whether a gap may call the field not applicable |
| [`profiles-1.json`](../vocabularies/profiles-1.json), [`profiles-2.json`](../vocabularies/profiles-2.json) | The domain profiles a card can select, with their paths; `@2` adds `ohf:aging@1` |
| [`terms-1.json`](../vocabularies/terms-1.json) | From OHF 1.1: the closed term lists (route, control type, endpoint kind, human proximity, exclusion reason) and the taxon table of the proximity rung |
| [`hallmarks-1.json`](../vocabularies/hallmarks-1.json) | From OHF 1.1: the twelve hallmarks of aging of López-Otín et al. 2023 |
| [`predicates-1.json`](../vocabularies/predicates-1.json) | From OHF 1.2: the predicates an atom triple may use, with their labels from RO and the Biolink Model, and the Biolink qualifier slots |
| [`licence-refs-1.json`](../vocabularies/licence-refs-1.json) | From OHF 1.3: the `LicenseRef-` licence ids that OHF defines, each with the release it is defined from |
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

Each gap names its exact catalogue path, a disposition, a reason, and the search queries and inspected artifacts behind it. The path is one the schema admits as a gap path: a field whose value the schema requires takes no gap, nor does a component that is not a member of its field (`GAP_PATH_REFUSED` in `tools/check_gaps.py`).

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
| `standard_version` | The version of the card format, `"1.0"`, `"1.1"`, `"1.2"` or `"1.3"`. |
| `identity` | The proposition identifier and version, superseded versions, retractions, duplicate-cluster and representative references, and the lifecycle state. |
| `vocabularies` | The pinned vocabularies, by id and SHA-256: `ohf:heuristics@1` and `ohf:profiles@1` or `@2`. From OHF 1.1 also `ohf:terms@1`, required, and `ohf:hallmarks@1`, required with the aging profile and forbidden without it. From OHF 1.2 also `ohf:predicates@1`, required when an atom has a triple. From OHF 1.3 also `ohf:licence-refs@1`, required when `author.source.license` is a `LicenseRef-` id. |
| `facets` | Search labels for the whole card: `topic[]`, `source_class` and, in the domain profile `ohf:intervention-pharmacology@1`, `intervention_type`. |
| `author.source` | The source of the author's assertions: kind, citation, DOI (optional), URL, licence and its basis, language, retrieval time and the SHA-256 of the retrieved text. |
| `author.generator` | Who or what generated the hypothesis: `human`, `ai_system`, `hybrid` or `unknown`, and for a system its name, version and model, each null when unknown. From OHF 1.1 a machine author may add the `prompt` (an artifact reference) and `generated_at`, which may not be later than `submitted_at` (`REF_TIME_ORDER`). |
| `author.generation` | For a hypothesis from a generation run: the run identifier, how many hypotheses the run generated and submitted, and whether it submitted all of them. Each member is null when unknown or not applicable. A reader can see from it whether the hypothesis was selected from a larger set. |
| `author.submitted_at` | When the hypothesis was submitted as a card. |
| `added.by`, `added.at` | The converter that wrote the added zone, and when. From OHF 1.3 `added.by.standard_release` may name the release of the standard the card was built and checked against. |
| `added.cutoff_date` | The date up to which the converter's knowledge and searches reach, or null when unknown. |
| `added.sources` | The source records that added values point to through `src`: source, locator, access time and tool. |
| `added.budget` | The model calls, HTTP requests and tokens spent on the added zone; token counts may be null. |
| `added.completeness` | The completeness level, the layers present and what the next level still needs. |
| `added.challenge_search` | Optional. The search for evidence against the hypothesis; see [completeness](#completeness). |

A card for a hypothesis that a person wrote without a generation tool still states `author.generation`, `added.by` and `added.budget`, because the schema requires them. With `author.generator.kind` `human`, every member of `author.generation` is null, which means not applicable: there was no generation run. When the added zone was written without a language model, `added.by.model` is `"none"`, `added.budget.model_calls` is 0 and the token counts are null; these too mean not applicable, not unknown. HTTP requests are counted as for any card. The fixture `tests/fixtures/fictional/fx_nine.json` follows this convention.

**Source licence.** `author.source.license` gives the licence of the source as an SPDX identifier, and `rights_basis` says what it rests on. It is the licence that the retrieved source record states at `retrieved_at`, not a claim about the licence under which the work was first published: a publisher or archive may restate it later. A Creative Commons Attribution licence that the article's own record (its permissions) names without a version is `LicenseRef-CC-BY-version-not-stated`; the version is not guessed. It is an Attribution licence only when the record names no NonCommercial, NoDerivatives or ShareAlike term. The CC BY versions do not ask for the same attribution, so whoever reuses a source under it follows a conservative OHF rule meant to meet the requirements of any version: give the authors, the title, the source, a link to the licence and a note that the material was changed and how, and keep every copyright, licence and disclaimer notice the source supplies. The example cards quote sources under `CC-BY-1.0`, `CC-BY-2.0`, `CC-BY-2.5`, `CC-BY-3.0`, `CC-BY-4.0`, `LicenseRef-CC-BY-version-not-stated` or, from OHF 1.2, `LicenseRef-public-domain-term` (`tests/test_examples.py`). Which `LicenseRef-` ids OHF defines, and from which release, is checked as described under [OHF 1.3](#ohf-13).

**Public domain by term (OHF 1.2).** A source whose copyright term has expired has `rights_basis` `public_domain_term` and the licence `LicenseRef-public-domain-term`; SPDX has no identifier for an expired term, and a dedication such as CC0 stays `license` with its own identifier. The added zone then records what the expiry rests on in `provenance.licence`, a rights record with the basis `public_domain_term` whose `conditions` give the year of publication, the year of death of each author, or that it is not known, and each jurisdiction whose term was checked, one condition each. `tools/check_refs.py` checks that this record exists with that basis and with conditions (`REF_RIGHTS_BASIS`); what the conditions say is read, not checked. `public_domain_term` records on what the card's author bases the expiry in the jurisdictions named; it is not a legal opinion, and the format does not check it. A 1.0 or 1.1 card has neither the basis nor the identifier.

## Domain profiles

A card names its domain profile in `added.layers.profile.domain`. [`profiles-1.json`](../vocabularies/profiles-1.json) lists the profiles and their paths; [`profiles-2.json`](../vocabularies/profiles-2.json) lists the same profiles and, from OHF 1.1, `ohf:aging@1`.

- `ohf:intervention-pharmacology@1`: claims about the effect of an intervention. It holds 22 paths in two layers: the details of the intervention and the intercurrent events (14 paths, layer 3, predictions), and dose response, combinations and harm (8 paths, layer 6, profile). `facets.intervention_type` is then required.
- `ohf:aging@1` (OHF 1.1): claims about aging. It holds the 22 paths of the intervention profile and `profile.aging_hallmarks[]`: the hallmarks of aging that atoms of the card concern, each with those atoms (`REF_UNKNOWN_ID` when an atom does not exist). It needs the pins `ohf:profiles@2` and `ohf:hallmarks@1`. Unlike the intervention profile it does not require `facets.intervention_type`, because an aging claim need not name an intervention.
- `none`: no domain profile. The 22 paths are absent, and they need no gaps; a gap for one of them is rejected.

From OHF 1.2, `profile.domain` is a list of profile ids, in both zones: at least one, each named once, and `none` only alone. A path of a domain profile is selected when any named profile has it, and the rules for a selected path and for an unselected one are those above. A named profile whose paths another named profile already holds adds nothing and gets a warning (`REF_PROFILE_REDUNDANT`): `ohf:aging@1` holds every path of `ohf:intervention-pharmacology@1`. The profiles and their pins are unchanged. A 1.0 or 1.1 card names one profile as a string.

Layer 6, profile, also holds general fields that every card may use, whatever its domain profile: biomarkers, human testability, transfer scope and the function or process concerned.

## Completeness

Completeness is structural:

- `accepted`: the author's assertion is checked against source bytes, and source, licence and provenance are present.
- `comparable`: `accepted`, plus a prediction that states, across both zones, its system, endpoint, form and epistemic status, and a direction when the form is `directional_contrast`.
- `full`: `comparable`, plus a typed mechanism step, claim atoms, and evidence on both sides. If no disputing evidence is found, `added.challenge_search` records the search queries. `added.challenge_search` records the search for disputing evidence: its queries, the artifacts inspected, the outcome and the evidence lines found.

Completeness says nothing about whether the claim or its reading is correct.

`tools/check_refs.py` computes the level from these conditions and reports, for each condition that is not met, the reason. It reads them as follows:

- The level is computed from the card's own records; the tools fetch nothing. The author's assertion counts as checked against source bytes when the card records `added.source_verification.status` `refetched_match` with the stored hash. The tools rely on that record and do not repeat the refetch or compare the quotations with the source. A source that is `not_refetchable` or `refetched_mismatch` cannot show this by machine; the condition goes to `manual_review_required` with the reason.
- The source is `author.source` with its citation, URL and source text SHA-256; the licence is its `license` and `rights_basis`; the provenance is `author.generator`, `added.by` and `added.produced_by`.
- A typed mechanism step has a `subject_ref`, a `relation` and an `object_ref`, across both zones.
- Evidence is on both sides when one evidence line supports and one disputes. Without a disputing line, the search for one is recorded by `added.challenge_search` with the outcome `not_found` and its query identifiers. The gap catalogue has no path for a missing disputing line, so a gap does not stand for this search; a gap on a member of an evidence line, such as `evidence.lines[].risk_of_bias`, is about that member. A search that stopped early, with the outcome `incomplete`, goes to `manual_review_required`.
- `added.challenge_search` is optional. When it is recorded with the outcome `found`, it names a disputing evidence line.
- From OHF 1.1 a disputing line whose quote is withheld (`quote_withheld`) is counted and shown, but it does not make the disputing side for `full`: its text cannot be read against the source.

The computed level is the highest level whose conditions, and those of every lower level, are met. A declared level that a condition at or below it rules out is an error (`REF_COMPLETENESS_OVERSTATED`); a declared level below the computed one is a warning (`REF_COMPLETENESS_UNDERSTATED`). `missing_for_next` must name each condition that the next level still needs; extra or missing items are a warning (`REF_MISSING_FOR_NEXT`). The checker's report gives the conditions in the words it expects.

## Integrity

The added zone records how it was produced and checked. These members describe the record, not the hypothesis, and have no catalogue rows.

| Member | Records |
| --- | --- |
| `added.produced_by` | Who produced the added zone: `independent_pipeline`, `submitter` or `example_converter`, with pipeline name, version and an optional run identifier. |
| `added.source_verification` | Whether the source was downloaded again and compared with `author.source.source_text_sha256`: `refetched_match`, `refetched_mismatch` or `not_refetchable` with a reason. A refetch gives its URL, time and SHA-256. An optional `metadata_check` records a registry lookup, such as Crossref: DOI and title match, and whether a retraction is listed. |
| `added.integrity.entailment[]` | Whether the source supports each added value: a JSON pointer to the value, the basis checked (`src` or `basis_quote`, and from OHF 1.2 `resolution`), a verdict (`entails`, `partial` or `no`, the last two with a note), the checker with its version and the SHA-256 of what it ran (a model checker's prompt; from OHF 1.2 a tool checker's tool), and the time. |

Rules:

- `refetched_match` requires the refetched SHA-256 to equal `author.source.source_text_sha256`; `refetched_mismatch` requires it to differ (`REF_SOURCE_MISMATCH`).
- The entailment checker is not the pass that wrote the added zone: its name differs from `added.by.converter`, and the SHA-256 of what it ran (its prompt, or from OHF 1.2 its tool) differs from `added.by.converter_hash` (`REF_CHECKER_NOT_INDEPENDENT`).
- Each entailment pointer resolves to a sourced added-zone value, once per basis. From OHF 1.2 it may also name a member of a sourced value, and a record with basis `resolution` names a value checked by resolution, which is checked against its external record rather than a `src`; see [OHF 1.2](#ohf-12).
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

- `ohf:hypothesis-relations@1` ([schema](../schema/hypothesis-relations-1.schema.json)) records typed edges between card versions in a fixed pool: `rival_same_explanandum`, `nested`, `compatible_independent`, `duplicate`, `refines`, `unrelated`, and from OHF 1.1 `analog` and `mechanism_neighbour`. Support and contradiction are evidence relations, not relations between hypotheses, and are not included. Within one card, from OHF 1.1, `core.atoms[].requires` and `core.atoms[].contradicts` link atoms of that card.
- `ohf:pair-brief@1` ([schema](../schema/pair-brief-1.schema.json)) describes two card versions side by side: their relation, the observations both explain, the observations they expect differently, and a decisive test or a gap saying why none is known. It does not judge which hypothesis is better.

Definitions of the relation types, from OHF 1.1. Source and target are card versions, or from OHF 1.1 one record of each, such as an atom, named by `pointer`:

| Type | The source and the target |
| --- | --- |
| `rival_same_explanandum` | explain the same observation, and as stated they cannot both be its main explanation |
| `nested` | the source is a special case of the target: what the source states, the target states for a wider scope |
| `compatible_independent` | can both hold, and neither depends on the other |
| `duplicate` | state the same claim for the same scope |
| `refines` | the source is a revision of the target: the same claim stated more precisely, more narrowly or corrected |
| `unrelated` | were compared and stand in none of the other relations |
| `analog` | make the same kind of claim about different agents or systems that share what the claim depends on, such as two compounds with the same molecular target and class (OHF 1.1) |
| `mechanism_neighbour` | make different claims that act through the same or an adjacent mechanism, without being rivals or nested (OHF 1.1) |

An edge between records describes those records only: two atoms of two cards can be compatible while the cards are rivals.

From OHF 1.1 an edge may list `scope_differs`: the `endpoint`, `population` or `system` on which the two cards differ, each with a pointer to the field in the source card and in the target card. Two rivals that measure different outcomes, or study different taxa, are not in flat contradiction, and the edge says so as data. `tools/check_relations.py` checks a relations artifact against the cards it names: each end names a given card by `content_hash` (`REL_CARD_MISSING`), every pointer resolves (`REL_POINTER_UNRESOLVED`), each `scope_differs` pointer is a field of its aspect (`REL_SCOPE_FIELD`), and the two fields differ once source wrappers are removed (`REL_SCOPE_SAME`).

A scope pointer starts at `/author/layers` or `/added/layers` and names one of these fields, or a value inside one:

| Aspect | In `predictions[n]` | In `evidence/lines[n]` | In `profile/dose_response` |
|---|---|---|---|
| `endpoint` | `endpoint`, `endpoint_kind` | `endpoint_kind` | `endpoint_ref` |
| `population` | `population` | `sample`, `sample_size`, `study_system` | — |
| `system` | `system` | `system`, `study_system` | — |

`study_system` belongs to two aspects, because a study's system names both the organism and the group studied. A pointer may go through a wrapper only by its `value`. It may not name, or pass through, `src`, `locator`, `assessment`, `assessment_status`, `provenance`, `basis_quote`, `paraphrase` or `confidence`. For `REL_SCOPE_SAME` the two values are compared after every wrapper is replaced by its `value` and those members are removed. So the same endpoint taken from two sources is the same.

A pair brief repeats the relation of its two card versions. The relations artifact is the record of that relation: if a pair brief and a relations artifact disagree about the same two card versions, the relations artifact holds and the pair brief must be corrected.

Examples are described in [`examples/README.md`](../examples/README.md).

## OHF 1.1

OHF 1.1 is a minor version. Every new member is optional, except that a 1.1 card pins `ohf:terms@1` and gives the closed `term` where it records a route or an endpoint kind in the added zone. A 1.0 card stays valid and is checked by the 1.0 rules: it may not carry a member introduced in 1.1, a `term` or `note` on a route or endpoint kind, or a `terms` pin, and a gap of a 1.0 card may not name a field of 1.1 or a component of one (`GAP_PATH_UNKNOWN`). The fields of 1.1 are marked `since: "1.1"` in the [field catalogue](field-catalogue.json). The one relaxation is stated below under *Novelty*. The rules are enforced by the schema unless a code of `tools/check_refs.py`, `tools/check_gaps.py` or `tools/check_relations.py` is named.

**Closed terms.** In the added zone a route (`predictions[].intervention.route`, `evidence.lines[].intervention.route`) and an endpoint kind (`predictions[].endpoint_kind`, `evidence.lines[].endpoint_kind`) keep the source wording in `value` and add `term` from [`terms-1.json`](../vocabularies/terms-1.json). A `note` is given exactly when the term is `other`. `predictions[].control_type` lists control types (`Term[]`); `none` and `not_stated` may not be combined with other types. In 1.1 `endpoint_kind` classifies the endpoint by what is measured: lifespan, mortality, function, disease, biomarker, physiological, molecular, behaviour, adverse event.

**Conditions of an evidence line.** A line may state the system and the intervention of the study behind it, with the same members as a prediction, an NCBI Taxonomy id (`system.taxon_id`), the `sample_size` and a `multi_site_program` (programme and number of sites, at least two). The intervention of a line is not gated by the domain profile: it describes the study, not the claim. When the quote names a dose or an age that the line neither records nor gives a gap for, `REF_CONDITION_IN_QUOTE` is a warning.

**Sample of a result.** `evidence.lines[].sample` says whether the result is about the whole sample or a named subgroup, whether the outcome is primary or secondary, and whether the analysis was pre-specified or post hoc; `not_stated` where the source does not say.

**Result estimate.** In 1.1 the added-zone `result_estimate.value` is an object: the reported text and the measure, contrast and scale as the source states them, or `not_stated`. When the quote reports a result in numbers and the line has neither an estimate nor a gap whose disposition is other than `not_supplied`, `REF_ESTIMATE_IN_QUOTE` is an error. A quote reports a result in numbers when it contains any of the following, matched case-sensitively except where stated, with an optional single space between the parts:
- a number followed by `%`;
- a p-value: `p` or `P`, then `<`, `=`, `>`, `≤` or `≥`, then a decimal;
- a confidence interval: two digits, `%` and `CI`, or `CI` alone;
- a fold change: a number and `fold` or `-fold`;
- `HR`, `OR`, `RR`, `IRR` or `SMD` followed by `=`, `:` or `(`;
- `η2` or `ηp2`, `md =`, `β =`;
- a correlation, `r =` followed by a decimal.

The expression is `RESULT_NUMBER` in `tools/check_refs.py`. A dose (a number with mg/kg, mg, µg, ppm, µM, nM, mM or IU) or an age (`N days|weeks|months|years of age|old`, or `starting|beginning|started|from at N …`) in the quote that the line does not record gives `REF_CONDITION_IN_QUOTE`. An estimate whose reported text is not in the quote is also an error (`REF_ESTIMATE_NOT_QUOTED`).

**Proximity to humans.** `evidence.lines[].human_proximity` is the rung of the line: in vitro, ex vivo, invertebrate, non-mammal vertebrate, mammal, human marker, human clinical. It follows from the line's conditions. For a taxon in the table of `terms-1.json` (or in rows given with `--taxa`, which add rows and never override one) the rung is derived; for humans the endpoint kind decides between marker (biomarker, physiological, molecular) and clinical (lifespan, mortality, function, disease, adverse event); with `behaviour`, `other` or no endpoint kind the human rung is not determined. A rung that differs from one derived from the pinned table is an error (`REF_PROXIMITY_MISMATCH`). A rung that differs from one derived only from a `--taxa` row is a warning with the same code, so the option never makes a card invalid. A rung that cannot be derived is a warning (`REF_PROXIMITY_NOT_DERIVED`). In vitro and ex vivo are taken as stated.

**Alternatives and list elements.** Elements of `core.alternative_explanations` may have an `id`, and an evidence line or an excluded record may target one. Elements of `alternative_explanations`, `uncertainties`, `opens` and `explains` may carry their own `src` (added zone) or `locator` (author zone), so an entailment record can name one element. An element without its own `src` is read from the `src` of its list, and an entailment record for it names the list; an element with its own `src` is read from that `src`, and a record may name the element (`REF_WRONG_TARGET` for a record that names an element without one).

**Novelty.** `core.novelty_assessment.status` may be `known_result`: the card restates a known result. It requires `prior_claim_refs` (at least one), `search_scope_ref` and `as_of`, and forbids `new_content`. **This is the one relaxation of 1.1:** in 1.0 every novelty assessment requires `new_content`; in 1.1 a `known_result` assessment does not, and every other status still does.

**Excluded evidence.** `evidence.excluded[]` records a source passage that was considered and not carried as a line: its target, a reason from `terms-1.json` (`note` exactly when `other`), the quote, `src`, and where the passage was found: an `artifact`, a `record`, or both, at least one.

**Atoms.** `core.atoms[].requires` and `.contradicts` name atoms of the same card; an atom may not name itself and `requires` may not form a cycle (`REF_ATOM_LINK`). `a requires b` means that `a` cannot hold unless `b` holds; it is directed. `a contradicts b` means that the two cannot both hold; it is symmetric, whether it is recorded on one atom or on both. `core.atoms[].triple` reads the atom as subject, relation and object for machine linking: the relation is an RO id or a Biolink slot, subject and object are a CURIE with a label or an `entity_ref` to `mechanism.entities` (`REF_UNKNOWN_ID`, `REF_WRONG_TARGET`), and qualifiers are Biolink qualifier slots. The statement stays the claim.

**Gaps for empty lists.** A gap may name a whole list that is empty, such as `core.assumptions` (`tools/check_gaps.py`). Lists of `identity` take no gap. 1.0 forbids these paths.

**Independence across cards.** `evidence.lines[].independence_group.key` names where the data of the group first appeared (DOI, PMID, PMCID, registry or accession, each with its pattern). Within a card one label has one key and one key one label, and once one line of a group gives a key every line of that group gives it (`REF_INDEPENDENCE_KEY`). A DOI is compared without regard to case; other identifiers exactly. Lines of two cards with the same key rest on the same data.

**Withheld quote.** `evidence.lines[].quote_withheld` replaces the quote when the text may not be quoted: licence unknown, CC BY-NC-ND, or no open text. It gives the locator, the record (DOI or PMID), a paraphrase in the added zone and the sentence of the abstract that entails it. A line has a quote or a withheld quote, not both. See completeness above.

**Relations.** See [Relations and pair briefs](#relations-and-pair-briefs): edges between atoms by `pointer`, the types `analog` and `mechanism_neighbour`, and `scope_differs`.

## OHF 1.2

OHF 1.2 is a minor version. Every new member is optional. 1.0 and 1.1 cards stay valid and are checked by their own rules, and they may not carry a member introduced in 1.2. A 1.2 card follows every rule of 1.1, with one change of form: its `profile.domain` is a list of profiles, not one string ([Domain profiles](#domain-profiles)). The rules are enforced by the schema unless a code of `tools/check_refs.py`, `tools/check_ledger.py` or `tools/check_mapping.py` is named.

**How a value is checked.** Each row of the [field catalogue](field-catalogue.json) has a `check`:

- `passage`: the value is checked against the paragraph its `src` names, by an entailment checker;
- `resolution`: the value is checked against an external record, by a tool;
- `card`: the value is checked against the card itself, by `tools/check_refs.py`, and no record is written for it.

The values checked by resolution are NCBI Taxonomy ids (`predictions[].system.taxon_id`, `evidence.lines[].system.taxon_id`), the rung `evidence.lines[].human_proximity`, the independence key `evidence.lines[].independence_group.key`, and the licence reason and record of a withheld quote. The values checked against the card are identifiers and references, among them `evidence.lines[].target_ref`, `core.atoms[].requires` and `.contradicts`, `predictions[].derives_from_atom_refs[]` and the label of `evidence.lines[].independence_group`. A row may give a check for each member of its value instead: `evidence.lines[].quote_withheld` is checked member by member, its `paraphrase` and `abstract_quote` against the passage, its `reason` and `record_ref` by resolution, and its `locator` against the card. Every row has a check, and the members of such a row are those of the schema (`tools/check_mapping.py`).

**The value a record names.** An entailment record names a value by its JSON pointer. The catalogue row of the pointer is found by dropping `/added/layers`, writing array indices as `[]` and dropping the `value` segment of a source wrapper; a value with no row of its own takes the check of the nearest row above it. In a 1.2 card a record may name a member of a sourced value (`…/quote_withheld/value/paraphrase`): a member checked against the passage takes the `src` of the value.

**Records by check.** In a 1.2 card:

- a record with basis `src` or `basis_quote` names a value checked against the passage, and a record with basis `resolution` a value checked by resolution; any other record is `REF_BASIS_KIND`, and so is a record on a whole value that is checked member by member. This rule comes before the rule that a record names a sourced value, so a record on a reference fails as `REF_BASIS_KIND`;
- the checker has a `kind`: `model` (the default, with `name`, `version` and `prompt_sha256`) for a record checked against a passage, and `tool` (with `name`, `version` and `tool_sha256`, and no `prompt_sha256`) for a record checked by resolution. A tool checker's independence is that it compares the value deterministically with an external record, bound to the record by `resolved_against`: the same checked value, read in the same card, with the same response, key and tool, gives the same verdict. The value itself is part of that input: for `human_proximity` the key is the line's taxon id, and the same response gives `entails` for the rung it supports and `no` for another. Another name does not make a check independent. In addition, as for a model checker, its name differs from `added.by.converter` and its `tool_sha256` from `added.by.converter_hash` (`REF_CHECKER_NOT_INDEPENDENT`);
- a resolution record has the verdict `entails` (the record was retrieved, matched one entry and agrees with the value) or `no` (it was retrieved, matched one entry and contradicts the value), never `partial`. It gives `resolved_against`: the `source` record in `added.sources`, the `response_sha256` of that response, which equals the `sha256` of the source record, and the `key` that was looked up (`REF_SOURCE_UNKNOWN`, `REF_RESOLUTION_BINDING`). The key is the value itself for a taxon id, the `id` of an independence key or of a withheld quote's record, the record's id for a withheld quote's licence reason, and the line's taxon id for a rung; it is compared without regard to case. A resolution record is not older than the access time of its source record, nor, as any record, than the nearest assessment of its value (`REF_TIME_ORDER`);
- when the external record could not be retrieved, or did not match exactly one entry, no record is written. A value checked by resolution with no record is reported as not checked (`REF_NOT_RESOLVED`, a warning);
- a source record in `added.sources` may give the `sha256` of the response it records.

**What a line bears on.** In a 1.2 card `evidence.lines[].target_ref` and `evidence.excluded[].target_ref` are references without a `src`. Whether a line bears on its target is the question of its `direction`, which is checked with the target's statement: an atom's statement; a prediction's population, endpoint and direction; a mechanism step's subject, relation and object; an alternative explanation's claim; or the proposition's statement, named by a pointer or by the card's own versioned reference (`target_statement` in `tools/check_ledger.py`, which also reads the sourced `target_ref` of a 1.1 card). A versioned reference to another card is given as it stands. The ledger hash of a direction check covers that statement, so a line given another target, or whose target's statement changes, no longer matches its check.

**Ledgers.** For a 1.2 card `tools/check_ledger.py` rebuilds and checks only the values checked against a passage, including each such member of a value checked member by member; records with basis `resolution` are not ledger entries.

**Closed predicates.** In a 1.2 card the relation of an atom triple (`core.atoms[].triple`) is a predicate of [`predicates-1.json`](../vocabularies/predicates-1.json) (`ohf:predicates@1`), and its label is that predicate's label there (`REF_PREDICATE_LABEL`). A qualifier names one of the qualifier slots listed there. A 1.2 card with a triple pins `ohf:predicates@1`; a 1.0 or 1.1 card may not pin it and keeps the open relation of 1.1. Each predicate has its id and label as the ontology release states them (RO, release 2026-09-04; Biolink Model 4.4.6), its inverse where the ontology gives one, and its kind: `causal`, `regulatory` or `associative`. The list holds every predicate the example cards and fixtures use and a small set of RO causal and regulatory relations. It has no `other`: when no predicate fits, the triple is not written, and the gap `core.atoms[].triple` with disposition `not_supplied` names the relation in its reason. Whether the subject and object are of the kinds the predicate expects is not checked.

**Atom scope.** In a 1.2 card an added-zone atom may have a `scope` (`core.atoms[].scope`): the systems and conditions to which this atom applies when they are narrower than `core.scope`, as a sourced text with its `src`, checked against its passage. An atom without it has the scope of the card and needs no gap. A gap on `core.atoms[].scope` says that the passage gives the atom a narrower scope which the card does not record, with the reason. It narrows the card scope and never widens it; whether it does is read in the passage, not checked mechanically. An atom scope with the same text as the card scope narrows nothing and gets a warning (`REF_ATOM_SCOPE_SAME`). `context_override` records how a child atom's conditions differ from its parent's; `scope` records which systems the atom covers. A 1.0 or 1.1 card has no atom scope and no gap on it.

**The claim author's interests.** In a 1.2 card `provenance.claim_author_coi` records the funding and conflict-of-interest declarations of the author whose claim the card records, as the source states them, in the same record as `evidence.references[].funding_coi`: funders, and a declaration that is a text, `none_declared` or `not_reported`. A cited work's declarations stay in `evidence.references[].funding_coi`.

**Data availability.** In a 1.2 card an evidence line may have `data_availability`: whether the data on which the line rests can be obtained, as the source states it. `availability` is `public`, `on_request` or `not_available`; `restriction` says what limits access, and `route`, required for `on_request`, says how the data are obtained. It is checked against its passage.

**An entry of the reference list.** A source record may name an entry of the source's own reference list, for example `XML .//ref[@id='r7']` in a JATS document, as it may name a paragraph. A value whose basis is the cited work, such as the independence group of a line that cites observations of that work, then has that entry as its `src`, so it is checked against the entry and not against the paragraph that carries only the citation marker. The locator is a string; the format does not parse it.

A 1.0 or 1.1 card has neither `claim_author_coi` nor `data_availability`, and no gap on them.

## OHF 1.3

OHF 1.3 is a minor version. Every new member is optional. 1.0, 1.1 and 1.2 cards stay valid and are checked by their own rules, and they may not carry a member introduced in 1.3. A 1.3 card follows every rule of 1.2. The rules are enforced by the schema unless a code of `tools/check_refs.py` is named.

**The release a card was built against.** `standard_version` names the version of the card format, major and minor. Whether a value is allowed can depend on the patch release: `LicenseRef-CC-BY-version-not-stated` is defined from 1.1.4. A 1.3 card may therefore name the release in `added.by.standard_release`: `version`, the full release such as `1.3.0`, and optionally `commit`, the 40-character commit of the tag `v<version>` in the repository of the standard. The release is of the card's minor version (`REF_RELEASE_VERSION`), and it is one that the checking tool knows from the release headings of its CHANGELOG and not newer than its `VERSION` (`REF_RELEASE_UNKNOWN`). The commit is not resolved. Without `standard_release` the release is not stated; it needs no gap, and nothing is inferred.

**Licence ids that OHF defines.** SPDX has no id for some licences a source states, so OHF defines its own `LicenseRef-` ids in [`licence-refs-1.json`](../vocabularies/licence-refs-1.json) (`ohf:licence-refs@1`), each with its meaning and `since`, the release it is defined from: `LicenseRef-CC-BY-version-not-stated` from 1.1.4 and `LicenseRef-public-domain-term` from 1.2.0. A new id comes only with a release of the standard. A 1.3 card whose `author.source.license` is a `LicenseRef-` id pins `ohf:licence-refs@1`; a 1.0, 1.1 or 1.2 card may not pin it. `tools/check_refs.py` checks the licence of a card of any version. A `LicenseRef-` id, in any letter case, that is not in the vocabulary has no meaning a reader could take (`REF_LICENCE_REF_UNKNOWN`). An id defined from a later release than the card can know is `REF_LICENCE_REF_RELEASE`: one whose `since` is of a later minor version than `standard_version`, and in a 1.3 card that names its release, one whose `since` is later than `standard_release.version`. Without a stated release a later patch of the card's own minor version cannot be told apart, and it is not reported: a 1.1 card with the id of 1.1.4 passes. Both are errors in a 1.3 card and warnings in a 1.0, 1.1 or 1.2 card, so a released card stays valid. Any other licence has the form of an SPDX id, letters, digits, `.`, `-` and `+`; a value of another form gets a warning (`REF_LICENCE_FORM`). The list of SPDX ids is not checked, and the format does not say which licences are open.
