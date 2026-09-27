#!/usr/bin/env python3
"""Parse UTF-8 SRT/WebVTT without deduplicating or inferring spoken meaning."""
import argparse
import json
import re
import sys
from pathlib import Path


def timestamp(value, vtt=False):
    pattern = r'(?:(\d{2,}):)?(\d{2}):(\d{2})\.(\d{3})' if vtt else r'(\d{2,}):(\d{2}):(\d{2}),(\d{3})'
    m = re.fullmatch(pattern, value)
    if not m:
        raise ValueError(f'invalid timestamp {value!r}')
    h, minute, sec, ms = m.groups()
    if int(minute) >= 60 or int(sec) >= 60:
        raise ValueError(f'invalid timestamp {value!r}')
    return int(h or 0) * 3600 + int(minute) * 60 + int(sec) + int(ms) / 1000


def parse(text, source_id, format_hint=None):
    text = text.lstrip('\ufeff').replace('\r\n', '\n').replace('\r', '\n')
    lines = text.splitlines()
    vtt = bool(lines and re.fullmatch(r'WEBVTT(?:[ \t].*)?', lines[0]))
    if format_hint == '.vtt' and not vtt:
        raise ValueError('line 1: WebVTT must begin with WEBVTT')
    blocks = []
    start, block = 1, []
    for n, line in enumerate(lines + [''], 1):
        if line.strip():
            if not block:
                start = n
            block.append(line)
        elif block:
            blocks.append((start, block))
            block = []
    cues = []
    for lineno, block in blocks:
        if vtt and (block[0].startswith('WEBVTT') or re.match(r'^(NOTE(?:\s|$)|STYLE$|REGION$)', block[0])):
            continue
        idx = 0 if '-->' in block[0] else 1
        if idx >= len(block) or '-->' not in block[idx]:
            raise ValueError(f'line {lineno}: missing cue timing')
        try:
            timing = re.fullmatch(r'(\S+)\s+-->\s+(\S+)(?:[ \t]+(.*))?', block[idx])
            if not timing:
                raise ValueError('invalid cue timing')
            a, b, settings = timing.groups()
            if settings and not vtt:
                raise ValueError('SRT cue settings are unsupported')
            start_s, end_s = timestamp(a, vtt), timestamp(b, vtt)
            if not 0 <= start_s < end_s:
                raise ValueError('expected 0 <= start_s < end_s')
            body = '\n'.join(block[idx + 1:])
            if not body.strip():
                raise ValueError('empty cue text')
        except ValueError as exc:
            raise ValueError(f'line {lineno + idx}: {exc}') from exc
        cues.append({'id': f'c{len(cues) + 1:04d}', 'start_s': start_s, 'end_s': end_s, 'text': body})
    if not cues:
        raise ValueError('no cues found')
    return {'schema_version': 1, 'source_id': source_id, 'cues': cues}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('input', type=Path)
    p.add_argument('--output', required=True, type=Path)
    p.add_argument('--source-id', required=True)
    args = p.parse_args()
    try:
        if not args.source_id.strip():
            raise ValueError('source-id must not be empty')
        if args.input.suffix.lower() not in {'.srt', '.vtt'}:
            raise ValueError('only .srt and .vtt inputs are supported')
        data = parse(args.input.read_text(encoding='utf-8-sig'), args.source_id, args.input.suffix.lower())
        with args.output.open('x', encoding='utf-8') as out:
            json.dump(data, out, ensure_ascii=False, indent=2, allow_nan=False)
            out.write('\n')
    except (OSError, ValueError, UnicodeError) as exc:
        print(f'error: {args.input}: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
