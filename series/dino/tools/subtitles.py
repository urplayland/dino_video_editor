#!/usr/bin/env python3
"""Create editable subtitles from verified selected dialogue, never sample/ASR text."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import dub
import production


def stamp(seconds,ass=False):
    units=round(seconds*(100 if ass else 1000))
    scale=100 if ass else 1000
    whole,fraction=divmod(units,scale)
    minute,second=divmod(whole,60);hour,minute=divmod(minute,60)
    return f'{hour}:{minute:02}:{second:02}.{fraction:02}' if ass else f'{hour:02}:{minute:02}:{second:02},{fraction:03}'


def wrap(text,font,width):
    if any(x in text for x in ('{','}','\\','\n','\r')):
        raise ValueError('Subtitle text contains unsupported control characters.')
    cjk=bool(re.search(r'[\u3400-\u9fff]',text))
    units=list(text) if cjk else text.split()
    separator='' if cjk else ' '
    lines=[];line=''
    for word in units:
        candidate=(line+separator+word).strip()
        if font.getlength(candidate)>width and line:
            lines.append(line);line=word
        else:line=candidate
    if line:lines.append(line)
    if len(lines)>2 or any(font.getlength(x)>width for x in lines):
        raise ValueError('Subtitle exceeds the readable two-line area; split the cue.')
    return lines


def generate(episode,settings):
    from PIL import ImageFont
    m=production.language_manifest(episode,settings['language'])
    font=ImageFont.truetype(str(dub.relative(settings['font_path'],True)),settings['font_size'],index=settings.get('font_index',0))
    cues=[];previous=0
    for row in m['dialogue']:
        start,end=row['start_s'],row['end_s']
        if start<previous-.001 or end<=start or end>m['duration_s']:
            raise ValueError('Subtitle timing overlaps or exceeds the story.')
        previous=end
        transcript=row.get('spoken_text',row['text'])
        cues.append(dict(id=row['id'],start_s=start,end_s=end,text=transcript,lines=wrap(transcript,font,settings['max_text_width'])))
    ass='''[Script Info]
ScriptType: v4.00+
PlayResX: 720
PlayResY: 1280
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
'''
    overlay=settings.get('layout')=='overlay'
    colors='&H00FFFFFF,&H00FFFFFF,&H00202020,&H80000000' if overlay else '&H004B4B4B,&H004B4B4B,&H00FFFDF9,&H00FFFDF9'
    outline,shadow=(settings.get('outline_px',2.5),settings.get('shadow_px',2)) if overlay else (0,0)
    ass+=f'Style: Learning,{settings["font_name"]},{settings["font_size"]},{colors},-1,0,0,0,100,100,0,0,1,{outline},{shadow},2,48,48,{settings["margin_bottom"]},1\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n'
    for row in cues:
        text=r'\N'.join(row['lines'])
        position=settings.get('cue_positions',{}).get(row['id'])
        if position:
            x,y=position
            if not 48<=x<=672 or not 80<=y<=1252:raise ValueError('Subtitle position exceeds picture safe bounds.')
            text=r'{\an2\pos('+str(x)+','+str(y)+')}'+text
        ass+=f'Dialogue: 0,{stamp(row["start_s"],True)},{stamp(row["end_s"],True)},Learning,,0,0,0,,{text}\n'
    srt='\n'.join(f'{i}\n{stamp(c["start_s"])} --> {stamp(c["end_s"])}\n'+ '\n'.join(c['lines'])+'\n' for i,c in enumerate(cues,1))
    # Standalone sidecar matches the final packaged movie, including the opening.
    offset=settings['packaged_offset_s']
    packaged='\n'.join(f'{i}\n{stamp(c["start_s"]+offset)} --> {stamp(c["end_s"]+offset)}\n'+ '\n'.join(c['lines'])+'\n' for i,c in enumerate(cues,1))
    for key,text in [('ass_path',ass),('story_srt_path',srt),('packaged_srt_path',packaged)]:
        path=dub.relative(settings[key]);path.parent.mkdir(parents=True,exist_ok=True)
        if path.exists() and path.read_text()!=text:raise ValueError('Subtitle output changed; select a new version.')
        if not path.exists():dub.write_new(path,text.encode())
    report={'language':settings['language'],'cues':cues,'settings':settings,'source':'Selected verified dialogue and actual fitted render windows','ass_sha256':hashlib.sha256(ass.encode()).hexdigest(),'status':'generated_pending_encoded_visual_review'}
    dest=dub.relative(settings['report_path'])
    if not dest.exists():dub.write_new(dest,(json.dumps(report,indent=2,ensure_ascii=False)+'\n').encode())
    print(f'Created {len(cues)} timed subtitle cues; no subtitles on brand bumpers.')
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('manifest');p.add_argument('settings');a=p.parse_args()
    try:generate(dub.load(dub.relative(a.manifest,True)),dub.load(dub.relative(a.settings,True)))
    except (ValueError,OSError,KeyError) as e:p.exit(1,f'Error: {e}\n')

if __name__=='__main__':main()
