# Changelog

## Unreleased

The card format, the schemas and the vocabularies are unchanged.

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
