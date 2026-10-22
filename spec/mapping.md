# Standard mapping

The catalogue distinguishes logical scientific fields from their storage. A direct target identifies a field representation, not evidence support or completeness. Deferred rows have no implemented serialization; source/provenance containers cannot substitute for them. The pair relation is stored in a detached relations artifact, and the hypothesis references and the decisive test of a pair in a pair brief; neither is part of the card.

| Catalogue path | Card paths | Status | Extension |
| --- | --- | --- | --- |
| `identity.proposition_id` | `identity.proposition_id` | system identity |  |
| `identity.version` | `identity.version` | system identity |  |
| `identity.question_refs[]` |  | unresolved question registry extension | A reference to a question is not a context qualifier. No question-registry serialization is implemented in OHF 1.0. |
| `identity.assertions[].id` |  | unresolved assertion registry extension | No typed assertion-registry serialization is implemented in OHF 1.0. General source or provenance metadata does not represent this assertion component. |
| `identity.assertions[].text` |  | unresolved assertion registry extension | No typed assertion-registry serialization is implemented in OHF 1.0. General source or provenance metadata does not represent this assertion component. |
| `identity.assertions[].agent_ref` |  | unresolved assertion registry extension | No typed assertion-registry serialization is implemented in OHF 1.0. General source or provenance metadata does not represent this assertion component. |
| `identity.assertions[].asserted_at` |  | unresolved assertion registry extension | No typed assertion-registry serialization is implemented in OHF 1.0. General source or provenance metadata does not represent this assertion component. |
| `identity.assertions[].stance` |  | unresolved assertion registry extension | No typed assertion-registry serialization is implemented in OHF 1.0. General source or provenance metadata does not represent this assertion component. |
| `identity.assertions[].confidence` |  | unresolved assertion registry extension | No typed assertion-registry serialization is implemented in OHF 1.0. General source or provenance metadata does not represent this assertion component. |
| `identity.duplicate_cluster_ref` | `identity.duplicate_cluster_ref` | system identity |  |
| `identity.representative_ref` | `identity.representative_ref` | system identity |  |
| `identity.supersedes[]` | `identity.supersedes[]` | system identity |  |
| `identity.retractions[]` | `identity.retractions[]` | system identity |  |
| `identity.lifecycle` | `identity.lifecycle` | system identity |  |
| `core.statement` | `author.layers.core.statement`, `added.layers.core.statement` | scientific field |  |
| `core.kind` | `author.layers.core.kind`, `added.layers.core.kind` | scientific field |  |
| `core.explanandum` | `author.layers.core.explanandum`, `added.layers.core.explanandum` | scientific field |  |
| `core.scope` | `author.layers.core.scope`, `added.layers.core.scope` | scientific field |  |
| `core.context[]` | `author.layers.core.context[]`, `added.layers.core.context[]` | scientific field |  |
| `core.assumptions[].id` | `author.layers.core.assumptions[].id`, `added.layers.core.assumptions[].id` | scientific field |  |
| `core.assumptions[].text` | `author.layers.core.assumptions[].text`, `added.layers.core.assumptions[].text` | scientific field |  |
| `core.assumptions[].fundamental` | `author.layers.core.assumptions[].fundamental`, `added.layers.core.assumptions[].fundamental` | scientific field |  |
| `core.assumptions[].assessment` | `author.layers.core.assumptions[].assessment`, `added.layers.core.assumptions[].assessment` | scientific field |  |
| `core.falsification_condition` | `author.layers.core.falsification_condition`, `added.layers.core.falsification_condition` | scientific field |  |
| `core.atoms[].id` | `author.layers.core.atoms[].id`, `added.layers.core.atoms[].id` | scientific field |  |
| `core.atoms[].statement` | `author.layers.core.atoms[].statement`, `added.layers.core.atoms[].statement` | scientific field |  |
| `core.atoms[].parent_ref` | `author.layers.core.atoms[].parent_ref`, `added.layers.core.atoms[].parent_ref` | scientific field |  |
| `core.atoms[].operator` | `author.layers.core.atoms[].operator`, `added.layers.core.atoms[].operator` | scientific field |  |
| `core.atoms[].context_override` | `author.layers.core.atoms[].context_override`, `added.layers.core.atoms[].context_override` | scientific field |  |
| `mechanism.summary` | `author.layers.mechanism.summary`, `added.layers.mechanism.summary` | scientific field |  |
| `mechanism.black_box` | `author.layers.mechanism.black_box`, `added.layers.mechanism.black_box` | scientific field |  |
| `mechanism.entities[].id` | `author.layers.mechanism.entities[].id`, `added.layers.mechanism.entities[].id` | scientific field |  |
| `mechanism.entities[].label` | `author.layers.mechanism.entities[].label`, `added.layers.mechanism.entities[].label` | scientific field |  |
| `mechanism.steps[].id` | `author.layers.mechanism.steps[].id`, `added.layers.mechanism.steps[].id` | scientific field |  |
| `mechanism.steps[].subject_ref` | `author.layers.mechanism.steps[].subject_ref`, `added.layers.mechanism.steps[].subject_ref` | scientific field |  |
| `mechanism.steps[].relation` | `author.layers.mechanism.steps[].relation`, `added.layers.mechanism.steps[].relation` | scientific field |  |
| `mechanism.steps[].sign` | `author.layers.mechanism.steps[].sign`, `added.layers.mechanism.steps[].sign` | scientific field |  |
| `mechanism.steps[].object_ref` | `author.layers.mechanism.steps[].object_ref`, `added.layers.mechanism.steps[].object_ref` | scientific field |  |
| `mechanism.steps[].evidence_type` | `author.layers.mechanism.steps[].evidence_type`, `added.layers.mechanism.steps[].evidence_type` | scientific field |  |
| `mechanism.steps[].evidence_refs[]` | `author.layers.mechanism.steps[].evidence_refs[]`, `added.layers.mechanism.steps[].evidence_refs[]` | scientific field |  |
| `mechanism.steps[].context` | `author.layers.mechanism.steps[].context`, `added.layers.mechanism.steps[].context` | scientific field |  |
| `predictions[].id` | `author.layers.predictions[].id`, `added.layers.predictions[].id` | scientific field |  |
| `predictions[].population` | `author.layers.predictions[].population`, `added.layers.predictions[].population` | scientific field |  |
| `predictions[].system.taxon` | `author.layers.predictions[].system.taxon`, `added.layers.predictions[].system.taxon` | scientific field |  |
| `predictions[].system.strain_or_line` | `author.layers.predictions[].system.strain_or_line`, `added.layers.predictions[].system.strain_or_line` | scientific field |  |
| `predictions[].system.sex` | `author.layers.predictions[].system.sex`, `added.layers.predictions[].system.sex` | scientific field |  |
| `predictions[].system.age_at_start` | `author.layers.predictions[].system.age_at_start`, `added.layers.predictions[].system.age_at_start` | scientific field |  |
| `predictions[].experimental_unit` | `author.layers.predictions[].experimental_unit`, `added.layers.predictions[].experimental_unit` | scientific field |  |
| `predictions[].system.assessment_age` | `author.layers.predictions[].system.assessment_age`, `added.layers.predictions[].system.assessment_age` | scientific field |  |
| `predictions[].system.site` | `author.layers.predictions[].system.site`, `added.layers.predictions[].system.site` | scientific field |  |
| `predictions[].intervention.agent` | `author.layers.predictions[].intervention.agent`, `added.layers.predictions[].intervention.agent` | scientific field |  |
| `predictions[].intervention.dose` | `author.layers.predictions[].intervention.dose`, `added.layers.predictions[].intervention.dose` | scientific field |  |
| `predictions[].intervention.regimen` | `author.layers.predictions[].intervention.regimen`, `added.layers.predictions[].intervention.regimen` | scientific field |  |
| `predictions[].intervention.duration` | `author.layers.predictions[].intervention.duration`, `added.layers.predictions[].intervention.duration` | scientific field |  |
| `predictions[].intervention.route` | `author.layers.predictions[].intervention.route`, `added.layers.predictions[].intervention.route` | scientific field |  |
| `predictions[].intervention.formulation` | `author.layers.predictions[].intervention.formulation`, `added.layers.predictions[].intervention.formulation` | scientific field |  |
| `predictions[].intervention.nominal_concentration` | `author.layers.predictions[].intervention.nominal_concentration`, `added.layers.predictions[].intervention.nominal_concentration` | scientific field |  |
| `predictions[].intervention.measured_concentration` | `author.layers.predictions[].intervention.measured_concentration`, `added.layers.predictions[].intervention.measured_concentration` | scientific field |  |
| `predictions[].intervention.intake` | `author.layers.predictions[].intervention.intake`, `added.layers.predictions[].intervention.intake` | scientific field |  |
| `predictions[].intervention.systemic_exposure` | `author.layers.predictions[].intervention.systemic_exposure`, `added.layers.predictions[].intervention.systemic_exposure` | scientific field |  |
| `predictions[].comparator` | `author.layers.predictions[].comparator`, `added.layers.predictions[].comparator` | scientific field |  |
| `predictions[].control_reference` | `author.layers.predictions[].control_reference`, `added.layers.predictions[].control_reference` | scientific field |  |
| `predictions[].control_quality` | `author.layers.predictions[].control_quality`, `added.layers.predictions[].control_quality` | scientific field |  |
| `predictions[].control_type` | `added.layers.predictions[].control_type` | scientific field |  |
| `predictions[].endpoint` | `author.layers.predictions[].endpoint`, `added.layers.predictions[].endpoint` | scientific field |  |
| `predictions[].endpoint_orientation` | `author.layers.predictions[].endpoint_orientation`, `added.layers.predictions[].endpoint_orientation` | scientific field |  |
| `predictions[].relational_prediction` | `author.layers.predictions[].relational_prediction`, `added.layers.predictions[].relational_prediction` | scientific field |  |
| `predictions[].endpoint_kind` | `author.layers.predictions[].endpoint_kind`, `added.layers.predictions[].endpoint_kind` | scientific field |  |
| `predictions[].summary_measure` | `author.layers.predictions[].summary_measure`, `added.layers.predictions[].summary_measure` | scientific field |  |
| `predictions[].summary_measure.contrast` | `author.layers.predictions[].summary_measure.contrast`, `added.layers.predictions[].summary_measure.contrast` | scientific field |  |
| `predictions[].summary_measure.scale` | `author.layers.predictions[].summary_measure.scale`, `added.layers.predictions[].summary_measure.scale` | scientific field |  |
| `predictions[].intercurrent_events[].event` | `author.layers.predictions[].intercurrent_events[].event`, `added.layers.predictions[].intercurrent_events[].event` | scientific field |  |
| `predictions[].intercurrent_events[].strategy` | `author.layers.predictions[].intercurrent_events[].strategy`, `added.layers.predictions[].intercurrent_events[].strategy` | scientific field |  |
| `predictions[].intercurrent_events[].justification` | `author.layers.predictions[].intercurrent_events[].justification`, `added.layers.predictions[].intercurrent_events[].justification` | scientific field |  |
| `predictions[].intercurrent_events[]` | `author.layers.predictions[].intercurrent_events[]`, `added.layers.predictions[].intercurrent_events[]` | scientific field |  |
| `predictions[].missing_data_plan` | `author.layers.predictions[].missing_data_plan`, `added.layers.predictions[].missing_data_plan` | scientific field |  |
| `predictions[].direction` | `author.layers.predictions[].direction`, `added.layers.predictions[].direction` | scientific field |  |
| `predictions[].threshold` | `author.layers.predictions[].threshold`, `added.layers.predictions[].threshold` | scientific field |  |
| `predictions[].equivalence_bounds` | `author.layers.predictions[].equivalence_bounds`, `added.layers.predictions[].equivalence_bounds` | scientific field |  |
| `predictions[].horizon` | `author.layers.predictions[].horizon`, `added.layers.predictions[].horizon` | scientific field |  |
| `predictions[].age_window` | `author.layers.predictions[].age_window`, `added.layers.predictions[].age_window` | scientific field |  |
| `predictions[].effect_modifiers[]` | `author.layers.predictions[].effect_modifiers[]`, `added.layers.predictions[].effect_modifiers[]` | scientific field |  |
| `predictions[].predictive_uncertainty` | `author.layers.predictions[].predictive_uncertainty`, `added.layers.predictions[].predictive_uncertainty` | scientific field |  |
| `predictions[].intermediate_tests[].observable` | `author.layers.predictions[].intermediate_tests[].observable`, `added.layers.predictions[].intermediate_tests[].observable` | scientific field |  |
| `predictions[].intermediate_tests[].validity_justification` | `author.layers.predictions[].intermediate_tests[].validity_justification`, `added.layers.predictions[].intermediate_tests[].validity_justification` | scientific field |  |
| `predictions[].test_plan_ref` | `author.layers.predictions[].test_plan_ref`, `added.layers.predictions[].test_plan_ref` | scientific field |  |
| `evidence.lines[].id` | `author.layers.evidence.lines[].id`, `added.layers.evidence.lines[].id` | scientific field |  |
| `evidence.lines[].target_ref` | `author.layers.evidence.lines[].target_ref`, `added.layers.evidence.lines[].target_ref` | scientific field |  |
| `evidence.lines[].direction` | `author.layers.evidence.lines[].direction`, `added.layers.evidence.lines[].direction` | scientific field |  |
| `evidence.lines[].items[]` | `author.layers.evidence.lines[].items[]`, `added.layers.evidence.lines[].items[]` | scientific field |  |
| `evidence.lines[].quote` | `author.layers.evidence.lines[].quote`, `added.layers.evidence.lines[].quote` | scientific field |  |
| `evidence.lines[].evidence_type` | `author.layers.evidence.lines[].evidence_type`, `added.layers.evidence.lines[].evidence_type` | scientific field |  |
| `evidence.lines[].knowledge_level` | `author.layers.evidence.lines[].knowledge_level`, `added.layers.evidence.lines[].knowledge_level` | scientific field |  |
| `evidence.lines[].agent_type` | `author.layers.evidence.lines[].agent_type`, `added.layers.evidence.lines[].agent_type` | scientific field |  |
| `evidence.lines[].hypothesis_flag` | `author.layers.evidence.lines[].hypothesis_flag`, `added.layers.evidence.lines[].hypothesis_flag` | scientific field |  |
| `evidence.lines[].negated_flag` | `author.layers.evidence.lines[].negated_flag`, `added.layers.evidence.lines[].negated_flag` | scientific field |  |
| `evidence.lines[].study_system` | `author.layers.evidence.lines[].study_system`, `added.layers.evidence.lines[].study_system` | scientific field |  |
| `evidence.lines[].study_type` | `author.layers.evidence.lines[].study_type`, `added.layers.evidence.lines[].study_type` | scientific field |  |
| `evidence.lines[].result_estimate` | `author.layers.evidence.lines[].result_estimate`, `added.layers.evidence.lines[].result_estimate` | scientific field |  |
| `evidence.lines[].confidence_interval` | `author.layers.evidence.lines[].confidence_interval`, `added.layers.evidence.lines[].confidence_interval` | scientific field |  |
| `evidence.lines[].statistical_procedure` | `author.layers.evidence.lines[].statistical_procedure`, `added.layers.evidence.lines[].statistical_procedure` | scientific field |  |
| `evidence.lines[].strength` | `author.layers.evidence.lines[].strength`, `added.layers.evidence.lines[].strength` | scientific field |  |
| `evidence.lines[].retraction_status` | `author.layers.evidence.lines[].retraction_status`, `added.layers.evidence.lines[].retraction_status` | scientific field |  |
| `evidence.references[].identifier` | `author.layers.evidence.references[].identifier`, `added.layers.evidence.references[].identifier` | scientific field |  |
| `evidence.references[].citation_relation` | `author.layers.evidence.references[].citation_relation`, `added.layers.evidence.references[].citation_relation` | scientific field |  |
| `provenance.claim_author` | `author.layers.provenance.claim_author`, `added.layers.provenance.claim_author` | scientific field |  |
| `provenance.author_type` | `author.layers.provenance.author_type`, `added.layers.provenance.author_type` | scientific field |  |
| `provenance.model` | `author.layers.provenance.model`, `added.layers.provenance.model` | scientific field |  |
| `provenance.origin_method` | `author.layers.provenance.origin_method`, `added.layers.provenance.origin_method` | scientific field |  |
| `provenance.generation_heuristic` | `author.layers.provenance.generation_heuristic`, `added.layers.provenance.generation_heuristic` | scientific field |  |
| `provenance.parent_refs[]` | `author.layers.provenance.parent_refs[]`, `added.layers.provenance.parent_refs[]` | scientific field |  |
| `provenance.inspiration_refs[]` | `author.layers.provenance.inspiration_refs[]`, `added.layers.provenance.inspiration_refs[]` | scientific field |  |
| `provenance.foreknowledge` | `author.layers.provenance.foreknowledge`, `added.layers.provenance.foreknowledge` | scientific field |  |
| `provenance.original_artifact` | `author.layers.provenance.original_artifact`, `added.layers.provenance.original_artifact` | scientific field |  |
| `provenance.field_sources[]` | `author.layers.provenance.field_sources[]`, `added.layers.provenance.field_sources[]` | scientific field |  |
| `provenance.transformation` | `author.layers.provenance.transformation`, `added.layers.provenance.transformation` | scientific field |  |
| `provenance.translation` | `author.layers.provenance.translation`, `added.layers.provenance.translation` | scientific field |  |
| `provenance.licence` | `author.layers.provenance.licence`, `added.layers.provenance.licence` | scientific field |  |
| `provenance.contributions[]` | `author.layers.provenance.contributions[]`, `added.layers.provenance.contributions[]` | scientific field |  |
| `provenance.registration` | `author.layers.provenance.registration`, `added.layers.provenance.registration` | scientific field |  |
| `profile.dose_response.shape` | `author.layers.profile.dose_response.shape`, `added.layers.profile.dose_response.shape` | scientific field |  |
| `profile.dose_response.x_axis` | `author.layers.profile.dose_response.x_axis`, `added.layers.profile.dose_response.x_axis` | scientific field |  |
| `profile.dose_response.endpoint_ref` | `author.layers.profile.dose_response.endpoint_ref`, `added.layers.profile.dose_response.endpoint_ref` | scientific field |  |
| `profile.dose_response.range` | `author.layers.profile.dose_response.range`, `added.layers.profile.dose_response.range` | scientific field |  |
| `profile.combination.components[]` | `author.layers.profile.combination.components[]`, `added.layers.profile.combination.components[]` | scientific field |  |
| `profile.combination.reference_model` | `author.layers.profile.combination.reference_model`, `added.layers.profile.combination.reference_model` | scientific field |  |
| `profile.combination.effect` | `author.layers.profile.combination.effect`, `added.layers.profile.combination.effect` | scientific field |  |
| `profile.biomarker.role` | `author.layers.profile.biomarker.role`, `added.layers.profile.biomarker.role` | scientific field |  |
| `profile.biomarker.validation` | `author.layers.profile.biomarker.validation`, `added.layers.profile.biomarker.validation` | scientific field |  |
| `profile.harm` | `author.layers.profile.harm`, `added.layers.profile.harm` | scientific field |  |
| `profile.transfer_scope` | `author.layers.profile.transfer_scope`, `added.layers.profile.transfer_scope` | scientific field |  |
| `profile.function_process` | `author.layers.profile.function_process`, `added.layers.profile.function_process` | scientific field |  |
| `appendix.rationale` | `author.layers.appendix.rationale`, `added.layers.appendix.rationale` | scientific field |  |
| `appendix.experiment_plan` | `author.layers.appendix.experiment_plan`, `added.layers.appendix.experiment_plan` | scientific field |  |
| `appendix.source_extensions` | `author.layers.appendix.source_extensions`, `added.layers.appendix.source_extensions` | scientific field |  |
| `appendix.limitations` | `author.layers.appendix.limitations`, `added.layers.appendix.limitations` | scientific field |  |
| `pair.hypothesis_refs` | `ohf:pair-brief@1:hypothesis_refs[]` | detached pair brief | Stored in a pair brief that binds the two immutable card versions it compares. |
| `pair.relation` | `ohf:hypothesis-relations@1:edges[].type` | detached relation artifact | Stored in a detached relations artifact that binds immutable card versions and a fixed pool. |
| `pair.discriminability` |  | unresolved external pair diagnostic extension | This comparison-level diagnostic has no serialization contract in OHF 1.0 and is not stored on an individual hypothesis. |
| `pair.diagnosticity_matrix` |  | unresolved external pair diagnostic extension | This comparison-level diagnostic has no serialization contract in OHF 1.0 and is not stored on an individual hypothesis. |
| `pair.decisive_test` | `ohf:pair-brief@1:decisive_test` | detached pair brief | Stored in a pair brief that binds the two immutable card versions it compares. |
| `pair.assumptions` |  | unresolved external pair diagnostic extension | This comparison-level diagnostic has no serialization contract in OHF 1.0 and is not stored on an individual hypothesis. |
| `pair.context_ref` |  | unresolved external pair diagnostic extension | This comparison-level diagnostic has no serialization contract in OHF 1.0 and is not stored on an individual hypothesis. |
| `provenance.heuristic_principle[]` | `author.layers.provenance.heuristic_principle.value[]`, `added.layers.provenance.heuristic_principle.value[]` | scientific field |  |
| `mechanism.molecular_targets[]` | `author.layers.mechanism.molecular_targets.value[]`, `added.layers.mechanism.molecular_targets.value[]` | scientific field |  |
| `predictions[].test_cost` | `author.layers.predictions[].test_cost`, `added.layers.predictions[].test_cost` | scientific field |  |
| `predictions[].role` | `author.layers.predictions[].role`, `added.layers.predictions[].role` | scientific field |  |
| `core.potential_benefit` | `author.layers.core.potential_benefit`, `added.layers.core.potential_benefit` | scientific field |  |
| `evidence.references[].access_context` | `author.layers.evidence.references[].access_context`, `added.layers.evidence.references[].access_context` | scientific field |  |
| `core.novelty_assessment` | `author.layers.core.novelty_assessment`, `added.layers.core.novelty_assessment` | scientific field |  |
| `core.uncertainties[]` | `author.layers.core.uncertainties.value[]`, `added.layers.core.uncertainties.value[]` | scientific field |  |
| `core.alternative_explanations[]` | `author.layers.core.alternative_explanations.value[]`, `added.layers.core.alternative_explanations.value[]` | scientific field |  |
| `predictions[].resolution` | `author.layers.predictions[].resolution`, `added.layers.predictions[].resolution` | scientific field |  |
| `evidence.lines[].replication` | `author.layers.evidence.lines[].replication`, `added.layers.evidence.lines[].replication` | scientific field |  |
| `core.base_rate` | `author.layers.core.base_rate`, `added.layers.core.base_rate` | scientific field |  |
| `predictions[].existing_data_tests[]` | `author.layers.predictions[].existing_data_tests.value[]`, `added.layers.predictions[].existing_data_tests.value[]` | scientific field |  |
| `evidence.references[].funding_coi` | `author.layers.evidence.references[].funding_coi`, `added.layers.evidence.references[].funding_coi` | scientific field |  |
| `profile.human_testability` | `author.layers.profile.human_testability`, `added.layers.profile.human_testability` | scientific field |  |
| `core.explains[]` | `author.layers.core.explains.value[]`, `added.layers.core.explains.value[]` | scientific field |  |
| `core.reinterprets[]` | `author.layers.core.reinterprets.value[]`, `added.layers.core.reinterprets.value[]` | scientific field |  |
| `core.opens[]` | `author.layers.core.opens.value[]`, `added.layers.core.opens.value[]` | scientific field |  |
| `core.testability` | `author.layers.core.testability`, `added.layers.core.testability` | scientific field |  |
| `predictions[].epistemic_status` | `author.layers.predictions[].epistemic_status`, `added.layers.predictions[].epistemic_status` | scientific field |  |
| `predictions[].known_result_ref` | `author.layers.predictions[].known_result_ref`, `added.layers.predictions[].known_result_ref` | scientific field |  |
| `predictions[].form` | `author.layers.predictions[].form`, `added.layers.predictions[].form` | scientific field |  |
| `predictions[].derives_from_atom_refs[]` | `author.layers.predictions[].derives_from_atom_refs.value[]`, `added.layers.predictions[].derives_from_atom_refs.value[]` | scientific field |  |
| `predictions[].also_expected_under[]` | `author.layers.predictions[].also_expected_under.value[]`, `added.layers.predictions[].also_expected_under.value[]` | scientific field |  |
| `predictions[].discrimination` | `added.layers.predictions[].discrimination` | scientific field |  |
| `predictions[].system.kind` | `author.layers.predictions[].system.kind`, `added.layers.predictions[].system.kind` | scientific field |  |
| `predictions[].system.environment` | `author.layers.predictions[].system.environment`, `added.layers.predictions[].system.environment` | scientific field |  |
| `predictions[].system.spatial_scale` | `author.layers.predictions[].system.spatial_scale`, `added.layers.predictions[].system.spatial_scale` | scientific field |  |
| `predictions[].system.temporal_scale` | `author.layers.predictions[].system.temporal_scale`, `added.layers.predictions[].system.temporal_scale` | scientific field |  |
| `core.first_proposed` | `author.layers.core.first_proposed`, `added.layers.core.first_proposed` | scientific field |  |
| `core.atoms[].claim_type` | `added.layers.core.atoms[].claim_type` | scientific field |  |
| `core.atoms[].role` | `added.layers.core.atoms[].role` | scientific field |  |
| `core.atoms[].modality` | `added.layers.core.atoms[].modality` | scientific field |  |
| `evidence.lines[].indirectness` | `added.layers.evidence.lines[].indirectness` | scientific field |  |
| `evidence.lines[].risk_of_bias` | `added.layers.evidence.lines[].risk_of_bias` | scientific field |  |
| `evidence.lines[].independence_group` | `added.layers.evidence.lines[].independence_group` | scientific field |  |
| `evidence.lines[].argument_kind` | `added.layers.evidence.lines[].argument_kind` | scientific field |  |
| `evidence.selection_record` | `added.layers.evidence.selection_record` | scientific field |  |

The intermediate-test record additionally stores sourced H0, H1, procedure and phase components in both zones. These refine the existing TestRecord and add no catalogue rows. The checker audits all sourced scientific wrapper locations in the card schema against direct targets and these explicit components. Operational metadata and source proof are separate contracts.
