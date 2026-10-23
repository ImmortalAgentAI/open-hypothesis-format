# Field reference

This reference lists all 216 logical catalogue paths. Each path has a short example value from the catalogue. Where a card fills the path, a longer example follows: from the example card muller-sheltering, converted from a published article, or from a fictional test card, whose values describe a fictional system and are not scientific evidence. A JSON pointer identifies each card example. An absent concept is illustrated by the card's explicit gap; no missing value is invented. Definitions and logical types describe the concept before provenance wrappers.

Generated from [the reference data](field-reference.json) with `python tools/build_field_reference.py`. Edit the reference data and regenerate this file.

The `basis` key records the catalogue's conceptual source family; it is not evidence for the example's scientific claim. Source records in each card supply that evidence.

The class says how a missing value is treated. `searchable`: the value can be looked for in sources, and a gap records the search. `author_only`: only the author can state it; absence means "not declared", and no search is made. `system`: the value is assigned by the record itself; an empty value is a valid value.

The check says how an added value is checked in an OHF 1.2 card. `passage`: against the paragraph its `src` names, by an entailment checker. `resolution`: against an external record, by a tool. `card`: against the card itself, by `tools/check_refs.py`; no record is written. An object gives the check of each member.

## 0 Identity and versions

### `identity.proposition_id`

Stable local identifier for the scientific proposition, distinct from any speaker or publication.

Type: `Identifier`. Vocabulary: OHF namespace, with external identifiers retained separately. Basis: `sepio`. Class: `system`. Check: `card`.

Example value: urn:example:proposition-a

Example from card muller-sheltering at `/identity/proposition_id`:

```json
"h_muller-sheltering-extension"
```

### `identity.version`

Immutable version of this proposition record, to which matches bind.

Type: `Version`. Vocabulary: Positive integer. Basis: `ohf`. Class: `system`. Check: `card`.

Example value: 1

Example from card muller-sheltering at `/identity/version`:

```json
1
```

### `identity.question_refs[]`

Optional references to the question, problem or knowledge gap addressed by the claim, retaining source attribution and any earlier bindings. Not required, and not a comparison or ranking key.

Type: `Reference[]`. Vocabulary: References to question or problem records, with source attribution. Basis: `ohf`. Class: `system`. Check: `card`.

Example value: problem-context-example@1 (optional)

### `identity.assertions[].id`

Identity of one attributed act of asserting or assessing a proposition.

Type: `Identifier`. Vocabulary: Card-local identifier, separate from the proposition identifier. Basis: `sepio`. Class: `system`. Check: `card`.

Example value: urn:example:assertion-a

### `identity.assertions[].text`

Source wording of this particular assertion, separate from canonical proposition text.

Type: `Text`. Vocabulary: SEPIO Statement.statementText. Basis: `sepio`. Class: `author_only`. Check: `passage`.

Example value: author's assertion wording

### `identity.assertions[].agent_ref`

Person, organization or agent responsible for this assertion, not the converter.

Type: `Reference`. Vocabulary: SEPIO Contribution / Agent identity. Basis: `sepio`. Class: `author_only`. Check: `card`.

Example value: urn:example:author-a

### `identity.assertions[].asserted_at`

Time the assertion was made, distinguished from extraction and registration time.

Type: `DateTime`. Vocabulary: ISO 8601 timestamp with stated precision. Basis: `sepio`. Class: `author_only`. Check: `passage`.

Example value: 2026-10-15T10:00:00Z

### `identity.assertions[].stance`

Speaker's stated position on the proposition, with original wording retained.

Type: `Term`. Vocabulary: Source vocabulary plus reviewed OHF mapping. Basis: `sepio`. Class: `author_only`. Check: `passage`.

Example value: supports

### `identity.assertions[].confidence`

Attributed confidence with scale, elicitation method and calibration status, not a BT score.

Type: `Assessment`. Vocabulary: Declared probability or ordinal scale. Basis: `hep`. Class: `author_only`. Check: `passage`.

Example value: 0.6, elicited and uncalibrated

### `identity.duplicate_cluster_ref`

Curated similarity/deduplication cluster, not proof of identical wording or meaning.

Type: `Reference`. Vocabulary: Reference to a cluster record kept by the publisher, or null. Basis: `micropublications`. Class: `system`. Check: `card`.

Example value: urn:example:cluster-a

### `identity.representative_ref`

Versioned representative of that cluster, with selection reason retained.

Type: `Reference`. Vocabulary: Versioned reference to one card of the cluster, or null. Basis: `micropublications`. Class: `system`. Check: `card`.

Example value: proposition-a@1

### `identity.supersedes[]`

Earlier versions explicitly superseded by an authorized author act, retaining history.

Type: `VersionReference[]`. Vocabulary: Versioned references to earlier records of the same proposition. Basis: `ohf`. Class: `system`. Check: `card`.

Example value: proposition-a@1

### `identity.retractions[]`

Author-issued withdrawal or source retraction with target, actor, time, reason and evidence.

Type: `Retraction[]`. Vocabulary: Retraction records; source notices are recorded separately. Basis: `nanopub`. Class: `system`. Check: `passage`.

Example value: withdrawal of assertion-a with source notice

### `identity.lifecycle`

The card's state in its publisher's process, as the publisher names it, not inferred from source praise. OHF 1.0 defines no states and no transitions.

Type: `Term`. Vocabulary: The publisher's own label, such as example or fixture; OHF 1.0 defines no lifecycle states or transitions. Basis: `hep`. Class: `system`. Check: `passage`.

Example value: example

Example from card muller-sheltering at `/identity/lifecycle`:

```json
"example"
```

## 1 Claim core

### `core.statement`

One bounded scientific assertion preserving negation, modality and quantities.

Type: `Text`. Vocabulary: Source wording plus confirmed canonical restatement. Basis: `ohf`. Class: `searchable`. Check: `passage`.

Example value: Compound X reduces readout Y in cell system Z at 48 hours.

Example from card muller-sheltering at `/author/layers/core/statement`:

```json
{
  "value": "By relaxing restrictive assumptions of earlier models, we show that sheltering promotes fixation of LOF mutations with sexually dimorphic fitness effects, resulting in decay of X-linked genes that are exclusively expressed by males and Y-linked genes that are primarily, though not necessarily exclusively, expressed by females.",
  "locator": "XML .//p[1] (1-based document order)"
}
```

### `core.kind`

Kind of claim, distinct from evidence type and generation method.

Type: `Term`. Vocabulary: OHF vocabulary: mechanism | association | intervention_effect | prediction. Basis: `ohf`. Class: `searchable`. Check: `passage`.

Example value: intervention_effect

Example from card muller-sheltering at `/added/layers/core/kind`:

```json
{
  "value": "mechanism",
  "src": "abstract"
}
```

### `core.explanandum`

Phenomenon or question the claim attempts to explain, without adding an unstated target. It names an observed phenomenon or an open question, not an intended outcome or the goal of an intervention.

Type: `Text`. Vocabulary: Author wording. Basis: `ohf`. Class: `searchable`. Check: `passage`.

Example value: variation of readout Y in system Z

Example from card muller-sheltering at `/author/layers/core/explanandum`:

```json
{
  "value": "the evolutionary patterns of both gene loss and sex-biased gene content on sex chromosome",
  "locator": "XML .//p[5] (1-based document order)"
}
```

### `core.scope`

Systems and conditions to which the claim applies, including explicit exclusions.

Type: `Text`. Vocabulary: Author wording and domain qualifiers. Basis: `biolink`. Class: `searchable`. Check: `passage`.

Example value: cell system Z only, not organism survival

Example from card muller-sheltering at `/added/layers/core/scope`:

```json
{
  "value": "A population-genetic model of homologous X and Y regions that no longer recombine and start with the same functional genes; it applies equally to Z and W chromosomes with the sexes switched. It concerns loss-of-function mutations: fixation on the X requires complete recessivity, while incomplete recessivity narrows, but does not remove, gene loss from the Y. Its importance in nature depends on the distribution of dominance and of sex-specific fitness effects.",
  "src": "aim"
}
```

### `core.context[]`

Typed context qualifiers with source locators and context inheritance rules.

Type: `Qualifier[]`. Vocabulary: Typed qualifiers, with the source terms retained. Basis: `biolink`. Class: `searchable`. Check: `passage`.

Example value: exposure duration: 48 hours

### `core.assumptions[].id`

Local identifier of one explicitly declared premise.

Type: `Identifier`. Vocabulary: OHF local identifiers. Basis: `micropublications`. Class: `system`. Check: `card`.

Example value: assumption-a

### `core.assumptions[].text`

Author-stated premise, not background supplied by an extractor.

Type: `Text`. Vocabulary: Source wording. Basis: `micropublications`. Class: `searchable`. Check: `passage`.

Example value: readout Y reflects the stated cellular process

### `core.assumptions[].fundamental`

Author's explicit fundamental/non-fundamental classification, never guessed.

Type: `Boolean`. Vocabulary: OHF author declaration. Basis: `ohf`. Class: `author_only`. Check: `passage`.

Example value: true, only if explicitly declared

### `core.assumptions[].assessment`

Separate attributed assessment of a premise, with direction, scale and evidence.

Type: `Assessment`. Vocabulary: Attributed assessment record. Basis: `sepio`. Class: `searchable`. Check: `passage`.

Example value: unassessed

### `core.falsification_condition`

Scoped contrary observation that would count against this claim.

Type: `Text`. Vocabulary: Author-defined resolution rule. Basis: `popper`. Class: `searchable`. Check: `passage`.

Example value: opposite direction under the same stated conditions

Example gap from card muller-sheltering: `core.falsification_condition` is a `not_supplied` gap. The article states testable predictions but no result that would count against the extended hypothesis.

### `core.atoms[].id`

Identity of a subclaim, retaining its original text and provenance.

Type: `Identifier`. Vocabulary: OHF local identifiers. Basis: `hyque`. Class: `system`. Check: `card`.

Example value: atom-a

Example from card muller-sheltering at `/added/layers/core/atoms/0/id`:

```json
"a_sex_dimorphic"
```

### `core.atoms[].statement`

Atomic assertion without losing condition, uncertainty or negation.

Type: `Text`. Vocabulary: Source wording. Basis: `hyque`. Class: `searchable`. Check: `passage`.

Example value: X affects Y under condition C

Example from card muller-sheltering at `/added/layers/core/atoms/0/statement`:

```json
{
  "value": "Loss-of-function mutations often reduce fitness by different amounts in females and males.",
  "src": "assumptions"
}
```

### `core.atoms[].parent_ref`

Parent claim or atomic group from which context may be inherited.

Type: `Reference`. Vocabulary: Reference to the parent claim or atom; null for a root atom. Basis: `hyque`. Class: `system`. Check: `card`.

Example value: proposition-a@1

### `core.atoms[].operator`

Explicit connective among child claims, not an inference from a list.

Type: `Term`. Vocabulary: AND | OR | XOR. Basis: `hyque`. Class: `searchable`. Check: `passage`.

Example value: AND

### `core.atoms[].context_override`

Explicit child context differing from its parent, with locator.

