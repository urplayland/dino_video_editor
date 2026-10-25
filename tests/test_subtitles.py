"""Check subtitle timing, readable wrapping, and safe-area rendering."""
from pathlib import Path
import sys
import json
import copy
import tempfile
from types import SimpleNamespace
from unittest.mock import patch
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import dub
import production
import subtitles
import brand_video

class FixedFont:
    def getlength(self,text):return len(text)*10

class SubtitleTests(unittest.TestCase):
    def test_timestamps_include_carry_and_frame_independent_precision(self):
        self.assertEqual(subtitles.stamp(59.9996),'00:01:00,000')
        self.assertEqual(subtitles.stamp(32.15,True),'0:00:32.15')
        self.assertEqual(subtitles.stamp(3600.01,True),'1:00:00.01')

    def test_lines_do_not_overflow_or_accept_ass_controls(self):
        self.assertEqual(subtitles.wrap('Moon! Can you hear me?',FixedFont(),150),['Moon! Can you','hear me?'])
        for text in ('{\\pos(0,0)}hi','a\\Nb','one\ntwo','one two three four five six seven eight'):
            with self.assertRaises(ValueError):subtitles.wrap(text,FixedFont(),70)

    def test_chinese_wrap_preserves_text_without_inserting_spaces(self):
        text='小迪诺，你为什么想救月亮？'
        lines=subtitles.wrap(text,FixedFont(),80)
        self.assertEqual(''.join(lines),text)
        self.assertEqual(len(lines),2)

    def test_overlay_layout_preserves_full_frame_and_subtitle_timing(self):
        manifest=dub.load(dub.ROOT/'episodes/save-the-moon/branding.en.json')
        cfg=dub.load(dub.relative(manifest['subtitles']))
        episode=dub.load(dub.ROOT/'episodes/save-the-moon/production.json')
        # A source-only checkout has no fonts, rendered ASS, reports or media.
        # Fake font metrics keep this contract test independent of Pillow/assets.
        fake_pil=SimpleNamespace(ImageFont=SimpleNamespace(truetype=lambda *a,**kw:FixedFont()))
        with tempfile.TemporaryDirectory() as tmp, patch.object(dub,'ROOT',Path(tmp)):
            font=dub.relative(cfg['font_path']);font.parent.mkdir(parents=True);font.write_bytes(b'font fixture')
            settings=dub.relative(manifest['subtitles']);settings.parent.mkdir(parents=True);settings.write_text(json.dumps(cfg))
            with patch.dict(sys.modules,{'PIL':fake_pil}):
                report=subtitles.generate(episode,cfg)
            graph=brand_video.caption_filter(manifest)
            self.assertNotIn('scale=',graph)
            self.assertNotIn('pad=',graph)
            self.assertIn('ass=filename=',graph)
            self.assertEqual(cfg['packaged_offset_s'],2)
            selected=production.language_manifest(episode,'en')['dialogue']
            self.assertEqual([x['id'] for x in report['cues']],[x['id'] for x in selected])
            self.assertNotIn('dino-call',[x['id'] for x in report['cues']])
            for cue in report['cues']:self.assertLessEqual(len(cue['lines']),2)
            first=report['cues'][0]
            self.assertIn(subtitles.stamp(first['start_s']+2),dub.relative(cfg['packaged_srt_path']).read_text())

    def test_additional_traditional_forms_do_not_hide_word_changes(self):
        self.assertEqual(production.normalize_words('誰敢闖入雲霧山'),production.normalize_words('谁敢闯入云雾山'))
        self.assertEqual(production.normalize_words('去哪兒為什麼'),production.normalize_words('去哪儿为什么'))
        self.assertNotEqual(production.normalize_words('谁敢'),production.normalize_words('你敢'))

    def test_long_malay_comparison_keeps_frequent_letters(self):
        expected='Alamak! Bulan pergi ke mana? '*12+'Kamukah itu? '+'Mari kita bantu dia bersama-sama. '*12
        heard=expected.replace('Kamukah','Kamuka')
        self.assertGreater(production.transcript_similarity(expected,heard),.99)
        self.assertLess(production.transcript_similarity(expected,'different speech'),.1)

    def test_verified_spoken_particle_preserves_original_tts_request(self):
        cue={'text':'月亮得救了！','spoken_text':'月亮得救啦！','spoken_text_evidence':['independent-ASR']}
        voices=dub.load(dub.ROOT/'config/voices.json')
        plain={'text':cue['text']}
        requested=dub.payload(cue,voices['characters']['dino'],'zh')
        self.assertEqual(requested,dub.payload(plain,voices['characters']['dino'],'zh'))
        self.assertEqual(requested['contents'][0]['parts'][0]['text'],'月亮得救了！')

    def test_cloud_override_is_preserved_by_refitting(self):
        from test_dub import wav_bytes
        actual=dub.load(dub.ROOT/'episodes/save-the-moon/production.json')
        cue=copy.deepcopy(next(c for c in actual['dialogue'] if c['id']=='cloud-challenge'))
        self.assertEqual(cue['timing_overrides']['en']['start_s'],32.15)
        cue['audio']={'en':{}}
        episode={'duration_s':70.927018,'output_dir':'episodes/test/media/derived/full',
                 'report_dir':'episodes/test/reports/full','dialogue':[cue]}
        with tempfile.TemporaryDirectory() as tmp, patch.object(dub,'ROOT',Path(tmp)):
            audio=dub.relative(episode['output_dir'])/'en/cloud-challenge.wav'
            audio.parent.mkdir(parents=True);audio.write_bytes(wav_bytes())
            production.fit_timeline(episode,'en')
        self.assertAlmostEqual(cue['audio']['en']['start_s'],32.15,places=3)
        self.assertEqual(cue['start_s'],31.5)
