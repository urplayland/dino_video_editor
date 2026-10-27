#!/usr/bin/env python3
"""Add reusable FLH cards/logo to a verified episode without regenerating voices."""
from array import array
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile

import dub


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def qpath(path):
    return "'" + str(path).replace('\\', '\\\\').replace("'", "'\\''").replace(':', '\\:') + "'"


def settings(manifest):
    if manifest.get('schema_version') != 1:
        raise ValueError('Unsupported branding manifest version.')
    cfg = dub.load(dub.relative(manifest['brand_config'], True))
    for asset in cfg['assets'].values():
        path = dub.relative(asset['path'], True)
        if digest(path) != asset['sha256']:
            raise ValueError('Brand asset changed; version and review it before rendering.')
    for key in ('intro_duration_s','outro_duration_s'):
        dub.number(cfg[key],key,.5,10)
    return cfg



def text_layer(text, font, size, color, y, path):
    """Rasterize new Unicode text; existing logo/mascot artwork is untouched."""
    if path.exists():
        return
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        raise ValueError('Install requirements-branding.txt to render localized Unicode title text.') from None
    image=Image.new('RGBA',(720,1280),(0,0,0,0))
    face=ImageFont.truetype(str(font),size)
    ImageDraw.Draw(image).text((360,y),text,font=face,fill='#'+color,anchor='mt')
    image.save(path)


def decoration_layer(path):
    if path.exists():
        return
    from PIL import Image,ImageDraw
    layer=Image.new('RGBA',(720,1280),(0,0,0,0))
    d=ImageDraw.Draw(layer)
    d.ellipse((-145,-110,175,210),fill='#EAF7FF')
    d.ellipse((592,1000,884,1292),fill='#EEF8E7')
    d.ellipse((18,1120,166,1268),fill='#FFF2CE')
    d.ellipse((632,170,770,308),fill='#F3EBF8')
    d.arc((468,12,780,324),125,295,fill='#D9EAF2',width=4)
    d.arc((-116,925,182,1223),280,95,fill='#E9DFC9',width=4)
    for x,y,r,color in [(120,98,7,'#1CB0F6'),(615,418,6,'#58CC02'),(98,624,7,'#FFC800'),(600,880,7,'#8549BA'),(188,1180,5,'#1CB0F6')]:
        d.ellipse((x-r,y-r,x+r,y+r),fill=color)
    layer.save(path)


def title_card(manifest,cfg,kind,target):
    if target.exists():
        return
    work=dub.relative(manifest['work_dir']);work.mkdir(parents=True,exist_ok=True)
    head=dub.relative(cfg['assets']['Outfit-800.ttf']['path'],True)
    body=dub.relative(cfg['assets']['Nunito-700.ttf']['path'],True)
    locale_head=dub.relative(manifest['title_font'],True) if manifest.get('title_font') else head
    locale_body=dub.relative(manifest['body_font'],True) if manifest.get('body_font') else body
    sources=[dub.relative(cfg['assets']['logo.png']['path'],True)]
    animated=cfg.get('animation',{}).get('enabled',False)
    static_owl=kind=='outro' and not animated
    if static_owl:
        sources.append(dub.relative(cfg['assets']['mascot.png']['path'],True))
    background='0:v'
    filters=[]
    if animated:
        decor=work/'playful-decoration.png';decoration_layer(decor)
        index=len(sources)+1;sources.append(decor)
        filters.append(f'[0:v][{index}:v]overlay=0:0[decorated]')
        background='decorated'
    if kind=='intro':
        logo_size,logo_y=224,190
        lines=[(cfg['brand'],44,466,head,cfg['text_color']),
               (manifest.get('presents_text','presents'),28,534,locale_body,cfg['secondary_color']),
               (manifest['series'],52,702,head,cfg['accent']),
               (manifest['title_lines'][0],56,804,locale_head,cfg['text_color']),
               (manifest['title_lines'][1],56,876,locale_head,cfg['text_color']),
               (cfg['website'],27,1132,body,cfg['secondary_color'])]
    else:
        logo_size,logo_y=164,150
        lines=[(cfg['brand'],42,370,head,cfg['text_color']),
               (manifest.get('ending_text','The End'),56,472,locale_head,cfg['accent']),
               (manifest['series'],32,560,head,cfg['text_color']),
               (cfg['website'],30,990,body,cfg['text_color']),
               (manifest.get('thanks_text','Thank you for watching'),28,1090,locale_body,cfg['secondary_color'])]
    filters += [f'[1:v]scale={logo_size}:{logo_size},format=rgba[logo]',f'[{background}][logo]overlay=(W-w)/2:{logo_y}[card0]']
    previous='card0'
    if static_owl:
        filters += ['[2:v]scale=232:-1,format=rgba[owl]','[card0][owl]overlay=(W-w)/2:630[card1]'];previous='card1'
    elif kind=='intro':
        filters.append('[card0]drawbox=x=320:y=608:w=80:h=6:color=0x'+cfg['accent']+':t=fill[card1]');previous='card1'
    for i,(text,size,y,font,color) in enumerate(lines):
        textfile=work/f'{kind}-text-{i}.txt';textfile.write_text(text,encoding='utf-8');label=f'text{i}'
        if any(ord(c)>127 for c in text):
            layer=work/f'{kind}-text-{i}-layer.png';text_layer(text,font,size,color,y,layer)
            index=len(sources)+1;sources.append(layer)
            filters += [f'[{index}:v]format=rgba[words{i}]',f'[{previous}][words{i}]overlay=0:0[{label}]']
        else:
            filters.append(f'[{previous}]drawtext=fontfile={qpath(font)}:textfile={qpath(textfile)}:fontsize={size}:fontcolor=0x{color}:x=(w-tw)/2:y={y}[{label}]')
        previous=label
    args=[dub.tool('ffmpeg'),'-v','error','-nostdin','-n','-f','lavfi','-i',f'color=c=0x{cfg["background"]}:s=720x1280:r=24']
    for source in sources:args += ['-i',str(source)]
    dub.run([*args,'-filter_complex',';'.join(filters),'-map',f'[{previous}]','-frames:v','1','-update','1',str(target)])


