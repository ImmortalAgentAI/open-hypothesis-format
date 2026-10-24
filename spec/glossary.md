# Glossary

This glossary defines the terms the Open Hypothesis Format (OHF) specification uses, with a link to the file where each term is specified.

**Added zone.** The `added` member of a card: what a converter or reviewer added to the author's assertions. Each value carries a `src` that points to a source record; the zone also holds the gaps, the completeness record, the source records and the integrity record. See [README](README.md).

**Argument kind.** `evidence.lines[].argument_kind`: whether an evidence line rests on observation or experiment (`empirical`), on a `simulation`, or on a mathematical `derivation` or proof. It is recorded in the added zone. See [fields](fields.md).

**Assessment.** A value that is the judgement of whoever recorded it, not a statement of the hypothesis author, such as `predictions[].discrimination`, `evidence.lines[].strength`, `evidence.lines[].indirectness` or `evidence.lines[].risk_of_bias`. It is held in the added zone with an `assessment` record that names the assessor, the time and the evidence it rests on. An assessment without a basis is not recorded; the field is a gap with `not_supplied`. See [integrity](README.md#integrity).

**Atom.** An item of `core.atoms[]`: one atomic assertion of the hypothesis, stated without losing its condition, uncertainty or negation. Atoms are linked by `parent_ref` and an explicit `operator`; every added-zone atom has a claim type, a role and a modality, and an author-zone atom needs an added-zone atom with the same `id` that carries them. From OHF 1.2 an added-zone atom may have a `scope` narrower than the scope of the card. See [fields](fields.md).

**Author zone.** The `author` member of a card: the author's assertions and their source, `author.source`. Each value carries a `locator` into the source text, and author source strings stay verbatim. See [README](README.md).

**`basis_quote`.** The exact source wording on which an added value rests: the passage that a paraphrase restates, or the author's wording behind an atom's modality. An entailment record may name it as the basis it checked. See [logical types](logical-types.md#paraphrases).

**Card.** A JSON document, valid against [`hypothesis-1.schema.json`](../schema/hypothesis-1.schema.json), that records one hypothesis bound to its sources. It holds identity and version metadata for the whole card, an author zone and an added zone. See [README](README.md).

**Card path.** The place where a logical path is stored in a card, for example `author.layers.core.statement` and `added.layers.core.statement` for `core.statement`. The [mapping](mapping.md) gives the card paths of each logical path, or why it has none.

**Card version.** One immutable version of a card, referenced by its `id`, `version` and `content_hash`. Relations artifacts and pair briefs bind to card versions, and `identity.supersedes[]` lists the earlier versions a card replaces. See [fields](fields.md).

**Catalogue.** The [field catalogue](field-catalogue.json): all 219 logical paths, each with its layer, definition, logical type, vocabulary, conceptual basis and field class. The [field reference](fields.md) gives an example for every path.

**Claim type.** `core.atoms[].claim_type`: what kind of claim an atom makes: `existence`, `distribution`, `association`, `causal_effect`, `mechanism`, `functional_attribution`, `evolutionary_explanation`, `development`, `constitution`, `quantitative_law`, `model_sufficiency`, `historical_reconstruction`, or `other` with a note. It is required on every added-zone atom. See [fields](fields.md).

**Check.** From OHF 1.2, how a catalogue row's added value is checked: `passage` (against the paragraph its `src` names, by an entailment checker), `resolution` (against an external record, by a tool) or `card` (against the card, by `tools/check_refs.py`, with no record). A row may give a check for each member of its value. See [README](README.md#ohf-12).

**Closed term.** From OHF 1.1, a `term` from [`terms-1.json`](../vocabularies/terms-1.json) next to the source wording of a route or an endpoint kind, with a `note` exactly when the term is `other`; `predictions[].control_type` lists terms. A 1.1 card gives the term wherever it records a route or an endpoint kind in the added zone. See [README](README.md#ohf-11).

**Completeness.** The structural level of a card, recorded in `added.completeness.level`. `accepted`: the author's assertion is checked against source bytes, and source, licence and provenance are present. `comparable`: `accepted`, plus a prediction with a system, an endpoint, a form and an epistemic status (and a direction when the form is `directional_contrast`). `full`: `comparable`, plus a typed mechanism step, claim atoms, and evidence on both sides, or a recorded search for disputing evidence (`added.challenge_search`). See [README](README.md#completeness).

**Content hash.** `content_hash`: the SHA-256 of the card's RFC 8785 canonical JSON form without the `content_hash` member, written `sha256:` followed by 64 hexadecimal digits. `tools/content_hash.py --check` verifies it. See [examples](../examples/README.md#content-hash).

**Converter.** The tool or pass that wrote a card's added zone, named in `added.by` with `converter`, `converter_version`, `converter_hash` (the SHA-256 of its rules) and `model`. The entailment checker must not be the converter. See [integrity](README.md#integrity).

**CURIE.** A compact identifier `prefix:local`, such as `NCBITaxon:10090` or `GO:0031931`, that names a term of an external ontology. OHF 1.1 uses CURIEs for taxa and for the subject and object of a triple.

**Deferred extension.** A catalogue path that has no serialization in OHF 1.0: question references, the assertion registry, and the pair-level discriminability, diagnosticity matrix, assumptions and comparison context. Source or provenance containers cannot substitute for them. See [mapping](mapping.md).

**Discrimination.** `predictions[].discrimination`: how well a prediction's outcome separates the hypothesis from the alternatives that also expect it (`predictions[].also_expected_under[]`): none, weak or strong. It is an assessment, held in the added zone. See [fields](fields.md).

**Domain profile.** The set of domain-specific paths a card selects in `added.layers.profile.domain`, from [`profiles-1.json`](../vocabularies/profiles-1.json): `ohf:intervention-pharmacology@1` for claims about the effect of an intervention (22 paths, in the predictions and profile layers; `facets.intervention_type` is then required), from OHF 1.1 `ohf:aging@1` ([`profiles-2.json`](../vocabularies/profiles-2.json): the same 22 paths and the hallmarks of aging), or `none`. With `none` the 22 paths are absent and need no gaps, and a gap for one of them is rejected; `author.layers.profile.domain`, if present, must match. From OHF 1.2 the domain is a list of profiles, and a path is selected when any of them has it. See [README](README.md#domain-profiles).

**Entailment record.** An item of `added.integrity.entailment[]`: a JSON pointer to a sourced added-zone value (from OHF 1.2 also a member of one, or a value checked by resolution, which is checked against an external record rather than a `src`), the basis checked (`src` or `basis_quote`, or from OHF 1.2 `resolution`), a verdict, the checker with its version and the SHA-256 of what it ran (a model checker's prompt; from OHF 1.2 a tool checker's tool), and the time. The checker is not the pass that wrote the added zone. See [integrity](README.md#integrity).

**Entailment verdict.** Whether the source passage supports an added value: `entails`, `partial` or `no`, the last two with a note. A value with a `partial` or `no` verdict is not presented as supported, and a value without a record has not been checked; a verdict concerns the source passage, not the truth of the claim. See [integrity](README.md#integrity).

**Epistemic status.** `predictions[].epistemic_status`: whether a prediction was stated before its result was known (`novel`), derived for a result already known (`retrodicted`), or adjusted to fit a known result (`accommodated`). `retrodicted` and `accommodated` require `known_result_ref`. See [fields](fields.md).

**Evidence line.** An item of `evidence.lines[]`: one evidence assessment about an exact claim, atom, mechanism step or prediction, named by `target_ref`. It records whether the evidence supports, disputes or is neutral toward the target, with its items, quotation, study and quality fields. See [fields](fields.md).

**Evidence selection record.** `evidence.selection_record`: how the evidence lines were selected: the queries run, the numbers of records identified, screened and included, and the exclusions with reasons and counts. See [fields](fields.md).

**Example card.** A card in [`examples/cards/`](../examples/cards) converted from one published article. Its added zone is the converter's reading of the article, not the authors' words, and a schema pass confirms only its shape. See [examples](../examples/README.md) and the [conversion rules](../examples/cards/CONVERSION.md).

**Excluded record.** From OHF 1.1, an item of `evidence.excluded[]`: a source passage that was considered for a target and not carried as an evidence line, with a reason (species, direction, endpoint, type or inherited mismatch, or `other` with a note) and the quote. See [README](README.md#ohf-11).

**Explanandum.** `core.explanandum`: the observed phenomenon or open question the claim attempts to explain, not an intended outcome or the goal of an intervention. See [fields](fields.md).

**Facets.** The `facets` member of a card: search labels for the whole card, `topic[]`, `source_class` and, for a claim in the domain profile `ohf:intervention-pharmacology@1`, `intervention_type`. Facets are not part of the claim and have no catalogue rows. See the [schema](../schema/hypothesis-1.schema.json).

**Field class.** The class of a catalogue path, which says how a missing value is treated. `searchable`: the value can be looked for in sources, and a gap records what was searched. `author_only`: only the author, or for an assessment the person who recorded it, can state the value, so absence means "not declared" and the gap disposition is `not_supplied`. `system`: the record itself assigns the value, an empty value is valid and needs no gap, and a search is rejected. See [README](README.md#field-classes).

**Gap.** An item of `added.gaps` that records a missing field instead of inventing a value. Each gap names its exact catalogue path in `path`, a `disposition`, a `reason`, the `query_ids` and `inspected_artifacts` behind it, and, for `not_applicable_scope`, a `scope_ref` to filled card content. See [README](README.md#gaps).

**Gap checker.** `tools/check_gaps.py`: applies the gap rules to a schema-valid card and lists under `review_required` the checks that only a reviewer can make. It does not check schema shape. See [README](README.md#when-not-applicable-is-allowed).

**Gap disposition.** The `disposition` of a gap: `not_applicable_contract`, `not_applicable_scope`, `searched_not_found`, `not_supplied`, `budget_exhausted`, `blocked`, `source_excluded`, `unknown_source_scope` or `converter_error`. Each value says why the value is missing; `blocked` and `converter_error` record a failure of the process, not a fact about the source. `searched_not_found` requires at least one query id, `not_applicable_scope` requires a `scope_ref`, and the field class and gap policy restrict which values a path may take. See [README](README.md#gaps) for the meaning of each value.

**Gap policy.** The file [`gap-path-policy.json`](gap-path-policy.json): for each catalogue path, whether a gap may call the field not applicable. `never`: it may not; `contract`: the path is stored outside the card and the disposition is `not_applicable_contract`; `scope`: the disposition is `not_applicable_scope`, only under the condition the policy names. See [README](README.md#when-not-applicable-is-allowed).

**Hallmarks of aging.** The twelve hallmarks of López-Otín et al. 2023, pinned as [`ohf:hallmarks@1`](../vocabularies/hallmarks-1.json). In the aging profile `profile.aging_hallmarks[]` names the hallmarks that atoms of the card concern, each with those atoms. See [README](README.md#domain-profiles).

**Human proximity.** From OHF 1.1, `evidence.lines[].human_proximity`: the rung of a line, from in vitro to human clinical, which follows from the line's taxon and, for humans, its endpoint kind. `tools/check_refs.py` derives it and reports a rung that differs. See [README](README.md#ohf-11).

**Hypothesis.** A proposed claim about a living system, typically an explanation of an observed phenomenon, that goes beyond established knowledge at the time it is stated, is stated with its scope and conditions, and entails observations that would count for or against it. A hypothesis later confirmed or refuted is still recorded as it stood when it was stated. See the [repository README](../README.md#why-ohf).

**Independence group.** `evidence.lines[].independence_group`: a card-local label; evidence lines with the same label rest on the same data, study or laboratory and are not independent of each other. It is recorded in the added zone. From OHF 1.1 its `key` names where the data first appeared (DOI, PMID, PMCID, registry or accession), so groups compare across cards. See [fields](fields.md).

**Indirectness.** `evidence.lines[].indirectness`: how far an evidence line is from the claim it is attached to, judged separately for the test system, the endpoint, the intervention and the comparison: `none`, `some`, `serious` or `not_applicable`. It is an assessment in OHF's own vocabulary, not mapped to GRADE. See [fields](fields.md).

**Known result.** From OHF 1.1, the novelty status `known_result`: the card restates a result already known, with the prior claims, the search scope and its date, and no `new_content`. See [README](README.md#ohf-11).

**Layer.** One of the seven scientific layers that both zones use: claim core (`core`), mechanism (`mechanism`), predictions (`predictions`), evidence (`evidence`), provenance (`provenance`), profile (`profile`) and appendix (`appendix`). The catalogue also has layer 0, identity and versions, which applies to the whole card, and the pair-level record, which is stored outside cards. See [README](README.md).

**Licence.** The terms under which a source may be reused. The prose of this specification spells the word *licence*; field names and values use *license*: `author.source.license` and `rights_basis: "license"`. `author.source.license` is the licence the retrieved source record states at `retrieved_at`, given as an SPDX identifier; a CC BY licence whose version the record does not state is `LicenseRef-CC-BY-version-not-stated`, and from OHF 1.2 a work whose copyright term has expired is `LicenseRef-public-domain-term` with `rights_basis: "public_domain_term"`. From OHF 1.3 the ids OHF defines are listed in `ohf:licence-refs@1` with the release each is defined from. See [source licence](README.md#card-members-outside-the-layers) and [logical types](logical-types.md).

**Locator.** The pointer from an author-zone value into the source text, held in `locator`, for example a paragraph of the source's full-text XML. Source records also carry a locator. See [README](README.md#logical-paths-and-storage).

**Logical path.** The name of a scientific concept in the catalogue, such as `core.statement` or `predictions[].form`, before provenance wrappers are added. Its storage in a card is given by its card path. See [README](README.md#logical-paths-and-storage).

**Logical type.** The type a catalogue path gives a value, such as Identifier, Text or Term. Quantities, intervals, assessments and other source-text records are nonblank source-literal strings, and unknown record keys are rejected. See [logical types](logical-types.md).

**Machine author.** An `author.generator` of kind `ai_system` or `hybrid`. Only a machine author may give the generation `prompt` and `generated_at` (OHF 1.1).

**Modality.** `core.atoms[].modality`: how firmly the author asserts an atom: `speculative`, `proposed`, `likely` or `claimed_shown`, with the author's exact wording in `basis_quote`. It is required on every added-zone atom. See [fields](fields.md).

**Pair brief.** A detached artifact, [`ohf:pair-brief@1`](../schema/pair-brief-1.schema.json), that describes two card versions side by side: their relation, the observations both explain, the observations they expect differently, and a decisive test or a gap saying why none is known. It does not judge which hypothesis is better. See [relations and pair briefs](README.md#relations-and-pair-briefs).

**Paraphrase.** An added string value that restates the source in other words, marked `paraphrase: true` and carrying the restated passage in `basis_quote`. It requires a non-null source and does not become an author quotation; a resolver must check the source and the exact supporting quote. See [logical types](logical-types.md#paraphrases).

**Prediction.** An item of `predictions[]`: an observation the hypothesis expects, distinct from an observed outcome, stated with its test system, endpoint, logical form and epistemic status. A prediction is comparable when, across both zones, it states its system, endpoint, form and epistemic status, and a direction if its form is `directional_contrast`. See [fields](fields.md).

**Prediction form.** `predictions[].form`: the logical form of a prediction, which says what kind of observation tests it: `directional_contrast`, `presence_absence`, `parameter_value`, `functional_form`, `pattern`, `distribution`, `phylogenetic_comparative` or `historical_counterfactual`. See [fields](fields.md).

**Producer.** `added.produced_by`: who produced the added zone, `independent_pipeline`, `submitter` or `example_converter`, with the pipeline name, version and an optional run identifier. Which producers a consumer accepts is the consumer's rule. See [integrity](README.md#integrity).

**Proposition.** The scientific claim a card records, identified by `identity.proposition_id` and distinct from any speaker or publication. `identity.version` is the immutable version of the proposition record. See [fields](fields.md).

**Reference checker.** `tools/check_refs.py`: resolves the internal references of a schema-valid card, applies the integrity rules the schema cannot express, and reports which predictions are comparable. See the [checker](../tools/check_refs.py).

**Relations artifact.** A detached artifact, [`ohf:hypothesis-relations@1`](../schema/hypothesis-relations-1.schema.json), that records typed edges between card versions in a fixed pool: `rival_same_explanandum`, `nested`, `compatible_independent`, `duplicate`, `refines`, `unrelated`, and from OHF 1.1 `analog` or `mechanism_neighbour`; from OHF 1.1 an edge may join single records, such as atoms, of the two card versions. Support and contradiction are evidence relations and are not included. See [relations and pair briefs](README.md#relations-and-pair-briefs).

**Resolution record.** From OHF 1.2, an entailment record with basis `resolution`: a tool checked the value against an external record and names that record's source, the SHA-256 of its response and the key it looked up. Its verdict is `entails` or `no`; when the record could not be retrieved or matched no single entry, no record is written. See [README](README.md#ohf-12).

**Result estimate.** From OHF 1.1, `evidence.lines[].result_estimate` in the added zone: the result the line's quote reports, word for word, with its measure, contrast and scale as the source states them, or `not_stated`. See [README](README.md#ohf-11).

**Risk of bias.** `evidence.lines[].risk_of_bias`: the risk that the study behind an evidence line is biased: `low`, `some`, `high` or `not_assessed`, with an optional tool reference and note. It is an assessment in OHF's own vocabulary, not mapped to RoB 2. See [fields](fields.md).

**Role.** `core.atoms[].role`: the part an atom plays in the hypothesis: `core`, `auxiliary` (an assumption the hypothesis needs), `consequence` (follows from other atoms) or `background_established`. It is required on every added-zone atom. See [fields](fields.md).

**Rung.** One step of the proximity ladder of `ohf:terms@1`, from in vitro to human clinical; see Human proximity.

**Sample of a result.** From OHF 1.1, `evidence.lines[].sample`: whether a line's result is about the whole sample or a named subgroup, a primary or secondary outcome, and a pre-specified or post hoc analysis. See [README](README.md#ohf-11).

**Schema pass.** Validity against the card schema. It checks shape only: it does not show that a quotation matches its source, that a source supports a claim, or that a card is complete. See [schema](../schema/README.md).

**Scope aspect.** From OHF 1.1, what a `scope_differs` item of a relations edge says two cards differ on: `endpoint`, `population` or `system`. Each aspect allows only certain fields; see [Relations and pair briefs](README.md#relations-and-pair-briefs).

**Source record.** An entry of `added.sources`, named by its key, that gives a `source`, a `locator`, the time `accessed_at` and the `tool` used. Added-zone values point to it through `src`. See [README](README.md#logical-paths-and-storage).

**Source verification.** `added.source_verification`: whether the source was downloaded again and compared with `author.source.source_text_sha256`: `refetched_match`, `refetched_mismatch`, or `not_refetchable` with a reason. A refetch gives its URL, time and SHA-256, and an optional `metadata_check` records a registry lookup; `retracted: false` means only that the registry listed no retraction at `checked_at`. See [integrity](README.md#integrity).

**Source-literal value.** A quantity, interval, assessment or other source-text record kept as a nonblank string in the source's own wording. OHF defines no normalized structure for it, and scientific values are not rewritten. See [logical types](logical-types.md#source-literal-records).

**`src`.** The member of an added-zone value that names, by its key in `added.sources`, the source record the value comes from. See [README](README.md#logical-paths-and-storage).

**`standard_version`.** The card member that names the format version: `"1.0"`, `"1.1"`, `"1.2"` or `"1.3"`; any other value is rejected. A card is checked by the rules of its version and may not carry a member introduced in a later one. The release of the standard, with its patch number, is `added.by.standard_release` (OHF 1.3). See [README](README.md).

**Test fixture.** A file in [`tests/fixtures/`](../tests/fixtures/README.md) that serves as input for the tests and illustrates fields in the [field reference](fields.md). Fixtures are not example cards, and the fictional cards among them are not scientific evidence.

**Triple.** From OHF 1.1, `core.atoms[].triple`: an atom read as subject, relation and object for machine linking. The relation is an RO id or a Biolink slot; subject and object are CURIEs or mechanism entities of the card. The atom's statement remains the claim. See [README](README.md#ohf-11).

**Validator.** `tools/validate.py`: checks a card against the schema, rejects duplicate JSON members, non-finite numbers and invalid calendar timestamps, and reports every schema error. See the [validator](../tools/validate.py).

**Vocabulary pin.** An entry of `vocabularies` that names a controlled vocabulary by id and SHA-256, such as `ohf:profiles@1` and `ohf:heuristics@1`, from OHF 1.1 `ohf:terms@1`, `ohf:profiles@2` and `ohf:hallmarks@1`, from OHF 1.2 `ohf:predicates@1`, and from OHF 1.3 `ohf:licence-refs@1`. The schema fixes the hash, so a card is bound to one exact vocabulary file. See [vocabularies](../vocabularies/profiles-1.json).

**Withheld quote.** From OHF 1.1, `evidence.lines[].quote_withheld`: in place of a quote that may not be reproduced, the reason, the locator, the record, a paraphrase and the abstract sentence that entails it. Such a line is counted but does not make the disputing side for `full`. See [README](README.md#ohf-11).

**Zone.** One of the two parts of a card that hold scientific values: the author zone and the added zone. Both use the same layers. See [README](README.md).
