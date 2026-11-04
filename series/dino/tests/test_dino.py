"""Regression checks for workspace creation and portable media integrity reports."""
import argparse
from contextlib import redirect_stdout
import importlib.util
import io
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location('dino', Path(__file__).resolve().parents[1] / 'tools/dino.py')
dino = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(dino)


class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve() / 'workspace'
        shutil.copytree(dino.ROOT / 'templates', self.root / 'templates')
        self.patch = patch.object(dino, 'ROOT', self.root)
        self.patch.start()
        self.addCleanup(self.patch.stop)
        self.stdout = redirect_stdout(io.StringIO())
        self.stdout.__enter__()
        self.addCleanup(self.stdout.__exit__, None, None, None)
        self.args = argparse.Namespace(slug='test-episode', title='Test Episode')
        dino.init_episode(self.args)
        self.source = self.root / 'episodes/test-episode/media/originals/source.bin'
        self.source.write_bytes(b'original fixture')

    def report(self):
        with patch.object(dino, 'find_tool', return_value=None):
            dino.inventory(self.args)
        reports = self.root / 'episodes/test-episode/reports'
        return sorted(reports.glob('*.json'))[-1]

    def test_creation_and_overwrite_protection(self):
        with self.assertRaises(ValueError):
            dino.init_episode(self.args)
        self.assertEqual(self.source.read_bytes(), b'original fixture')
        for slug in ('../escape', 'UPPER', 'two--words', ''):
            with self.assertRaises(ValueError):
                dino.episode_path(slug)

    def test_report_survives_workspace_relocation(self):
        report = self.report()
        relocated = self.root.parent / 'relocated'
        shutil.copytree(self.root, relocated)
        moved_report = relocated / report.relative_to(self.root)
        with patch.object(dino, 'ROOT', relocated):
            dino.verify(argparse.Namespace(slug=self.args.slug, report=str(moved_report)))

    def test_verification_detects_changes_and_missing_files(self):
        report = self.report()
        args = argparse.Namespace(slug=self.args.slug, report=str(report))
        self.source.write_bytes(b'changed fixture')
        with self.assertRaisesRegex(ValueError, 'Changed'):
            dino.verify(args)
        self.source.unlink()
        with self.assertRaisesRegex(ValueError, 'Missing'):
            dino.verify(args)

    def test_reports_are_distinct_and_source_unchanged(self):
        first, second = self.report(), self.report()
        self.assertNotEqual(first, second)
        self.assertEqual(self.source.read_bytes(), b'original fixture')

    def test_rejects_symlinks_and_escaping_report_paths(self):
        report = self.report()
        document = json.loads(report.read_text())
        document['files'][0]['path'] = '../outside.bin'
        report.write_text(json.dumps(document))
        with self.assertRaises(ValueError):
            dino.verify(argparse.Namespace(slug=self.args.slug, report=str(report)))
        self.source.with_name('linked.bin').symlink_to(self.source)
        with self.assertRaises(ValueError):
            self.report()


if __name__ == '__main__':
    unittest.main()
