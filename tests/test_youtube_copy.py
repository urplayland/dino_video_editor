import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import dub
from prepare_youtube_copy import prepare


class YoutubeCopyTests(unittest.TestCase):
    def fixture(self, root):
        profile={'schema_version':1,'brand':'Family Learning Hub','youtube':{'handle':'@familylearninghub-flh','url':'https://www.youtube.com/@familylearninghub-flh'},'publishing':{'strategy':'separate_language_videos','subtitle_delivery':'embedded','video_title_template':'{episode_title} | {series} | {language_label}','playlist_title_template':'{series} — {language_label}','append_channel_name_to_video_titles':False,'language_order':['en','zh','ms'],'languages':{'en':{'label':'English'},'zh':{'label':'中文'},'ms':{'label':'Bahasa Melayu'}}},'profile_descriptions':{'en':'Channel','zh':'频道','ms':'Saluran'}}
        episode={'schema_version':1,'series':'Dino Adventures','selection_manifest':'selection.json','releases':{lang:{'episode_title':'Episode '+lang,'drive_id':'file-'+lang,'description':'Copy '+lang,'playlist_description':'Playlist '+lang} for lang in ['en','zh','ms']}}
        selection={'media':{lang:{'file':'exports/'+lang+'.mp4','sha256':'a'*64,'has_burned_subtitles':True} for lang in ['en','zh','ms']}}
        for name,value in [('profile.json',profile),('release.json',episode),('selection.json',selection)]:
            (root/name).write_text(json.dumps(value))
        return profile,episode,selection

    def test_writes_each_language_with_matching_video_playlist_and_no_brand_suffix(self):
        with tempfile.TemporaryDirectory() as tmp,patch.object(dub,'ROOT',Path(tmp)):
            root=Path(tmp);self.fixture(root)
            outputs=prepare('profile.json','release.json','kit')
            for lang,label in [('en','English'),('zh','中文'),('ms','Bahasa Melayu')]:
                text=outputs['04_Copy_And_Setup/first-episode-'+lang+'.txt']
                self.assertIn('Episode '+lang+' | Dino Adventures | '+label+'\n',text)
                self.assertNotIn('| Family Learning Hub',text)
                self.assertIn('Dino Adventures — '+label,outputs['04_Copy_And_Setup/playlist-copy.txt'])
                self.assertIn('file-'+lang,outputs['04_Copy_And_Setup/UPLOAD_CHECKLIST.txt'])
            self.assertTrue((root/'kit/04_Copy_And_Setup/UPLOAD_CHECKLIST.txt').is_file())

    def test_rejects_clean_source_before_any_copy_is_written(self):
        with tempfile.TemporaryDirectory() as tmp,patch.object(dub,'ROOT',Path(tmp)):
            root=Path(tmp);_,_,selection=self.fixture(root)
            selection['media']['ms']['has_burned_subtitles']=False
            (root/'selection.json').write_text(json.dumps(selection))
            with self.assertRaises(ValueError):prepare('profile.json','release.json','kit')
            self.assertFalse((root/'kit').exists())

    def test_dry_run_does_not_write(self):
        with tempfile.TemporaryDirectory() as tmp,patch.object(dub,'ROOT',Path(tmp)):
            root=Path(tmp);self.fixture(root)
            outputs=prepare('profile.json','release.json','kit',True)
            self.assertIn('04_Copy_And_Setup/UPLOAD_CHECKLIST.txt',outputs)
            self.assertFalse((root/'kit').exists())


if __name__=='__main__':unittest.main()