Type: `Qualifier[]`. Vocabulary: Typed qualifiers, with a locator. Basis: `ohf`. Class: `system`. Check: `passage`.

Example value: different exposure duration, when stated

### `core.atoms[].claim_type`

What kind of claim the atom makes. The value other needs a note that says what the claim is.

Type: `Term`. Vocabulary: OHF vocabulary: existence | distribution | association | causal_effect | mechanism | functional_attribution | evolutionary_explanation | development | constitution | quantitative_law | model_sufficiency | historical_reconstruction | other. Basis: `ohf`. Class: `author_only`. Check: `passage`. Zones: `added`.

Example value: causal_effect

Example from card muller-sheltering at `/added/layers/core/atoms/0/claim_type`:

```json
{
  "value": "distribution",
  "src": "assumptions"
}
```

### `core.atoms[].role`

The part the atom plays in the hypothesis: a core claim, an auxiliary assumption, a consequence of other atoms, or established background knowledge.

Type: `Term`. Vocabulary: OHF vocabulary: core | auxiliary | consequence | background_established. Basis: `ohf`. Class: `author_only`. Check: `passage`. Zones: `added`.

Example value: core

Example from card muller-sheltering at `/added/layers/core/atoms/0/role`:

```json
{
  "value": "core",
  "src": "assumptions"
}
```

### `core.atoms[].modality`

How firmly the author asserts the atom, with the exact author wording on which the value rests.

Type: `Term`. Vocabulary: OHF vocabulary: speculative | proposed | likely | claimed_shown. Basis: `ohf`. Class: `author_only`. Check: `passage`. Zones: `added`.

Example value: proposed, "Here, I hypothesize that"

Example from card muller-sheltering at `/added/layers/core/atoms/0/modality`:

```json
{
  "value": "proposed",
  "src": "assumptions",
  "basis_quote": "It therefore seems plausible for LOF alleles to differentially affect the fitness of each sex, though this has not yet been systematically tested."
}
```

### `core.atoms[].requires`

Atoms of this card that must hold for this atom to hold.

Type: `Reference`. Vocabulary: Identifiers of atoms of this card. Basis: `ohf`. Class: `author_only`. Check: `card`. Zones: `added`. Since: OHF 1.1.

Example value: a_mtorc1_inhibition

### `core.atoms[].contradicts`

Atoms of this card that cannot hold together with this atom as stated, such as a version the card states and rejects. Not a relation between hypotheses: that is evidence.

Type: `Reference`. Vocabulary: Identifiers of atoms of this card. Basis: `ohf`. Class: `author_only`. Check: `card`. Zones: `added`. Since: OHF 1.1.

Example value: a_mtorc1_inhibition

### `core.atoms[].triple`

The atom as subject, relation and object for machine linking. The statement stays the claim; the triple is a reading of it and may be coarser. Subject and object are ontology terms or mechanism entities of this card.

Type: `Triple`. Vocabulary: Relation from RO (RO:nnnnnnn) or the Biolink Model (biolink:slot); subject and object as CURIEs; qualifiers as Biolink qualifier slots. Basis: `ohf`. Class: `author_only`. Check: `passage`. Zones: `added`. Since: OHF 1.1.

Example value: rapamycin RO:0002212 negatively regulates mTORC1

### `core.potential_benefit`

Source-grounded potential benefit, target system, causal bridge, horizon and constraints without an unsupported effect estimate.

Type: `PotentialBenefit`. Vocabulary: OHF record. Basis: `ohf`. Class: `searchable`. Check: `passage`.

Example value: outcome "counter Y stays high for longer", for operators of system four, constrained to the fictional system

Example from fictional card fx_four at `/added/layers/core/potential_benefit`:

```json
{
  "value": {
    "outcome": "Counter Y stays high for longer in system four.",
    "beneficiaries_or_system": "Operators of fictional system four",
    "constraints": [
      "Fictional system only"
    ]
  },
  "src": "benefit"
}
```

### `core.novelty_assessment`

Bounded, source-grounded assessment of new and shared content with retained search or review evidence.

Type: `NoveltyAssessment`. Vocabulary: OHF record; status claimed | bounded_search | expert_review | known_result (OHF 1.1: the result is already published, named by prior_claim_refs within a recorded search, and there is no new content). Basis: `ohf`. Class: `searchable`. Check: `passage`.

Example value: new: agent Q as a way to act on target T; shared: the link between T and counter Y

Example from fictional card fx_four at `/author/layers/core/novelty_assessment`:

```json
{
  "value": {
    "status": "claimed",
    "new_content": "Agent Q as a way to act on target T.",
    "shared_content": "The link between target T and counter Y."
  },
  "locator": "JSON:/prior_work"
}
```

### `core.uncertainties[]`

Explicit unresolved scientific questions and their consequences, targets and possible resolution tests.

Type: `Uncertainty[]`. Vocabulary: OHF record. Basis: `ohf`. Class: `searchable`. Check: `passage`.

Example value: question "does target T limit counter Y in system five?", consequence: the claim is limited to system four

Example from fictional card fx_four at `/added/layers/core/uncertainties`:

```json
{
  "value": [
    {
      "id": "u1",
      "question": "Does target T limit counter Y in fictional system five as well?",
      "consequence": "The claim would be limited to system four."
    }
  ],
  "src": "open_question"
}
```

### `core.alternative_explanations[]`

Source-grounded alternative explanations outside the pinned comparison pool, retaining shared observations and distinguishing predictions. In-pool comparisons use pair-level diagnostics.

Type: `AlternativeExplanation[]`. Vocabulary: OHF record. Basis: `ohf`. Class: `searchable`. Check: `passage`.

Example value: agent Q raises counter Y through target U instead of T, told apart by prediction p1

Example from fictional card fx_four at `/added/layers/core/alternative_explanations`:

```json
{
  "value": [
    {
      "claim_or_ref": {
        "kind": "literal",
        "text": "Agent Q may raise counter Y through fictional target U instead of T."
      },
      "distinguishing_prediction_refs": [
        {
          "kind": "card",
          "pointer": "/added/layers/predictions/0"
        }
      ]
    }
  ],
  "src": "alternative"
}
```

### `core.alternative_explanations[].id`

Identifier of the alternative explanation, so that an evidence line or a prediction can name it without depending on its position in the list.

Type: `Identifier`. Vocabulary: Card-local identifier, unique among alternatives. Basis: `ohf`. Class: `system`. Check: `card`. Since: OHF 1.1.

Example value: alt_cr_mimetic

### `core.base_rate`

Source-grounded rate in an explicit reference class, with denominator and source horizon preserving its stated precision.

Type: `BaseRate`. Vocabulary: OHF record. Basis: `ohf`. Class: `searchable`. Check: `passage`.

Example value: 6 of 40 agents screened in system four raised counter Y (rate 0.15, as of 2026-01-01)

Example from fictional card fx_four at `/added/layers/core/base_rate`:

```json
{
  "value": {
    "reference_class": "Fictional agents screened in system four",
    "rate": 0.15,
    "denominator": 40,
    "source": {
      "kind": "artifact",
      "sha256": "sha256:82d82118fca7a79c3837cafa3d89f14cc612ae24e3023e975b45d829dcf9f53d",
      "json_pointer": "/base_rate"
    },
    "as_of": "2026-01-01"
  },
  "src": "base_rate"
}
```

### `core.explains[]`

Observations the hypothesis accounts for. Each item records the observation, its current status (unexplained, contested, explained by a rival hypothesis, or explained by an accepted account), whether the hypothesis explains it directly or as a consequence, and the atoms or predictions that do the explaining. Only unexplained and contested observations count as gaps in knowledge. Serves the question: which gaps in knowledge would the hypothesis close if confirmed?

Type: `Explanandum[]`. Vocabulary: OHF vocabulary: status unexplained | contested | explained_by_rival | explained; mode direct | consequence. Basis: `ohf`. Class: `searchable`. Check: `passage`. Question part: `gaps_closed`.

Example value: Y-linked gene loss after recombination stops, explained by an accepted account

Example from card muller-sheltering at `/added/layers/core/explains/value/0`:

```json
{
  "id": "x_y_loss",
  "observation": "After recombination stops between the X and Y, the Y loses genes.",
  "status": "explained",
  "mode": "direct",
  "atom_refs": [
    "a_y_decay",
    "a_reinforce"
  ]
}
```

### `core.reinterprets[]`

Existing findings that the hypothesis reads differently: the finding, its current interpretation, the proposed interpretation and the atoms that ground it. Serves the question: which existing data would the hypothesis make us reinterpret?

Type: `Reinterpretation[]`. Vocabulary: No fixed vocabulary; each item holds the finding, its current and proposed interpretations and the atom identifiers. Basis: `ohf`. Class: `searchable`. Check: `passage`. Question part: `data_reinterpreted`.

Example value: early models read as a rejection of sheltering, reread under sex-specific costs

Example from card muller-sheltering at `/added/layers/core/reinterprets/value/0`:

```json
{
  "id": "r_early_models",
  "finding": "Early models showed that recessive lethal mutations stay rare on the Y in large populations, because the same mutations also arise on the X.",
  "finding_ref": {
    "kind": "card",
    "pointer": "/added/layers/evidence/lines/0"
  },
  "current_interpretation": "Sheltering cannot cause Y-linked gene loss, so Muller's hypothesis is rejected.",
  "proposed_interpretation": "The models assumed lethal mutations with equal costs in both sexes. When costs differ between the sexes, sheltering fixes loss-of-function alleles on the X or the Y.",
  "atom_refs": [
    "a_sex_dimorphic",
    "a_y_decay",
    "a_x_decay"
  ]
}
```

### `core.opens[]`

New questions that the hypothesis makes worth asking, why they are not asked today and, when known, the method that would answer them. Serves the question: which new directions would the hypothesis open?

Type: `OpenedQuestion[]`. Vocabulary: No fixed vocabulary; each item holds the question, why it could not be asked before, the enabling method and the atom identifiers. Basis: `ohf`. Class: `searchable`. Check: `passage`. Question part: `directions_opened`.

Example value: whether ants spread bactericidal fatty acids by grooming

Example from card muller-sheltering at `/added/layers/core/opens/value/0`:

```json
{
  "id": "o_dominance_distribution",
  "new_question": "What is the full distribution of dominance of loss-of-function mutations, not only its mean?",
  "why_not_askable_today": "Most available mutation data were insufficient for estimating aspects of the distribution of dominance other than its mean.",
  "enabling_method": "Genetic engineering combined with high-throughput phenotyping.",
  "atom_refs": [
    "a_recessive"
  ]
}
```

### `core.testability`

Whether the claim can be tested in any system, in principle and in practice, with a justification and the cheapest known test. When a human study is the cheapest test, the test refers to profile.human_testability instead of restating it.

Type: `Testability`. Vocabulary: OHF vocabulary: in_principle testable | not_testable | unclear; in_practice feasible_now | needs_new_method | not_feasible | unclear. Basis: `ohf`. Class: `searchable`. Check: `passage`.

Example value: testable and feasible now, cheapest test a chemical disruptor

Example from card muller-sheltering at `/added/layers/core/testability`:

