#!/usr/bin/env python3
"""Generate DSH discovery metadata from the shared skill entrypoints."""
import argparse
import json
from pathlib import Path
import re

import yaml

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Fail if the committed catalog is stale.')
    args = parser.parse_args()
    catalog = []
    for entry in sorted((ROOT / 'skills').glob('*/SKILL.md')):
        match = re.match(r'^---\n(.*?)\n---', entry.read_text(encoding='utf-8'), re.S)
        if match is None:
            raise ValueError(f'{entry}: missing frontmatter')
        meta = yaml.safe_load(match.group(1))
        name, description = meta['name'], meta['description']
        if name != entry.parent.name or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name):
            raise ValueError(f'{entry}: invalid name')
        if not isinstance(description, str) or not description.strip():
            raise ValueError(f'{entry}: empty description')
        catalog.append({'name': name, 'description': description})
    output = json.dumps(catalog, ensure_ascii=False, indent=2) + '\n'
    target = ROOT / 'dsh/catalog.json'
    if args.check:
        if not target.exists() or target.read_text(encoding='utf-8') != output:
            parser.exit(1, 'DSH catalog is stale; run python3 scripts/build_dsh_catalog.py\n')
        print(f'DSH catalog matches {len(catalog)} skill entrypoints.')
    else:
        target.write_text(output, encoding='utf-8')
        print(f'Generated {target.relative_to(ROOT)} with {len(catalog)} skills.')


if __name__ == '__main__':
    main()