def card_media(manifest,cfg,intro,outro):
    if not cfg.get('animation',{}).get('enabled',False):
        return intro,outro
    work=dub.relative(manifest['work_dir'])
    result=[]
    for kind,base,duration in [('intro',intro,cfg['intro_duration_s']),('outro',outro,cfg['outro_duration_s'])]:
        target=work/f'{kind}-animated.mp4';result.append(target)
        if target.exists():continue
        star=dub.relative(cfg['assets']['star.webp']['path'],True)
        moon=dub.relative(cfg['assets']['moon.webp']['path'],True)
        args=[dub.tool('ffmpeg'),'-v','error','-nostdin','-n']
        for source in [base,star,moon]:args += ['-loop','1','-framerate','24','-i',str(source)]
        filters=[
            '[1:v]format=rgba,split=3[s1][s2][s3]',
            '[s1]scale=64:64,rotate=0.07*sin(2*PI*t/3):ow=84:oh=84:c=none[star1]',
            '[s2]scale=42:42,rotate=-0.09*sin(2*PI*t/2.8):ow=56:oh=56:c=none[star2]',
            '[s3]scale=32:32,rotate=0.08*sin(2*PI*t/3.2):ow=44:oh=44:c=none[star3]',
            '[2:v]scale=84:84,rotate=0.035*sin(2*PI*t/3):ow=104:oh=104:c=none[moon]',
            '[0:v][star1]overlay=x=58+4*sin(2*PI*t/3):y=260+8*sin(2*PI*t/3):shortest=1[c1]',
            '[c1][star2]overlay=x=609+3*sin(2*PI*t/2.8):y=655+7*sin(2*PI*t/2.8):shortest=1[c2]',
            '[c2][star3]overlay=x=104:y=967+6*sin(2*PI*t/3.2):shortest=1[c3]',
            '[c3][moon]overlay=x=548:y=70+5*sin(2*PI*t/3):shortest=1[c4]',
        ]
        last='c4'
        if kind=='outro':
            owl=dub.relative(cfg['assets']['mascot.png']['path'],True)
            args += ['-loop','1','-framerate','24','-i',str(owl)]
            filters += ['[3:v]scale=260:-1,format=rgba,rotate=0.045*sin(2*PI*t/2.4):ow=312:oh=260:c=none,fade=t=in:d=0.18:alpha=1[owl]',
                        '[c4][owl]overlay=x=(W-w)/2:y=600+36*exp(-5*t)*cos(10*t)+7*sin(2*PI*t/2.4):shortest=1[c5]']
            last='c5'
        filters.append(f'[{last}]format=yuv420p[view]')
        dub.run([*args,'-filter_complex',';'.join(filters),'-map','[view]','-t',str(duration),'-an','-c:v','libx264','-preset','veryfast','-crf','17','-threads','2','-r','24','-pix_fmt','yuv420p',str(target)],timeout=180)
    return tuple(result)


