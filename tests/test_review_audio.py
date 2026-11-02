"""Verify phrase automation and final-audio bounds used by offline reviews."""
import sys
from pathlib import Path
import unittest
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from review_audio import active_bounds, duck_envelope


class ReviewAudioTests(unittest.TestCase):
    def test_phrase_reduction_and_overlap_do_not_double_duck(self):
        env = duck_envelope(4000, [(1,2),(1.5,2.5)], 8, rate=1000)
        self.assertAlmostEqual(float(env[1700]), 10**(-8/20), places=6)
        self.assertEqual(env[0], 1)
        self.assertEqual(env[-1], 1)
        self.assertTrue(np.all(np.diff(env[850:1000]) <= 0))
        self.assertTrue(np.all(np.diff(env[2500:2800]) >= 0))
        with self.assertRaises(ValueError): duck_envelope(4000, [(3,5)], 8, rate=1000)

    def test_final_audio_edges_retain_quiet_consonants(self):
        pcm = np.zeros((3000,2),dtype='float32')
        pcm[1000:1100]=.0004  # quiet leading consonant must not be lost
        pcm[1100:2000]=.1
        self.assertEqual(active_bounds(pcm,1000),(.975,2.045))
        with self.assertRaises(ValueError): active_bounds(np.zeros((1000,2)))

    def test_english_plan_is_separate_and_uses_all_existing_cues(self):
        import json
        root=Path(__file__).resolve().parents[1]
        cfg=json.loads((root/'episodes/rainbow-bridge/review-en-v002.json').read_text())
        baseline=json.loads((root/cfg['episode']).read_text())
        self.assertEqual(cfg['language'],'en')
        self.assertEqual(set(cfg['dialogue_edits']),{c['id'] for c in baseline['dialogue']})
        self.assertIn('v002',cfg['delivery_dir'])
        self.assertNotEqual(cfg['sfx_plan'],'episodes/rainbow-bridge/sfx-cues.json')


if __name__=='__main__': unittest.main()
