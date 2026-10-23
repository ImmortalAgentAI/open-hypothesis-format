# Examples

| Path | Hypothesis |
| --- | --- |
| [cards/muller-sheltering.json](cards/muller-sheltering.json) | Muller's sheltering hypothesis extended to fitness costs that differ between the sexes |
| [cards/intermittent-rapamycin-mtorc2.json](cards/intermittent-rapamycin-mtorc2.json) | Intermittent rapamycin inhibits mTORC1 while largely sparing mTORC2 (OHF 1.1) |
| [cards/peto-paradox-mammals.json](cards/peto-paradox-mammals.json) | Cancer mortality across mammals is largely independent of body mass and life expectancy and is associated with diet (OHF 1.1) |

[index.json](index.json) gives each card's ID, version, content hash, source and conversion metadata. Each card is a reading of one published article. Its added zone is a reading of the article by a language model. The authors have not reviewed it. A schema pass confirms a card's shape, not its scientific support.

## Muller's sheltering hypothesis

[CONVERSION.md](cards/CONVERSION.md) gives the conversion rules, pinned by `added.by.converter_hash`. Every author-zone value is an exact passage of the article with a paragraph locator. Evidence lines quote only the article's own text, never the works it cites. The source was downloaded again and matched its stored hash. A separate pass, given only the passages and the instructions in [ENTAILMENT-PROMPT.md](cards/ENTAILMENT-PROMPT.md), judged whether each passage supports the value taken from it; its verdicts, including `partial` and `no`, are in `added.integrity.entailment`.

Source: Andrea Mrnjavac, Beatriz Vicoso and Tim Connallon, [An Extension of Muller's Sheltering Hypothesis for the Evolution of Sex Chromosome Gene Content](https://doi.org/10.1093/molbev/msaf177), Molecular Biology and Evolution 2025, © the authors, CC BY 4.0.

The licence was confirmed from the article's full-text XML. The card reproduces passages of the article and adds a structured reading of them; the zone marks that reading as a change.

## Intermittent rapamycin (OHF 1.1)

[converters/ohf-1-1-upgrade-1.0.2/UPGRADE.md](converters/ohf-1-1-upgrade-1.0.2/UPGRADE.md) gives the rules by which an accepted OHF 1.0 card of this article was upgraded to OHF 1.1, pinned by `added.by.converter_hash`. Unlike the Muller card, its evidence lines quote passages of cited works as well as the article, each under its own licence (CC BY), and three lines carry a withheld quote: a paraphrase and an abstract sentence of a work that may not be quoted. Taxon identifiers and the hallmark hints come from database calls, each a source record of the card. A separate pass judged the new values against their passages; its verdicts are in `added.integrity.entailment`. Taxon identifiers, proximity rungs, hallmarks, the atom triple, the `requires` links and the excluded record are checked by the schema and `tools/check_refs.py` against the card and the pinned vocabularies, not by that pass. The card has no ledger: `tools/check_ledger.py` does not yet read OHF 1.1 values.

Source: Dudley W. Lamming, [Rapamycin: the beginning of the end of aging?](https://doi.org/10.1007/s11357-026-02306-8), GeroScience 2026, CC BY 4.0.

## Peto's paradox across mammals (OHF 1.1)

[converters/ohf-1-1-upgrade-peto-1.0.1/UPGRADE.md](converters/ohf-1-1-upgrade-peto-1.0.1/UPGRADE.md) gives the rules by which an accepted OHF 1.0 card of this article was upgraded to OHF 1.1, pinned by `added.by.converter_hash`. Its evidence lines quote the article and the CC BY works that answer it. The card selects no domain profile. It shows:
- endpoint kinds, result estimates and sample sizes in the passages' own words;
- proximity rungs, most of them for clades such as "mammals", which have no species identifier, so `tools/check_refs.py` reports them as not derivable;
- DOI keys for three independence groups, so a later reanalysis of the article's zoo data shows as the same group as the original analysis.

A separate pass judged the endpoint kinds, organism words, estimates and sample sizes against their passages; its verdicts are in `added.integrity.entailment`. The proximity rungs, the keys, the `requires` links and the alternative ids are checked by the schema and `tools/check_refs.py`, not by that pass. The card has no ledger, for the reason given above.

Source: Orsolya Vincze et al., [Cancer risk across mammals](https://doi.org/10.1038/s41586-021-04224-5), Nature 2022, CC BY 4.0.

## Converter pins and entailment ledgers

`added.by.converter_hash` pins the rules a card was converted under. The rules are kept in this repository, so the pin can be recomputed from it alone. A card from `ohf-example-conversion` pins the SHA-256 of [CONVERSION.md](cards/CONVERSION.md). A card from another converter pins the rules in `converters/<converter>-<version>/`. The pin is the SHA-256 of a listing with one line per file, `<path> sha256:<hex>`, with the path relative to that directory, sorted by path:

```sh
python3 tools/converter_hash.py --check examples/cards/*.json
```

The card schema allows no extra member in an entailment record, so the text each verdict is about is recorded next to the card, in `ledgers/<slug>.json` (format `ohf-entailment-ledger/2`). For each record, the ledger keeps every check of the value: the SHA-256 of the value as the checker saw it, the SHA-256 of the passage, the time, the verdict and the note. The converter only adds checks. The checker cannot see whether a check was removed; the ledger's history in this repository shows it. A card's record must show the worst check of its current value and passage, so a later `entails` on the same text does not hide an earlier `no`; for values from source documents, see the limit below. A value whose checks disagree is reported as disputed. That is information, not a failure.

```sh
python3 tools/check_ledger.py examples/cards/<slug>.json examples/ledgers/<slug>.json
```

Without the source documents, as in CI, the ledger checker verifies the values and the verdicts, and the passages of quotations, which are in the card. For a value taken from a source document, the passage is not known there, so it is taken to be the passage of the check the record shows. A check of the same value against another passage, made after its source reference changed, is then not told apart from a check of the current passage: a later `entails` against another passage can stand in for an earlier `no`. The converter runs the check with the source documents, where only the current passage's checks count. Anyone can repeat it by downloading the sources; their SHA-256 values are in the card. The muller-sheltering card was converted before ledgers were kept and has none.

## Content hash

`content_hash` is the SHA-256 of the card's RFC 8785 canonical JSON form without the `content_hash` member:

```sh
python3 tools/content_hash.py --check examples/cards/*.json
```
