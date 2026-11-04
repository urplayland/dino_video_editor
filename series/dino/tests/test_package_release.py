"""Protect originals and existing file-by-file releases from packaging mistakes."""
import copy
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import dub
import package_release


class ReleaseTests(unittest.TestCase):
    def test_resume_and_changed_source_never_overwrite_release(self):
        with tempfile.TemporaryDirectory() as tmp,patch.object(dub,'ROOT',Path(tmp)):
            root=Path(tmp);(root/'source.txt').write_text('preserve original')
            manifest={'schema_version':1,'review_status':'fixture','output_dir':'episodes/test/exports/release-v001',
                      'files':[{'source':'source.txt','destination':'en/script.txt'}]}
            result=package_release.export(manifest)
            out=root/manifest['output_dir']/'en/script.txt';before=out.stat().st_mtime_ns
            self.assertFalse(result['archive_created'])
            self.assertEqual(package_release.export(manifest),result)
            self.assertEqual(out.stat().st_mtime_ns,before)
            (root/'source.txt').write_text('new source revision')
            with self.assertRaisesRegex(ValueError,'new release version'):
                package_release.export(manifest)
            self.assertEqual(out.read_text(),'preserve original')

    def test_path_escape_and_duplicate_destinations_rejected_before_writes(self):
        with tempfile.TemporaryDirectory() as tmp,patch.object(dub,'ROOT',Path(tmp)):
            root=Path(tmp);(root/'source.txt').write_text('source')
            manifest={'schema_version':1,'review_status':'fixture','output_dir':'episodes/test/exports/release-v001',
                      'files':[{'source':'source.txt','destination':'../escape.txt'}]}
            with self.assertRaises(ValueError):package_release.export(manifest)
            manifest['files'][0]['destination']='en/script.txt'
            manifest['files'].append(copy.deepcopy(manifest['files'][0]))
            with self.assertRaises(ValueError):package_release.export(manifest)
            self.assertFalse((root/manifest['output_dir']).exists())


if __name__=='__main__':unittest.main()
