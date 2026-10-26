import tempfile
from pathlib import Path
import sys
import unittest
import xml.etree.ElementTree as ET
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
import position_captions as captions


class PositionedCaptionTests(unittest.TestCase):
    def test_preserves_multiline_unicode_escaping_and_full_film_offset(self):
        with tempfile.TemporaryDirectory() as temp:
            source, target = Path(temp)/'input.srt', Path(temp)/'output.ttml'
            source.write_text('1\n00:00:06,500 --> 00:00:09,638\n迪诺 & Moon\nLook <up>!\n', encoding='utf-8')
            captions.convert(source, target, 'zh')
            root = ET.parse(target).getroot()
            cue = root.find('.//{'+captions.TT+'}p')
            self.assertEqual(cue.attrib['begin'], '00:00:06.500')
            self.assertEqual(cue.attrib['end'], '00:00:09.638')
            self.assertEqual([cue.text, cue[0].tail], ['迪诺 & Moon', 'Look <up>!'])
            self.assertEqual(root.attrib['{'+captions.XML+'}lang'], 'zh')
            region = root.find('.//{'+captions.TT+'}region')
            self.assertEqual(region.attrib['{'+captions.TTS+'}displayAlign'], 'after')
            with self.assertRaises(ValueError):
                captions.convert(source, target, 'zh')

    def test_rejects_overlap_before_writing_output(self):
        with tempfile.TemporaryDirectory() as temp:
            source, target = Path(temp)/'input.srt', Path(temp)/'output.ttml'
            source.write_text('1\n00:00:01,000 --> 00:00:03,000\nHello\n\n2\n00:00:02,000 --> 00:00:04,000\nMoon\n')
            with self.assertRaises(ValueError):
                captions.convert(source, target, 'en')
            self.assertFalse(target.exists())


if __name__ == '__main__':
    unittest.main()
