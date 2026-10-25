"""Check scene coverage, deterministic MIDI timing and the owner's language hold."""
import copy
from pathlib import Path
import struct
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import dub
import production
import scene_score

class SceneScoreTests(unittest.TestCase):
    def setUp(self):
        self.plan=dub.load(dub.ROOT/'episodes/save-the-moon/music-v002.json')
        self.registry=dub.load(dub.ROOT/self.plan['registry'])

    def test_score_has_full_coverage_and_bounded_deterministic_notes(self):
        scene_score.validate_plan(self.plan,self.registry)
        notes=scene_score.arrange(self.plan,self.registry)
        self.assertEqual(notes,scene_score.arrange(self.plan,self.registry))
        self.assertGreater(len(notes),100)
        self.assertTrue(all(0<=n['start_s']<n['end_s']<=self.plan['duration_s'] for n in notes))
        self.assertGreaterEqual(len({n['instrument'] for n in notes}),8)
        data=scene_score.midi_bytes(self.plan,self.registry,notes)
        self.assertEqual(data[:4],b'MThd')
        fmt,tracks,ppq=struct.unpack('>HHH',data[8:14])
        self.assertEqual((fmt,tracks,ppq),(1,1+len(self.registry['instruments']),480))
        self.assertEqual(data.count(b'MTrk'),tracks)

    def test_gap_or_overlap_cannot_silently_change_music_timing(self):
        for shift in (-.1,.1):
            bad=copy.deepcopy(self.plan);bad['cues'][1]['start_s']+=shift
            with self.assertRaisesRegex(ValueError,'gaps/overlaps'):
                scene_score.validate_plan(bad,self.registry)

    def test_midi_variable_delta_lengths(self):
        self.assertEqual(scene_score.vlq(0),b'\x00')
        self.assertEqual(scene_score.vlq(127),b'\x7f')
        self.assertEqual(scene_score.vlq(128),b'\x81\x00')
        self.assertEqual(scene_score.vlq(16383),b'\xff\x7f')
        for value in (-1,0x10000000,1.5):
            with self.assertRaises(ValueError):scene_score.vlq(value)

    def test_owner_language_hold_blocks_all_language_production(self):
        ep={'languages':['en','zh','ms'],'production_languages':['en']}
        self.assertEqual(production.allowed_languages(ep,'all'),['en'])
        for lang in ('zh','ms'):
            with self.assertRaisesRegex(ValueError,'on hold'):production.allowed_languages(ep,lang)
        self.assertEqual(production.allowed_languages({'languages':['en','zh']},'all'),['en','zh'])
