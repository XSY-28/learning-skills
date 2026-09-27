import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[2] / 'skills/course-to-notes/scripts/parse_captions.py'


class Captions(unittest.TestCase):
    def run_cli(self, content, extension='.srt'):
        with tempfile.TemporaryDirectory() as tmp:
            source, out = Path(tmp) / ('input' + extension), Path(tmp) / 'out.json'
            if content is not None:
                source.write_text(content, encoding='utf-8')
            p = subprocess.run([sys.executable, str(SCRIPT), str(source), '--output', str(out), '--source-id', 'fixture'], capture_output=True, text=True)
            return p, json.loads(out.read_text()) if out.exists() else None

    def test_repeated_sentences_preserved(self):
        p, data = self.run_cli('1\n00:00:01,000 --> 00:00:02,000\n这个条件非常重要。\n\n2\n00:00:03,000 --> 00:00:04,000\n这个条件非常重要。\n')
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(data['source_id'], 'fixture')
        self.assertEqual([(x['start_s'], x['end_s'], x['text']) for x in data['cues']], [(1., 2., '这个条件非常重要。'), (3., 4., '这个条件非常重要。')])

    def test_vtt_metadata_overlap_and_multiline(self):
        p, d = self.run_cli('\ufeffWEBVTT\nKind: captions\n\nNOTE ignore\ncomment\n\nSTYLE\n::cue {color:red}\n\nREGION\nid:r1\n\nfirst\n00:01.123 --> 00:03.456 align:start position:0%\n<v Teacher>hello\nworld\n\n00:02.000 --> 00:04.000\nhello\n', '.vtt')
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(len(d['cues']), 2)
        self.assertEqual(d['cues'][0]['text'], '<v Teacher>hello\nworld')
        self.assertEqual(d['cues'][0]['start_s'], 1.123)

    def test_bad_times_report_line(self):
        for timestamp in ['00:99:01,000', '-1:00:00,000', 'NaN', '00:00:03,000']:
            with self.subTest(timestamp=timestamp):
                p, d = self.run_cli(f'1\n{timestamp} --> 00:00:02,000\ntext\n')
                self.assertNotEqual(p.returncode, 0)
                self.assertIn('line 2', p.stderr)
                self.assertIsNone(d)

    def test_missing_file(self):
        p, d = self.run_cli(None)
        self.assertNotEqual(p.returncode, 0)
        self.assertIsNone(d)

    def test_bad_header_empty_and_unsupported(self):
        for body, ext in [('00:01.000 --> 00:02.000\nhi\n', '.vtt'), ('WEBVTT\n', '.vtt'), ('{}', '.json'), ('1\n00:00:01,000 --> 00:00:02,000\n', '.srt')]:
            p, _ = self.run_cli(body, ext)
            self.assertNotEqual(p.returncode, 0)

    def test_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            source, dest = Path(tmp) / 'in.srt', Path(tmp) / 'out.json'
            source.write_text('1\n00:00:01,000 --> 00:00:02,000\nhi\n')
            dest.write_text('manual')
            p = subprocess.run([sys.executable, str(SCRIPT), str(source), '--output', str(dest), '--source-id', 'test'], capture_output=True)
            self.assertNotEqual(p.returncode, 0)
            self.assertEqual(dest.read_text(), 'manual')
