from array import array
import copy
import io
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import wave
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import dub
import sfx
import audio_production as audio

ROOT=Path(__file__).resolve().parents[1]


class SfxTests(unittest.TestCase):
    def setUp(self):
        self.registry=json.loads((ROOT/'library/presets/v002/sfx_presets.json').read_text())

    def plan(self):
        return {'schema_version':1,'status':'verified','duration_s':4,'scenes':[{'id':'test','description':'Synthetic test fixture, not film timing'}],'cues':[{'id':'step','scene_id':'test','preset_id':'dino_footstep','preset_version':'v001','timestamp_s':1,'status':'verified','timing_basis':'Synthetic fixture'}]}

    def test_requested_library_and_legacy_compatibility(self):
        sfx.validate_registry(self.registry)
        for key in sfx.GENERATORS:self.assertEqual(len(self.registry['effects'][key]['variations']),3)
        old=json.loads((ROOT/'library/presets/v001/sfx_presets.json').read_text())
        for key,old_preset in old['effects'].items():
            for name,value in old_preset.items():self.assertEqual(self.registry['effects'][key][name],value)

    def test_variation_stability_and_preset_cue_gain(self):
        plan=self.plan();plan['cues'][0]['gain_db']=3
        first=sfx.validate_plan(plan,self.registry,True)[0]
        again=sfx.validate_plan(plan,self.registry,True)[0]
        self.assertEqual(first['selected_variation'],again['selected_variation'])
        self.assertEqual(first['effective_gain_db'],self.registry['effects']['dino_footstep']['default_gain_db']+3)
        plan['cues'][0]['variation']='v02'
        self.assertEqual(sfx.validate_plan(plan,self.registry,True)[0]['selected_variation'],'v02')

    def test_unknown_draft_times_not_production_and_invalid_cues_fail(self):
        plan=self.plan();plan['status']='draft';plan['cues'][0]['timestamp_s']=None
        self.assertIsNone(sfx.validate_plan(plan,self.registry)[0]['timestamp_s'])
        with self.assertRaises(ValueError):sfx.validate_plan(plan,self.registry,True)
        for field,value in [('scene_id','unknown'),('variation','unknown'),('preset_version','future'),('timestamp_s',3.9),('gain_db',float('nan'))]:
            bad=self.plan();bad['cues'][0][field]=value
            with self.assertRaises(ValueError):sfx.validate_plan(bad,self.registry,True)

    def test_deterministic_wav_and_tamper_safe_cache(self):
        preset=copy.deepcopy(self.registry['effects']['dino_footstep']);variant=preset['variations'][0]
        a=sfx.synthesize(variant);self.assertEqual(a,sfx.synthesize(variant))
        other=sfx.synthesize(preset['variations'][1]);self.assertNotEqual(a,other)
        with wave.open(io.BytesIO(a)) as stream:
            self.assertEqual((stream.getnchannels(),stream.getsampwidth(),stream.getframerate()),(2,2,48000))
            self.assertEqual(stream.getnframes(),round(variant['duration_s']*48000))
        with tempfile.TemporaryDirectory() as tmp,patch.object(dub,'ROOT',Path(tmp)):
            variant['asset_path']='library/media/test.wav'
            path=sfx.ensure_asset(preset,variant)
            self.assertEqual(path.read_bytes(),sfx.ensure_asset(preset,variant).read_bytes())
            path.write_bytes(b'tampered')
            with self.assertRaises(ValueError):sfx.ensure_asset(preset,variant)
            self.assertEqual(path.read_bytes(),b'tampered')

    def test_no_third_party_import_without_rights_and_integrity_metadata(self):
        preset=self.registry['effects']['dino_footstep']
        preset['variations']=[{'id':'licensed','asset_path':'library/media/a.wav','duration_s':1}]
        with self.assertRaises(ValueError):sfx.validate_registry(self.registry)


@unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'),'FFmpeg integration')
class SharedMixTests(unittest.TestCase):
    def test_full_three_language_mix_ducking_cache_and_source_protection(self):
        with tempfile.TemporaryDirectory() as tmp,patch.object(dub,'ROOT',Path(tmp)):
            root=Path(tmp)
            (root/'schemas').mkdir()
            for name in ['sfx','sfx-cues','audio-production']:
                shutil.copyfile(ROOT/'schemas'/f'{name}.schema.json',root/'schemas'/f'{name}.schema.json')
            ep=root/'episodes/test';(ep/'media/originals').mkdir(parents=True)
            source=ep/'media/originals/source.mp4'
            dub.run(['ffmpeg','-v','error','-f','lavfi','-i','color=c=blue:s=160x240:r=24:d=4','-c:v','libx264','-an',str(source)])
            source_sha=sfx.digest(source)
            bed=root/'library/media/bed.wav';bed.parent.mkdir(parents=True)
            dub.run(['ffmpeg','-v','error','-f','lavfi','-i','sine=frequency=220:duration=4','-ar','48000','-ac','2',str(bed)])
            registry=json.loads((ROOT/'library/presets/v002/sfx_presets.json').read_text())
            (root/'registry.json').write_text(json.dumps(registry))
            plan={'schema_version':1,'status':'verified','duration_s':4,'scenes':[{'id':'fixture','description':'Synthetic test scene'}],'cues':[{'id':'step','scene_id':'fixture','preset_id':'dino_footstep','preset_version':'v001','timestamp_s':1,'status':'verified','timing_basis':'Synthetic fixture; not production footage'}]}
            (root/'plan.json').write_text(json.dumps(plan))
            m=json.loads((ROOT/'templates/episode/audio-production.json').read_text().replace('__EPISODE__','test'))
            m.update(status='verified',duration_s=4,source_video=source.relative_to(root).as_posix(),source_video_sha256=source_sha,sfx_plan='plan.json',sfx_registry='registry.json')
            for index,lang in enumerate(['en','zh','ms']):
                path=ep/f'{lang}.wav';begin=.5+index*.5;end=begin+1
                dub.run(['ffmpeg','-v','error','-f','lavfi','-i',f'sine=frequency={400+index*100}:duration=4','-af',f"volume='if(between(t,{begin},{end}),3,0)':eval=frame",'-ar','48000','-ac','2',str(path)])
                report=ep/f'{lang}.json';report.write_text(json.dumps({'stems':{'dialogue':path.relative_to(root).as_posix()},'note':'Synthetic audio fixture; not generated character speech'}))
                m['dialogue'][lang]={'path':path.relative_to(root).as_posix(),'sha256':sfx.digest(path),'status':'verified','provenance':'Test-only tone fixture','license':'Project test synthesis','provenance_report':report.relative_to(root).as_posix()}
            bed_spec={'path':bed.relative_to(root).as_posix(),'sha256':sfx.digest(bed),'status':'verified','provenance':'Test tone','license':'Project test synthesis','scene_id':'fixture','timestamp_s':0,'duration_s':4,'gain_db':-12,'timing_basis':'Synthetic fixture'}
            m['music']=[bed_spec];m['ambience']=[dict(bed_spec)]
            m['ducking']['music']['threshold']=.004;m['ducking']['sfx']['threshold']=.004
            result=audio.build(m)
            self.assertEqual({r['common_music_sha256'] for r in result.values()}, {result['en']['common_music_sha256']})
            self.assertEqual({r['common_sfx_sha256'] for r in result.values()}, {result['en']['common_sfx_sha256']})
            self.assertEqual(sfx.digest(source),source_sha)
            for lang,r in result.items():
                self.assertLessEqual(float(r['encoded_audio_measurement']['input_tp']),-.8)
                self.assertAlmostEqual(float(r['encoded_audio_measurement']['input_i']),-16,delta=1)
                self.assertEqual(r['picture_packet_hash'],dub.video_hash(source))
            def rms(path,start):
                data=subprocess.run(['ffmpeg','-v','error','-ss',str(start),'-i',str(path),'-t','0.2','-ac','1','-ar','48000','-f','f32le','-'],check=True,capture_output=True).stdout
                values=array('f');values.frombytes(data)
                return math.sqrt(sum(x*x for x in values)/len(values))
            work=dub.relative(m['output_dir'])
            for group in ['music','sfx']:
                active=rms(work/f'common.{group}.wav',1.1)/rms(work/f'{group}.raw.wav',1.1)
                idle=rms(work/f'common.{group}.wav',3.6)/rms(work/f'{group}.raw.wav',3.6)
                self.assertLess(active,.7)
                self.assertGreater(idle,.8)
            # Resuming does not write or re-normalize valid output files.
            before={lang:dub.relative(m['exports'][lang]).stat().st_mtime_ns for lang in result}
            audio.build(m)
            self.assertEqual(before,{lang:dub.relative(m['exports'][lang]).stat().st_mtime_ns for lang in result})
            (work/'common.sfx.wav').write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError,'cache modified'):audio.prepare(m)


if __name__=='__main__':unittest.main()
