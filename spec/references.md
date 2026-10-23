# Identifiers and references

A card names its own records by identifier or by card pointer. This page lists the identifier namespaces of a card and what each reference field must name. [`tools/check_refs.py`](../tools/check_refs.py) applies these rules; the vocabulary of each field is in the [field reference](fields.md).

Paths are logical paths, the same in both zones. A card pointer is a `reference` with `kind: "card"`; `N` stands for an array index and `<zone>` for `author` or `added`.

## Namespaces

An identifier is unique within its namespace and zone (`REF_DUPLICATE_ID`). The same identifier in the author and added zones names one record, seen from both zones.

| Namespace | Identifier | Card pointer of one record |
| --- | --- | --- |
| atoms | `core.atoms[].id` | `/<zone>/layers/core/atoms/N` |
| predictions | `predictions[].id` | `/<zone>/layers/predictions/N` |
| evidence lines | `evidence.lines[].id` | `/<zone>/layers/evidence/lines/N` |
| mechanism entities | `mechanism.entities[].id` | `/<zone>/layers/mechanism/entities/N` |
| mechanism steps | `mechanism.steps[].id` | `/<zone>/layers/mechanism/steps/N` |
| assumptions | `core.assumptions[].id` | |
| uncertainties | `core.uncertainties[].id` | |
| explained observations | `core.explains[].id` | |
| reinterpretations | `core.reinterprets[].id` | |
| opened questions | `core.opens[].id` | |
| alternatives (OHF 1.1) | `core.alternative_explanations[].id` | `/<zone>/layers/core/alternative_explanations/value/N` |
| excluded records (OHF 1.1) | `evidence.excluded[].id` | `/added/layers/evidence/excluded/N` |

These records have no identifier and are named by card pointer only:

| Record | Card pointer |
| --- | --- |
| an alternative explanation without an identifier (OHF 1.0) | `/<zone>/layers/core/alternative_explanations/value/N` |
| the proposition of the card | `/<zone>/layers/core/statement` |
| the experiment plan | `/<zone>/layers/appendix/experiment_plan` |

These values look like identifiers but are not card-local namespaces: `mechanism.molecular_targets[].id`, an identifier in the registry named by `id_scheme`; `evidence.references[].identifier`, a DOI, PMID or accession; and `evidence.lines[].independence_group`, a label that lines share on purpose.

## Reference forms

- **Identifier**: a string that is an identifier of the named namespace. An identifier of another namespace is the wrong target (`REF_WRONG_TARGET`); an identifier of no namespace is unknown (`REF_UNKNOWN_ID`). An identifier that names records of two kinds the field accepts is ambiguous (`REF_WRONG_TARGET`).
- **Card pointer**: it resolves to a filled value (`REF_UNRESOLVED`) and, where the field names a kind, to one record of that kind (`REF_WRONG_TARGET`).
- **Versioned proposition**: a string `h_<id>@<version>`, the form of `identity.supersedes[]`. The card's own identifier and version name the card's proposition; any other is listed as external.
- **External**: an `external`, `artifact` or `unavailable` reference. It is listed, not fetched.
- **Text**: a free label, such as a preregistration identifier. It is not resolved.

A form that a field does not allow is the wrong target. A card pointer in a field not listed below must resolve.

## Typed reference fields

