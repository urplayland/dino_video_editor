import hashlib,json
from pathlib import Path
import sys,tempfile,unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from media_restore import restore

class MediaRestoreTests(unittest.TestCase):
    def fixture(self,base):
        p=base/'manifest.json';p.write_text(json.dumps(dict(schema_version=1,files=[dict(path='episodes/test/media/a.wav',drive_file_id='observed-drive-id',bytes=4,sha256=hashlib.sha256(b'good').hexdigest())])));return p
    def test_verified_install_and_existing_file_never_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);m=self.fixture(root);dest=root/'fresh'
            def download(args,**kwargs):Path(args[-1]).write_bytes(b'good')
            with patch('media_restore.shutil.which',return_value='rclone'),patch('media_restore.subprocess.run',side_effect=download) as run:
                self.assertEqual(restore(m,dest)['restored'],1)
                self.assertEqual(restore(m,dest)['restored'],0);self.assertEqual(run.call_count,1)
                (dest/'episodes/test/media/a.wav').write_bytes(b'bad!')
                with self.assertRaisesRegex(ValueError,'refusing overwrite'):restore(m,dest)
    def test_corrupt_download_is_not_installed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);m=self.fixture(root)
            with patch('media_restore.shutil.which',return_value='rclone'),patch('media_restore.subprocess.run',side_effect=lambda args,**kw:Path(args[-1]).write_bytes(b'evil')):
                with self.assertRaisesRegex(ValueError,'checksum'):restore(m,root/'fresh')
            self.assertFalse((root/'fresh/episodes/test/media/a.wav').exists())
    def test_path_escape_rejected_before_network(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);m=self.fixture(root);d=json.loads(m.read_text());d['files'][0]['path']='../outside';m.write_text(json.dumps(d))
            with patch('media_restore.subprocess.run') as run:
                with self.assertRaises(ValueError):restore(m,root/'fresh')
                run.assert_not_called()
if __name__=='__main__':unittest.main()