```json
{
  "value": {
    "in_principle": "testable",
    "in_practice": "feasible_now",
    "justification": "The model is formal; its predictions can be compared with the gene content and gene losses of sex chromosomes in taxa where the ancestral genes and their sex-specific functions are known. Its importance in nature also needs measurements of dominance and of sex-specific fitness costs, which are harder to obtain.",
    "cheapest_test": {
      "kind": "literal",
      "text": "In a taxon with known ancestral sex-chromosome genes, test whether Y-linked genes whose ancestral function mattered most for females decayed fastest."
    }
  },
  "src": "y_rates",
  "assessment": {
    "assessor": "ohf-example-conversion 1.0.0",
    "assessed_at": "2026-10-20T17:04:22Z",
    "evidence_ref": {
      "kind": "artifact",
      "sha256": "sha256:aec24a2447826a7ba21328f44dd243644e621fc0eb07894800e2bf124eadf09e"
    }
  }
}
```

### `core.first_proposed`

When the idea was first proposed: a date at the stated precision, the record that shows it, and whether the date comes from the author's statement or from a bounded search. A bounded search names its search scope.

Type: `FirstProposal`. Vocabulary: OHF vocabulary: precision year | month | day; basis author_statement | bounded_search. Basis: `ohf`. Class: `searchable`. Check: `passage`.

Example value: 1971, author statement

Example from card muller-sheltering at `/added/layers/core/first_proposed`:

```json
{
  "value": {
    "source_ref": {
      "kind": "external",
      "uri": "https://doi.org/10.1093/molbev/msaf177",
      "limitation": "The article itself; its full text is not in this repository."
    },
    "date": "2025-07-26",
    "precision": "day",
    "basis": "author_statement",
    "note": "The extension is proposed in this article (paragraph 5); the date is its electronic publication date. Muller's original sheltering hypothesis dates from 1914. The article also credits Neuhaus (1939) with the intuition that X-linked male-limited genes might decay, and builds on the model of Mrnjavac et al. (2023) (paragraph 45)."
  },
  "src": "pubdate"
}
```

## 2 Mechanism

### `mechanism.summary`

Author's narrative mechanism, separate from a verified causal conclusion.

Type: `Text`. Vocabulary: Source wording. Basis: `indra`. Class: `searchable`. Check: `passage`.

Example value: X may alter process Y

Example from card muller-sheltering at `/author/layers/mechanism/summary`:

```json
{
  "value": "Our model shows that sheltering of LOF mutations promotes the evolutionary decay of certain types of genes from X and Y chromosomes, resulting in enrichments of female-biased genes on the X (owing to a deficit of male-limited genes) and male-biased genes on the Y (owing to a deficit of genes that are more important for female than male fitness).",
  "locator": "XML .//p[34] (1-based document order)"
}
```

### `mechanism.black_box`

Whether mechanism is explicitly treated as unknown/black-box, not merely omitted.

Type: `Boolean`. Vocabulary: OHF author declaration. Basis: `ohf`. Class: `author_only`. Check: `passage`.

Example value: true, if author states mechanism unknown

Example gap from fictional card fx_eight: `mechanism.black_box` is a `not_supplied` gap. The source does not say whether the mechanism is treated as unknown.

### `mechanism.entities[].id`

Stable identifier for an explicitly grounded biological entity.

Type: `Identifier`. Vocabulary: Identifiers from ChEBI, UniProt, GO, Reactome or another named registry. Basis: `indra`. Class: `searchable`. Check: `card`.

Example value: UniProt:P42345 as a vocabulary example only

### `mechanism.entities[].label`

Source name of the entity and any verified normalized label.

Type: `Text`. Vocabulary: Source wording; a normalized label names its registry release. Basis: `indra`. Class: `searchable`. Check: `passage`.

Example value: protein X

### `mechanism.steps[].id`

Identity of one proposed mechanistic step.

Type: `Identifier`. Vocabulary: OHF local identifiers. Basis: `indra`. Class: `system`. Check: `card`.

Example value: step-a

### `mechanism.steps[].subject_ref`

Grounded subject entity of the proposed step.

Type: `Reference`. Vocabulary: Identifier of an entity in mechanism.entities[]. Basis: `indra`. Class: `searchable`. Check: `card`.

Example value: entity-a

### `mechanism.steps[].relation`

Typed relation, with its ontology identifier and version when mapped.

Type: `Term`. Vocabulary: RO or a reviewed domain relation mapping. Basis: `biolink`. Class: `searchable`. Check: `passage`.

Example value: positively regulates, if stated

### `mechanism.steps[].sign`

Declared positive, negative or unspecified effect, distinct from truth/negation.

Type: `Term`. Vocabulary: OHF vocabulary: positive | negative | unspecified. Basis: `indra`. Class: `searchable`. Check: `passage`.

Example value: negative

### `mechanism.steps[].object_ref`

Grounded object entity of the proposed step.

Type: `Reference`. Vocabulary: Identifier of an entity in mechanism.entities[]. Basis: `indra`. Class: `searchable`. Check: `card`.

Example value: entity-b

### `mechanism.steps[].evidence_type`

Type of support for this step, not a numeric confidence invented from a citation.

Type: `Term`. Vocabulary: ECO identifier with release/source locator. Basis: `eco`. Class: `searchable`. Check: `passage`.

Example value: author-stated experimental evidence type

### `mechanism.steps[].evidence_refs[]`

Evidence lines that assess this exact step.

Type: `Reference[]`. Vocabulary: Identifiers of evidence.lines[] in this card. Basis: `sepio`. Class: `searchable`. Check: `card`.

Example value: evidence-line-a

### `mechanism.steps[].context`

System and conditions of this step, retaining explicit deviations from the claim.

Type: `Qualifier[]`. Vocabulary: Typed qualifiers, with the source terms retained. Basis: `biolink`. Class: `searchable`. Check: `passage`.

Example value: cell system Z

### `mechanism.molecular_targets[]`

Identified molecular targets and their supported roles in the proposed mechanism.

Type: `MolecularTarget[]`. Vocabulary: OHF record. Basis: `ohf`. Class: `searchable`. Check: `passage`.

Example value: fictional target T, with the primary role in the mechanism

Example from fictional card fx_four at `/added/layers/mechanism/molecular_targets`:

```json
{
  "value": [
    {
      "label": "Fictional target T",
      "id": "FICTIONAL-T",
      "id_scheme": "GO",
      "role": "primary"
    }
  ],
  "src": "rationale"
}
```

## 3 Predictions and estimands

### `predictions[].id`

Local identity of one prediction, distinct from an observed outcome.

Type: `Identifier`. Vocabulary: OHF local identifiers. Basis: `ohf`. Class: `system`. Check: `card`.

Example value: prediction-a

Example from card muller-sheltering at `/added/layers/predictions/0/id`:

```json
"p_y_female_genes"
```

### `predictions[].population`

Target population/system definition, not a convenience sample inferred by the converter.

Type: `Text`. Vocabulary: ICH estimand population, in the source terms. Basis: `ich`. Class: `searchable`. Check: `passage`.

Example value: cell system Z as stated

Example from card muller-sheltering at `/added/layers/predictions/2/population`:

```json
{
  "value": "Populations large enough to evolve deterministically, with a loss-of-function mutation rate of 10^-5 per gene in each sex; recessive loss-of-function alleles of male-limited genes",
  "src": "rate"
}
```

### `predictions[].system.taxon`

Source-stated organism, with a verified taxonomy mapping when available.

Type: `Term`. Vocabulary: NCBI Taxonomy, otherwise explicit missingness. Basis: `arrive`. Class: `searchable`. Check: `passage`.

Example value: NCBITaxon:10090 as a vocabulary example only

Example from card muller-sheltering at `/added/layers/predictions/2/system/taxon`:

```json
{
  "value": "Drosophila; the generation time is that of D. melanogaster, and the compared neo-X chromosomes are those of D. miranda, D. americana and D. albomicans",
  "src": "rate"
}
```

### `predictions[].system.taxon_id`

NCBI Taxonomy identifier of the taxon named in taxon.

Type: `Identifier`. Vocabulary: NCBI Taxonomy, as NCBITaxon:<number>. Basis: `ohf`. Class: `searchable`. Check: `resolution`. Zones: `added`. Since: OHF 1.1.

Example value: NCBITaxon:10090

### `predictions[].system.strain_or_line`

Strain, genotype or cell-line identity, keeping supplied identifiers.

Type: `TextOrTerm`. Vocabulary: Free text; use a strain or cell-line registry identifier where one exists. Basis: `arrive`. Class: `searchable`. Check: `passage`.

Example value: cell line Z

### `predictions[].system.sex`

Source-stated sex or applicable population description.

Type: `TextOrTerm`. Vocabulary: Source wording, without defaulting to both sexes. Basis: `arrive`. Class: `searchable`. Check: `passage`.

Example value: not stated

### `predictions[].system.age_at_start`

Age when treatment or observation starts, with units and origin.

Type: `QuantityOrInterval`. Vocabulary: UCUM-compatible units and explicit time origin. Basis: `arrive`. Class: `searchable`. Check: `passage`.

Example value: 10 weeks, fictional example

### `predictions[].experimental_unit`

Unit assigned to intervention or observed, distinct from organism label and analysis unit.

Type: `TextOrTerm`. Vocabulary: Source study design. Basis: `arrive`. Class: `searchable`. Check: `passage`.

Example value: culture well, fictional

### `predictions[].system.assessment_age`

Age at endpoint assessment, distinguished from treatment-start age and follow-up.

Type: `QuantityOrInterval`. Vocabulary: Source-defined time origin. Basis: `arrive`. Class: `searchable`. Check: `passage`.

Example value: not stated

### `predictions[].system.site`

Experimental site, laboratory or cohort context when relevant.

Type: `TextOrReference`. Vocabulary: Source identifiers. Basis: `arrive`. Class: `searchable`. Check: `passage`.

Example value: site A

### `predictions[].system.kind`

Level of organization of the test system.

Type: `Term`. Vocabulary: OHF vocabulary: cell | tissue | organism | population | community | ecosystem | clade | in_silico | other. Basis: `ohf`. Class: `searchable`. Check: `passage`.

Example value: community

Example from card muller-sheltering at `/added/layers/predictions/0/system/kind`:

```json
{
  "value": "clade",
  "src": "y_rates"
}
```

### `predictions[].system.environment`

Conditions in which the system is studied, such as laboratory culture, a field site or a simulation.

Type: `Text`. Vocabulary: Source text. Basis: `ohf`. Class: `searchable`. Check: `passage`.

Example value: laboratory colonies

### `predictions[].system.spatial_scale`

Spatial extent of the system or of the observation, such as a culture well, a lake or a continent.

Type: `Text`. Vocabulary: Source text. Basis: `ohf`. Class: `searchable`. Check: `passage`.

Example value: whole lakes

### `predictions[].system.temporal_scale`

Time span over which the prediction applies, such as hours, a growing season or evolutionary time.

Type: `Text`. Vocabulary: Source text. Basis: `ohf`. Class: `searchable`. Check: `passage`.

Example value: about 350,000 generations

Example from card muller-sheltering at `/added/layers/predictions/2/system/temporal_scale`:

