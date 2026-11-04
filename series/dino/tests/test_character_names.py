"""A high sentence similarity cannot waive an incorrect character name."""
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import dub
import production
import revoice

class CharacterNameTests(unittest.TestCase):
    def test_names_match_final_owner_choice(self):
        names=dub.load(dub.ROOT/'config/character_names.json')['characters']
        self.assertEqual([names[k]['zh'] for k in ('dino','moon','cloud')],['迪诺','月亮','云爷爷'])
        self.assertEqual(names['dino']['pinyin'],'dí nuò')

    def test_wrong_initial_does_not_pass_fuzzy_sentence_match(self):
        cue={'required_names':['迪诺']}
        for wrong in ('小比诺，你为什么想救月亮？','依诺，救救我！','谢谢你，Dino！'):
            self.assertFalse(all(x['passed'] for x in production.check_required_names(cue,wrong)))
        self.assertTrue(all(x['passed'] for x in production.check_required_names(cue,'謝謝你，迪諾！')))
        self.assertTrue(all(x['passed'] for x in production.check_required_names({},'No names.')))

    def test_homophones_preserve_sounds_but_wrong_initials_still_fail(self):
        cue={'required_names':['迪诺'],'name_asr_aliases':{'迪诺':['敌诺','狄懦']}}
        for correct in ('敵諾，救救我！','谢谢你，狄懦！'):
            self.assertTrue(all(x['passed'] for x in production.check_required_names(cue,correct)))
            self.assertIn('迪诺',production.canonical_name_transcript(cue,correct))
        for wrong in ('李诺，救救我！','比诺，你做到了！','Yino'):
            self.assertFalse(all(x['passed'] for x in production.check_required_names(cue,wrong)))

    def test_delivery_changes_request_identity_but_metadata_does_not(self):
        char={'model':'test-tts','preset_version':'v001','voice':'Puck','style':{'zh':'natural'}}
        cue={'text':'迪诺，救救我！','delivery_style':'warm'}
        old=revoice.identity(cue,char,'zh')
        self.assertEqual(old,revoice.identity(dict(cue,required_names=['迪诺']),char,'zh'))
        self.assertNotEqual(old,revoice.identity(dict(cue,delivery_style='conversational'),char,'zh'))
