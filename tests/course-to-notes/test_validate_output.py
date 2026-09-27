import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'skills/course-to-notes/scripts'))
from validate_output import validate
from fixture_factory import make_project, write_json


class Output(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.root = make_project(self.base)

    def tearDown(self):
        self.tmp.cleanup()

    def change(self, file, mutate):
        p = self.root / file
        data = json.loads(p.read_text())
        mutate(data)
        write_json(p, data)

    def errors(self):
        return '\n'.join(validate(self.root)['errors'])

    def test_empty_profile_unknown_is_valid(self):
        self.assertEqual(validate(self.root), {'schema_version': 1, 'errors': [], 'warnings': []})

    def test_gap(self):
        self.change('coverage.json', lambda d: d['segments'][0].update(start_s=1))
        self.assertIn('gap or overlap', self.errors())

    def test_negative_time(self):
        self.change('coverage.json', lambda d: d['segments'][0].update(start_s=-1))
        self.assertIn('finite 0 <=', self.errors())

    def test_wrong_section(self):
        self.change('coverage.json', lambda d: d['segments'][0].update(section_id='missing'))
        self.assertIn('section_id not found', self.errors())

    def test_missing_image(self):
        self.change('manifest.json', lambda d: d['assets'].append({'path': 'missing.png', 'source_id': 'v1', 'requested_time_s': 1, 'timestamp_basis': 'requested_seek_time'}))
        self.assertIn('missing file missing.png', self.errors())

    def test_studied_requires_evidence(self):
        self.change('section-annotations.json', lambda d: d['sections'][0]['concepts'][0].update(learning_status='studied'))
        self.assertIn('needs evidence', self.errors())

    def test_nonexistent_evidence(self):
        self.change('section-annotations.json', lambda d: d['sections'][0]['concepts'][0].update(evidence_ids=['ghost']))
        self.assertIn('nonexistent evidence', self.errors())

    def test_duplicate_section(self):
        self.change('section-annotations.json', lambda d: d['sections'].append(d['sections'][0].copy()))
        self.assertIn('duplicate section_id', self.errors())

    def test_missing_importance_reason(self):
        self.change('section-annotations.json', lambda d: d['sections'][0]['importance'].update(reasons=[]))
        self.assertIn('missing reasons', self.errors())

    def test_stale_profile_and_unreadable(self):
        self.change('../learner-profile.json', lambda d: d.update(revision=1, evidence_records=[{'id': 'e1', 'source_ref': 'synthetic://missing', 'observed_at': None, 'domain': 'math', 'concept': 'definition', 'depth': 'definition', 'assertion': 'asked', 'origin': 'generated_material', 'readable': False}]))
        report = validate(self.root)
        self.assertEqual(report['errors'], [])
        self.assertIn('stale profile_revision', '\n'.join(report['warnings']))
        self.assertIn('cannot be reread', '\n'.join(report['warnings']))

    def test_mastery_requires_matching_origin(self):
        self.change('section-annotations.json', lambda d: d['sections'][0]['concepts'][0].update(mastery_basis='self_reported'))
        self.assertIn('mastery_basis lacks', self.errors())

    def test_unknown_enum(self):
        self.change('section-annotations.json', lambda d: d['sections'][0]['concepts'][0].update(learning_status='mastered'))
        self.assertIn('invalid learning_status', self.errors())

    def test_missing_opening_marker(self):
        p = self.root / 'notes.md'
        p.write_text(p.read_text().replace('> 重点：本段核心定义。', ''))
        self.assertIn('marker missing immediately', self.errors())

    def test_index_out_of_sync(self):
        (self.base / 'index.md').write_text('stale')
        self.assertIn('out-of-sync', self.errors())

    def test_internal_reference(self):
        p = self.root / 'notes.md'
        p.write_text(p.read_text() + '\n[不存在](#ghost)\n')
        self.assertIn('unresolved explicit anchor', self.errors())

    def test_manual_edit_hash_warning_preserves_bytes(self):
        p = self.root / 'notes.md'
        p.write_text(p.read_text() + '\n用户批注：保留。\n')
        before = p.read_bytes()
        report = validate(self.root)
        self.assertEqual(report['errors'], [])
        self.assertIn('hash changed', '\n'.join(report['warnings']))
        self.assertEqual(p.read_bytes(), before)

    def test_unresolved_warning(self):
        self.change('coverage.json', lambda d: d['segments'][0].update(disposition='unresolved'))
        self.assertIn('coverage unresolved', '\n'.join(validate(self.root)['warnings']))

    def test_invalid_types_and_nonfinite_json(self):
        self.change('coverage.json', lambda d: d.update(segments='bad'))
        self.assertIn('expected array', self.errors())
        (self.root / 'coverage.json').write_text('{"schema_version":1,"processing_range":{"start_s":NaN,"end_s":10},"segments":[]}')
        self.assertIn('nonfinite JSON', self.errors())

    def test_cli_nonzero_report_and_no_overwrite(self):
        self.change('coverage.json', lambda d: d['segments'][0].update(start_s=-1))
        script = Path(__file__).resolve().parents[2] / 'skills/course-to-notes/scripts/validate_output.py'
        out = self.base / 'report.json'
        p = subprocess.run([sys.executable, str(script), str(self.root), '--report', str(out)], capture_output=True)
        self.assertNotEqual(p.returncode, 0)
        self.assertTrue(json.loads(out.read_text())['errors'])
        original = (self.root / 'notes.md').read_bytes()
        p = subprocess.run([sys.executable, str(script), str(self.root), '--report', str(self.root / 'notes.md')], capture_output=True)
        self.assertNotEqual(p.returncode, 0)
        self.assertEqual((self.root / 'notes.md').read_bytes(), original)
