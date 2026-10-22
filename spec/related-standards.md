# Related standards and models

These standards and models are the conceptual sources of OHF fields. Each entry names the version its facts come from. Generated from [related-standards.json](related-standards.json) with `python tools/build_related_standards.py`; edit the JSON and regenerate this file.

Relations:

- **Field basis**: The catalogue paths listed take their concept from this standard. No term is copied.
- **Recommended vocabulary**: The catalogue names identifiers of this vocabulary for the paths listed. OHF does not bind or check the values.
- **Different problem**: The standard solves another task; OHF takes one idea from it for the paths listed.

The card path that stores each catalogue path is in the [storage mapping](mapping.md).

## SEPIO Core Information Model
An information model for scientific assertions with their evidence and provenance, with separate proposition, statement, evidence line, data and contribution objects.

- Version: sepio-linkml commit acb4ddde6011d6e0958048fb99e7d4aca057588f; many definitions are marked Draft and there is no release number
- Maintainer: sepio-framework (GitHub organisation of the repository)
- Licence: Apache-2.0 (LICENSE file of the repository)
- Source: <https://github.com/sepio-framework/sepio-linkml/blob/acb4ddde6011d6e0958048fb99e7d4aca057588f/src/sepio_linkml/schema/sepio_classes.yaml>
- Relation to OHF: Field basis. Catalogue paths: `identity.proposition_id`, `identity.assertions[].id`, `identity.assertions[].text`, `identity.assertions[].agent_ref`, `identity.assertions[].asserted_at`, `identity.assertions[].stance`, `core.assumptions[].assessment`, `mechanism.steps[].evidence_refs[]`, `evidence.lines[].id`, `evidence.lines[].target_ref`, `evidence.lines[].direction`, `evidence.lines[].items[]`, `evidence.lines[].strength`, `provenance.claim_author`, `provenance.contributions[]`
- How OHF differs: SEPIO is a general model of assertions and evidence. OHF takes from it the separation of proposition, statement, evidence line and contribution, and adds a card for one hypothesis with an author and an added zone, predictions and explicit gaps.

## Nanopublications
A small self-contained publication of one assertion with its provenance and publication information, in RDF named graphs.

- Version: Guidelines working draft; no numbered stable release
- Maintainer: Not stated by the source
- Licence: Creative Commons ShareAlike Attribution 3.0 License, as stated in the footer of the guidelines document (Guidelines page footer)
- Source: <https://nanopub.net/guidelines/working_draft/>
- Relation to OHF: Field basis. Catalogue paths: `identity.retractions[]`, `provenance.original_artifact`
- How OHF differs: OHF keeps the separation of assertion provenance from publication provenance. It binds the original artifact by SHA-256, not by a Trusty URI, and is a JSON card rather than RDF graphs.

## ICH E9(R1): estimands and sensitivity analysis in clinical trials
A regulatory guideline for specifying the treatment effect (estimand) a clinical trial targets: population, treatment, endpoint, intercurrent events and their strategies, and the summary measure.

- Version: Final Step 4 addendum, adopted 20 November 2019
- Maintainer: International Council for Harmonisation (ICH)
- Licence: ICH copyright; reuse under the conditions of the legal notice in the guideline (Legal notice, page 2 of the guideline PDF)
- Source: <https://database.ich.org/sites/default/files/E9-R1_Step4_Guideline_2019_1203.pdf>
- Relation to OHF: Field basis. Catalogue paths: `predictions[].population`, `predictions[].intervention.agent`, `evidence.lines[].intervention.agent`, `predictions[].intervention.regimen`, `evidence.lines[].intervention.regimen`, `predictions[].comparator`, `predictions[].endpoint`, `predictions[].summary_measure`, `predictions[].summary_measure.contrast`, `predictions[].summary_measure.scale`, `predictions[].intercurrent_events[].event`, `predictions[].intercurrent_events[].strategy`, `predictions[].intercurrent_events[].justification`, `predictions[].intercurrent_events[]`, `predictions[].missing_data_plan`, `predictions[].horizon`
- How OHF differs: OHF uses the estimand dimensions for the predictions of a hypothesis about an intervention. It does not require a biological hypothesis to be stated as a clinical trial, and applies a strategy for an intercurrent event only when the source states it.

