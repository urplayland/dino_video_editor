"""Recover a completed canonical first take without another provider request."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import dub
import revoice


class RetakeRecoveryTests(unittest.TestCase):
    def test_canonical_first_take_is_recoverable_and_checksum_protected(self):
        with tempfile.TemporaryDirectory() as tmp,patch.object(dub,'ROOT',Path(tmp)):
            folder=Path(tmp)/'episode/en';folder.mkdir(parents=True)
            audio=folder/'line.wav';audio.write_bytes(b'opaque test fixture')
            record={'fingerprint':'expected','output':'episode/en/line.wav',
                    'sha256':hashlib.sha256(audio.read_bytes()).hexdigest(),'created_at':'2026-11-01T00:00:00Z'}
            (folder/'line.json').write_text(json.dumps(record))
            self.assertEqual(revoice.matching_take(folder,{'id':'line'},'expected'),record)
            self.assertIsNone(revoice.matching_take(folder,{'id':'line'},'different request'))
            audio.write_bytes(b'tampered')
            self.assertIsNone(revoice.matching_take(folder,{'id':'line'},'expected'))


if __name__=='__main__':unittest.main()
