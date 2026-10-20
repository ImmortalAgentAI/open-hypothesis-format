# Source-literal logical types

## Primitive values

Primitive values are explicitly typed. Source wrappers and the source binding of a containing record are kept. Identity metadata uses the Identifier, Version, VersionReference, Retraction, Reference and Term types. The cluster and representative references may be null. A root atom's `parent_ref` is null; this null is structural and is not a fabricated parent reference. Source fields of the generator record, such as the system and model that produced a hypothesis, may be null.

## Source-literal records

Quantities, intervals, assessments and other source-text records are nonblank source-literal strings. OHF 1.0 does not define normalized structures for them. Scientific values are not rewritten.

The following record forms are closed:

- qualifier kind and text;
- source artifact and attribution;
- field source;
- contribution;
- confidence interval.

Unknown record keys are rejected. So are arbitrary objects, boolean or numeric substitutes for text, and empty literals.

`RightsRecord` holds either the licence text as the source states it or a `RightsTerms` record of what the recorded terms allow. Neither grants permission to publish. A `RightsTerms` record has these members; `publication_allowed`, `spdx`, `basis` and `conditions` are required:

- `publication_allowed`: whether the recorded terms allow publication; `null` when not established;
- `usage`: `publication_permitted_under_recorded_terms`, `publication_not_confirmed`, `publication_not_permitted`, or `internal_only` (the material may be used but not published);
- `basis`: `license` (a licence, named by `spdx` where it has an SPDX identifier), `permission_with_attribution` (a permission recorded by the publisher of the card, with the attribution it requires; `spdx` is then null), or `unknown`;
- `conditions`, `attribution`, `scope`, `label` and `url`: the conditions, the required attribution, what the terms cover, a readable name and the address of the terms.

The schema enforces consistency: permitted usage requires `publication_allowed: true` and a `license` or `permission_with_attribution` basis, and `publication_not_permitted` or `internal_only` requires `publication_allowed: false`.

`evidence.references[].access_context` records how a cited source was read: `source_ref` (the artifact read, or an unavailable record with its label and reason), `text_scope` (`abstract`, `full_text`, `supplement`, `metadata` or `unknown`), `truncated`, `inspected_locator_range` (byte or code-point ranges, or null for the whole text), `retrieval_status` (`retrieved`, `failed`, `excluded` or `unknown`), optional `alternate_source_refs` and `limitation`, and `retrieval_record_ref`, the artifact that records the retrieval itself.

The catalogue type of the observable component is Text. Its parent test record requires five sourced components: `observable`, `h0`, `h1`, `test` and `status`.

## Schema definitions

The card schema names these shared definitions in `$defs`. The `Logical:` definitions implement the logical types of the [catalogue](field-catalogue.json); the `extended:` definitions belong to the fields of the [scientific field extensions](../schema/scientific-field-extensions.schema.json).

The definitions named `author:<path>`, `added:<path>`, `extended:author:<path>` and `extended:added:<path>` are per field: each holds one catalogue path in the author or added zone, and they are not listed here.

| Definition | What it holds |
| --- | --- |
| `artifact_ref`, `extended:artifact_ref` | A reference to retained bytes: `kind: "artifact"`, their `sha256` and an optional JSON pointer into them. |
| `reference`, `extended:reference` | A reference to one of four targets, named by `kind`: a value in the same card (`card`, with a JSON `pointer`), retained bytes (`artifact`, as `artifact_ref`), an external resource (`external`, with a `uri` and a `limitation`), or a source that could not be obtained (`unavailable`, with a `label` and a `reason`). |
| `assessment`, `extended:assessment` | Who made a judgement and on what: the `assessor`, the `assessed_at` time and an `evidence_ref` to the retained bytes it was made from. |
| `Gap` | One entry of `added.gaps`: the catalogue `path`, a `disposition`, a `reason`, the `query_ids` and `inspected_artifacts` behind it, and a `scope_ref` when the disposition is `not_applicable_scope`. A `searched_not_found` gap names at least one query. See [Gaps](README.md#gaps). |
| `Logical:SourceText` | A nonblank string, kept as the source gives it. |
| `Logical:EvidenceItem` | One item of an evidence line: source text, a `Logical:EvidenceArtifact` or a `Logical:EvidenceAttribution`. |
| `Logical:EvidenceArtifact` | A retained artifact named by `artifact`, its `sha256` and a `locator` inside it. |
| `Logical:EvidenceAttribution` | Why an evidence line has its agent type and knowledge level: `line_id`, `agent_type_scope`, `agent_justification` and `knowledge_level_justification`. |
| `Logical:SourceExtension` | One retained external section in `appendix.source_extensions`: source text, a `Logical:ProtocolDiscrepancy` or a `Logical:RelatedArtifact`. |
| `Logical:ProtocolDiscrepancy` | A stated difference between a protocol and what was done: its `kind`, `details` and source `locators`. |
| `Logical:RelatedArtifact` | A related artifact with its `role` and the SHA-256 of its retained bytes. |
| `ChallengeSearch` | `added.challenge_search`: the query identifiers, the artifacts inspected, the `outcome` (`found`, `not_found` or `incomplete`) and the evidence lines found. |
| `TestRecordAuthor`, `TestRecordAdded` | One intermediate test in `predictions[].intermediate_tests[]`, in the author or added zone: `observable`, `h0`, `h1`, `test` and `status` (`planned`, `registered`, `ongoing`, `completed`, `stopped` or `unknown`), with an optional `validity_justification`. |
| `extended:MoneyRange` | A cost range: `low` and `high` (not negative), a three-letter `currency` code and the price `year`. |
| `extended:Duration` | A positive `value` with its `unit`. |

## Extension records

The [scientific field extensions](../schema/scientific-field-extensions.schema.json) also define the records that an artifact reference in those fields can point to. Each record names its form in `schema`. The schema checks the shape of a record, not that its contents are true.

| Definition | `schema` | What it holds |
| --- | --- | --- |
| `retrieval_record` | `ohf:retrieval-record@1` | One retrieval of a source: what was received, the response kind and HTTP status, when and by whom, and which byte or code-point ranges were delivered and inspected. `evidence.references[].access_context.retrieval_record_ref` points to such a record. |
| `search_record` | `ohf:search-record@1` | A bounded search: the cutoff, the sources searched, and each query with its time, status, results and the SHA-256 of the saved response. `core.novelty_assessment.search_scope_ref` points to such a record. |
| `expert_review_record` | `ohf:expert-review@1` | A review by a human expert: the assessor, the target, the scope, and quotations with locators from the review and from the record of the assessor's expertise. `core.novelty_assessment.review_ref` points to such a record. |
| `assessment_record` | `ohf:assessment-record@1` | One attributed assessment: the assessor and its kind, the time, the target, the statement, and the source quotation with its locator. |
| `assessment_evidence` | | Either an `expert_review_record` or an `assessment_record`. |

## Paraphrases

An added source-text value may carry `paraphrase: true` together with `basis_quote`, but only when the value is a string. Author source strings stay verbatim. Paraphrase metadata does not turn a paraphrase into an author quotation, and it requires a non-null source.

A resolver must check the selected source and the exact supporting quote for every paraphrase. The schema shape does not establish support.

## What the schema does not check

These compound forms do not establish scientific entailment, interval order, permission or coverage. An implementation must check those properties separately.

Record-level scalar fields that are bound to a source keep their scalar spelling with type constraints. A resolver binds them through the containing record. A valid scalar never establishes source support on its own.