## ARRIVE guidelines 2.0
A reporting guideline for animal research: the Essential 10 and the Recommended Set of items an article should report.

- Version: Published 14 July 2020
- Maintainer: Developed by Percie du Sert et al. with the NC3Rs
- Licence: CC0-1.0 (permissions block of the article's full-text XML (Europe PMC, PMC7360023): Creative Commons CC0 public domain dedication)
- Source: <https://doi.org/10.1371/journal.pbio.3000410>, <https://arriveguidelines.org/arrive-guidelines>
- Relation to OHF: Field basis. Catalogue paths: `predictions[].system.taxon`, `evidence.lines[].system.taxon`, `predictions[].system.strain_or_line`, `evidence.lines[].system.strain_or_line`, `predictions[].system.sex`, `evidence.lines[].system.sex`, `predictions[].system.age_at_start`, `evidence.lines[].system.age_at_start`, `predictions[].experimental_unit`, `predictions[].system.assessment_age`, `evidence.lines[].system.assessment_age`, `predictions[].system.site`, `evidence.lines[].system.site`, `predictions[].intervention.route`, `evidence.lines[].intervention.route`, `predictions[].intervention.formulation`, `evidence.lines[].intervention.formulation`, `evidence.lines[].study_system`, `evidence.lines[].study_type`, `evidence.lines[].statistical_procedure`
- How OHF differs: OHF uses ARRIVE items to describe the test system and study of a prediction or evidence line. For a hypothesis without its own experiment, a missing reporting item is not by itself a required gap.

## Micropublications
An ontology that connects a scientific claim to its supporting data and methods and to its challenges, with explicit attribution.

- Version: OWL versionInfo 1.18, repository commit 8c9100506cc60eb744c9ecec0da1c2a27b14ae3a
- Maintainer: Developed by Tim Clark, Paolo Ciccarese and Carole Goble
- Licence: Not established. OHF reuses no text or terms from it.
- Source: <https://raw.githubusercontent.com/timclark001/mp/8c9100506cc60eb744c9ecec0da1c2a27b14ae3a/mp.owl>, <https://pmc.ncbi.nlm.nih.gov/articles/PMC4530550/>
- Relation to OHF: Field basis. Catalogue paths: `identity.duplicate_cluster_ref`, `identity.representative_ref`, `core.assumptions[].id`, `core.assumptions[].text`
- How OHF differs: OHF takes the idea of a representative claim among duplicates and of explicit assumptions. No Micropublications term is reused, because the licence is not established.

## CiTO, the Citation Typing Ontology
Properties that state why one work cites another, such as citing as evidence, as a data source, or to dispute it.

- Version: 2.9.0 (version IRI 2026-09-03)
- Maintainer: Developed by Silvio Peroni and David Shotton in the SPAR Ontologies project
- Licence: CC-BY-4.0 (dcterms:license of the ontology)
- Source: <https://sparontologies.github.io/cito/current/cito.html>
- Relation to OHF: Recommended vocabulary. Catalogue paths: `evidence.references[].citation_relation`
- How OHF differs: CiTO types the relation between two works. OHF uses it only for the relation of a cited reference to the citing source; the direction of an evidence line toward a hypothesis is a separate OHF field.

## POPPER
An agent system that tests a hypothesis against supplied data by proposing testable consequences, running analyses and combining the results sequentially.

- Version: Repository commit 59611864e09dd15d7528e240ad87c7ddbb4a701c
- Maintainer: Developed by Kexin Huang, Ying Jin, Ryan Li, Michael Y. Li, Emmanuel Candès and Jure Leskovec
- Licence: Not established. OHF reuses no text or terms from it.
- Source: <https://github.com/snap-stanford/POPPER/tree/59611864e09dd15d7528e240ad87c7ddbb4a701c>, <https://arxiv.org/abs/2502.09858>
- Relation to OHF: Different problem. Catalogue paths: `core.falsification_condition`, `predictions[].intermediate_tests[].observable`, `predictions[].intermediate_tests[].validity_justification`
- How OHF differs: POPPER runs tests; OHF records a hypothesis. OHF takes from it the description of an intermediate test and its validity, and the falsification condition.

## OSF Preregistration
A form for specifying hypotheses, data collection and analysis before a study, including what the investigators already know of the data.

- Version: Template version 3
- Maintainer: Center for Open Science
- Licence: Not established. OHF reuses no text or terms from it.
- Source: <https://www.cos.io/initiatives/prereg>, <https://github.com/CenterForOpenScience/osf.io/blob/bc997fb7aed9eee273cb941191d07e25d66024ff/website/project/metadata/osf-preregistration-3.json>
- Relation to OHF: Field basis. Catalogue paths: `predictions[].test_plan_ref`, `provenance.foreknowledge`, `appendix.experiment_plan`
- How OHF differs: A preregistration plans one study. OHF links a prediction to such a plan and records what was known before the prediction, but does not itself plan a study.

## HyQue
A system that evaluates formalised hypotheses, made of events joined by logical operators, against a knowledge base with explicit rules.

- Version: System rules, repository commit 526a5faacf9f089df888aa85197d31df8b75fcf3
- Maintainer: Developed by Alison Callahan, Michel Dumontier and Nigam Shah
- Licence: Not established. OHF reuses no text or terms from it.
- Source: <https://doi.org/10.1186/2041-1480-2-S2-S3>, <https://github.com/alisoncallahan/hyque-spin-rules/tree/526a5faacf9f089df888aa85197d31df8b75fcf3>
- Relation to OHF: Different problem. Catalogue paths: `core.atoms[].id`, `core.atoms[].statement`, `core.atoms[].parent_ref`, `core.atoms[].operator`
- How OHF differs: HyQue scores a hypothesis against a knowledge base. OHF takes from it the decomposition of a claim into atoms joined by AND, OR and XOR, and does not score.

## Evidence & Conclusion Ontology (ECO)
Terms for types of scientific evidence and for how an assertion was made, used to record the basis of annotations in biological databases.

- Version: Release 2026-07-10
- Maintainer: evidenceontology (GitHub organisation of the repository)
- Licence: CC0-1.0 (Header of the released ontology file)
- Source: <https://evidenceontology.org/about_eco/>, <https://github.com/evidenceontology/evidenceontology/blob/6bbc0730de4f3d04a5a1347946cd231e40fde4bd/eco.obo>
- Relation to OHF: Recommended vocabulary. Catalogue paths: `mechanism.steps[].evidence_type`, `evidence.lines[].evidence_type`
- How OHF differs: ECO classifies the basis of an assertion; it does not state effect size or strength. The catalogue names ECO identifiers for evidence types; in OHF 1.0 the value is free text and is not checked against ECO.

## Biolink Model
A data model and taxonomy of entities and associations for biological knowledge graphs, with predicates, qualifiers and knowledge-level and agent-type enumerations.

- Version: 4.4.6
- Maintainer: Developed in the NCATS Biomedical Data Translator community
- Licence: CC0-1.0 (license key of the released model file)
- Source: <https://github.com/biolink/biolink-model/blob/v4.4.6/biolink-model.yaml>, <https://doi.org/10.1111/cts.13302>
- Relation to OHF: Recommended vocabulary. Catalogue paths: `core.scope`, `core.context[]`, `mechanism.steps[].relation`, `mechanism.steps[].context`, `predictions[].effect_modifiers[]`, `evidence.lines[].knowledge_level`, `evidence.lines[].agent_type`
- How OHF differs: Biolink describes edges of a knowledge graph. OHF uses its predicates, context and knowledge-level and agent-type terms to describe a mechanism step and an evidence line; in OHF the values are free text.

## INDRA
A JSON schema of molecular statements, such as activation or phosphorylation between agents, assembled into computational models.

- Version: 1.24.0, repository commit 7ae3337dcae88baed918d7ae6af2ddc21f9946fa
- Maintainer: Developed by Benjamin M. Gyori, John A. Bachman and collaborators
- Licence: BSD-2-Clause (Licence badge of the repository README)
- Source: <https://github.com/gyorilab/indra/blob/7ae3337dcae88baed918d7ae6af2ddc21f9946fa/indra/resources/statements_schema.json>, <https://doi.org/10.15252/msb.20177651>
- Relation to OHF: Field basis. Catalogue paths: `mechanism.summary`, `mechanism.entities[].id`, `mechanism.entities[].label`, `mechanism.steps[].id`, `mechanism.steps[].subject_ref`, `mechanism.steps[].sign`, `mechanism.steps[].object_ref`, `evidence.lines[].hypothesis_flag`, `evidence.lines[].negated_flag`
- How OHF differs: INDRA statements are machine-assembled molecular interactions. OHF describes a mechanism as entities and signed steps bound to a source, and keeps the hypothesis and negation flags of an evidence line.

## Hypothesis Evolution Protocol (HEP)
An append-only, event-sourced registry and tool set that keeps each hypothesis of a language-model research agent as a persistent object: statement, elicited belief P(H), lifecycle state, provenance, predicted observable and lineage. It is evaluated on materials-science tasks.

- Version: arXiv:2607.09195v1, 10 July 2026; no code has been released
- Maintainer: Izumi Takahara and Teruyasu Mizoguchi, Institute of Industrial Science, The University of Tokyo (authors of the paper)
- Licence: CC-BY-4.0 (licence link on the arXiv abstract page of v1)
- Source: <https://arxiv.org/abs/2607.09195v1>
- Relation to OHF: Field basis. Catalogue paths: `identity.assertions[].confidence`, `identity.lifecycle`, `provenance.origin_method`, `provenance.parent_refs[]`
- How OHF differs: HEP keeps one self-reported belief per hypothesis inside one agent run, with five verdict states and four generation mechanisms. OHF takes the ideas of an elicited belief, a lifecycle state, the generation mechanisms de_novo, refine and merge, and lineage that excludes inspiration. In OHF 1.0 the lifecycle state is a label of the publisher; OHF defines no states and does not enforce transitions. It attaches confidence to attributed assertions with a declared scale and calibration, adds the origins import and published_restatement. HEP has no record versions; OHF record versioning is its own.

## MOOSE-Chem
A language-model framework that composes chemistry hypotheses from a research background and one to three inspirations, usually papers, and ranks them. It builds on MOOSE (Findings of ACL 2024) and defines no record format.

- Version: arXiv:2410.07076v6, 27 October 2025 (ICLR 2025); code at commit f8cda98a3bed30b0f0d85fba625e343d688461ab
- Maintainer: Zonglin Yang and co-authors (Nanyang Technological University, Shanghai Artificial Intelligence Laboratory and others); the code repository belongs to its first author
- Licence: CC-BY-4.0 (licence link on the arXiv abstract page of v6; the code repository is MIT (LICENSE file at the pinned commit))
- Source: <https://arxiv.org/abs/2410.07076v6>, <https://github.com/ZonglinY/MOOSE-Chem/tree/f8cda98a3bed30b0f0d85fba625e343d688461ab>
- Relation to OHF: Field basis. Catalogue paths: `provenance.inspiration_refs[]`
- How OHF differs: In MOOSE-Chem an inspiration is an input that a model retrieves and combines with the background to generate a hypothesis, and it must not be already known to relate to the background. OHF only records inspirations as attributed references in the provenance, and an inspiration does not make the hypothesis a descendant. OHF sets no count, novelty condition or retrieval step.

## Co-Scientist
A closed multi-agent system that generates, critiques, ranks and evolves research hypotheses and proposals from a research goal, applied to three biomedical problems. Its code and any record format are not public.

- Version: arXiv:2502.18864v2, 29 June 2026; Nature 655, 487–496 (2026), doi:10.1038/s41586-026-10644-y. Version 1 of the preprint was titled "Towards an AI co-scientist"
- Maintainer: Google Cloud AI Research, Google DeepMind and Google Research, with academic co-authors
- Licence: CC-BY-4.0 (arXiv abstract page of v2 and the open-access statement of the Nature article; preprint v1 was posted under CC-BY-NC-ND-4.0)
- Source: <https://arxiv.org/abs/2502.18864v2>, <https://doi.org/10.1038/s41586-026-10644-y>
- Relation to OHF: Field basis. Catalogue paths: `appendix.rationale`
- How OHF differs: In the example proposal of Supplementary Note 10.2 a separate "Rationale and specificity" section follows the hypothesis. OHF takes only this idea of a separate, attributed rationale and keeps it in appendix.rationale, apart from structured fields. The sections are example output, not a published format.

## The AI Scientist
A language-model pipeline that generates research ideas, runs experiments, writes a paper and reviews it automatically, shown on machine-learning research. It defines JSON shapes inside its prompts, not a data standard.

- Version: arXiv:2408.06292v3, 1 September 2024; code at commit 1de1dbc1f4ee2c5f61e9c94348d55eb51d7fa2eb. The appendix.source_extensions example follows The AI Scientist-v2, arXiv:2504.08066v1
- Maintainer: Sakana AI (licensor of the code repository)
- Licence: CC-BY-4.0 (licence link on the arXiv abstract page of v3; the code at the pinned commit is under "The AI Scientist Source Code License", Version 1.0, which has no SPDX identifier)
- Source: <https://arxiv.org/abs/2408.06292v3>, <https://github.com/SakanaAI/AI-Scientist/tree/1de1dbc1f4ee2c5f61e9c94348d55eb51d7fa2eb>, <https://arxiv.org/abs/2504.08066v1>
- Relation to OHF: Field basis. Catalogue paths: `appendix.source_extensions`, `appendix.limitations`
- How OHF differs: The AI Scientist writes limitations as free text in the generated paper and as a separate list from its automated reviewer; the idea records of version 2 have a "Risk Factors and Limitations" field. OHF keeps author-stated limitations apart from attributed curator commentary, and keeps sections of other formats as versioned extension records. Neither version defines an extension mechanism.

## The Unified Code for Units of Measure (UCUM)
A code system of unit symbols, prefixes and an expression syntax for unambiguous machine-to-machine communication of quantities with their units.

- Version: 2.2, 17 June 2024
- Maintainer: Regenstrief Institute, Inc.
- Licence: UCUM Copyright Notice and License, Version 1.1 (June 2024) (https://ucum.org/license; no SPDX identifier is stated)
- Source: <https://ucum.org/ucum>, <https://ucum.org/license>
- Relation to OHF: Recommended vocabulary. Catalogue paths: `predictions[].intervention.dose`, `evidence.lines[].intervention.dose`, `predictions[].intervention.duration`, `evidence.lines[].intervention.duration`, `predictions[].intervention.nominal_concentration`, `evidence.lines[].intervention.nominal_concentration`, `profile.dose_response.range`
- How OHF differs: OHF recommends UCUM unit syntax but stores dose, duration, concentration and range values as strings that keep the source wording. It does not parse or validate UCUM expressions, and it adds what UCUM does not cover: administration basis, denominator, biological basis and time origin.
