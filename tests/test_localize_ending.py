"""Exercise ending-only replacement with real B-frame video and primed AAC."""
from pathlib import Path
import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import dub
import localize_ending


class LocalizedEndingTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'),'FFmpeg required')
    def test_splice_preserves_original_frame_clock_prefix_and_audio(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);source=root/'source.mp4';card=root/'card.mp4'
            dub.run(['ffmpeg','-v','error','-f','lavfi','-i','color=c=blue:s=64x64:r=24:d=3',
                '-f','lavfi','-i','sine=frequency=440:sample_rate=48000:duration=3',
                '-c:v','libx264','-g','24','-keyint_min','24','-sc_threshold','0','-threads','1',
                '-ac','2','-c:a','aac','-shortest',str(source)])
            dub.run(['ffmpeg','-v','error','-f','lavfi','-i','color=c=green:s=64x64:r=24:d=1',
                '-an','-c:v','libx264','-threads','1',str(card)])
            settings=root/'ending.json';settings.write_text(json.dumps(dict(duration_s=1,title='TAMAT',series='Pengembaraan Dino')))
            config=root/'config.json';config.write_text(json.dumps(dict(language='ms',
                source_final=dict(path='source.mp4',sha256=hashlib.sha256(source.read_bytes()).hexdigest()),
                ending_settings='ending.json',story_end_s=2,work_dir='work',output='localized.mp4',report='qa.json')))
            with patch.object(dub,'ROOT',root),patch.object(localize_ending.end_card,'render',return_value=card):
                localize_ending.replace(config)
            q=json.loads((root/'qa.json').read_text())
            self.assertEqual(q['frames'],72)
            self.assertEqual(q['duration_s'],3)
            self.assertEqual(q['copied_story_frames'],24)
            self.assertTrue(q['video_timestamps_unchanged'])
            self.assertTrue(q['audio_packets_and_timestamps_unchanged'])
            self.assertEqual(q['title'],'TAMAT')


if __name__=='__main__':unittest.main()