def caption_filter(manifest):
    if not manifest.get('subtitles'):
        return None
    sub=dub.load(dub.relative(manifest['subtitles'],True))
    ass_filter=f"ass=filename={qpath(dub.relative(sub['ass_path'],True))}:fontsdir={qpath(dub.relative(sub['font_path'],True).parent)}"
    if sub.get('layout')=='overlay':
        return ass_filter
    width,height,x=sub['picture_width'],sub['picture_height'],sub['picture_x']
    if (width,height,x)!=(630,1120,45) or sub['margin_bottom']<30:
        raise ValueError('Invalid reserved subtitle layout.')
    return f"scale={width}:{height},pad=720:1280:{x}:0:color=0x{sub['background']},"+ass_filter


def preview(manifest,cfg):
    work=dub.relative(manifest['work_dir']);previews=dub.relative(manifest['preview_dir'])
    work.mkdir(parents=True,exist_ok=True);previews.mkdir(parents=True,exist_ok=True)
    stamp=work/'preview-provenance.json'
    identity=hashlib.sha256(json.dumps({'manifest':manifest,'brand':cfg},sort_keys=True).encode()).hexdigest()
    if stamp.exists() and dub.load(stamp).get('fingerprint')!=identity:
        raise ValueError('Brand preview settings changed; choose new work/preview directories.')
    intro,outro=work/'intro.png',work/'outro.png'
    if cfg.get('animation',{}).get('type')=='logo_bumper':
        from logo_bumper import make_clips
        intro_media,outro_media=make_clips(manifest,cfg)
    else:
        title_card(manifest,cfg,'intro',intro);title_card(manifest,cfg,'outro',outro)
        intro_media,outro_media=card_media(manifest,cfg,intro,outro)
    shown=[]
    for kind,media in [('intro',intro_media),('outro',outro_media)]:
        if media.suffix=='.mp4':
            still=previews/f'{kind}-animated-preview.png'
            if not still.exists():dub.run([dub.tool('ffmpeg'),'-v','error','-nostdin','-n','-ss','1.2','-i',str(media),'-frames:v','1','-update','1',str(still)])
            shown.append(still)
        else:shown.append(media)
    body=previews/'body.png'
    if not body.exists():
        mark=cfg['watermark'];source=dub.relative(manifest['source_video'],True)
        if mark.get('enabled',True):
            logo=dub.relative(cfg['assets']['logo.png']['path'],True)
            graph=f'[1:v]scale={mark["size_px"]}:{mark["size_px"]},format=rgba,colorchannelmixer=aa={mark["opacity"]}[logo];[0:v][logo]overlay={mark["x"]}:{mark["y"]}:eof_action=repeat[view]'
            dub.run([dub.tool('ffmpeg'),'-v','error','-nostdin','-n','-ss','12','-i',str(source),'-i',str(logo),'-filter_complex',graph,'-map','[view]','-frames:v','1','-update','1',str(body)])
        else:
            captions=caption_filter(manifest)
            dub.run([dub.tool('ffmpeg'),'-v','error','-nostdin','-n','-i',str(source),*(['-vf',captions] if captions else []),'-ss','12','-frames:v','1','-update','1',str(body)])
    sheet=previews/'brand-preview.png'
    if not sheet.exists():dub.run([dub.tool('ffmpeg'),'-v','error','-nostdin','-n','-i',str(shown[0]),'-i',str(body),'-i',str(shown[1]),'-filter_complex','[0:v]scale=360:640[a];[1:v]scale=360:640[b];[2:v]scale=360:640[c];[a][b][c]hstack=inputs=3[view]','-map','[view]','-frames:v','1','-update','1',str(sheet)])
    if not stamp.exists():dub.write_new(stamp,(json.dumps({'fingerprint':identity,'manifest':manifest,'brand_config':cfg},indent=2)+'\n').encode())
    print(sheet.relative_to(dub.ROOT))
    return intro_media,outro_media


