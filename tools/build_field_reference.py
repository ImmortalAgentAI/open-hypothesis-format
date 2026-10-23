"""Generate the readable field reference spec/fields.md from spec/field-reference.json."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def label(card):
    return 'fictional card ' + card if card.startswith('fx_') else 'card ' + card


def render(catalogue):
    fields = catalogue['fields']
    paths = [field['path'] for field in fields]
    if not paths or len(set(paths)) != len(paths):
        raise ValueError('The field catalogue must contain unique paths')
    blocks = [
        '# Field reference',
        f'This reference lists all {len(fields)} logical catalogue paths. Each path has a short example value from the catalogue. Where a card fills the path, a longer example follows: from the example card muller-sheltering, converted from a published article, or from a fictional test card, whose values describe a fictional system and are not scientific evidence. A JSON pointer identifies each card example. An absent concept is illustrated by the card\'s explicit gap; no missing value is invented. Definitions and logical types describe the concept before provenance wrappers.',
        'Generated from [the reference data](field-reference.json) with `python tools/build_field_reference.py`. Edit the reference data and regenerate this file.',
        'The `basis` key records the catalogue\'s conceptual source family; it is not evidence for the example\'s scientific claim. Source records in each card supply that evidence.',
        'The class says how a missing value is treated. `searchable`: the value can be looked for in sources, and a gap records the search. `author_only`: only the author can state it; absence means "not declared", and no search is made. `system`: the value is assigned by the record itself; an empty value is a valid value.',
    ]
    layer = None
    for field in fields:
        if field['layer'] != layer:
            layer = field['layer']
            blocks.append('## ' + layer)
        facts = f"Type: `{field['logical_type']}`. Vocabulary: {field['vocabulary']}. Basis: `{field['basis']}`. Class: `{field['field_class']}`."
        if 'zones' in field:
            facts += ' Zones: ' + ', '.join(f'`{zone}`' for zone in field['zones']) + '.'
        if 'since' in field:
            facts += f" Since: OHF {field['since']}."
        if 'question_part' in field:
            facts += f" Question part: `{field['question_part']}`."
        blocks.extend(['### `' + field['path'] + '`', field['definition'], facts])
        blocks.append(f"Example value: {field['example']}")
        example = field.get('card_example')
        if example is None:
            continue
        if 'gap' in example:
            blocks.append(f"Example gap from {label(example['card'])}: {example['gap']}")
        else:
            blocks.append(f"Example from {label(example['card'])} at `{example['pointer']}`:")
            blocks.append('```json\n' + json.dumps(example['value'], ensure_ascii=False, indent=2) + '\n```')
    return '\n\n'.join(blocks) + '\n'


def check(root=ROOT):
    catalogue = json.loads((root / 'spec/field-reference.json').read_text())
    output = root / 'spec/fields.md'
    if output.read_text() != render(catalogue):
        return ['spec/fields.md is stale; run python tools/build_field_reference.py']
    return []


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    if args.check:
        errors = check()
        if errors:
            raise SystemExit('\n'.join(errors))
        print('Field reference: current')
    else:
        catalogue = json.loads((ROOT / 'spec/field-reference.json').read_text())
        (ROOT / 'spec/fields.md').write_text(render(catalogue))


if __name__ == '__main__':
    main()
