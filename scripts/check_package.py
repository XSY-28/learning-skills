#!/usr/bin/env python3
"""Check the public skill packages; this does not evaluate teaching quality."""
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

import yaml

ROOT = Path(__file__).resolve().parents[1]
NAMES = ('course-to-notes', 'explain-for-understanding', 'obsidian-lecture-writing')


def outside_fences(text):
    marker = None
    for line in text.splitlines():
        fence = re.match(r'^\s*(`{3,}|~{3,})', line)
        if fence:
            candidate = fence.group(1)
            if marker is None:
                marker = candidate
            elif candidate[0] == marker[0] and len(candidate) >= len(marker):
                marker = None
            continue
        if marker is None:
            yield line


def check():
    errors = []
    files = []
    for name in NAMES:
        root = ROOT / 'skills' / name
        try:
            skill = root / 'SKILL.md'
            match = re.match(r'^---\n(.*?)\n---', skill.read_text(encoding='utf-8'), re.S)
            if match is None:
                raise ValueError('missing YAML frontmatter')
            meta = yaml.safe_load(match.group(1))
            if not isinstance(meta, dict) or meta.get('name') != name:
                raise ValueError('frontmatter name does not match folder')
            description = meta.get('description')
            if not isinstance(description, str) or not 0 < len(description.strip()) <= 1024:
                raise ValueError('missing or oversized description')
            ui = yaml.safe_load((root / 'agents/openai.yaml').read_text(encoding='utf-8'))
            for field in ('display_name', 'short_description', 'default_prompt'):
                if not isinstance(ui['interface'].get(field), str) or not ui['interface'][field].strip():
                    raise ValueError(f'missing interface.{field}')
            if '$' + name not in ui['interface']['default_prompt']:
                raise ValueError('default prompt does not invoke this skill')
            if ui.get('policy', {}).get('allow_implicit_invocation') is not True:
                raise ValueError('invocation policy changed')
            if (root / 'LICENSE').read_bytes() != (ROOT / 'LICENSE').read_bytes():
                raise ValueError('bundled license differs')
            files.extend(p for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts)
        except (OSError, ValueError, TypeError, KeyError, yaml.YAMLError) as exc:
            errors.append(f'{name}: {exc}')

    links = 0
    docs = [ROOT / 'README.md', ROOT / 'README.zh-CN.md', ROOT / 'docs/validation.md']
    for path in docs + [p for p in files if p.suffix == '.md']:
        if not path.is_file():
            errors.append(f'missing {path.relative_to(ROOT)}')
            continue
        for line in outside_fences(path.read_text(encoding='utf-8')):
            line = re.sub(r'(`+).*?\1', '', line)
            for target in re.findall(r'\[[^\]]*\]\(([^)\s]+)\)', line):
                parsed = urlsplit(target)
                if parsed.scheme or not parsed.path:
                    continue
                destination = (path.parent / unquote(parsed.path)).resolve()
                if not destination.is_relative_to(ROOT) or not destination.exists():
                    errors.append(f'{path.relative_to(ROOT)}: broken local link {target}')
                links += 1
    print(f'{len(NAMES)} skills; {len(files)} runtime files; {links} local links; {len(errors)} errors')
    for error in errors:
        print(error, file=sys.stderr)
    return bool(errors)


if __name__ == '__main__':
    sys.exit(check())
