# Open Hypothesis Format

Open Hypothesis Format (OHF) describes a biological hypothesis as a structured record bound to its sources. An OHF card keeps what the author said apart from what was added later, and it records each missing value as an explicit gap.

## Why OHF

Biological hypotheses are written as prose, spread across papers, preprints and, increasingly, the output of AI systems. Comparing, searching and tracking them then rests on each reader's own reading of that prose. An OHF card records what exactly is claimed, under which conditions, on what evidence, what would refute it and where it came from. It keeps the author's words apart from later interpretation and records each missing value that a reader could expect. Comparison, search and tracking become explicit, reproducible and machine-readable, so hypotheses from people and from machines can be compared on a common structure and the most promising ones tested.

In OHF, a **hypothesis** is a proposed claim about a living system, typically an explanation of an observed phenomenon, that goes beyond established knowledge at the time it is stated, is stated with its scope and conditions, and entails observations that would count for or against it. The [glossary](spec/glossary.md) defines the other terms.

This repository holds OHF 1.0.0: the specification, the JSON Schemas, the vocabularies, an example card and a reference validator.

- **Implementers** who write, convert or read cards: start with the [schema](schema/hypothesis-1.schema.json) and the [validator](tools/validate.py).
- **Scientists and reviewers**: start with the [field reference](spec/fields.md) and the [specification](spec/README.md).

## What a card contains

A card has two zones. `author` holds the author's assertions; each value carries a `locator` into the source text. `added` holds what a converter or reviewer added; each value carries a `src` that points to a source record. Both zones use the same seven scientific layers:

1. claim core;
2. mechanism;
3. predictions;
4. evidence;
5. provenance;
6. profile: biomarkers, human testability, transfer scope, the function or process concerned, and the dose-response, combination and harm fields of a domain profile;
7. appendix.

The field catalogue also has layer 0, identity and versions, which applies to the whole card, and the pair-level record, which describes two cards together and is stored outside them. A field with no value is listed in `added.gaps` with the reason. Each field has a class, `searchable`, `author_only` or `system`, that says whether a missing value calls for a search.

Every card states `"standard_version": "1.0"`. This names the version of the card format. It changes only when the format changes; a release that fixes only text or tools, such as 1.0.1, keeps it. A card names its domain profile: `ohf:intervention-pharmacology@1` for a claim about the effect of an intervention, or `none`. The intervention details and intercurrent events of that profile are stored in the predictions layer. The added zone records how it was produced, whether the source was downloaded again and matched, and whether the source supports each added value.

## Repository layout

| Path | Contents |
| --- | --- |
| [`spec/`](spec) | Specification, glossary, field catalogue and reference, logical types, gap policy, storage mapping, related standards |
| [`schema/`](schema) | JSON Schemas, draft 2020-12: card, pair relations, pair brief, scientific field extensions, gap policy |
| [`vocabularies/`](vocabularies) | Controlled vocabularies, pinned by SHA-256 in the schema |
| [`examples/`](examples) | Example cards converted from published articles |
| [`tools/`](tools) | Validator, gap checker, reference checker, content-hash tool, mapping checker, generators of the field reference and the list of related standards |
| [`tests/`](tests) | Tests of the tools and the repository files; test fixtures in `tests/fixtures/` |

## Validate a card

The tools need Python 3.11 or later, because the pinned `rpds-py` requires it. They are tested on Python 3.12, the version both CI workflows use.

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python tools/validate.py examples/cards/muller-sheltering.json
.venv/bin/python tools/content_hash.py --check examples/cards/muller-sheltering.json
.venv/bin/python tools/check_gaps.py examples/cards/muller-sheltering.json
.venv/bin/python tools/check_refs.py examples/cards/muller-sheltering.json
```

The validator rejects duplicate JSON members, non-finite numbers and invalid calendar timestamps, and reports every schema error. The gap checker applies the [gap rules](spec/README.md#gaps) to the gaps a card lists and lists the checks that need a reviewer. It does not show that every missing applicable field is listed: a field that is absent and has no gap is not reported. The reference checker resolves the internal references of a card, as listed in [identifiers and references](spec/references.md), applies the integrity rules the schema cannot express, lists which predictions are comparable, and computes the [completeness](spec/README.md#completeness) level; a declared level above the computed one is an error. Both checkers assume a schema-valid card.

A schema pass checks shape only. It does not show that a quotation matches its source, that a source supports a claim, or that a card is complete.

CI runs the repository checks on every pull request and on `main`, on both hosting sites: the [Forgejo workflow](.forgejo/workflows/check.yml) and the [GitHub workflow](.github/workflows/check.yml) ([runs on GitHub](https://github.com/ImmortalAgentAI/open-hypothesis-format/actions/workflows/check.yml)). The main repository checks:

```sh
.venv/bin/python -m pytest
.venv/bin/python tools/check_mapping.py
.venv/bin/python tools/build_field_reference.py --check
.venv/bin/python tools/build_related_standards.py --check
```

## Known limits

- The example card's added zone is a reading of the article by a language model, and its entailment verdicts come from a separate machine pass. The authors have not reviewed either. See [`examples/README.md`](examples/README.md).
- Many fields are illustrated in the [field reference](spec/fields.md) only by a short example value or by fictional test fixtures, not by a card from a published source.
- Evidence types, taxa and agent types are free text, not identifiers from external vocabularies. The indirectness and risk-of-bias vocabularies are OHF's own and are not mapped to GRADE or RoB 2.
- Quantities, intervals and assessments are source-literal strings; see [logical types](spec/logical-types.md).
- Question references and the assertion registry have no serialization in OHF 1.0. Of the pair-level fields, the relation is stored in a relations artifact and the hypothesis references and the decisive test in a pair brief; discriminability, the diagnosticity matrix, pair assumptions and comparison context have none. The [storage mapping](spec/mapping.md) marks the fields without serialization as deferred.

## Licensing

Each file is under one of two licences, assigned by path.

| Licence | Applies to |
| --- | --- |
| MIT, [`LICENSE`](LICENSE) | Code: [`tools/`](tools), [`tests/`](tests), [`schema/`](schema), [`.forgejo/`](.forgejo), [`.github/`](.github), `requirements.txt`, `pytest.ini`, `.gitignore` |
| CC BY 4.0, [`LICENSE-SPEC`](LICENSE-SPEC) | Specification: everything else, including this README, [`CHANGELOG.md`](CHANGELOG.md), [`spec/`](spec), [`vocabularies/`](vocabularies) and [`examples/`](examples) |

The JSON Schemas in `schema/` are validators and are under MIT with the code, although the specification describes them. The test fixtures in `tests/fixtures/` are under MIT with the tests. The field catalogue, mapping and policies in `spec/` are under CC BY 4.0 with the specification.

Attribution for the specification: "Open Hypothesis Format (OHF), Open Longevity".

Material from third parties is not relicensed. Passages that the example cards quote from published articles keep the licences of their sources, listed in [`examples/README.md`](examples/README.md). Quotations from sources with no established licence are not included: the card gives the source, its SHA-256 and a locator instead.
