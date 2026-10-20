# Test fixtures

The fixtures are inputs for the tests and illustrations in the [field reference](../../spec/fields.md). They are not example cards.

## Fictional cards

The cards in [`fictional/`](fictional) describe a fictional test system. They are not scientific evidence. Each one binds the SHA-256 of its source file in [`fictional/sources/`](fictional/sources).

- `fx_one`: a literal author statement.
- `fx_two`: the five source-bound components of an intermediate test.
- `fx_three`: an added value with a retained source locator.
- `fx_four`: a claim about a fictional intervention, in the domain profile `ohf:intervention-pharmacology@1`, with many intervention and study fields filled.
- `fx_five`: a claim with no intervention, in the domain profile `none`: the intervention fields are absent and need no gap, and an author-only field is `not_supplied`.
- `fx_six` and `fx_seven`: two rival accounts of the same oscillation. [`pair-brief-six-seven.json`](fictional/pair-brief-six-seven.json) records what they share and which observations tell them apart; [`relations-six-seven.json`](fictional/relations-six-seven.json) records the relation in `ohf:hypothesis-relations@1`.
- `fx_eight`: failed integrity checks. The refetched source differs from the stored one ([`fx_eight.refetched.json`](fictional/sources/fx_eight.refetched.json)), one entailment verdict is `partial` and one is `no`, and two evidence lines share an independence group.

## Fragments

A fragment shows the shape of a few fields. It is not a complete card. `sourced-fields.json` does not validate against the card schema, and its protocol, budget and molecular target are illustrations, not evidence.