```json
{
  "value": "about 350,000 generations, or about 23,000 years",
  "src": "rate"
}
```

### `predictions[].intervention.agent`

Intervention identity, preserving mixtures and unresolved names.

Type: `TextOrTerm`. Vocabulary: ChEBI or another named registry, otherwise the source name. Basis: `ich`. Class: `searchable`. Check: `passage`.

Example value: compound X

### `predictions[].intervention.dose`

Dose value or range with unit, denominator and administration basis.

Type: `Quantity`. Vocabulary: UCUM-compatible expression plus original dose string. Basis: `ucum`. Class: `searchable`. Check: `passage`.

Example value: 5 arbitrary units per culture, fictional

### `predictions[].intervention.regimen`

Frequency and administration schedule, without deriving it from a dose.

Type: `Text`. Vocabulary: Source wording. Basis: `ich`. Class: `searchable`. Check: `passage`.

Example value: single exposure

### `predictions[].intervention.duration`

Length of intervention, separate from observation horizon.

Type: `QuantityOrInterval`. Vocabulary: UCUM-compatible duration. Basis: `ucum`. Class: `searchable`. Check: `passage`.

Example value: 48 hours, fictional

### `predictions[].intervention.route`

Administration route when stated and applicable.

Type: `TextOrTerm`. Vocabulary: Source wording in value; in the added zone also a closed term (ohf:terms@1, route), required from OHF 1.1, with a note for other. Basis: `arrive`. Class: `searchable`. Check: `passage`.

Example value: in culture medium, fictional

### `predictions[].intervention.formulation`

Source-stated formulation and preparation, not inferred from the agent name.

Type: `Text`. Vocabulary: Free text; use a domain registry identifier where one exists. Basis: `arrive`. Class: `searchable`. Check: `passage`.

Example value: not stated

### `predictions[].intervention.nominal_concentration`

Nominal feed/medium concentration, with its own denominator and original unit.

Type: `Quantity`. Vocabulary: UCUM-compatible syntax plus biological basis. Basis: `ucum`. Class: `searchable`. Check: `passage`.

Example value: source dietary concentration, not delivered body dose

### `predictions[].intervention.measured_concentration`

Assayed concentration in the named preparation, with measurement context.

Type: `QuantityAndSource`. Vocabulary: Declared assay/context. Basis: `ohf`. Class: `searchable`. Check: `passage`.

Example value: not measured in supplied material

### `predictions[].intervention.intake`

Consumed quantity and timing when supplied, separate from concentration.

Type: `QuantityAndSource`. Vocabulary: Source intake basis. Basis: `ohf`. Class: `searchable`. Check: `passage`.

Example value: not stated

### `predictions[].intervention.systemic_exposure`

Measured or predicted systemic exposure, retaining specimen/time context.

Type: `QuantityAndSource`. Vocabulary: Source assay, with specimen and time. Basis: `ohf`. Class: `searchable`. Check: `passage`.

Example value: blood concentration, if supplied

### `predictions[].comparator`

Treatment/control condition defining the contrast.

Type: `TextOrRecord`. Vocabulary: ICH treatment conditions, PICO comparator. Basis: `ich`. Class: `searchable`. Check: `passage`.

Example value: vehicle-treated system Z

Example from fictional card fx_six at `/added/layers/predictions/0/comparator`:

```json
{
  "value": "The N-to-M link is cut while the external clock runs.",
  "src": "prediction"
}
```

### `predictions[].control_reference`

Reference control distribution, line or protocol used to assess control quality.

Type: `SourceBoundRecord`. Vocabulary: Source-bound record of the control. Basis: `ohf`. Class: `searchable`. Check: `passage`.

Example value: matched control protocol A

### `predictions[].control_quality`

Attributed assessment of control comparability against that reference.

Type: `Assessment`. Vocabulary: Declared criteria, not an imported p-value. Basis: `ohf`. Class: `searchable`. Check: `passage`.

Example value: not assessed

### `predictions[].control_type`

Kind of each control condition of the comparator, as closed terms. The value other needs a note that says what the control is.

Type: `Term[]`. Vocabulary: OHF terms vocabulary (ohf:terms@1, control_type): placebo | vehicle | untreated | wild_type | active_comparator | baseline | historical | none | not_stated | other. Basis: `ohf`. Class: `searchable`. Check: `passage`. Zones: `added`. Since: OHF 1.1.

Example value: vehicle, active_comparator

### `predictions[].endpoint`

Variable measured and its operational definition, not a summary statistic.

Type: `TextOrTerm`. Vocabulary: PATO/MP or reviewed phenotype mapping. Basis: `ich`. Class: `searchable`. Check: `passage`.

Example value: readout Y at 48 hours

Example from card muller-sheltering at `/added/layers/predictions/0/endpoint`:

```json
{
  "value": "rate of loss-of-function substitution in Y-linked genes",
  "src": "y_rates",
  "paraphrase": true,
  "basis_quote": "substitution rates of LOF alleles should remain the highest among Y-linked genes whose X-linked gametologs are under strong purifying selection in females"
}
```

### `predictions[].endpoint_orientation`

Meaning of increasing or decreasing this endpoint, without assuming benefit.

Type: `Text`. Vocabulary: Source-defined endpoint semantics. Basis: `ohf`. Class: `searchable`. Check: `passage`.

Example value: higher deterioration differs from higher function

### `predictions[].relational_prediction`

Declared multi-arm ordering or interaction contrast, not invented independent binary effects.

Type: `RelationRecord`. Vocabulary: Author-stated ordering and conditions. Basis: `ohf`. Class: `searchable`. Check: `passage`.

Example value: A exceeds B exceeds C, fictional

### `predictions[].endpoint_kind`

Kind of endpoint: what is measured, such as lifespan, function or a biomarker. The level of the system, such as in vitro, is evidence.lines[].human_proximity.

Type: `Term`. Vocabulary: Source wording in value; in the added zone also a closed term (ohf:terms@1, endpoint_kind), required from OHF 1.1, with a note for other. Basis: `ohf`. Class: `searchable`. Check: `passage`.

Example value: biomarker

### `predictions[].summary_measure`

Population-level summary and contrast, including scale and statistic identity.

Type: `SummaryMeasure`. Vocabulary: ICH estimand, STATO where verified. Basis: `ich`. Class: `searchable`. Check: `passage`.

Example value: difference in mean readout Y

### `predictions[].summary_measure.contrast`

Exact difference, ratio or other contrast and reference direction.

Type: `TextOrTerm`. Vocabulary: Author-defined contrast. Basis: `ich`. Class: `searchable`. Check: `passage`.

Example value: difference versus vehicle

### `predictions[].summary_measure.scale`

Scale of the target summary, not the inferential test used.

Type: `TextOrTerm`. Vocabulary: Source definition and verified STATO mapping when available. Basis: `ich`. Class: `searchable`. Check: `passage`.

Example value: original readout units

### `predictions[].intercurrent_events[].event`

Event affecting interpretation of the stated endpoint.

Type: `TextOrTerm`. Vocabulary: Source event definition. Basis: `ich`. Class: `searchable`. Check: `passage`.

Example value: treatment discontinuation, when relevant

### `predictions[].intercurrent_events[].strategy`

Declared strategy for this particular event.

Type: `Term`. Vocabulary: ICH strategy family only when source-stated. Basis: `ich`. Class: `author_only`. Check: `passage`.

Example value: hypothetical, if explicitly declared

### `predictions[].intercurrent_events[].justification`

Source rationale for the event strategy and target scientific question.

Type: `TextAndSource`. Vocabulary: ICH-informed OHF adaptation. Basis: `ich`. Class: `author_only`. Check: `passage`.

Example value: not stated

### `predictions[].intercurrent_events[]`

Each event affecting interpretation and its declared estimand strategy.

Type: `EventStrategy[]`. Vocabulary: ICH five strategy families. Basis: `ich`. Class: `searchable`. Check: `passage`.

Example value: event E handled by a hypothetical strategy, if stated

### `predictions[].missing_data_plan`

Missing observations and administrative censoring, separate from intercurrent events.

Type: `Text`. Vocabulary: Study/analysis plan. Basis: `ich`. Class: `author_only`. Check: `passage`.

Example value: not stated

### `predictions[].direction`

Source-stated increase, decrease, qualitative no-change, exact-null or bounded equivalence, retaining modality and reference direction. Missing equivalence margins remain an operationalization gap; a non-significant result establishes none of these claims.

Type: `Term`. Vocabulary: Term for one of the directions in the definition; bounded equivalence requires explicit margins, scale and decision rule. Basis: `ohf`. Class: `searchable`. Check: `passage`.

Example value: decrease

Example from card muller-sheltering at `/added/layers/predictions/0/direction`:

```json
{
  "value": "higher in genes whose X-linked copies are under strong purifying selection in females, at a given male fitness cost",
  "src": "y_rates"
}
```

### `predictions[].threshold`

Author-stated decision/effect threshold, its units and strictness.

Type: `QuantityOrRule`. Vocabulary: Source wording. Basis: `ohf`. Class: `author_only`. Check: `passage`.

Example value: qualitatively lower, no numeric threshold supplied

### `predictions[].equivalence_bounds`

Prespecified equivalence margins and scale; absence of significance is not equivalence.

Type: `IntervalAndRule`. Vocabulary: Declared SESOI/TOST-style design, not inferred. Basis: `ohf`. Class: `author_only`. Check: `passage`.

Example value: lower/upper margins not stated

### `predictions[].horizon`

Time from an explicitly stated origin to the predicted endpoint.

Type: `QuantityOrInterval`. Vocabulary: UCUM-compatible duration. Basis: `ich`. Class: `searchable`. Check: `passage`.

Example value: 48 hours after exposure

### `predictions[].age_window`

Age range in which the effect is asserted, separate from study start age.

Type: `Interval`. Vocabulary: Source wording, with the age unit the source states. Basis: `ohf`. Class: `searchable`. Check: `passage`.

Example value: not stated

### `predictions[].effect_modifiers[]`

Prespecified factors modifying the predicted effect and their stated directions.

Type: `Qualifier[]`. Vocabulary: Typed qualifiers declared by the author. Basis: `biolink`. Class: `author_only`. Check: `passage`.

Example value: sex-specific effect, if stated

### `predictions[].predictive_uncertainty`

Author-stated predictive interval or event probability with target and scale.

Type: `DistributionOrAssessment`. Vocabulary: Explicit method/coverage or elicitation. Basis: `ohf`. Class: `author_only`. Check: `passage`.

Example value: interval and coverage not stated

### `predictions[].intermediate_tests[].observable`

Intermediate observable and null/alternative hypotheses. This path is the sourced observable component; H0, H1, procedure and phase are its TestRecord siblings.

Type: `Text`. Vocabulary: Source text of the observable. Basis: `popper`. Class: `searchable`. Check: `passage`.

Example value: test h0 versus h1 for observable Y

Example from fictional card fx_two at `/author/layers/predictions/0/intermediate_tests/0/observable`:

```json
{
  "value": "The fictional counter Y.",
  "locator": "JSON:/observable"
}
```

