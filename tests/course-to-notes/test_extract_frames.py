import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[2] / 'skills/course-to-notes/scripts/extract_frames.py'


class Frames(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):
            raise unittest.SkipTest('ffmpeg/ffprobe unavailable: extraction NOT verified')
        cls.tmp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.tmp.name)
        cls.video = cls.root / 'red then blue.mp4'
        subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-f', 'lavfi', '-i', 'color=red:s=64x48:d=1:r=10', '-f', 'lavfi', '-i', 'color=blue:s=64x48:d=1:r=10', '-filter_complex', '[0:v][1:v]concat=n=2:v=1:a=0', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', str(cls.video)], check=True)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def cli(self, times, out, env=None, video=None):
        times_path = self.root / 'times.json'
        times_path.write_text(json.dumps(times))
        return subprocess.run([sys.executable, str(SCRIPT), str(video or self.video), '--times', str(times_path), '--out-dir', str(out), '--source-id', 'color-fixture'], capture_output=True, text=True, env=env)

    def test_color_time_and_no_overwrite(self):
        out = self.root / 'valid'
        p = self.cli([0.2, 1.2], out)
        self.assertEqual(p.returncode, 0, p.stderr)
        info = json.loads((out / 'frames.json').read_text())
        self.assertEqual(info['timestamp_basis'], 'requested_seek_time')
        self.assertEqual([f['requested_time_s'] for f in info['frames']], [0.2, 1.2])
        for name, channel in [('frame-0001.png', 0), ('frame-0002.png', 2)]:
            raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-i', str(out / name), '-vf', 'scale=1:1', '-pix_fmt', 'rgb24', '-f', 'rawvideo', '-'])
            self.assertGreater(raw[channel], 200)
            self.assertTrue(all(raw[i] < 40 for i in range(3) if i != channel))
        before = (out / 'frame-0001.png').read_bytes()
        self.assertNotEqual(self.cli([0.3], out).returncode, 0)
        self.assertEqual(before, (out / 'frame-0001.png').read_bytes())

    def test_invalid_times(self):
        for times in [[], [-1], [2], [float('nan')], [float('inf')], ['1'], [True], {'time': 1}]:
            with self.subTest(times=times):
                p = self.cli(times, self.root / 'invalid')
                self.assertNotEqual(p.returncode, 0)

    def test_missing_tools_and_input(self):
        p = self.cli([0.1], self.root / 'missing-tools', {**os.environ, 'PATH': ''})
        self.assertNotEqual(p.returncode, 0)
        self.assertIn('ffmpeg and ffprobe', p.stderr)
        self.assertNotEqual(self.cli([0.1], self.root / 'missing-video', video=self.root / 'missing.mp4').returncode, 0)
