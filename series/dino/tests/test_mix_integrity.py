"""An encoded mix must retain its known speech, not merely pass a transcript guess."""
from pathlib import Path
import importlib.util
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from review_mix_integrity import similarity


class MixIntegrityTests(unittest.TestCase):
    @unittest.skipUnless(importlib.util.find_spec('numpy'),'Optional transcription/QA environment')
    def test_level_codec_noise_and_small_alignment_preserve_content(self):
        import numpy as np
        rng=np.random.default_rng(42);x=rng.normal(size=4000)
        y=np.roll(x,3)*2+rng.normal(size=4000)*.01
        result=similarity(x,y)
        self.assertGreater(result['correlation'],.99)
        self.assertEqual(abs(result['alignment_ms']),3/8)
        self.assertAlmostEqual(result['level_ratio'],2,places=2)
        self.assertLess(similarity(x,rng.normal(size=4000))['correlation'],.1)
        self.assertLess(similarity(x,np.zeros(4000))['correlation'],.95)


if __name__=='__main__':unittest.main()