### `predictions[].intermediate_tests[].validity_justification`

Separate justification for the required main-null implies subtest-null relation.

Type: `TextAndSource`. Vocabulary: A declared proof/argument, never inferred from the prompt. Basis: `popper`. Class: `searchable`. Check: `passage`.

Example value: not established

### `predictions[].test_plan_ref`

Source-bound experimental plan, kept separate from actual results.

Type: `Reference`. Vocabulary: Reference to appendix.experiment_plan or to a preregistration. Basis: `osf`. Class: `searchable`. Check: `card`.

Example value: experiment-plan-a

### `predictions[].test_cost`

Source-grounded basis and confidence for estimated test resources, duration and monetary cost; unavailable components remain gaps.

Type: `TestCost`. Vocabulary: OHF record. Basis: `ohf`. Class: `searchable`. Check: `passage`.

Example value: about two weeks on one bench, 1000 to 1500 EUR in 2026

Example from fictional card fx_four at `/added/layers/predictions/0/test_cost`:

```json
{
  "value": {
    "money_range": {
      "low": 1000,
      "high": 1500,
      "currency": "EUR",
      "year": 2026
    },
    "duration": {
      "value": 2,
      "unit": "weeks"
    },
    "resources": [
      "One fictional bench"
    ],
    "basis": "Cost stated in the fictional source.",
    "confidence": "medium"
  },
  "src": "cost"
}
```

### `predictions[].role`

Source-grounded primary or secondary role of the prediction.

Type: `primary|secondary`. Vocabulary: OHF record. Basis: `ohf`. Class: `searchable`. Check: `passage`.

Example value: primary

Example from fictional card fx_four at `/added/layers/predictions/0/role`:

```json
{
  "value": "primary",
  "src": "statement"
}
```

### `predictions[].resolution`

Source-supported resolution criterion, event or check location, official outcome and separately attributed candidate observations; unavailable components remain gaps.

Type: `Resolution`. Vocabulary: OHF record. Basis: `ohf`. Class: `searchable`. Check: `passage`.

Example value: holds if counter Y is at least 10 percent higher with agent Q after 20 cycles

Example from fictional card fx_four at `/added/layers/predictions/0/resolution`:

```json
{
  "value": {
    "criterion": "The prediction holds if counter Y is at least 10 percent higher with agent Q after 20 cycles.",
    "outcome": {
      "status": "pending"
    }
  },
  "src": "resolution"
}
```

### `predictions[].existing_data_tests[]`

Identified existing datasets and what each could test, with source-supported access and partial duration or cost estimates. Retaining a reference or access record does not imply possession of the dataset.

Type: `ExistingDataTest[]`. Vocabulary: OHF record. Basis: `ohf`. Class: `searchable`. Check: `passage`.

Example value: dataset D4: counter Y for 200 runs with and without agent Q

Example from fictional card fx_four at `/added/layers/predictions/0/existing_data_tests`:

```json
{
  "value": [
    {
      "dataset": {
        "name": "Fictional dataset D4",
        "ref": {
          "kind": "artifact",
          "sha256": "sha256:82d82118fca7a79c3837cafa3d89f14cc612ae24e3023e975b45d829dcf9f53d",
          "json_pointer": "/dataset"
        }
      },
      "access": "open",
      "what_it_can_show": "Counter Y with and without agent Q in system four."
    }
  ],
  "src": "dataset"
}
```

### `predictions[].epistemic_status`

Whether the prediction was stated before its result was known (novel), derived for a result already known (retrodicted), or adjusted to fit a known result (accommodated).

Type: `Term`. Vocabulary: OHF vocabulary: novel | retrodicted | accommodated. Basis: `ohf`. Class: `searchable`. Check: `passage`.

Example value: retrodicted

Example from card muller-sheltering at `/added/layers/predictions/1/epistemic_status`:

```json
{
  "value": "retrodicted",
  "src": "x_losses"
}
```

### `predictions[].known_result_ref`

The known result that a retrodicted or accommodated prediction was derived for or fitted to: an evidence line of this card or an external record. Required for those two statuses.

Type: `Reference`. Vocabulary: Card pointer or external reference. Basis: `ohf`. Class: `searchable`. Check: `card`.

Example value: a pointer to an evidence line

Example from card muller-sheltering at `/added/layers/predictions/1/known_result_ref`:

```json
{
  "value": {
    "kind": "card",
    "pointer": "/added/layers/evidence/lines/1"
  },
  "src": "x_losses"
}
```

### `predictions[].form`

Logical form of the prediction, which says what kind of observation tests it. A direction is needed only for a directional contrast.

Type: `Term`. Vocabulary: OHF vocabulary: directional_contrast | presence_absence | parameter_value | functional_form | pattern | distribution | phylogenetic_comparative | historical_counterfactual. Basis: `ohf`. Class: `searchable`. Check: `passage`.

Example value: phylogenetic_comparative

Example from card muller-sheltering at `/added/layers/predictions/1/form`:

```json
{
  "value": "phylogenetic_comparative",
  "src": "x_losses"
}
```

### `predictions[].derives_from_atom_refs[]`

Identifiers of the claim atoms from which the prediction follows.

Type: `Identifier[]`. Vocabulary: Identifiers of core.atoms[] in this card. Basis: `ohf`. Class: `searchable`. Check: `card`.

Example value: a_bactericide_first

Example from card muller-sheltering at `/added/layers/predictions/0/derives_from_atom_refs/value/0`:

```json
"a_y_decay"
```

### `predictions[].also_expected_under[]`

Alternatives under which the same outcome is also expected: a reference to an item of core.alternative_explanations[], or the vocabulary value unspecified_other_mechanism. Free text is not allowed.

Type: `AlternativeReference[]`. Vocabulary: OHF vocabulary: card pointer or unspecified_other_mechanism. Basis: `ohf`. Class: `searchable`. Check: `card`.

Example value: a pointer to an item of core.alternative_explanations

Example gap from card muller-sheltering: `predictions[2].also_expected_under[]` is a `not_supplied` gap. The article names no other process that would also expect this rate of loss.

### `predictions[].discrimination`

How well the outcome separates the hypothesis from the alternatives that also expect it: none, weak or strong. It is the assessment of whoever recorded it, held in the added zone with its assessor, not a statement of the hypothesis author.

Type: `Assessment`. Vocabulary: OHF vocabulary: none | weak | strong. Basis: `ohf`. Class: `author_only`. Check: `passage`. Zones: `added`.

Example value: weak

Example from fictional card fx_eight at `/added/layers/predictions/0/discrimination`:

```json
{
  "value": "strong",
  "src": "prediction",
  "assessment": {
    "assessor": "fixture-builder",
    "assessed_at": "2026-01-01T00:00:00Z",
    "evidence_ref": {
      "kind": "artifact",
      "sha256": "sha256:fb8912e787413a98b8d40c77dcf57f3f367db4e79c64b8acb679603c059a263e"
    }
  }
}
```

## 4 Evidence

### `evidence.lines[].id`

Identity of one evidence assessment about an exact claim, step or prediction.

Type: `Identifier`. Vocabulary: Card-local identifier. Basis: `sepio`. Class: `system`. Check: `card`.

Example value: evidence-line-a

Example from card muller-sheltering at `/added/layers/evidence/lines/0/id`:

```json
"e_early_models"
```

### `evidence.lines[].target_ref`

Versioned proposition, atom, mechanism step or prediction being assessed.

Type: `Reference`. Vocabulary: OHF scoped references. Basis: `sepio`. Class: `searchable`. Check: `card`.

Example value: prediction-a of proposition-a@1

Example from card muller-sheltering at `/added/layers/evidence/lines/0/target_ref`:

```json
"a_y_decay"
```

### `evidence.lines[].direction`

Whether the assessed evidence supports, disputes or is neutral toward the target.

Type: `Term`. Vocabulary: SEPIO direction with original source stance retained. Basis: `sepio`. Class: `searchable`. Check: `passage`.

Example value: neutral, not a missing-evidence marker

Example from card muller-sheltering at `/added/layers/evidence/lines/0/direction`:

```json
"neutral"
```

### `evidence.lines[].items[]`

Data, study or passage items supporting the assessment, with versions and locators.

Type: `SourceBoundRecord[]`. Vocabulary: SEPIO evidence items. Basis: `sepio`. Class: `searchable`. Check: `passage`.

Example value: source A, passage locator B

Example from card muller-sheltering at `/added/layers/evidence/lines/0/items/0`:

```json
{
  "value": {
    "artifact": "PMC12342767.xml",
    "sha256": "sha256:aec24a2447826a7ba21328f44dd243644e621fc0eb07894800e2bf124eadf09e",
    "locator": "XML .//p[7] (1-based document order)"
  },
  "src": "rejection"
}
```

### `evidence.lines[].quote`

Exact quoted text with byte/text locator, verification state and reuse basis.

Type: `VerifiedQuotation`. Vocabulary: OHF quotation contract. Basis: `ohf`. Class: `searchable`. Check: `passage`.

Example value: short source passage or not supplied

Example from card muller-sheltering at `/added/layers/evidence/lines/0/quote`:

```json
"Using a deterministic model, Fisher (1935) showed that recessive lethal mutations cannot reach high frequencies on the Y chromosome because similar mutations also arise on the X and render Y-linked sheltering effects incomplete"
```

### `evidence.lines[].quote_withheld`

The quote of the line is not reproduced because the text may not be quoted: its licence is unknown, it forbids derivatives (NC-ND), or no open text exists. The line keeps the locator and the record of the source, a paraphrase in the added zone, and the sentence of the abstract that entails the paraphrase. Such a line counts in the card and is shown to judges, but it does not make the disputing side for completeness full.

Type: `WithheldQuotation`. Vocabulary: reason licence_unknown | nc_nd | no_open_text; record_ref scheme doi | pmid. Basis: `ohf`. Class: `searchable`. Check by member: `reason` resolution, `record_ref` resolution, `locator` card, `paraphrase` passage, `abstract_quote` passage. Zones: `added`. Since: OHF 1.1.

Example value: nc_nd, Table 2, doi 10.1000/fictional, paraphrase and abstract sentence

### `evidence.lines[].evidence_type`

Evidence category, not a quality score.

Type: `Term`. Vocabulary: ECO with pinned term/version. Basis: `eco`. Class: `searchable`. Check: `passage`.

Example value: source-stated assay evidence

### `evidence.lines[].knowledge_level`

Knowledge-level qualifier for the particular association/assertion.

Type: `Term`. Vocabulary: Pinned Biolink enum. Basis: `biolink`. Class: `searchable`. Check: `passage`.

Example value: prediction, only after an explicit reviewed source mapping

### `evidence.lines[].agent_type`

How the evidence assertion was produced, attached to the specific association.

Type: `Term`. Vocabulary: Pinned Biolink enum. Basis: `biolink`. Class: `searchable`. Check: `passage`.

Example value: automated_agent, only if explicitly supported

### `evidence.lines[].hypothesis_flag`

Explicit source epistemic hypothesis flag; absence is not false.

Type: `Boolean`. Vocabulary: INDRA optional epistemics. Basis: `indra`. Class: `searchable`. Check: `passage`.

