#!/usr/bin/env python3
"""Extract requested video frames with ffmpeg; never claim exact decoded timestamps."""
import argparse
import json
import math
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def run(command):
    result = subprocess.run(command, capture_output=True, text=True, timeout=120)
    if result.returncode:
        raise ValueError(f'{Path(command[0]).name}: {result.stderr.strip()[-1500:]}')
    return result.stdout


def extract(video, times, out_dir, source_id):
    ffmpeg, ffprobe = shutil.which('ffmpeg'), shutil.which('ffprobe')
    if not ffmpeg or not ffprobe:
        raise ValueError('ffmpeg and ffprobe must both be on PATH')
    if not video.is_file():
        raise ValueError(f'video not found: {video}')
    if not source_id.strip():
        raise ValueError('source-id must not be empty')
    info = json.loads(run([ffprobe, '-v', 'error', '-show_entries', 'format=duration:stream=codec_type', '-of', 'json', str(video)]))
    duration = float(info.get('format', {}).get('duration', 'nan'))
    if not math.isfinite(duration) or duration <= 0 or not any(s.get('codec_type') == 'video' for s in info.get('streams', [])):
        raise ValueError('cannot determine a finite video duration / video stream')
    if not isinstance(times, list) or not times:
        raise ValueError('times must be a nonempty JSON numeric array')
    for t in times:
        if isinstance(t, bool) or not isinstance(t, (int, float)) or not math.isfinite(t) or not 0 <= t < duration:
            raise ValueError(f'invalid requested time {t!r}; expected 0 <= time < {duration}')
    names = [f'frame-{i:04d}.png' for i in range(1, len(times) + 1)]
    out_dir.mkdir(parents=True, exist_ok=True)
    if any((out_dir / n).exists() for n in names + ['frames.json']):
        raise ValueError('output exists; choose a new out-dir (no overwrite)')
    result = {'schema_version': 1, 'source_id': source_id, 'duration_s': duration, 'timestamp_basis': 'requested_seek_time', 'frames': []}
    # Decode all frames before publishing; incomplete decoding leaves no published assets.
    with tempfile.TemporaryDirectory(prefix='.frames-', dir=out_dir) as tmp:
        for t, name in zip(times, names):
            dest = Path(tmp) / name
            run([ffmpeg, '-nostdin', '-v', 'error', '-ss', str(t), '-i', str(video), '-map', '0:v:0', '-frames:v', '1', '-threads', '1', '-n', str(dest)])
            if not dest.is_file() or dest.read_bytes()[:8] != b'\x89PNG\r\n\x1a\n':
                raise ValueError(f'no decodable image near requested time {t}')
            result['frames'].append({'requested_time_s': t, 'path': name})
        for name in names:
            with (out_dir / name).open('xb') as out:
                out.write((Path(tmp) / name).read_bytes())
        with (out_dir / 'frames.json').open('x', encoding='utf-8') as out:
            json.dump(result, out, indent=2, ensure_ascii=False, allow_nan=False)
            out.write('\n')
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('video', type=Path)
    p.add_argument('--times', required=True, type=Path)
    p.add_argument('--out-dir', required=True, type=Path)
    p.add_argument('--source-id', required=True)
    a = p.parse_args()
    try:
        extract(a.video, json.loads(a.times.read_text(encoding='utf-8')), a.out_dir, a.source_id)
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        print(f'error: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
