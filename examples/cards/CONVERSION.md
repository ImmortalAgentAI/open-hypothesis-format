# How the example card muller-sheltering was converted

The card was converted by a language model, without an automated pipeline, from a published article under CC BY 4.0. The licence was confirmed from the `permissions` block of the full-text XML, not only from search metadata. The conversion followed these rules.

1. **Author zone: exact text.** Every value in `author.layers` is an exact passage from the article. The passage is taken from one paragraph after tags are removed and whitespace is collapsed. Its locator names that paragraph: `XML .//p[N] (1-based document order)` in the Europe PMC full-text XML. The SHA-256 of that XML is in `author.source.source_text_sha256`.
2. **Added zone: the converter's reading.** Atoms, mechanism, predictions and the fields for what the hypothesis explains, reinterprets and opens are the converter's reading of the article. Each value names its source passage through `src`, a key of `added.sources`. A value that restates the article in other words carries `paraphrase: true` and the passage it restates in `basis_quote`. These values are changes to the article in the sense of the licence. They are not the authors' words, and the authors have not reviewed them.
3. **Assessments are attributed and grounded.** `predictions[].discrimination`, `core.testability` and the evidence-quality fields are the converter's assessments, with the assessor and date in `assessment`. An assessment is kept only where it follows from the passage it cites; otherwise the field is a `not_supplied` gap.
4. **Quotations of other works are not reproduced.** The article's licence does not cover the works it cites. Evidence lines quote only the article's own text. A cited work is named by its reference, not quoted.
5. **Nothing is invented.** A field the article does not support is left empty, or a gap records why it is missing. The card makes no claim beyond the article.
6. **Atoms are classified.** Each atom has a claim type, a role and a modality. The modality rests on the authors' exact wording, given in `basis_quote`; the claim type and the role are the converter's reading.
7. **Evidence quality is the converter's assessment.** `indirectness` and `risk_of_bias` carry an assessor and date. Where the converter did not examine the methods of the study behind a line, `risk_of_bias` says `not_assessed`. `independence_group` is set only where the article shows that two lines rest on the same data; the article does not.
8. **First proposal.** `core.first_proposed` takes the date from the article: its publication date when the authors propose the idea there, or the earlier work they credit.
9. **Source check.** The source XML was downloaded again from Europe PMC and its SHA-256 compared with the stored hash. The DOI was looked up in the Crossref REST API. `retracted: false` means only that the Crossref record listed no retraction or other update notice at the time of the check. The Crossref response is not stored.
10. **Entailment is checked by a separate pass.** A second model pass, without the conversion context, compared each sourced added-zone value with its source paragraph. Its instructions are in `ENTAILMENT-PROMPT.md`, and their SHA-256 is `checker.prompt_sha256`.
11. **No domain profile.** The claim is not about an intervention, so the card selects `profile.domain: "none"`, and the intervention and pharmacology fields are absent.

The source XML is not included in this repository. The citation, DOI, licence and source hash of the card are in `author.source` and in [`index.json`](../index.json).

`added.by.converter_hash` is the SHA-256 of this file.
