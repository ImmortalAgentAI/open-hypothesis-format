"""The spec README names exactly the fields whose fixed list applies only to the added zone."""
import re
from pathlib import Path
from urllib.parse import unquote

from tools.strict_json import load

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = load(ROOT / 'schema/hypothesis-1.schema.json')


def walk(node, path, paths, enums, refs=()):
    """Collect every logical path under node, and the paths that carry an enum."""
    if not isinstance(node, dict):
        return
    paths.add(path)
    if 'enum' in node:
        enums.add(path)
    if '$ref' in node:
        name = unquote(node['$ref'].removeprefix('#/$defs/'))
        if name not in refs:
            walk(SCHEMA['$defs'][name], path, paths, enums, refs + (name,))
    for key in ('anyOf', 'oneOf', 'allOf'):
        for branch in node.get(key, []):
            walk(branch, path, paths, enums, refs)
    for name, child in node.get('properties', {}).items():
        walk(child, path + ('' if name == 'value' else '.' + name), paths, enums, refs)
    if isinstance(node.get('items'), dict):
        walk(node['items'], path + '[]', paths, enums, refs)


def zone(name):
    paths, enums = set(), set()
    walk(SCHEMA['properties'][name]['properties']['layers'], '', paths, enums)
    return paths, enums


def test_readme_lists_the_added_only_enums():
    author_paths, author_enums = zone('author')
    _, added_enums = zone('added')
    expected = {p.lstrip('.') for p in added_enums - author_enums if p in author_paths}
    text = (ROOT / 'spec/README.md').read_text(encoding='utf-8')
    sentence = re.search(r'restricted only in the added zone: ([^.]*(?:\.[^ ][^.]*)*)\.', text).group(1)
    assert set(re.findall(r'`([^`]+)`', sentence)) == expected