def decoded_audio(path, start, duration):
    graph = f'atrim=start={start}:duration={duration},asetpts=N/SR/TB,aresample=8000,apad=whole_dur={duration},asetpts=N/SR/TB,atrim=duration={duration}'
    result = subprocess.run([dub.tool('ffmpeg'),'-v','error','-nostdin','-i',str(path),'-vn','-af',graph,'-ac','1','-f','s16le','-'],capture_output=True,timeout=180,check=False)
    if result.returncode:
        raise ValueError('Cannot decode comparison audio.')
    values = array('h',result.stdout)
    if sys.byteorder != 'little':
        values.byteswap()
    return values


def audio_similarity(source, packaged, offset, duration):
    original = decoded_audio(source,0,duration)
    branded = decoded_audio(packaged,offset,duration)
    count = min(len(original),len(branded))
    if abs(len(original)-len(branded)) > 16 or not count:
        raise ValueError(f'Packaged story audio duration differs from its source: source={len(original)} samples, branded={len(branded)} samples at 8000 Hz.')
    dot = sum(a*b for a,b in zip(original,branded))
    left = sum(a*a for a in original[:count])
    right = sum(a*a for a in branded[:count])
    correlation = dot/math.sqrt(left*right) if left and right else 0
    if correlation < .98:
        raise ValueError(f'Packaged story audio does not match the source closely enough ({correlation:.4f}).')
    return correlation


def guard_encoded_peak(movie,work,total,measurement):
    """Catch AAC intersample overshoot after joining clips; keep picture untouched."""
    if float(measurement['input_tp'])<=-.8:
        return movie,measurement,None
    # Limit only transient peaks, oversampled to protect intersample amplitude.
    graph='aresample=192000,alimiter=limit=0.79:level=false:attack=5:release=50:latency=1,aresample=48000'
    target=work/'peak-guarded-brand.mp4';stamp=target.with_suffix('.json')
    expected={'source_sha256':digest(movie),'audio_filter':graph,'duration_s':total}
    if target.exists():
        if not stamp.exists():raise ValueError('Peak-guard cache lacks provenance; choose a new work version.')
        record=dub.load(stamp)
        if any(record.get(k)!=v for k,v in expected.items()) or record.get('output_sha256')!=digest(target):
            raise ValueError('Peak-guard cache is stale or changed.')
    else:
        dub.run([dub.tool('ffmpeg'),'-v','error','-nostdin','-n','-i',str(movie),'-map','0:v:0','-map','0:a:0',
                 '-c:v','copy','-af',graph,'-c:a','aac','-b:a','192k','-ar','48000','-ac','2','-t',str(total),'-movflags','+faststart',str(target)],timeout=300)
        after=dub.loudness_info(target)
        if float(after['input_tp'])>-.8 or abs(float(after['input_i'])+16)>1:
            raise ValueError('Final AAC peak guard did not meet unchanged loudness/peak checks.')
        if dub.video_hash(movie)!=dub.video_hash(target):raise ValueError('Audio peak repair changed picture packets.')
        record=dict(expected,output_sha256=digest(target),before=measurement,after=after,picture_packets_unchanged=True)
        dub.write_new(stamp,(json.dumps(record,indent=2)+'\n').encode())
    return target,record['after'],record