Example value: not stated

### `evidence.lines[].negated_flag`

Explicit source negation flag; distinguish negating a relation from negative evidence.

Type: `Boolean`. Vocabulary: INDRA optional epistemics. Basis: `indra`. Class: `searchable`. Check: `passage`.

Example value: true only when stated

### `evidence.lines[].study_system`

System, population and context of the evidence, not automatically that of the claim.

Type: `TextOrRecord`. Vocabulary: Source wording of the study system. Basis: `arrive`. Class: `searchable`. Check: `passage`.

Example value: cell system Q, distinct from Z

Example from card muller-sheltering at `/added/layers/evidence/lines/0/study_system`:

```json
"theoretical X and Y chromosomes"
```

### `evidence.lines[].system.taxon`

Source-stated organism, with a verified taxonomy mapping when available. Here: of the study the evidence line reports, not of the claim.

Type: `Term`. Vocabulary: NCBI Taxonomy, otherwise explicit missingness. Basis: `arrive`. Class: `searchable`. Check: `passage`. Since: OHF 1.1.

Example value: NCBITaxon:10090 as a vocabulary example only

### `evidence.lines[].system.taxon_id`

NCBI Taxonomy identifier of the taxon named in taxon.

Type: `Identifier`. Vocabulary: NCBI Taxonomy, as NCBITaxon:<number>. Basis: `ohf`. Class: `searchable`. Check: `resolution`. Zones: `added`. Since: OHF 1.1.

Example value: NCBITaxon:10090

### `evidence.lines[].system.strain_or_line`

Strain, genotype or cell-line identity, keeping supplied identifiers. Here: of the study the evidence line reports, not of the claim.

Type: `TextOrTerm`. Vocabulary: Free text; use a strain or cell-line registry identifier where one exists. Basis: `arrive`. Class: `searchable`. Check: `passage`. Since: OHF 1.1.

Example value: cell line Z

### `evidence.lines[].system.sex`

Source-stated sex or applicable population description. Here: of the study the evidence line reports, not of the claim.

Type: `TextOrTerm`. Vocabulary: Source wording, without defaulting to both sexes. Basis: `arrive`. Class: `searchable`. Check: `passage`. Since: OHF 1.1.

Example value: not stated

### `evidence.lines[].system.age_at_start`

Age when treatment or observation starts, with units and origin. Here: of the study the evidence line reports, not of the claim.

Type: `QuantityOrInterval`. Vocabulary: UCUM-compatible units and explicit time origin. Basis: `arrive`. Class: `searchable`. Check: `passage`. Since: OHF 1.1.

Example value: 10 weeks, fictional example

### `evidence.lines[].system.assessment_age`

Age at endpoint assessment, distinguished from treatment-start age and follow-up. Here: of the study the evidence line reports, not of the claim.

Type: `QuantityOrInterval`. Vocabulary: Source-defined time origin. Basis: `arrive`. Class: `searchable`. Check: `passage`. Since: OHF 1.1.

Example value: not stated

### `evidence.lines[].system.site`

Experimental site, laboratory or cohort context when relevant. Here: of the study the evidence line reports, not of the claim.

Type: `TextOrReference`. Vocabulary: Source identifiers. Basis: `arrive`. Class: `searchable`. Check: `passage`. Since: OHF 1.1.

Example value: site A

### `evidence.lines[].system.kind`

Level of organization of the test system. Here: of the study the evidence line reports, not of the claim.

Type: `Term`. Vocabulary: OHF vocabulary: cell | tissue | organism | population | community | ecosystem | clade | in_silico | other. Basis: `ohf`. Class: `searchable`. Check: `passage`. Since: OHF 1.1.

Example value: community

### `evidence.lines[].system.environment`

Conditions in which the system is studied, such as laboratory culture, a field site or a simulation. Here: of the study the evidence line reports, not of the claim.

Type: `Text`. Vocabulary: Source text. Basis: `ohf`. Class: `searchable`. Check: `passage`. Since: OHF 1.1.

Example value: laboratory colonies

### `evidence.lines[].system.spatial_scale`

Spatial extent of the system or of the observation, such as a culture well, a lake or a continent. Here: of the study the evidence line reports, not of the claim.

Type: `Text`. Vocabulary: Source text. Basis: `ohf`. Class: `searchable`. Check: `passage`. Since: OHF 1.1.

Example value: whole lakes

### `evidence.lines[].system.temporal_scale`

Time span of the study the evidence line reports, such as hours, a growing season or evolutionary time.

Type: `Text`. Vocabulary: Source text. Basis: `ohf`. Class: `searchable`. Check: `passage`. Since: OHF 1.1.

Example value: about 350,000 generations

### `evidence.lines[].intervention.agent`

Intervention identity, preserving mixtures and unresolved names. Here: of the study the evidence line reports, not of the claim.

Type: `TextOrTerm`. Vocabulary: ChEBI or another named registry, otherwise the source name. Basis: `ich`. Class: `searchable`. Check: `passage`. Since: OHF 1.1.

Example value: compound X

### `evidence.lines[].intervention.dose`

Dose value or range with unit, denominator and administration basis. Here: of the study the evidence line reports, not of the claim.

Type: `Quantity`. Vocabulary: UCUM-compatible expression plus original dose string. Basis: `ucum`. Class: `searchable`. Check: `passage`. Since: OHF 1.1.

Example value: 5 arbitrary units per culture, fictional

### `evidence.lines[].intervention.regimen`

Frequency and administration schedule, without deriving it from a dose. Here: of the study the evidence line reports, not of the claim.

Type: `Text`. Vocabulary: Source wording. Basis: `ich`. Class: `searchable`. Check: `passage`. Since: OHF 1.1.

Example value: single exposure

### `evidence.lines[].intervention.duration`

Length of intervention, separate from observation horizon. Here: of the study the evidence line reports, not of the claim.

Type: `QuantityOrInterval`. Vocabulary: UCUM-compatible duration. Basis: `ucum`. Class: `searchable`. Check: `passage`. Since: OHF 1.1.

Example value: 48 hours, fictional

### `evidence.lines[].intervention.route`

Administration route when stated and applicable. Here: of the study the evidence line reports, not of the claim.

Type: `TextOrTerm`. Vocabulary: Source wording in value; in the added zone also a closed term (ohf:terms@1, route), required from OHF 1.1, with a note for other. Basis: `arrive`. Class: `searchable`. Check: `passage`. Since: OHF 1.1.

Example value: in culture medium, fictional

### `evidence.lines[].intervention.formulation`

Source-stated formulation and preparation, not inferred from the agent name. Here: of the study the evidence line reports, not of the claim.

Type: `Text`. Vocabulary: Free text; use a domain registry identifier where one exists. Basis: `arrive`. Class: `searchable`. Check: `passage`. Since: OHF 1.1.

Example value: not stated

### `evidence.lines[].intervention.nominal_concentration`

Nominal feed/medium concentration, with its own denominator and original unit. Here: of the study the evidence line reports, not of the claim.

Type: `Quantity`. Vocabulary: UCUM-compatible syntax plus biological basis. Basis: `ucum`. Class: `searchable`. Check: `passage`. Since: OHF 1.1.

Example value: source dietary concentration, not delivered body dose

### `evidence.lines[].intervention.measured_concentration`

Assayed concentration in the named preparation, with measurement context. Here: of the study the evidence line reports, not of the claim.

Type: `QuantityAndSource`. Vocabulary: Declared assay/context. Basis: `ohf`. Class: `searchable`. Check: `passage`. Since: OHF 1.1.

Example value: not measured in supplied material

### `evidence.lines[].intervention.intake`

Consumed quantity and timing when supplied, separate from concentration. Here: of the study the evidence line reports, not of the claim.

Type: `QuantityAndSource`. Vocabulary: Source intake basis. Basis: `ohf`. Class: `searchable`. Check: `passage`. Since: OHF 1.1.

Example value: not stated

### `evidence.lines[].intervention.systemic_exposure`

Measured or predicted systemic exposure, retaining specimen/time context. Here: of the study the evidence line reports, not of the claim.

Type: `QuantityAndSource`. Vocabulary: Source assay, with specimen and time. Basis: `ohf`. Class: `searchable`. Check: `passage`. Since: OHF 1.1.

Example value: blood concentration, if supplied

### `evidence.lines[].multi_site_program`

The result comes from a programme that runs the same protocol at several sites, and how many.

Type: `Record`. Vocabulary: Programme name and number of sites, at least 2. Basis: `ohf`. Class: `searchable`. Check: `passage`. Zones: `added`. Since: OHF 1.1.

Example value: ITP, 3 sites

### `evidence.lines[].sample`

Which part of the study the result comes from: the whole sample or a named subgroup; a primary or secondary outcome; a pre-specified or post hoc analysis.

Type: `Record`. Vocabulary: population: whole_sample | subgroup (with the subgroup named); outcome: primary | secondary | not_stated; analysis: pre_specified | post_hoc | not_stated. Basis: `ohf`. Class: `searchable`. Check: `passage`. Zones: `added`. Since: OHF 1.1.

Example value: subgroup: males on the lower dose; secondary outcome; analysis not stated

### `evidence.lines[].endpoint_kind`

Kind of endpoint the evidence line measures, as for predictions[].endpoint_kind.

Type: `Term`. Vocabulary: Source wording in value and a closed term (ohf:terms@1, endpoint_kind), with a note for other. Basis: `ohf`. Class: `searchable`. Check: `passage`. Zones: `added`. Since: OHF 1.1.

Example value: biomarker

### `evidence.lines[].human_proximity`

How close the system of the evidence is to humans. Derived where it can be: from the taxon (ohf:terms@1, taxa) and the endpoint kind, by the rule in spec/README.md; in vitro and ex vivo are stated, not derived.

Type: `Term`. Vocabulary: ohf:terms@1, human_proximity: in_vitro | ex_vivo | invertebrate | non_mammal_vertebrate | mammal | human_marker | human_clinical. Basis: `ohf`. Class: `searchable`. Check: `resolution`. Zones: `added`. Since: OHF 1.1.

Example value: human_marker

### `evidence.lines[].sample_size`

Number of experimental units the result rests on, as the source states it.

Type: `Quantity`. Vocabulary: Positive integer. Basis: `ohf`. Class: `searchable`. Check: `passage`. Zones: `added`. Since: OHF 1.1.

Example value: 48

### `evidence.lines[].study_type`

Study design and status, including whether proposed or executed.

Type: `Term`. Vocabulary: Source design vocabulary with reviewed mapping. Basis: `arrive`. Class: `searchable`. Check: `passage`.

Example value: in vitro experiment

Example from card muller-sheltering at `/added/layers/evidence/lines/0/study_type`:

```json
"earlier population-genetic models, as summarized by the article"
```

### `evidence.lines[].result_estimate`

Observed estimate with units, contrast, sample/context and source, separate from its target quantity.

Type: `QuantityAndSource`. Vocabulary: Source analysis output. In the added zone of a 1.1 card a record: reported, the words of the quote that give the result; measure, contrast and scale, each as the source states it or not_stated. Basis: `ohf`. Class: `searchable`. Check: `passage`.

