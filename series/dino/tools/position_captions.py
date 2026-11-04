#!/usr/bin/env python3
"""Convert packaged SRT into lower-positioned TTML without changing cue content.

TTML expresses author placement/style preferences. Platform/player accessibility
settings can override them; this is not a guarantee of YouTube Shorts rendering.
"""
import argparse
from pathlib import Path
import re
import xml.etree.ElementTree as ET

TT = 'http://www.w3.org/ns/ttml'
TTS = TT+'/styling'
TTP = TT+'/parameter'
XML = 'http://www.w3.org/XML/1998/namespace'
for prefix, uri in [('', TT), ('tts', TTS), ('ttp', TTP)]:
    ET.register_namespace(prefix, uri)


def convert(source, output, language):
    source, output = Path(source), Path(output)
    if output.exists():
        raise ValueError('Output exists; choose a new version.')
    blocks = re.split(r'\n\s*\n', source.read_text(encoding='utf-8-sig').strip())
    cues = []
    previous_end = 0
    def milliseconds(stamp):
        h, m, s, ms = map(int, re.split('[:,]', stamp))
        return ((h*60+m)*60+s)*1000+ms
    for block in blocks:
        rows = block.splitlines()
        if len(rows) < 3 or not rows[0].isdigit():
            raise ValueError('Unsupported SRT block.')
        match = re.fullmatch(r'(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})', rows[1])
        if not match:
            raise ValueError('Unsupported SRT timestamps.')
        start, end = match.groups()
        if milliseconds(start) < previous_end or milliseconds(end) <= milliseconds(start):
            raise ValueError('Overlapping or reversed cue.')
        previous_end = milliseconds(end)
        cues.append((start, end, rows[2:]))
    root = ET.Element('{'+TT+'}tt', {'{'+XML+'}lang': language,
        '{'+TTP+'}timeBase': 'media', '{'+TTS+'}extent': '720px 1280px'})
    head = ET.SubElement(root, '{'+TT+'}head')
    styling = ET.SubElement(head, '{'+TT+'}styling')
    ET.SubElement(styling, '{'+TT+'}style', {'{'+XML+'}id': 'learning',
        '{'+TTS+'}fontFamily': 'proportionalSansSerif', '{'+TTS+'}fontSize': '36px',
        '{'+TTS+'}fontWeight': 'bold', '{'+TTS+'}color': '#FFFFFF',
        '{'+TTS+'}backgroundColor': 'transparent', '{'+TTS+'}textOutline': '#202020 2px',
        '{'+TTS+'}textAlign': 'center', '{'+TTS+'}wrapOption': 'wrap'})
    layout = ET.SubElement(head, '{'+TT+'}layout')
    ET.SubElement(layout, '{'+TT+'}region', {'{'+XML+'}id': 'lower',
        '{'+TTS+'}origin': '8% 78%', '{'+TTS+'}extent': '84% 12%',
        '{'+TTS+'}displayAlign': 'after', '{'+TTS+'}backgroundColor': 'transparent'})
    div = ET.SubElement(ET.SubElement(root, '{'+TT+'}body'), '{'+TT+'}div')
    for index, (start, end, lines) in enumerate(cues, 1):
        para = ET.SubElement(div, '{'+TT+'}p', {'{'+XML+'}id': 'cue'+str(index),
            'begin': start.replace(',', '.'), 'end': end.replace(',', '.'),
            'region': 'lower', 'style': 'learning'})
        para.text = lines[0]
        for line in lines[1:]:
            ET.SubElement(para, '{'+TT+'}br').tail = line
    # Round-trip XML validation protects text, timestamps and explicit line breaks.
    for para, (start, end, lines) in zip(root.findall('.//{'+TT+'}p'), cues):
        parsed = ET.fromstring(ET.tostring(para))
        assert [parsed.text]+[child.tail for child in parsed] == lines
        assert parsed.attrib['begin'].replace('.', ',') == start
        assert parsed.attrib['end'].replace('.', ',') == end
    output.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(root).write(output, encoding='utf-8', xml_declaration=True)
    print(f'Exported {len(cues)} unchanged cues; lower region ends at 90% frame height. Player review required.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source')
    parser.add_argument('output')
    parser.add_argument('--language', default='en')
    args = parser.parse_args()
    convert(args.source, args.output, args.language)
