"""Full-length manifest and source-preservation checks."""
import copy
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import dub
import production
from score import compose
from test_dub import wav_bytes


class ProductionTests(unittest.TestCase):
    def setUp(self):
        self.episode=dub.load(dub.ROOT/'episodes/save-the-moon/production.json')
        self.voices=dub.load(dub.ROOT/'config/voices.json')

    def test_schema_rejects_missing_translations_and_wrong_types(self):
        bad=copy.deepcopy(self.episode)
        del bad['dialogue'][0]['text']['ms']
        with self.assertRaisesRegex(ValueError,'schema'):
            production.validate_schema(bad,'production')
        bad=copy.deepcopy(self.voices)
        bad['characters']['moon']['reference_wavs']='not a list'
        with self.assertRaisesRegex(ValueError,'schema'):
            production.validate_schema(bad,'voices')

    def test_full_episode_and_all_languages_supported(self):
        for lang in ('en','zh','ms'):
            m=production.language_manifest(self.episode,lang)
            dub.validate(m,self.voices)
            self.assertEqual(m['duration_s'],70.927018)
            self.assertEqual(m['source_start_s'],0)
            self.assertEqual(len(m['dialogue']),17)
            self.assertTrue(all(isinstance(x['text'],str) and x['text'] for x in m['dialogue']))

    def test_owner_omission_removes_only_standalone_call(self):
        source=next(c for c in self.episode['dialogue'] if c['id']=='dino-call')
        self.assertEqual(source['text']['en'],'Moon!')
        self.assertFalse(source['include_in_dub'])
        dialogue=production.language_manifest(self.episode,'en')['dialogue']
        ids={c['id'] for c in dialogue}
        self.assertNotIn('dino-call',ids)
        self.assertIn('dino-opening',ids)
        later=next(c for c in dialogue if c['id']=='dino-call-hear')
        self.assertEqual(later['text'],'Moon! Can you hear me?')

    def test_production_cannot_be_a_subclip_or_overlap(self):
        m=production.language_manifest(self.episode,'en')
        m['source_start_s']=10
        with self.assertRaisesRegex(ValueError,'begin at the start'):
            dub.validate(m,self.voices)
        m['source_start_s']=0
        m['dialogue'][1]['start_s']=5
        with self.assertRaisesRegex(ValueError,'Overlapping'):
            dub.validate(m,self.voices)

    def test_future_characters_append_without_replacing_approved_voices(self):
        voices=copy.deepcopy(self.voices)
        voices['characters']['star']=dict(voices['characters']['moon'],display_name='Star')
        m=production.language_manifest(self.episode,'en')
        m['dialogue'][0]['character']='star'
        dub.validate(m,voices)
        self.assertEqual(self.voices['characters']['moon']['voice'],'Sulafat')

    def test_local_score_is_deterministic_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            compose(.2,root/'m1.wav',root/'a1.wav')
            compose(.2,root/'m2.wav',root/'a2.wav')
            self.assertEqual((root/'m1.wav').read_bytes(),(root/'m2.wav').read_bytes())
            self.assertEqual((root/'a1.wav').read_bytes(),(root/'a2.wav').read_bytes())
            with self.assertRaises(ValueError):
                compose(.2,root/'m1.wav',root/'a1.wav')

    def test_timeline_fit_records_small_shifts_and_rejects_large_drift(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(dub,'ROOT',Path(tmp)):
            episode={'duration_s':10,'output_dir':'episodes/test/media/derived/full','report_dir':'episodes/test/reports/full',
                'dialogue':[{'id':'one','start_s':1,'end_s':1.5},{'id':'two','start_s':1.6,'end_s':2.1}]}
            folder=Path(tmp)/episode['output_dir']/'en'
            folder.mkdir(parents=True)
            for cue in episode['dialogue']:
                (folder/(cue['id']+'.wav')).write_bytes(wav_bytes())
            result=production.fit_timeline(episode,'en')
            self.assertEqual(episode['dialogue'][0]['start_s'],1)
            self.assertLessEqual(result[0]['tempo'],1.10)
            self.assertGreater(result[1]['dub_start_s'],result[0]['dub_end_s'])
            self.assertLess(result[1]['shift_s'],1.5)
            (folder/'one.wav').write_bytes(wav_bytes(5))
            with self.assertRaisesRegex(ValueError,'cannot fit naturally'):
                production.fit_timeline(episode,'en')

    def test_export_resume_requires_unchanged_manifest_and_checksum(self):
        import hashlib,json
        with tempfile.TemporaryDirectory() as tmp, patch.object(dub,'ROOT',Path(tmp)):
            episode=copy.deepcopy(self.episode)
            self.assertFalse(production.verified_export(episode,'en'))
            output=dub.relative(episode['exports']['en'])
            output.parent.mkdir(parents=True)
            output.write_bytes(b'fixture movie')
            output.with_suffix('.json').write_text(json.dumps({'manifest':{},'output_sha256':hashlib.sha256(output.read_bytes()).hexdigest()}))
            with self.assertRaisesRegex(ValueError,'differs from current manifest'):
                production.verified_export(episode,'en')

    def test_completion_requires_final_mixed_audio_check(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(dub,'ROOT',Path(tmp)):
            episode=copy.deepcopy(self.episode)
            for lang in episode['languages']:
                output=dub.relative(episode['exports'][lang])
                output.parent.mkdir(parents=True,exist_ok=True)
                output.write_bytes(b'fixture export')
                for cue in episode['dialogue']:
                    path=dub.relative(cue.get('audio',{}).get(lang,{}).get('audio_path') or f'{episode["output_dir"]}/{lang}/{cue["id"]}.wav')
                    path.parent.mkdir(parents=True,exist_ok=True)
                    path.write_bytes(b'fixture stem')
            with patch.object(production,'verified_export',return_value=True), patch.object(production,'mixed_check_valid',return_value=False):
                self.assertFalse(production.production_status(episode)['complete'])
            with patch.object(production,'verified_export',return_value=True), patch.object(production,'mixed_check_valid',return_value=True):
                self.assertTrue(production.production_status(episode)['complete'])

    def test_spoken_chinese_normalization_preserves_meaningful_differences(self):
        self.assertEqual(production.normalize_words('我看見他了'),production.normalize_words('我看见她了'))
        self.assertEqual(production.normalize_words('小迪諾'),production.normalize_words('小Dino'))
        self.assertNotEqual(production.normalize_words('原諒自由了'),production.normalize_words('月亮自由了'))

    def test_selected_language_uses_its_own_verification(self):
        episode=copy.deepcopy(self.episode)
        episode['dialogue'][0]['audio']={'en':{'audio_review_status':'verified_automated','audio_verification_report':'episodes/save-the-moon/reports/en-check.json'}}
        self.assertIn('audio_review_status',production.language_manifest(episode,'en')['dialogue'][0])
        self.assertNotIn('audio_review_status',production.language_manifest(episode,'ms')['dialogue'][0])


if __name__=='__main__':
    unittest.main()