def render(manifest, cfg):
    source = dub.relative(manifest['source_video'],True)
    original_report = dub.load(source.with_suffix('.json'))
    if original_report.get('output_sha256') != digest(source):
        raise ValueError('English source export no longer matches its verification report.')
    subtitle_provenance=None
    if manifest.get('subtitles'):
        import production
        from subtitles import generate
        episode=dub.load(dub.relative(manifest['source_manifest'],True))
        expected=production.language_manifest(episode,manifest['language'])
        if original_report.get('manifest')!=expected:
            expected_dialogue={key:expected[key] for key in ('language','duration_s','dialogue')}
            if original_report.get('dialogue_manifest')!=expected_dialogue:
                raise ValueError('Subtitle dialogue does not match the selected rendered source.')
        sub=dub.load(dub.relative(manifest['subtitles'],True))
        subtitle_provenance=generate(episode,sub)
    source_info = dub.probe(source)
    duration = float(source_info['format']['duration'])
    if abs(duration-manifest['source_duration_s']) > .01:
        raise ValueError('Unexpected source story duration.')
    output = dub.relative(manifest['output'])
    if output.exists() or output.with_suffix('.json').exists():
        raise ValueError('Brand export exists; choose a new version.')
    intro,outro = preview(manifest,cfg)
    logo = dub.relative(cfg['assets']['logo.png']['path'],True)
    music = dub.relative(manifest['music'],True)
    music_length = float(dub.probe(music)['format']['duration'])
    lead,tail = cfg['intro_duration_s'],cfg['outro_duration_s']
    total = duration+lead+tail
    mark = cfg['watermark']
    graph = [
        '[0:v]format=yuv420p,setsar=1,settb=AVTB,setpts=PTS-STARTPTS[opening]',
        *([f'[3:v]scale={mark["size_px"]}:{mark["size_px"]},format=rgba,colorchannelmixer=aa={mark["opacity"]}[logo]',
           f'[1:v][logo]overlay={mark["x"]}:{mark["y"]}:eof_action=repeat:shortest=1,format=yuv420p,setsar=1,settb=AVTB,setpts=PTS-STARTPTS[story]']
          if mark.get('enabled',True) else ['[1:v]format=yuv420p,setsar=1,settb=AVTB,setpts=PTS-STARTPTS[story]']),
        '[2:v]format=yuv420p,setsar=1,settb=AVTB,setpts=PTS-STARTPTS[closing]',
        '[opening][story][closing]concat=n=3:v=1:a=0[video]',
        '[4:a]asplit=2[mlead][mtail]',
        f'[mlead]atrim=duration={lead},asetpts=N/SR/TB,aresample=48000,aformat=channel_layouts=stereo,volume=0.5,afade=t=in:d=0.12,afade=t=out:st={lead-.25}:d=0.25[ai]',
        f'[1:a]atrim=duration={duration},apad=whole_dur={duration},asetpts=N/SR/TB,aresample=48000,aformat=channel_layouts=stereo,atrim=duration={duration}[ab]',
        f'[mtail]atrim=start={music_length-tail}:duration={tail},asetpts=N/SR/TB,aresample=48000,aformat=channel_layouts=stereo,volume=0.5,afade=t=in:d=0.12,afade=t=out:st={tail-.5}:d=0.5[ao]',
        *(['[5:a]asplit=2[sting1][sting2]',
           f'[sting1]atrim=duration={lead},asetpts=N/SR/TB,aresample=48000,aformat=channel_layouts=stereo[si]',
           f'[sting2]atrim=duration={tail},asetpts=N/SR/TB,aresample=48000,aformat=channel_layouts=stereo[so]',
           '[ai][si]amix=inputs=2:normalize=0[opening_audio]',
           '[ao][so]amix=inputs=2:normalize=0[closing_audio]',
           '[opening_audio][ab][closing_audio]concat=n=3:v=0:a=1[audio]']
          if cfg.get('sonic_logo') else ['[ai][ab][ao]concat=n=3:v=0:a=1[audio]']),
    ]
    captions=caption_filter(manifest)
    if captions:
        graph[3:4]=[f'[story]{captions}[captioned_story]', '[opening][captioned_story][closing]concat=n=3:v=1:a=0[video]'] if not mark.get('enabled',True) else graph[3:4]
        if mark.get('enabled',True):
            raise ValueError('Caption layout requires the approved watermark-free story.')
    output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='brand-',dir=output.parent) as tmp:
        staged = dub.relative(manifest['work_dir'])/'encoded-brand.mp4'
        stage_inputs=staged.with_suffix('.inputs.json')
        expected_inputs={'source_sha256':digest(source),'manifest':manifest,'brand_config':cfg,'subtitles':subtitle_provenance}
        if staged.exists():
            if not stage_inputs.exists():
                raise ValueError('Staged branding encode lacks provenance; choose a new work version.')
            cached=dub.load(stage_inputs)
            if any(cached.get(k)!=v for k,v in expected_inputs.items()) or cached.get('encoded_sha256')!=digest(staged):
                raise ValueError('Staged branding encode is stale or changed; choose a new work version.')
        movie = staged if staged.exists() else Path(tmp)/'branded.mp4'
        intro_args=['-i',str(intro)] if intro.suffix=='.mp4' else ['-loop','1','-framerate','24','-t',str(lead),'-i',str(intro)]
        outro_args=['-i',str(outro)] if outro.suffix=='.mp4' else ['-loop','1','-framerate','24','-t',str(tail),'-i',str(outro)]
        args=[dub.tool('ffmpeg'),'-v','error','-nostdin','-n',*intro_args,
              '-i',str(source),*outro_args,
              '-loop','1','-framerate','24','-i',str(logo),'-i',str(music),
              *(['-i',str(dub.relative(cfg['sonic_logo'],True))] if cfg.get('sonic_logo') else []),
              '-filter_complex',';'.join(graph),'-map','[video]','-map','[audio]','-t',str(total),
              '-c:v','libx264','-preset','medium','-crf','18','-threads','4','-pix_fmt','yuv420p',
              '-fps_mode:v','passthrough','-enc_time_base:v','1:15360','-c:a','aac','-b:a','192k','-ar','48000','-ac','2','-movflags','+faststart',str(movie)]
        if not staged.exists():
            dub.run(args,timeout=1800)
            dub.write_new(staged,movie.read_bytes())
            movie=staged
            dub.write_new(stage_inputs,(json.dumps(dict(expected_inputs,encoded_sha256=digest(staged)),indent=2)+'\n').encode())
        info=dub.probe(movie)
        if abs(float(info['format']['duration'])-total)>.12:
            raise ValueError('Branded duration check failed.')
        expected_frames = int(next(s for s in source_info['streams'] if s['codec_type']=='video')['nb_frames']) + round(24*lead) + round(24*tail)
        actual_frames = int(next(s for s in info['streams'] if s['codec_type']=='video')['nb_frames'])
        if actual_frames != expected_frames:
            raise ValueError('Branding lost or duplicated picture frames.')
        dub.run([dub.tool('ffmpeg'),'-v','error','-nostdin','-i',str(movie),'-f','null','-'],timeout=900)
        measured=dub.loudness_info(movie)
        movie,measured,final_audio_mastering=guard_encoded_peak(movie,dub.relative(manifest['work_dir']),total,measured)
        info=dub.probe(movie)
        if int(next(stream for stream in info['streams'] if stream['codec_type']=='video')['nb_frames'])!=expected_frames:
            raise ValueError('Audio peak repair changed video frame count.')
        if abs(float(measured['input_i'])+16)>1 or float(measured['input_tp'])>-.8:
            raise ValueError('Branded loudness/peak check failed.')
        correlation=audio_similarity(source,movie,lead,duration)
        if digest(source)!=original_report['output_sha256']:
            raise ValueError('Source export changed during branding.')
        info['format']['filename']=manifest['output']
        report={'status':'technical_checks_passed_pending_owner_branding_review','manifest':manifest,'brand_config':cfg,
            'source_sha256':digest(source),'output_sha256':digest(movie),'source_story_duration_s':duration,'intro_duration_s':lead,
            'outro_duration_s':tail,'story_offset_s':lead,'story_audio_correlation':correlation,'encoded_audio_measurement':measured,
            'output_metadata':info,'ffmpeg_version':dub.run([dub.tool('ffmpeg'),'-version']).stdout.splitlines()[0],
            'picture_processing':'Complete story retained; derived picture encoded to join brand cards. Unbranded original unchanged.',
            'story_watermark_applied':mark.get('enabled',True),'animated_brand_cards':cfg.get('animation',{}).get('enabled',False),
            'final_audio_mastering':final_audio_mastering, 'subtitles':subtitle_provenance, 'api_calls':0, 'expected_video_frames':expected_frames, 'actual_video_frames':actual_frames}
        dub.write_new(output,movie.read_bytes())
        dub.write_new(output.with_suffix('.json'),(json.dumps(report,indent=2)+'\n').encode())
    print(f'Rendered {manifest["output"]} ({total:.6f}s), story audio correlation {correlation:.6f}.')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('manifest')
    p.add_argument('command',choices=('preview','render'))
    args=p.parse_args()
    try:
        manifest=dub.load(dub.relative(args.manifest,True))
        cfg=settings(manifest)
        if args.command=='preview':
            preview(manifest,cfg)
        else:
            render(manifest,cfg)
    except (ValueError,OSError,KeyError,TypeError) as exc:
        p.exit(1,f'Error: {exc}\n')


if __name__=='__main__':
    main()