| Field | Must name | Forms |
| --- | --- | --- |
| `core.atoms[].parent_ref` | an atom; null for a root atom. An atom is not its own ancestor. | identifier, card pointer, versioned proposition, external |
| `core.explains[].atom_refs[]` | an atom | identifier |
| `core.explains[].prediction_refs[]` | a prediction | identifier |
| `core.reinterprets[].atom_refs[]` | an atom | identifier |
| `core.opens[].atom_refs[]` | an atom | identifier |
| `core.alternative_explanations[].distinguishing_prediction_refs[]` | a prediction | card pointer, external |
| `mechanism.steps[].subject_ref` | a mechanism entity | identifier, card pointer |
| `mechanism.steps[].object_ref` | a mechanism entity | identifier, card pointer |
| `mechanism.steps[].evidence_refs[]` | an evidence line | identifier, card pointer |
| `mechanism.molecular_targets[].entity_ref` | a mechanism entity | identifier |
| `predictions[].derives_from_atom_refs[]` | an atom | identifier |
| `predictions[].known_result_ref` | an evidence line | card pointer, external |
| `predictions[].also_expected_under[]` (`kind: "alternative"`) | an alternative explanation | card pointer, external |
| `predictions[].test_plan_ref` | the experiment plan, or a preregistration | card pointer, external, text |
| `evidence.lines[].target_ref` | an atom, a prediction, a mechanism step, an alternative explanation (OHF 1.1) or the proposition | identifier, card pointer, versioned proposition, external |
| `evidence.lines[].items[].line_id` | an evidence line | identifier |
| `evidence.excluded[].target_ref` (OHF 1.1) | what the excluded record was found for: an atom, a prediction, a mechanism step, an alternative explanation or the proposition | identifier, card pointer, versioned proposition, external |
| `profile.dose_response.endpoint_ref` | a prediction | identifier, card pointer, versioned proposition, external |
| `added.challenge_search.evidence_refs[]` | an evidence line | card pointer |

## Open reference fields

The vocabulary of these fields names no namespace. A card pointer must resolve; an `external`, `artifact` or `unavailable` reference is listed as external, and a string is not resolved.

| Field | Names |
| --- | --- |
| `core.explains[].observation_ref` | the observation |
| `core.explains[].rival_ref` | the rival explanation |
| `core.reinterprets[].finding_ref` | the finding |
| `core.uncertainties[].target_ref` | what the uncertainty concerns |
| `core.uncertainties[].resolution_test_ref` | a test that could resolve it |
| `core.alternative_explanations[].claim_or_ref.ref` | the alternative claim |
| `core.alternative_explanations[].shared_observation_refs[]` | an observation both accounts explain |
| `core.first_proposed.source_ref` | the source of the first proposal |
| `core.testability.cheapest_test.ref` | the cheapest test |
| `core.novelty_assessment.prior_claim_refs[]` | a prior claim |
| `core.potential_benefit.target_refs[]` | a target of the benefit |
| `predictions[].resolution.resolves_by.event_ref` | the resolving event |
| `evidence.lines[].risk_of_bias.tool_ref` | the risk-of-bias tool |
| `evidence.references[].access_context.alternate_source_refs[]` | another copy of the source |
| `provenance.inspiration_refs[]` | a source of inspiration |
| `profile.harm` | the harm endpoint |

## Other references

| Field | Rule | Checked by |
| --- | --- | --- |
| `src` of an added-zone value or record | a key of `added.sources` (`REF_SOURCE_UNKNOWN`); an empty `added.sources` with any `src` is also `REF_SOURCES_EMPTY` | `check_refs.py` |
| `locator` of an author-zone value | a place in the text of `author.source`. OHF 1.0 defines no locator syntax, so locators are not resolved. | none |
| `added.integrity.entailment[].pointer` | a sourced added-zone value, once per basis; from OHF 1.1 also an element of `core.alternative_explanations`, `core.uncertainties`, `core.opens` or `core.explains` that carries its own `src`, or a record of `evidence.excluded` | `check_refs.py` |
| `added.gaps[].scope_ref` | filled scientific card content | `check_gaps.py` |
| `provenance.parent_refs[]`, `identity.supersedes[]` | other versions of propositions, `h_<id>@<version>` | not resolved |
| `identity.duplicate_cluster_ref`, `identity.representative_ref` | records kept by the publisher | not resolved |
| `evidence_ref` of an assessment, and other `artifact` references | retained bytes outside the card | not resolved |
