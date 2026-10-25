"""Pipeline contract tests. All media fixtures are synthetic, never episode content."""
import base64
from contextlib import redirect_stdout
import copy
import hashlib
import io
import json
import math
import os
from pathlib import Path
import shutil
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch
import wave

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import dub


def wav_bytes(seconds=1):
    out = io.BytesIO()
    with wave.open(out, 'wb') as w:
        w.setparams((1, 2, 24000, 0, 'NONE', 'not compressed'))
        w.writeframes(b''.join(struct.pack('<h', int(2000*math.sin(2*math.pi*440*i/24000))) for i in range(int(seconds*24000))))
    return out.getvalue()


class DubbingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.voices = dub.load(dub.ROOT / 'config/voices.json')
        self.m = {'schema_version':1, 'kind':'dubbing_poc', 'status':'verified', 'language':'en',
            'source_video':'episodes/test/media/originals/source.mp4', 'source_start_s':0,
            'duration_s':8, 'output_dir':'episodes/test/media/derived/poc', 'original_audio':'replace',
            'mix':{'integrated_lufs':-18, 'true_peak_db':-2}, 'beds':[], 'sfx':[],
            'dialogue':[{'id':'test-line','character':'dino','voice_version':'v001','text':'Test fixture only.',
                'status':'verified','start_s':1,'end_s':3,'audio_review_status':'approved'}]}
        self.patch = patch.object(dub, 'ROOT', self.root)
        self.patch.start()
        self.addCleanup(self.patch.stop)
        self.silence = redirect_stdout(io.StringIO())
        self.silence.__enter__()
        self.addCleanup(self.silence.__exit__, None, None, None)

    def test_presets_and_request_contract(self):
        self.assertEqual({k:v['voice'] for k,v in self.voices['characters'].items()},
                         {'dino':'Puck','cloud':'Charon','moon':'Sulafat'})
        body = dub.payload(self.m['dialogue'][0], self.voices['characters']['dino'], 'en')
        part = body['contents'][0]['parts'][0]
        self.assertEqual(part['text'], 'Test fixture only.')
        self.assertIn('style', part['speech_metadata'])
        self.assertEqual(body['generationConfig']['speechConfig']['voiceConfig']['voice'], 'Puck')
        dub.validate(self.m, self.voices)

    def test_unknowns_and_overlapping_windows_rejected(self):
        for key,value in [('duration_s',None),('duration_s',float('nan')),('duration_s',True),('source_start_s',-1),('original_audio','retain')]:
            m = copy.deepcopy(self.m)
            m[key] = value
            with self.assertRaises(ValueError):
                dub.validate(m,self.voices)
        other = dict(self.m['dialogue'][0],id='second-line',start_s=2,end_s=4)
        self.m['dialogue'].append(other)
        with self.assertRaisesRegex(ValueError,'Overlapping'):
            dub.validate(self.m,self.voices)

    def test_character_and_version_validation(self):
        for changes in ({'character':'missing'},{'voice_version':'v002'},{'text':''},{'start_s':4}):
            m=copy.deepcopy(self.m)
            m['dialogue'][0].update(changes)
            with self.assertRaises(ValueError):
                dub.validate(m,self.voices)

    def test_unreviewed_background_rejected(self):
        self.m['beds']=[{'path':'library/media/bed.wav','start_s':0,'duration_s':8,'gain_db':-12,'status':'draft','dialogue_free':False}]
        with self.assertRaisesRegex(ValueError,'dialogue-free'):
            dub.validate(self.m,self.voices)

    def test_path_traversal_and_symlinks_rejected(self):
        for path in ('../escape', '/etc/passwd', ''):
            with self.assertRaises(ValueError):
                dub.relative(path)
        (self.root/'link').symlink_to(self.root/'target')
        with self.assertRaises(ValueError):
            dub.relative('link/test.wav')

    def test_dotenv_without_shell_execution_and_environment_precedence(self):
        env=self.root/'.env'
        env.write_text('IGNORED=unused\nexport GEMINI_API_KEY="fixture-key" # comment\n')
        with patch.dict(os.environ,{},clear=True):
            dub.load_env(env)
            self.assertEqual(os.environ['GEMINI_API_KEY'],'fixture-key')
            env.write_text('GEMINI_API_KEY=replacement\n')
            dub.load_env(env)
            self.assertEqual(os.environ['GEMINI_API_KEY'],'fixture-key')
        env.write_text('GEMINI_API_KEY=$(false)\n')
        with patch.dict(os.environ,{},clear=True):
            dub.load_env(env)
            self.assertEqual(os.environ['GEMINI_API_KEY'],'$(false)')

    def test_explicit_alternate_key_selection_does_not_load_other_settings(self):
        env=self.root/'.env'
        env.write_text('GEMINI_API_KEY=first-fixture\nGEMINI_API_KEY_B=second-fixture\nUNRELATED=ignore\n')
        with patch.dict(os.environ,{},clear=True):
            dub.load_env(env,'GEMINI_API_KEY_B')
            self.assertEqual(os.environ['GEMINI_API_KEY'],'second-fixture')
            self.assertNotIn('UNRELATED',os.environ)
            self.assertNotIn('GEMINI_API_KEY_B',os.environ)
        with self.assertRaises(ValueError):
            dub.load_env(env,'OTHER_SERVICE_SECRET')

    def test_wav_and_legacy_pcm_decoding(self):
        data=wav_bytes()
        def response(mime,blob):
            return {'candidates':[{'content':{'parts':[{'inlineData':{'mimeType':mime,'data':base64.b64encode(blob).decode()}}]}}]}
        self.assertEqual(dub.decode_audio(response('audio/wav',data)),data)
        self.assertAlmostEqual(dub.wav_info(data)['duration_s'],1)
        legacy=dub.decode_audio(response('audio/L16;codec=pcm;rate=24000', b'\0\0'*24000))
        self.assertEqual(dub.wav_info(legacy)['duration_s'],1)
        with self.assertRaises(ValueError):
            dub.decode_audio(response('audio/mp3',data))
        with self.assertRaises(ValueError):
            dub.decode_audio({})
        with self.assertRaises(ValueError):
            dub.wav_info(data[:-10])

    def generate_fixture(self):
        data=wav_bytes()
        response={'candidates':[{'content':{'parts':[{'inlineData':{'mimeType':'audio/wav','data':base64.b64encode(data).decode()}}]}}]}
        stream=io.BytesIO(json.dumps(response).encode())
        with patch.dict(os.environ,{'GEMINI_API_KEY':'fixture-key'}), patch.object(dub.request,'urlopen',return_value=stream) as call:
            dub.generate(self.m,self.voices,live=True)
            self.assertEqual(call.call_count,1)
        return self.root/'episodes/test/media/derived/poc/en/test-line.wav'

    def test_dry_run_never_calls_provider(self):
        with patch.object(dub.request,'urlopen') as call:
            dub.generate(self.m,self.voices)
            call.assert_not_called()
        self.assertFalse((self.root/'episodes').exists())

    def test_generation_skip_change_detection_and_new_takes(self):
        path=self.generate_fixture()
        original=path.read_bytes()
        with patch.object(dub.request,'urlopen') as call:
            dub.generate(self.m,self.voices,live=True)
            call.assert_not_called()
        self.m['dialogue'][0]['text']='Changed fixture.'
        with self.assertRaisesRegex(ValueError,'configuration changed'):
            dub.generate(self.m,self.voices)
        # A dry-run new take does not alter the previous output.
        dub.generate(self.m,self.voices,regenerate=True)
        self.assertEqual(path.read_bytes(),original)

    def test_selected_alternate_take_is_reused_without_touching_original(self):
        original=self.generate_fixture()
        before=original.read_bytes()
        cue=self.m['dialogue'][0]
        cue['delivery_style']='Pronounce the character name clearly.'
        data=wav_bytes()
        response={'candidates':[{'content':{'parts':[{'inlineData':{'mimeType':'audio/wav','data':base64.b64encode(data).decode()}}]}}]}
        with patch.dict(os.environ,{'GEMINI_API_KEY':'fixture-key'}),patch.object(dub.request,'urlopen',return_value=io.BytesIO(json.dumps(response).encode())):
            dub.generate(self.m,self.voices,live=True,regenerate=True)
        takes=list(original.parent.glob('take-*/test-line.wav'))
        self.assertEqual(len(takes),1)
        cue['audio_path']=takes[0].relative_to(self.root).as_posix()
        with patch.object(dub.request,'urlopen') as call:
            dub.generate(self.m,self.voices,live=True)
            call.assert_not_called()
        self.assertEqual(original.read_bytes(),before)
        record=dub.load(takes[0].with_suffix('.json'))
        self.assertTrue(record['request']['contents'][0]['parts'][0]['speech_metadata']['style'].endswith(cue['delivery_style']))

    def test_http_errors_do_not_leak_secrets_or_retry(self):
        exc=dub.error.HTTPError('https://example.invalid',429,'secret response',{},None)
        with patch.dict(os.environ,{'GEMINI_API_KEY':'fixture-secret'}), patch.object(dub.request,'urlopen',side_effect=exc) as call:
            with self.assertRaisesRegex(ValueError,'HTTP 429') as caught:
                dub.generate(self.m,self.voices,live=True)
            self.assertEqual(call.call_count,1)
            self.assertNotIn('secret',str(caught.exception))

    @unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'),'FFmpeg integration test')
    def test_real_render_replaces_source_audio_and_preserves_original(self):
        source=dub.relative(self.m['source_video'])
        source.parent.mkdir(parents=True)
        # Test pattern has a distinct original tone. Neither is production media.
        dub.run([dub.tool('ffmpeg'),'-v','error','-nostdin','-f','lavfi','-i','color=c=blue:s=160x240:r=24:d=8',
                 '-f','lavfi','-i','sine=frequency=880:duration=8','-c:v','libx264','-pix_fmt','yuv420p','-c:a','aac','-shortest',str(source)])
        before=hashlib.sha256(source.read_bytes()).hexdigest()
        path=self.generate_fixture()
        dub.render(self.m,self.voices,'episodes/test/exports/review_v001.mp4')
        target=self.root/'episodes/test/exports/review_v001.mp4'
        info=dub.probe(target)
        self.assertAlmostEqual(float(info['format']['duration']),8,delta=.15)
        self.assertEqual({s['codec_type'] for s in info['streams']},{'video','audio'})
        self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(),before)
        # Before the placed dialogue begins, exported audio must be silent.
        check=dub.run([dub.tool('ffmpeg'),'-hide_banner','-i',str(target),'-t','0.5','-af','volumedetect','-f','null','-']).stderr
        self.assertIn('max_volume: -91.0 dB',check)
        self.assertTrue(target.with_suffix('.mix.wav').exists())
        with self.assertRaisesRegex(ValueError,'already exists'):
            dub.render(self.m,self.voices,'episodes/test/exports/review_v001.mp4')
        self.m['dialogue'][0]['end_s']=1.5
        with self.assertRaisesRegex(ValueError,'10% speedup'):
            dub.render(self.m,self.voices,'episodes/test/exports/review_v002.mp4')


    @unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'),'FFmpeg integration test')
    def test_full_production_stream_copy_and_separate_buses(self):
        self.m.update(kind='dubbing_production',duration_s=72)
        source=dub.relative(self.m['source_video'])
        source.parent.mkdir(parents=True)
        dub.run([dub.tool('ffmpeg'),'-v','error','-nostdin','-f','lavfi','-i','color=c=green:s=160x240:r=24:d=72',
                 '-an','-c:v','libx264','-pix_fmt','yuv420p',str(source)])
        bed=self.root/'library/media/test-bed.wav'
        bed.parent.mkdir(parents=True)
        dub.run([dub.tool('ffmpeg'),'-v','error','-nostdin','-f','lavfi','-i','sine=frequency=220:duration=72',
                 '-af','volume=0.005','-c:a','pcm_s16le',str(bed)])
        self.m['beds']=[{'path':'library/media/test-bed.wav','category':'music','start_s':0,'duration_s':72,'gain_db':-6,'status':'verified','dialogue_free':True}]
        self.generate_fixture()
        dub.render(self.m,self.voices,'episodes/test/exports/full.mp4')
        target=self.root/'episodes/test/exports/full.mp4'
        args=['-v','error','-nostdin','-i']
        suffix=['-map','0:v:0','-c','copy','-f','hash','-hash','sha256','-']
        before=dub.run([dub.tool('ffmpeg'),*args,str(source),*suffix]).stdout
        after=dub.run([dub.tool('ffmpeg'),*args,str(target),*suffix]).stdout
        self.assertEqual(before,after)
        self.assertAlmostEqual(float(dub.probe(target)['format']['duration']),72,delta=.15)
        for group in ('dialogue','music'):
            stem=target.with_suffix('.'+group+'.wav')
            self.assertTrue(stem.is_file())
            self.assertAlmostEqual(float(dub.probe(stem)['format']['duration']),72,delta=.01)
        report=dub.load(target.with_suffix('.json'))
        self.assertIn('sidechaincompress',report['music_ducking'])


if __name__=='__main__':
    unittest.main()
