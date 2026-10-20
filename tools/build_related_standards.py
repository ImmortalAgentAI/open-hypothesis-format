"""Generate the readable list spec/related-standards.md from spec/related-standards.json."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'spec/related-standards.json'
TARGET = ROOT / 'spec/related-standards.md'
RELATION = {'field_basis': 'Field basis', 'recommended_vocabulary': 'Recommended vocabulary',
            'different_problem': 'Different problem'}


def paths(items):
    return ', '.join(f'`{path}`' for path in items)


def render(data):
    blocks = [
        '# Related standards and models',
        'These standards and models are the conceptual sources of OHF fields. Each entry names the version its facts '
        'come from. Generated from [related-standards.json](related-standards.json) with '
        '`python tools/build_related_standards.py`; edit the JSON and regenerate this file.',
        'Relations:\n\n' + '\n'.join(f'- **{RELATION[key]}**: {text}' for key, text in data['relations'].items()),
        'The card path that stores each catalogue path is in the [storage mapping](mapping.md).',
    ]
    for entry in data['standards']:
        licence = entry['license']
        licence_text = (f"{licence['value']} ({licence['source']})" if licence['value']
                        else 'Not established. OHF reuses no text or terms from it.')
        lines = [
            f"## {entry['name']}",
            entry['scope'],
            f"- Version: {entry['version']}",
            f"- Maintainer: {entry['maintainer'] or 'Not stated by the source'}",
            f'- Licence: {licence_text}',
            '- Source: ' + ', '.join(f'<{url}>' for url in entry['urls']),
            f"- Relation to OHF: {RELATION[entry['relation']]}. Catalogue paths: {paths(entry['catalogue_paths'])}",
            f"- How OHF differs: {entry['difference']}",
        ]
        blocks.append('\n'.join(lines[:2]) + '\n\n' + '\n'.join(lines[2:]))
    return '\n\n'.join(blocks) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='fail when the Markdown file is not current')
    args = parser.parse_args()
    text = render(json.loads(SOURCE.read_text()))
    if args.check:
        if TARGET.read_text() != text:
            print(f'{TARGET.relative_to(ROOT)} is not current; run tools/build_related_standards.py')
            return 1
        print('Related standards: current')
        return 0
    TARGET.write_text(text)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