Example value: estimate not supplied

### `evidence.lines[].confidence_interval`

Interval for an estimate with confidence level/method, not a predictive interval or author belief.

Type: `IntervalAndSource`. Vocabulary: Source statistical report. Basis: `ohf`. Class: `searchable`. Check: `passage`.

Example value: not supplied

### `evidence.lines[].statistical_procedure`

Analysis/test actually proposed or performed, with status and assumptions.

Type: `TextAndSource`. Vocabulary: Study analysis report. Basis: `arrive`. Class: `searchable`. Check: `passage`.

Example value: test name only when stated

### `evidence.lines[].strength`

Attributed strength/score with scale, assessor and interpretation retained. It is the assessment of whoever recorded it, with that assessor and a justification, not necessarily the hypothesis author.

Type: `Assessment`. Vocabulary: SEPIO strength/score, no automatic OHF scale. Basis: `sepio`. Class: `author_only`. Check: `passage`.

Example value: author qualitative assessment

### `evidence.lines[].retraction_status`

Source notices, corrections and retractions with verification date and locator.

Type: `SourceBoundRecord`. Vocabulary: Publisher or registry notices, with the date of the check. Basis: `ohf`. Class: `searchable`. Check: `passage`.

Example value: not checked

### `evidence.references[].identifier`

Persistent source identifier or unresolved source reference without fabrication.

Type: `IdentifierOrLocator`. Vocabulary: DOI/PMID/accession when supplied. Basis: `ohf`. Class: `searchable`. Check: `passage`.

Example value: urn:example:source-a (reserved illustrative identifier)

### `evidence.references[].citation_relation`

Typed relation of this citation to the current assertion, distinct from biological causation.

Type: `Term`. Vocabulary: CiTO when explicitly reviewed. Basis: `cito`. Class: `searchable`. Check: `passage`.

Example value: source cited as context

### `evidence.references[].access_context`

Retained retrieval and inspection context distinguishing available material from material actually inspected.

Type: `AccessContext`. Vocabulary: OHF record. Basis: `ohf`. Class: `system`. Check: `passage`.

Example value: full text retrieved and inspected on 2026-01-01

Example from fictional card fx_four at `/added/layers/evidence/references/0/access_context`:

```json
{
  "value": {
    "source_ref": {
      "kind": "artifact",
      "sha256": "sha256:82d82118fca7a79c3837cafa3d89f14cc612ae24e3023e975b45d829dcf9f53d",
      "json_pointer": ""
    },
    "text_scope": "full_text",
    "truncated": false,
    "inspected_locator_range": null,
    "retrieval_status": "retrieved",
    "retrieval_record_ref": {
      "kind": "artifact",
      "sha256": "sha256:82d82118fca7a79c3837cafa3d89f14cc612ae24e3023e975b45d829dcf9f53d",
      "json_pointer": ""
    }
  },
  "src": "prior_work"
}
```

### `evidence.lines[].replication`

Source-supported independent and failed replication evidence with an explicit assessment status.

Type: `Replication`. Vocabulary: OHF record. Basis: `ohf`. Class: `searchable`. Check: `passage`.

Example value: repeated once by an independent group with the same result

Example from fictional card fx_four at `/added/layers/evidence/lines/0/replication`:

```json
{
  "value": {
    "status": "replicated",
    "independent": [
      {
        "kind": "artifact",
        "sha256": "sha256:82d82118fca7a79c3837cafa3d89f14cc612ae24e3023e975b45d829dcf9f53d",
        "json_pointer": "/replication"
      }
    ]
  },
  "src": "replication"
}
```

### `evidence.lines[].indirectness`

How far the evidence is from the claim it is attached to, judged separately for the test system, the endpoint, the intervention and the comparison: none, some, serious or not applicable. It is the assessment of whoever recorded it.

Type: `Assessment`. Vocabulary: OHF vocabulary, not GRADE or RoB 2: a mapping to external schemes follows only after a check against their primary sources; none | some | serious | not_applicable. Basis: `ohf`. Class: `author_only`. Check: `passage`. Zones: `added`.

Example value: system serious (mouse for human), endpoint none

Example from card muller-sheltering at `/added/layers/evidence/lines/0/indirectness`:

```json
{
  "value": {
    "system": "none",
    "endpoint": "some",
    "intervention": "not_applicable",
    "comparison": "not_applicable"
  },
  "src": "rejection",
  "assessment": {
    "assessor": "ohf-example-conversion 1.0.0",
    "assessed_at": "2026-10-20T17:04:22Z",
    "evidence_ref": {
      "kind": "artifact",
      "sha256": "sha256:aec24a2447826a7ba21328f44dd243644e621fc0eb07894800e2bf124eadf09e"
    }
  }
}
```

### `evidence.lines[].risk_of_bias`

Risk that the study behind the line is biased: low, some, high or not assessed, with an optional tool reference and note. It is the assessment of whoever recorded it.

Type: `Assessment`. Vocabulary: OHF vocabulary, not GRADE or RoB 2: a mapping to external schemes follows only after a check against their primary sources; low | some | high | not_assessed. Basis: `ohf`. Class: `author_only`. Check: `passage`. Zones: `added`.

Example value: not_assessed

Example from fictional card fx_eight at `/added/layers/evidence/lines/0/risk_of_bias`:

```json
{
  "value": {
    "level": "not_assessed",
    "note": "A fictional fixture."
  },
  "src": "run_a",
  "assessment": {
    "assessor": "fixture-builder",
    "assessed_at": "2026-01-01T00:00:00Z",
    "evidence_ref": {
      "kind": "artifact",
      "sha256": "sha256:fb8912e787413a98b8d40c77dcf57f3f367db4e79c64b8acb679603c059a263e"
    }
  }
}
```

### `evidence.lines[].independence_group`

Lines with the same group label rest on the same data, study or laboratory and are not independent of each other.

Type: `Identifier`. Vocabulary: Card-local label. Basis: `ohf`. Class: `author_only`. Check: `card`. Zones: `added`.

Example value: g_head_extracts

Example from fictional card fx_eight at `/added/layers/evidence/lines/1/independence_group`:

```json
{
  "value": "g_run_a_log",
  "src": "run_b"
}
```

### `evidence.lines[].independence_group.key`

Where the data of the group first appeared: the article, registry record or accession. Lines of two cards with the same key rest on the same data, whatever their labels.

Type: `Identifier`. Vocabulary: scheme doi | pmid | pmcid | registry | accession, and its identifier. Basis: `ohf`. Class: `searchable`. Check: `resolution`. Zones: `added`. Since: OHF 1.1.

Example value: registry NCT04488601

### `evidence.lines[].argument_kind`

Whether the line rests on observation or experiment (empirical), on a simulation, or on a mathematical derivation or proof.

Type: `Term`. Vocabulary: OHF vocabulary: empirical | simulation | derivation. Basis: `ohf`. Class: `author_only`. Check: `passage`. Zones: `added`.

Example value: derivation

Example from card muller-sheltering at `/added/layers/evidence/lines/0/argument_kind`:

```json
{
  "value": "derivation",
  "src": "rejection"
}
```

### `evidence.selection_record`

How the evidence lines were selected: the queries run and the number of records identified, screened and included, with the reasons and counts for exclusions.

Type: `SelectionRecord`. Vocabulary: OHF vocabulary: counts, not a PRISMA flow diagram. Basis: `ohf`. Class: `system`. Check: `passage`. Zones: `added`.

Example value: 3 queries, 40 identified, 12 screened, 4 included

Example from fictional card fx_eight at `/added/layers/evidence/selection_record`:

```json
{
  "value": {
    "query_ids": [
      "q_runs"
    ],
    "identified": 3,
    "screened": 3,
    "included": 2,
    "excluded": [
      {
        "reason": "log file unreadable",
        "count": 1
      }
    ]
  },
  "src": "run_b"
}
```

### `evidence.excluded[]`

A record that was found for a target and not used as an evidence line, with the type of the mismatch, its quotation and where it stands; the counts stay in selection_record.

Type: `Record`. Vocabulary: reason from ohf:terms@1, exclusion_reason: species_mismatch | direction_mismatch | endpoint_mismatch | type_mismatch | inherited_mismatch | other (with a note). Basis: `ohf`. Class: `searchable`. Check: `passage`. Zones: `added`. Since: OHF 1.1.

Example value: inherited_mismatch: a mouse finding against a claim about humans

### `evidence.references[].funding_coi`

Source-reported funding and conflict-of-interest declarations, distinguishing explicit absence from unreported information.

Type: `FundingCOI`. Vocabulary: OHF record. Basis: `ohf`. Class: `searchable`. Check: `passage`.

Example value: funded by fund G; authors declare no competing interests

Example from fictional card fx_four at `/added/layers/evidence/references/0/funding_coi`:

```json
{
  "value": {
    "funders": [
      "Fictional fund G"
    ],
    "coi_declared": {
      "kind": "none_declared"
    }
  },
  "src": "funding"
}
```

## 5 Provenance

### `provenance.claim_author`

Author of the scientific content, separate from whoever entered the record and from any translator.

Type: `AgentReference`. Vocabulary: Declared person/organization/AI identity. Basis: `sepio`. Class: `searchable`. Check: `passage`.

Example value: author-a

Example from card muller-sheltering at `/added/layers/provenance/claim_author`:

```json
{
  "value": "Andrea Mrnjavac, Beatriz Vicoso, Tim Connallon",
  "src": "meta"
}
```

### `provenance.author_type`

Declared author/agent kind without inferring legal identity.

Type: `Term`. Vocabulary: OHF agent vocabulary, with source declaration. Basis: `ohf`. Class: `searchable`. Check: `passage`.

Example value: human

Example from card muller-sheltering at `/added/layers/provenance/author_type`:

```json
{
  "value": "human",
  "src": "meta"
}
```

### `provenance.model`

Actual declared model and version used for generation or extraction, with attestation basis.

Type: `SourceBoundRecord`. Vocabulary: Provider report or explicitly client-declared identity. Basis: `ohf`. Class: `searchable`. Check: `passage`.

Example value: model declaration not supplied

### `provenance.origin_method`

How this claim arose, distinct from who authored it.

Type: `Term`. Vocabulary: OHF: de_novo, refine, merge, import, published_restatement. Basis: `hep`. Class: `searchable`. Check: `passage`.

Example value: published_restatement

Example from card muller-sheltering at `/added/layers/provenance/origin_method`:

```json
{
  "value": "published_restatement",
  "src": "meta"
}
```

### `provenance.generation_heuristic`

Author-declared method such as anomaly, analogy or screening.

Type: `TextOrTerm`. Vocabulary: Method declared by the author, not inferred from writing style. Basis: `ohf`. Class: `author_only`. Check: `passage`.

Example value: analogy, if stated

### `provenance.parent_refs[]`

Actual refinement/merge parents with versioned lineage and transformation scope.

Type: `VersionReference[]`. Vocabulary: HEP generation lineage. Basis: `hep`. Class: `system`. Check: `card`.

Example value: proposition-parent@1

### `provenance.inspiration_refs[]`

Attributed inspirations; inspiration does not itself create a descendant relation.

