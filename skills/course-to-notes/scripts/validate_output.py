#!/usr/bin/env python3
"""Validate the v1 course sidecar contract, never semantic truth or mastery."""
import argparse
import hashlib
import json
import math
import re
import sys
import zipfile
from pathlib import Path
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree as ET


class Audit:
    def __init__(self):
        self.errors = []
        self.warnings = []

    def error(self, message):
        self.errors.append(message)

    def warning(self, message):
        self.warnings.append(message)

    def fields(self, obj, fields, where):
        if not isinstance(obj, dict):
            raise ValueError(f'{where}: expected object')
        for key in fields.split():
            if key not in obj:
                self.error(f'{where}: missing {key}')
        return obj

    def array(self, obj, key, where):
        value = obj.get(key, [])
        if not isinstance(value, list):
            raise ValueError(f'{where}.{key}: expected array')
        return value

    def read(self, path):
        try:
            value = json.loads(path.read_text(encoding='utf-8'), parse_constant=lambda s: (_ for _ in ()).throw(ValueError(f'nonfinite JSON {s}')))
            self.fields(value, 'schema_version', path.name)
            if value.get('schema_version') != 1:
                self.error(f'{path.name}: expected schema_version 1')
            return value
        except (OSError, ValueError) as exc:
            self.error(f'{path.name}: {exc}')
            return {}

    def span(self, obj, where):
        a, b = obj.get('start_s'), obj.get('end_s')
        if not number(a) or not number(b) or not 0 <= a < b:
            self.error(f'{where}: expected finite 0 <= start_s < end_s')
            return None
        return a, b

    def enum(self, obj, key, choices, where):
        if obj.get(key) not in choices:
            self.error(f'{where}: invalid {key} {obj.get(key)!r}')


def number(x):
    return not isinstance(x, bool) and isinstance(x, (int, float)) and math.isfinite(x)


def local_path(base, relative, audit, where):
    if not isinstance(relative, str) or not relative.strip() or Path(relative).is_absolute():
        audit.error(f'{where}: expected nonempty relative path')
        return None
    resolved = (base / relative).resolve()
    if not resolved.is_relative_to(base.resolve()):
        audit.error(f'{where}: path escapes directory')
        return None
    if not resolved.is_file():
        audit.error(f'{where}: missing file {relative}')
        return None
    return resolved


def unique(rows, key, audit, where):
    ids = [r.get(key) for r in rows]
    if any(not isinstance(i, str) or not i for i in ids) or len(set(ids)) != len(ids):
        audit.error(f'{where}: missing or duplicate {key}')
    return set(ids)


def validate(root):
    a = Audit()
    try:
        _validate(Path(root), a)
    except (ValueError, TypeError, AttributeError, KeyError, OSError, ET.ParseError, zipfile.BadZipFile) as exc:
        a.error(f'invalid structure: {exc}')
    return {'schema_version': 1, 'errors': a.errors, 'warnings': a.warnings}


