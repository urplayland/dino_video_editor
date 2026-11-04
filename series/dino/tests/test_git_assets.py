import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from check_git_assets import validate,ROOT

class GitAssetTests(unittest.TestCase):
    def fixture(self,root):
        target=root/'library/media/test.wav';target.parent.mkdir(parents=True);target.write_bytes(b'original')
        cfg=dict(schema_version=1,max_file_bytes=100,max_total_bytes=100,files=[dict(path='library/media/test.wav',sha256=hashlib.sha256(b'original').hexdigest())])
        manifest=root/'policy.json';manifest.write_text(json.dumps(cfg));return target,manifest,cfg

    def test_pinned_bytes_are_verified_and_changed_asset_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);target,manifest,cfg=self.fixture(root)
            self.assertEqual(validate(manifest,root)['files'],1)
            target.write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError,'changed'):validate(manifest,root)

    def test_paths_and_symlinks_cannot_escape_or_include_credentials(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);target,manifest,cfg=self.fixture(root)
            for bad in ['../secret.wav','.env','library/media/../../.env']:
                cfg['files'][0]['path']=bad;manifest.write_text(json.dumps(cfg))
                with self.assertRaises(ValueError):validate(manifest,root)
            cfg['files'][0]['path']='library/media/test.wav';manifest.write_text(json.dumps(cfg))
            target.unlink();target.symlink_to(root/'elsewhere')
            with self.assertRaisesRegex(ValueError,'symlinks'):validate(manifest,root)

    def test_real_git_ignore_rules_allow_only_pinned_media(self):
        for name,ignored in [('library/media/branding/flh-v001/logo.png',False),
                             ('episodes/rainbow-bridge/media/derived/ending-v002/zh/end-card.mp4',False),
                             ('library/media/not-curated.wav',True),
                             ('episodes/rainbow-bridge/media/originals/example.mp4',True),
                             ('episodes/rainbow-bridge/exports/example.mp4',True),
                             ('.env',True),('work/private.json',True)]:
            result=subprocess.run(['git','check-ignore','--no-index',name],cwd=ROOT,capture_output=True)
            self.assertEqual(result.returncode==0,ignored,name)

if __name__=='__main__':unittest.main()
