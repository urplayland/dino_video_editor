"""Verify phrase automation and final-audio bounds used by offline reviews."""
import sys
from pathlib import Path
import hashlib
import io
import json
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import wave
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from review_audio import active_bounds, duck_envelope, review_options, take_pcm
import dub


class ReviewAudioTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('ffmpeg'), 'FFmpeg required for actual take loading')
    def test_retake_requires_matching_transcript_voice_and_file_hash(self):
        voices=dub.load(dub.ROOT/'config/voices.json')
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); wav=root/'take.wav'
            samples=(np.sin(np.arange(12000)*2*np.pi*220/24000)*3000).astype('<i2')
            with wave.open(str(wav),'wb') as stream:
                stream.setparams((1,2,24000,0,'NONE','not compressed'));stream.writeframes(samples.tobytes())
            cue={'text':'Synthetic verification fixture.'}
            identity=dict(model=voices['characters']['bunny']['model'],voice_version='v001',request=dub.payload(cue,voices['characters']['bunny'],'en'))
            digest=hashlib.sha256(wav.read_bytes()).hexdigest()
            record=dict(identity,sha256=digest,character='bunny',language='en',fingerprint=hashlib.sha256(json.dumps(identity,sort_keys=True,ensure_ascii=False).encode()).hexdigest())
            wav.with_suffix('.json').write_text(json.dumps(record))
            report=root/'check.json';check=dict(status='passed_automated',sha256=digest,expected_text=cue['text']);report.write_text(json.dumps(check))
            spec=dict(path='take.wav',sha256=digest,character='bunny',verification_report='check.json')
            with patch.object(dub,'ROOT',root):
                self.assertGreater(len(take_pcm(spec,cue['text'],voices)),1000)
                with self.assertRaises(ValueError):take_pcm(spec,cue['text'],voices,language='ms')
                with self.assertRaises(ValueError):take_pcm(spec,'Changed transcript',voices)
                with self.assertRaises(ValueError):take_pcm(spec,cue['text'],voices,nonverbal=True)
                record['request']['generationConfig']['speechConfig']['voiceConfig']['voice']='Puck'
                wav.with_suffix('.json').write_text(json.dumps(record))
                with self.assertRaises(ValueError):take_pcm(spec,cue['text'],voices)
                with wav.open('ab') as stream:stream.write(b'changed')
                with self.assertRaises(ValueError):take_pcm(spec,cue['text'],voices)

    def test_finalization_rejects_changed_approved_audio_before_encoding(self):
        import finalize_approved
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);source=root/'approved.mp4';source.write_bytes(b'Changed approved source fixture')
            config=root/'final.json';config.write_text(json.dumps(dict(schema_version=1,owner_approval='Test fixture approval',approved_review=dict(path='approved.mp4',sha256='0'*64))))
            with patch.object(dub,'ROOT',root):
                with self.assertRaisesRegex(ValueError,'checksum changed'):finalize_approved.finalize(config)

    @unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'), 'FFmpeg required')
    def test_direct_review_master_keeps_audio_checks_without_picture_copy(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);source=root/'picture.mp4';audio=root/'tone.wav';movie=root/'review.mp4'
            dub.run(['ffmpeg','-v','error','-f','lavfi','-i','color=c=blue:s=64x64:r=24:d=2','-an','-c:v','libx264','-threads','1',str(source)])
            dub.run(['ffmpeg','-v','error','-f','lavfi','-i','sine=frequency=440:sample_rate=48000:duration=2','-ac','2',str(audio)])
            original_hash=hashlib.sha256(source.read_bytes()).hexdigest()
            m=dict(kind='dubbing_production',source_start_s=0,duration_s=2,mix=dict(integrated_lufs=-18,true_peak_db=-2))
            info,_,measurement,picture_hash=dub.master_audio(m,source,audio,movie,video_filter='scale=32:32',video_options=['-preset','veryfast','-crf','28','-threads','1'])
            video=next(x for x in info['streams'] if x['codec_type']=='video')
            self.assertEqual((video['width'],video['height'],int(video['nb_frames'])),(32,32,48))
            self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(),original_hash)
            self.assertEqual(picture_hash,dub.video_hash(source))
            self.assertNotEqual(dub.video_hash(movie),picture_hash)
            self.assertLess(float(measurement['input_tp']),-.8)

    def test_versioned_compact_review_keeps_old_default(self):
        self.assertEqual(review_options({}), ('v002',720,23,'fast'))
        self.assertEqual(review_options({'output_version':'v003','review_video':{'width':540,'crf':28,'preset':'veryfast'}}),('v003',540,28,'veryfast'))
        for bad in ({'output_version':'../v003'}, {'review_video':{'width':541}}, {'review_video':{'crf':50}}):
            with self.assertRaises(ValueError): review_options(bad)

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