Type: `Reference[]`. Vocabulary: References to attributed sources of inspiration. Basis: `moose`. Class: `searchable`. Check: `card`.

Example value: source-a

### `provenance.foreknowledge`

What relevant data/results the author knew, with declaration time and scope.

Type: `SourceBoundRecord`. Vocabulary: Source-bound declaration of what the author knew. Basis: `osf`. Class: `searchable`. Check: `passage`.

Example value: outcome knowledge not stated

### `provenance.original_artifact`

Exact original bytes or retained artifact reference, encoding/media type and byte hash.

Type: `ByteArtifact`. Vocabulary: OHF SHA-256 byte binding, not a Trusty URI. Basis: `nanopub`. Class: `system`. Check: `passage`.

Example value: source artifact A with hash supplied by ingestion

Example from card muller-sheltering at `/added/layers/provenance/original_artifact`:

```json
{
  "value": "PMC12342767.xml",
  "src": "meta"
}
```

### `provenance.field_sources[]`

Field path, exact source artifact hash and locator for each extracted assertion.

Type: `FieldSource[]`. Vocabulary: OHF extraction provenance. Basis: `ohf`. Class: `system`. Check: `passage`.

Example value: core.statement -> source-a span

### `provenance.transformation`

Converter versions, prompt or configuration references, and explicit changes.

Type: `SourceBoundRecord`. Vocabulary: OHF immutable component identity. Basis: `ohf`. Class: `system`. Check: `passage`.

Example value: converter version and exact configuration

### `provenance.translation`

Original language/text, translated proposal and translator identity/basis.

Type: `TranslationRecord`. Vocabulary: OHF labelled translation contract. Basis: `ohf`. Class: `searchable`. Check: `passage`.

Example value: proposed English translation, source retained

### `provenance.licence`

Asset-specific licence/permission and conditions, distinct from source-site software licence.

Type: `RightsRecord`. Vocabulary: SPDX identifier only when verified, otherwise verbatim terms. Basis: `ohf`. Class: `searchable`. Check: `passage`.

Example value: reuse basis pending

Example from card muller-sheltering at `/added/layers/provenance/licence`:

```json
{
  "value": "CC-BY-4.0",
  "src": "meta"
}
```

### `provenance.contributions[]`

Who created, curated, translated or reviewed each record and when.

Type: `Contribution[]`. Vocabulary: SEPIO Contribution, nanopub publication provenance. Basis: `sepio`. Class: `system`. Check: `passage`.

Example value: curator-a reviewed version 1

### `provenance.registration`

Registration time and immutable record, distinct from assertion/source times. It records the registration of this hypothesis record itself; registrations of studies cited as evidence, such as trial registry entries, belong in evidence.references.

Type: `SourceBoundRecord`. Vocabulary: Source-bound record of the registration event. Basis: `ohf`. Class: `system`. Check: `passage`.

Example value: registration pending

### `provenance.heuristic_principle[]`

Source-grounded heuristic principles used in the claim, with a pinned vocabulary and explicit justification.

Type: `HeuristicPrinciple[]`. Vocabulary: OHF record. Basis: `ohf`. Class: `searchable`. Check: `passage`.

Example value: competing-explanations, justified by "We compared competing explanations"

Example from fictional card fx_four at `/added/layers/provenance/heuristic_principle`:

```json
{
  "value": [
    {
      "term": "competing-explanations",
      "basis_quote": "We compared competing explanations for the rise in counter Y."
    }
  ],
  "src": "heuristic"
}
```

## 6 Profile

### `profile.dose_response.shape`

Author-stated form of the dose-response relation, not fitted from prose.

Type: `Term`. Vocabulary: Source wording, such as monotone; OHF 1.0 fixes no list. Basis: `ohf`. Class: `author_only`. Check: `passage`.

Example value: monotone, if stated

### `profile.dose_response.x_axis`

What varies along the curve: concentration, delivered dose or exposure, with units.

Type: `TextAndQuantity`. Vocabulary: Source declaration. Basis: `ohf`. Class: `searchable`. Check: `passage`.

Example value: exposure duration, not automatically dose

### `profile.dose_response.endpoint_ref`

Endpoint and system whose response shape is claimed.

Type: `Reference`. Vocabulary: Versioned prediction/context. Basis: `ohf`. Class: `searchable`. Check: `card`.

Example value: prediction-a

### `profile.dose_response.range`

Dose range and conditions to which that shape applies.

Type: `QuantityInterval`. Vocabulary: UCUM-compatible quantities with original wording. Basis: `ucum`. Class: `searchable`. Check: `passage`.

Example value: not stated

### `profile.combination.components[]`

Individual agents/doses and how their combination is administered.

Type: `Intervention[]`. Vocabulary: Intervention records, as in predictions[].intervention. Basis: `ohf`. Class: `searchable`. Check: `passage`.

Example value: X plus Y, fictional

### `profile.combination.reference_model`

Named reference expectation for the exact endpoint/system, with its assumptions and scale; reference models are not interchangeable additive formulas.

Type: `Term`. Vocabulary: Bliss, Loewe, HSA or ZIP when explicitly supplied. Basis: `ohf`. Class: `searchable`. Check: `passage`.

Example value: not stated

### `profile.combination.effect`

Observed or predicted combination contrast under that named model.

Type: `Assessment`. Vocabulary: Declared scale and study context. Basis: `ohf`. Class: `searchable`. Check: `passage`.

Example value: not assessed

### `profile.biomarker.role`

Repeatable attributed roles bound to an explicit readout/prediction reference and context of use; roles may include exposure, target engagement, mediator, prognostic marker, clock, surrogate or direct endpoint.

Type: `Term`. Vocabulary: Source wording of the role; OHF 1.0 fixes no list. Basis: `ohf`. Class: `searchable`. Check: `passage`.

Example value: biomarker, not lifespan

### `profile.biomarker.validation`

Repeatable validation assessments bound to an explicit readout/prediction reference, target outcome, system/population and intervention context; validation cannot transfer between predictions by proximity.

Type: `EvidenceAssessment`. Vocabulary: Endpoint/population/intervention-specific validation. Basis: `ohf`. Class: `searchable`. Check: `passage`.

Example value: not established

### `profile.harm`

Predicted or observed adverse effects with dose/system/time context and source.

Type: `PredictionOrOutcomeReference`. Vocabulary: Separate harm endpoint and provenance. Basis: `ohf`. Class: `searchable`. Check: `passage`.

Example value: harm not stated

### `profile.transfer_scope`

Limits on transfer across sex, strain, species or human populations.

Type: `TextAndEvidence`. Vocabulary: Declared applicability assessment. Basis: `ohf`. Class: `searchable`. Check: `passage`.

Example value: no human benefit claim

### `profile.function_process`

Function/process under discussion, with optional hallmarks mapping kept separate.

Type: `TextOrTerm`. Vocabulary: Reviewed GO/Reactome mapping, no mandatory hallmarks ontology. Basis: `ohf`. Class: `searchable`. Check: `passage`.

Example value: process Y

### `profile.aging_hallmarks[]`

Hallmarks of aging that atoms of this card concern, each with the atoms that concern it. A classification of the card, not a claim of the source; only in the aging profile.

Type: `Term[]`. Vocabulary: ohf:hallmarks@1: the twelve hallmarks of López-Otín et al. 2023. Basis: `ohf`. Class: `author_only`. Check: `passage`. Zones: `added`. Since: OHF 1.1.

Example value: deregulated_nutrient_sensing: a_mtorc1_inhibition

### `profile.human_testability`

Source-supported human feasibility, ethical constraints, regulatory path and prerequisites, preserving unknown components.

Type: `HumanTestability`. Vocabulary: OHF record. Basis: `ohf`. Class: `searchable`. Check: `passage`.

Example value: no human counterpart; no human study applies

Example from fictional card fx_four at `/added/layers/profile/human_testability`:

```json
{
  "value": {
    "feasible": "no"
  },
  "src": "human"
}
```

## 7 Free appendix

### `appendix.rationale`

Source-attributed scientific explanation/background kept separate from field extraction.

Type: `Text`. Vocabulary: Author narrative. Basis: `coscientist`. Class: `searchable`. Check: `passage`.

Example value: source rationale retained as narrative

### `appendix.experiment_plan`

Detailed proposed experiment with design, sampling, controls and analysis plan.

Type: `TextOrArtifact`. Vocabulary: OSF/ARRIVE-informed plan, not a completed study. Basis: `osf`. Class: `author_only`. Check: `passage`.

Example value: planned matched-system assay

### `appendix.source_extensions`

Lossless retained external sections that no card field represents.

Type: `SourceBoundRecord[]`. Vocabulary: Versioned foreign-format extension. Basis: `ai-scientist`. Class: `system`. Check: `passage`.

Example value: source Risk Factors and Limitations section

### `appendix.limitations`

Author-stated limitations and separate curator commentary with clear attribution.

Type: `TextAndAttribution`. Vocabulary: Source narrative. Basis: `ai-scientist`. Class: `searchable`. Check: `passage`.

Example value: mechanism not established

## Pair-level record

### `pair.hypothesis_refs`

The two fixed hypothesis versions being related or compared.

Type: `VersionReference[2]`. Vocabulary: OHF pair record. Basis: `ohf`. Class: `system`. Check: `card`.

Example value: proposition-a@1 and proposition-b@1

### `pair.relation`

Curated relation of claims, not forced mutual exclusivity.

Type: `Term`. Vocabulary: The relation types of ohf:hypothesis-relations@1: rival_same_explanandum | nested | compatible_independent | duplicate | refines | unrelated | analog | mechanism_neighbour. Basis: `ohf`. Class: `system`. Check: `passage`.

Example value: rival_same_explanandum

### `pair.discriminability`

Whether a scoped observation could distinguish the pair, with assessor/reason.

Type: `Assessment`. Vocabulary: OHF comparison context. Basis: `ohf`. Class: `system`. Check: `passage`.

Example value: not established

### `pair.diagnosticity_matrix`

Observation alternatives and each hypothesis's predicted result/likelihood, retaining unknowns.

Type: `DiagnosticityRecord[]`. Vocabulary: OHF adaptation of competing-hypothesis reasoning. Basis: `ohf`. Class: `system`. Check: `passage`.

Example value: observation O favors A only if stated predictions differ

### `pair.decisive_test`

Proposed discriminating test with context, predictions and resolution rule.

Type: `TestRecord`. Vocabulary: Declared pair-level design. Basis: `ohf`. Class: `system`. Check: `passage`.

Example value: test O under matched conditions

### `pair.assumptions`

Shared and differing assumptions needed to interpret the pair test.

Type: `Reference[]`. Vocabulary: References to separately attributed premises. Basis: `ohf`. Class: `system`. Check: `card`.

Example value: assumption-a

### `pair.context_ref`

Reference to the comparison context binding the pool, criterion version and protocol, together with the exact hypothesis versions and displayed-source/brief contracts. A question is optional claim context, not the comparison key.

Type: `Reference`. Vocabulary: OHF pool / versioned criterion / protocol context. Basis: `ohf`. Class: `system`. Check: `card`.

Example value: pool-example / criterion@1 / protocol@1