def _validate(root, a):
    parent = root.parent
    manifest = a.read(root / 'manifest.json')
    coverage = a.read(root / 'coverage.json')
    annotations = a.read(root / 'section-annotations.json')
    profile = a.read(parent / 'learner-profile.json')
    glossary = a.read(parent / 'glossary.json')
    revisions = a.read(parent / 'revisions.json')
    a.fields(manifest, 'course_id lecture_id target_language requested_format artifact_path source_video_id processing_range sources assets unresolved_items document_sha256 review_status', 'manifest')
    a.fields(coverage, 'processing_range segments', 'coverage')
    a.fields(profile, 'profile_id revision learning_goal source_scope evidence_records', 'profile')
    a.fields(annotations, 'profile_id profile_revision sections', 'annotations')
    a.fields(glossary, 'course_id entries', 'glossary')
    a.fields(revisions, 'entries', 'revisions')
    if glossary.get('course_id') != manifest.get('course_id'):
        a.error('glossary: course_id mismatch')
    if not isinstance(profile.get('revision'), int) or isinstance(profile.get('revision'), bool) or profile.get('revision', -1) < 0:
        a.error('profile: revision must be nonnegative integer')
    if annotations.get('profile_id') != profile.get('profile_id'):
        a.error('annotations: profile_id mismatch')
    if annotations.get('profile_revision') != profile.get('revision'):
        a.warning('annotations: stale profile_revision; reassess markers and index without changing conclusions automatically')
    for record in a.array(revisions, 'entries', 'revisions'):
        a.fields(record, 'at correction affected_files checked_scope unchecked_scope backup_paths', 'revision')
    keys = []
    for term in a.array(glossary, 'entries', 'glossary'):
        a.fields(term, 'source_term domain concept target_language rendering keep_original evidence user_override', 'glossary entry')
        keys.append(tuple(term.get(k) for k in ('source_term', 'domain', 'concept', 'target_language')))
    if len(keys) != len(set(keys)):
        a.error('glossary: duplicate context/concept key')
    for source in a.array(manifest, 'sources', 'manifest'):
        a.fields(source, 'id kind ref version attribution license verification', 'source')
        if source.get('verification') != 'checked':
            a.warning(f'source {source.get("id")}: not checked')
    source_ids = unique(manifest.get('sources', []), 'id', a, 'sources')
    if manifest.get('source_video_id') not in source_ids:
        a.error('manifest: source_video_id is not in sources')
    for item in a.array(manifest, 'unresolved_items', 'manifest'):
        a.warning(f'unresolved: {item}')
    a.enum(manifest, 'review_status', {'unprocessed', 'drafted', 'checked'}, 'manifest')
    if manifest.get('review_status') != 'checked':
        a.warning('document has not completed content review')
    pspan = a.span(manifest.get('processing_range', {}), 'manifest processing_range')
    cspan = a.span(coverage.get('processing_range', {}), 'coverage processing_range')
    if pspan != cspan:
        a.error('coverage: processing_range differs from manifest')
    records = a.array(profile, 'evidence_records', 'profile')
    evidence_ids = unique(records, 'id', a, 'profile evidence')
    evidence = {}
    for ev in records:
        a.fields(ev, 'id source_ref observed_at domain concept depth assertion origin', 'evidence')
        if not ev.get('source_ref'):
            a.error('evidence: empty source_ref')
        if ev.get('readable') is False:
            a.warning(f'evidence {ev.get("id")}: source cannot be reread')
        evidence[ev.get('id')] = ev
    sections = a.array(annotations, 'sections', 'annotations')
    section_ids = unique(sections, 'section_id', a, 'annotations sections')
    labels = {}
    for section in sections:
        sid = section.get('section_id')
        a.fields(section, 'section_id concepts importance reading_advice display', f'section {sid}')
        concepts = a.array(section, 'concepts', f'section {sid}')
        if not concepts:
            a.error(f'section {sid}: concepts empty')
        for concept in concepts:
            a.fields(concept, 'domain concept depth learning_status mastery_basis evidence_ids rationale', f'concept {sid}')
            a.enum(concept, 'learning_status', {'studied', 'exposure_only', 'explicitly_unlearned', 'unknown'}, f'concept {sid}')
            a.enum(concept, 'mastery_basis', {'not_assessed', 'self_reported', 'performance_supported'}, f'concept {sid}')
            ids = a.array(concept, 'evidence_ids', f'concept {sid}')
            if concept.get('learning_status') != 'unknown' and not ids:
                a.error(f'concept {sid}: non-unknown learning_status needs evidence')
            if set(ids) - evidence_ids:
                a.error(f'concept {sid}: nonexistent evidence ID')
            basis = concept.get('mastery_basis')
            origins = {'self_reported': 'user_self_report', 'performance_supported': 'observed_performance'}
            if basis in origins and not any(evidence.get(i, {}).get('origin') == origins[basis] for i in ids):
                a.error(f'concept {sid}: mastery_basis lacks corresponding evidence origin')
        importance = a.fields(section.get('importance', {}), 'level reasons', f'importance {sid}')
        a.enum(importance, 'level', {'key', 'regular', 'undetermined'}, f'importance {sid}')
        reasons = a.array(importance, 'reasons', f'importance {sid}')
        if not reasons:
            a.error(f'importance {sid}: missing reasons')
        for reason in reasons:
            a.fields(reason, 'basis_type text source_ref', f'importance {sid}')
            a.enum(reason, 'basis_type', {'teacher_emphasis', 'course_dependency', 'learning_goal', 'editorial_assessment'}, f'importance {sid}')
            if not reason.get('text') or not reason.get('source_ref'):
                a.error(f'importance {sid}: empty reason or source')
        advice = a.fields(section.get('reading_advice', {}), 'level reason', f'advice {sid}')
        a.enum(advice, 'level', {'read_carefully', 'targeted_review', 'quick_review', 'undetermined'}, f'advice {sid}')
        if not advice.get('reason'):
            a.error(f'advice {sid}: empty reason')
        display = a.fields(section.get('display', {}), 'learning importance advice', f'display {sid}')
        if any(not isinstance(display.get(k), str) or not display.get(k, '').strip() for k in ('learning', 'importance', 'advice')):
            a.error(f'display {sid}: empty marker')
        labels[sid] = display
    cursor = cspan[0] if cspan else None
    segments = a.array(coverage, 'segments', 'coverage')
    unique(segments, 'id', a, 'coverage segments')
    for segment in segments:
        a.fields(segment, 'id start_s end_s disposition section_id evidence reason', 'segment')
        span = a.span(segment, f'segment {segment.get("id")}')
        a.enum(segment, 'disposition', {'included', 'omitted_noninstructional', 'omitted_assignment', 'unresolved'}, 'segment')
        if span and cursor is not None:
            if abs(span[0] - cursor) > 1e-6:
                a.error(f'coverage: gap or overlap at {cursor} -> {span[0]}')
            cursor = span[1]
        if span and cspan and not cspan[0] <= span[0] < span[1] <= cspan[1]:
            a.error('coverage: segment outside processing_range')
        if segment.get('disposition') == 'included' and segment.get('section_id') not in section_ids:
            a.error('coverage: included section_id not found')
        if not segment.get('evidence') or not segment.get('reason'):
            a.error('coverage: evidence and reason required')
        if segment.get('disposition') == 'unresolved':
            a.warning(f'coverage unresolved: {segment.get("id")}')
    if cspan and cursor != cspan[1]:
        a.error('coverage: missing final interval')
    asset_paths = set()
    for asset in a.array(manifest, 'assets', 'manifest'):
        a.fields(asset, 'path source_id', 'asset')
        asset_path = local_path(root, asset.get('path'), a, 'asset')
        if asset_path:
            asset_paths.add(asset_path)
        if asset.get('source_id') not in source_ids:
            a.error('asset: unknown source_id')
        time = asset.get('requested_time_s')
        page = asset.get('page')
        if time is not None:
            if not number(time) or time < 0:
                a.error('asset: invalid requested_time_s')
            if asset.get('timestamp_basis') != 'requested_seek_time':
                a.error('asset: requested_time_s requires timestamp_basis requested_seek_time')
        elif not isinstance(page, int) or isinstance(page, bool) or page < 1:
            a.error('asset: requires valid video time or page')
    artifact = local_path(root, manifest.get('artifact_path'), a, 'artifact')
    if not artifact:
        return
    expected_hash = manifest.get('document_sha256')
    if not isinstance(expected_hash, str) or not re.fullmatch('[a-f0-9]{64}', expected_hash):
        a.error('manifest: invalid document_sha256')
    elif hashlib.sha256(artifact.read_bytes()).hexdigest() != expected_hash:
        a.warning('document hash changed: preserve manual edits; back up before revision')
    fmt = manifest.get('requested_format')
    suffixes = {'markdown': '.md', 'docx': '.docx', 'pdf': '.pdf', 'html': '.html'}
    if fmt not in suffixes or artifact.suffix.lower() != suffixes.get(fmt):
        a.error('artifact: requested_format / extension mismatch or unsupported format')
    index_path = parent / 'index.md'
    if not index_path.is_file():
        a.error('missing course index.md')
        index = ''
    else:
        index = index_path.read_text(encoding='utf-8')
    if fmt == 'markdown':
        text = artifact.read_text(encoding='utf-8')
        found = re.findall(r'^<!-- section: ([A-Za-z0-9_-]+) -->$', text, re.M)
        if set(found) != section_ids or len(found) != len(set(found)):
            a.error('body: sections and annotations must map one-to-one')
        for sid, display in labels.items():
            pattern = rf'<!-- section: {re.escape(sid)} -->\s*\n(?:<a id="{re.escape(sid)}"></a>\s*\n)?##[^\n]*\n(?P<opening>(?:\s*\n)*>[^\n]*(?:\n>[^\n]*)*)'
            match = re.search(pattern, text)
            opening = match.group('opening') if match else ''
            for value in display.values():
                if value not in opening:
                    a.error(f'body {sid}: marker missing immediately after heading')
            if not re.search(rf'^- \[[^\n]+\]\([^\n]*#{re.escape(sid)}\).*' + re.escape(display.get('learning', '')) + '.*' + re.escape(display.get('importance', '')) + '.*' + re.escape(display.get('advice', '')), index, re.M):
                a.error(f'index {sid}: missing or out-of-sync markers')
        # This is a portable inline-link subset, not a complete Markdown parser.
        for image, target in re.findall(r'(!?)\[[^\]]*\]\(([^)\s]+)\)', text):
            parsed = urlsplit(unquote(target))
            if parsed.scheme or parsed.netloc:
                continue
            dest = artifact if not parsed.path else (root / parsed.path).resolve()
            if not dest.is_file():
                a.error(f'body: missing local reference {target}')
                continue
            if image and dest not in asset_paths:
                a.error(f'body: image absent from manifest {target}')
            if parsed.fragment:
                if dest.suffix == '.md':
                    target_text = dest.read_text(encoding='utf-8')
                    anchors = set(re.findall(r'<a id="([^"]+)"', target_text))
                    if parsed.fragment not in anchors:
                        a.error(f'body: unresolved explicit anchor {target}')
                else:
                    a.warning(f'internal fragment not checked: {target}')
        if re.search(r'!\[[^\]]*\]\[|^\[[^\]]+\]:', text, re.M):
            a.warning('reference-style links require manual check; prefer inline links')
    else:
        mapping = a.read(root / 'artifact-map.json')
        a.fields(mapping, 'artifact_sha256 sections', 'artifact-map')
        if mapping.get('artifact_sha256') != hashlib.sha256(artifact.read_bytes()).hexdigest():
            a.error('artifact-map: stale artifact hash')
        rows = a.array(mapping, 'sections', 'artifact-map')
        if unique(rows, 'section_id', a, 'artifact-map') != section_ids:
            a.error('artifact-map: section IDs do not match annotations')
        for row in rows:
            a.fields(row, 'section_id locator display', 'artifact-map section')
            if row.get('display') != labels.get(row.get('section_id')):
                a.error('artifact-map: display markers differ from annotations')
        if fmt == 'docx':
            with zipfile.ZipFile(artifact) as archive:
                xml = ET.fromstring(archive.read('word/document.xml'))
                ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
                paragraphs = [''.join(p.itertext()) for p in xml.findall('.//w:p', ns)]
                for row in rows:
                    locator = row.get('locator', {})
                    n = locator.get('paragraph_index')
                    if not isinstance(n, int) or n < 0 or n >= len(paragraphs):
                        a.error('docx: invalid paragraph locator')
                    elif any(value not in '\n'.join(paragraphs[n + 1:n + 4]) for value in row.get('display', {}).values()):
                        a.error('docx: marker missing after heading')
        elif fmt == 'pdf' and not artifact.read_bytes().startswith(b'%PDF-'):
            a.error('artifact: not a PDF')
        a.warning('non-Markdown output: mapping/package check only; actual rendering, images, formulas and index need visual review')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('lecture_dir', type=Path)
    p.add_argument('--report', required=True, type=Path)
    args = p.parse_args()
    # Never let a diagnostic output replace course inputs or other existing artifacts.
    if args.report.exists():
        print('error: report exists; choose a new report path', file=sys.stderr)
        return 1
    report = validate(args.lecture_dir)
    try:
        with args.report.open('x', encoding='utf-8') as out:
            json.dump(report, out, ensure_ascii=False, indent=2, allow_nan=False)
            out.write('\n')
    except OSError as exc:
        print(f'error: {exc}', file=sys.stderr)
        return 1
    print(f'{len(report["errors"])} errors, {len(report["warnings"])} warnings')
    return int(bool(report['errors']))


if __name__ == '__main__':
    sys.exit(main())
