"""An already branded master must not gain bumpers or re-encoded audio."""
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import brand_video
import dub


class ExistingBrandingTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('ffmpeg'),'FFmpeg integration check')
    def test_captions_keep_complete_timeline_and_audio(self):
        font=next((p for p in (Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'),
                  dub.ROOT/'library/media/branding/flh-v001/Nunito-700.ttf') if p.exists()),None)
        if font is None:
            self.skipTest('Optional local fixture font unavailable')
        with tempfile.TemporaryDirectory() as tmp,patch.object(dub,'ROOT',Path(tmp)):
            root=Path(tmp)
            (root/'assets').mkdir()
            shutil.copyfile(font,root/'assets/font.ttf')
            (root/'assets/test.ass').write_text('''[Script Info]
ScriptType: v4.00+
PlayResX: 320
PlayResY: 568
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,DejaVu Sans,20,&H00FFFFFF,&H00FFFFFF,&H00202020,&H80000000,-1,0,0,0,100,100,0,0,1,2,1,2,20,20,25,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.20,0:00:01.80,Default,,0,0,0,,Synthetic test fixture
''')
            sub={'layout':'overlay','packaged_offset_s':0,'ass_path':'assets/test.ass','font_path':'assets/font.ttf'}
            (root/'subtitles.json').write_text(json.dumps(sub))
            dub.run(['ffmpeg','-v','error','-f','lavfi','-i','color=c=blue:s=320x568:r=24:d=2',
                '-f','lavfi','-i','sine=frequency=440:sample_rate=48000:duration=2',
                '-c:v','libx264','-preset','ultrafast','-threads','1','-pix_fmt','yuv420p',
                '-af','loudnorm=I=-16:TP=-2.5:LRA=11','-c:a','aac','-ar','48000','-ac','2',str(root/'source.mp4')])
            m={'source_video':'source.mp4','output':'exports/captioned.mp4','source_duration_s':2,
               'subtitles':'subtitles.json','existing_branding':True}
            original={'output_sha256':hashlib.sha256((root/'source.mp4').read_bytes()).hexdigest()}
            result=brand_video.render_existing_picture(m,original,{'test':'fixture'})
            self.assertEqual(result['actual_video_frames'],48)
            self.assertEqual(result['duration_s'],2)
            self.assertTrue(result['audio_packets_preserved'])
            self.assertEqual(result['story_offset_s'],0)
            out=root/m['output'];modified=out.stat().st_mtime_ns
            brand_video.render_existing_picture(m,original,{'test':'fixture'})
            self.assertEqual(out.stat().st_mtime_ns,modified)
            sub['packaged_offset_s']=2
            (root/'subtitles.json').write_text(json.dumps(sub))
            with self.assertRaisesRegex(ValueError,'zero-offset'):
                brand_video.render_existing_picture(m,original,{'test':'fixture'})


if __name__=='__main__':
    unittest.main()
