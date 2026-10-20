# Changelog

## 1.0.1

The card format, the schemas and the vocabularies are unchanged; cards valid under 1.0.0 stay schema-valid. The reference checker is stricter, so a card that passed it under 1.0.0 can now fail it.

- `tools/check_refs.py` checks every `src` in the added zone against `added.sources` (`REF_SOURCE_UNKNOWN`, `REF_SOURCES_EMPTY`).
- Identifiers are unique per namespace, and each reference field names a record of the kind it allows. The namespaces and fields are listed in the new [`spec/references.md`](spec/references.md).
- `author.generation` counts must agree (`REF_GENERATION_INCONSISTENT`). Entailment checks and assessments must be in time order (`REF_TIME_ORDER`).
- The completeness level is computed by the new `tools/check_completeness.py`. A declared level above the computed one is an error (`REF_COMPLETENESS_OVERSTATED`); a lower one, or a `missing_for_next` that does not match, is a warning.
- The example card declares its computed level, `comparable`, with a derived `missing_for_next`.
- spec/README.md states how a card written without a generation tool fills the required process members: null generation members, `model: "none"`, zero model calls; each means not applicable. The fixture `fx_nine` follows it and reaches `accepted`. Regression tests cover each new rule.
- README: the gap checker checks only the gaps a card lists; Python 3.11 or later is required and 3.12 is tested; `.github/` is under the MIT licence.

## 1.0.0

- Initial public release.
