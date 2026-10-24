# Schemas

All schemas use JSON Schema draft 2020-12. The `$id` of each schema is its OHF identifier, such as `ohf:hypothesis@1`.

| Schema | Validates |
| --- | --- |
| [hypothesis-1.schema.json](hypothesis-1.schema.json) | A hypothesis card, `"standard_version"` `"1.0"`, `"1.1"`, `"1.2"` or `"1.3"`. |
| [hypothesis-relations-1.schema.json](hypothesis-relations-1.schema.json) | A detached relations artifact: typed edges between card versions in a fixed pool. Types: `rival_same_explanandum`, `nested`, `compatible_independent`, `duplicate`, `refines`, `unrelated`, `analog`, `mechanism_neighbour` (the last two from OHF 1.1; an end may name one record of its card version). Support and contradiction are evidence relations, not relations between hypotheses, and are not included. |
| [pair-brief-1.schema.json](pair-brief-1.schema.json) | A pair brief: what two card versions share and what would tell them apart. It describes the pair and does not judge which hypothesis is better. |
| [scientific-field-extensions.schema.json](scientific-field-extensions.schema.json) | Nothing on its own. It is a library of named definitions for five scientific fields and the records they reference. Validate a fragment against one definition by reference, for example `{"$ref": "#/$defs/author:core.potential_benefit"}`. |
| [gap-path-policy-1.schema.json](gap-path-policy-1.schema.json) | The gap policy file [`spec/gap-path-policy.json`](../spec/gap-path-policy.json): one row per catalogue path, with its inapplicability rule and condition. |

A pattern ends with `(?![\s\S])`, which matches only at the end of the string; no pattern uses `$`. In Python's `re`, which `tools/validate.py` uses, `$` also matches before one final line feed, so a value such as a SHA-256 followed by a line feed passed there and failed in an ECMA-262 validator. Such a value never had the meaning of its pattern, and the released schemas used the same end for some patterns since 1.0; the others now use it too. In a JSON pointer a key may hold a line feed, also at the end, as in any JSON pointer. `tests/test_pattern_ends.py` checks every pattern.

A schema pass checks shape only. Source support, quotation accuracy and completeness need separate checks.
