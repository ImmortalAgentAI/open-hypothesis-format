# Examples

| Path | Hypothesis |
| --- | --- |
| [cards/muller-sheltering.json](cards/muller-sheltering.json) | Muller's sheltering hypothesis extended to fitness costs that differ between the sexes |

[index.json](index.json) gives each card's ID, version, content hash, source and conversion metadata. Each card is produced from one published article. Its added zone is a reading of the article by a language model. The authors have not reviewed it. A schema pass confirms a card's shape, not its scientific support.

## Muller's sheltering hypothesis

[CONVERSION.md](cards/CONVERSION.md) gives the conversion rules, pinned by `added.by.converter_hash`. Every author-zone value is an exact passage of the article with a paragraph locator. Evidence lines quote only the article's own text, never the works it cites. The source was downloaded again and matched its stored hash. A separate pass, given only the passages and the instructions in [ENTAILMENT-PROMPT.md](cards/ENTAILMENT-PROMPT.md), judged whether each passage supports the value taken from it; its verdicts, including `partial` and `no`, are in `added.integrity.entailment`.

Source: Andrea Mrnjavac, Beatriz Vicoso and Tim Connallon, [An Extension of Muller's Sheltering Hypothesis for the Evolution of Sex Chromosome Gene Content](https://doi.org/10.1093/molbev/msaf177), Molecular Biology and Evolution 2025, © the authors, CC BY 4.0.

The licence was confirmed from the article's full-text XML. The card reproduces passages of the article and adds a structured reading of them; the zone marks that reading as a change.

## Content hash

`content_hash` is the SHA-256 of the card's RFC 8785 canonical JSON form without the `content_hash` member:

```sh
python3 tools/content_hash.py --check examples/cards/*.json
```
