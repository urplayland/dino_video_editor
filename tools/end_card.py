#!/usr/bin/env python3
"""Render a reusable FLH motion-graphics ending, preserving the input picture."""
import argparse
import hashlib
import json
import math
import subprocess

import dub
from logo_bumper import clamp


def render(settings):
    from PIL import Image, ImageDraw, ImageFont
    cfg = dub.load(dub.relative(settings['brand_config'], True))
    target = dub.relative(settings['output'])
    target.parent.mkdir(parents=True, exist_ok=True)
    provenance = {'settings': settings, 'brand': cfg}
    for name in ('title_font_path','series_font_path'):
        if settings.get(name):
            provenance[name+'_sha256'] = hashlib.sha256(dub.relative(settings[name],True).read_bytes()).hexdigest()
    identity = hashlib.sha256(json.dumps(provenance, sort_keys=True).encode()).hexdigest()
    report = target.with_suffix('.json')
    if target.exists():
        old = dub.load(report)
        if old['fingerprint'] != identity or old['sha256'] != hashlib.sha256(target.read_bytes()).hexdigest():
            raise ValueError('End card changed; choose a new version.')
        return target
    logo = Image.open(dub.relative(cfg['assets']['logo.png']['path'], True)).convert('RGBA')
    heading = str(dub.relative(cfg['assets']['Outfit-800.ttf']['path'], True))
    body = str(dub.relative(cfg['assets']['Nunito-700.ttf']['path'], True))
    title_path = str(dub.relative(settings['title_font_path'],True)) if settings.get('title_font_path') else heading
    series_path = str(dub.relative(settings['series_font_path'],True)) if settings.get('series_font_path') else body
    title_font = ImageFont.truetype(title_path, settings.get('title_font_size',102), index=settings.get('title_font_index',0))
    series_font = ImageFont.truetype(series_path, settings.get('series_font_size',31), index=settings.get('series_font_index',0))
    if title_font.getlength(settings.get('title','THE END'))>620 or series_font.getlength(settings.get('series','Dino Adventures'))>620:
        raise ValueError('Localized ending text exceeds its safe width.')
    brand_font = ImageFont.truetype(heading, 32)
    website_font = ImageFont.truetype(body, 26)
    palette = cfg['playful_palette']
    frames = round(settings['duration_s'] * 24)
    cmd = [dub.tool('ffmpeg'), '-v', 'error', '-nostdin', '-n', '-f', 'rawvideo', '-pixel_format', 'rgb24', '-video_size', '720x1280', '-framerate', '24', '-i', '-', '-an', '-frames:v', str(frames), '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '17', '-threads', '2', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(target)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        for n in range(frames):
            t = n / 24
            canvas = Image.new('RGBA', (720, 1280), '#' + cfg['background'])
            draw = ImageDraw.Draw(canvas)
            drift = 7 * math.sin(t * 1.5)
            draw.rounded_rectangle((-155, 125+drift, 100, 390+drift), radius=90, fill='#'+palette['blue_tint'])
            draw.ellipse((598, 270-drift, 790, 462-drift), fill='#'+palette['yellow_tint'])
            draw.rounded_rectangle((615, 950+drift, 855, 1200+drift), radius=85, fill='#'+palette['green_tint'])
            draw.ellipse((-75, 1070, 95, 1240), fill='#'+palette['purple_tint'])
            u = clamp((t-.12)/.65)
            ease = 1+2.2*(u-1)**3+1.2*(u-1)**2
            layer = Image.new('RGBA', canvas.size)
            ld = ImageDraw.Draw(layer)
            y = round(565+35*(1-ease))
            ld.text((360, y+5), settings.get('title', 'THE END'), font=title_font, anchor='mm', fill='#'+palette['blue_rim'])
            ld.text((360, y), settings.get('title', 'THE END'), font=title_font, anchor='mm', fill='#'+palette['blue'])
            for j, color in enumerate(('blue', 'green', 'yellow', 'purple')):
                x = 281+j*44
                ld.rounded_rectangle((x, 659, x+26, 666), radius=3, fill='#'+palette[color])
            for i, (x, sy) in enumerate(((157, 465), (571, 486), (128, 659), (599, 648))):
                size = 4+3*(.5+.5*math.sin(t*2+i))
                ld.line((x-size, sy, x+size, sy), fill='#'+palette['yellow'], width=3)
                ld.line((x, sy-size, x, sy+size), fill='#'+palette['yellow'], width=3)
            if u < 1:
                layer.putalpha(layer.getchannel('A').point([round(a*u) for a in range(256)]))
            canvas.alpha_composite(layer)
            # Brand assets live in the lower third, clear of the central title.
            v = clamp((t-.65)/.45)
            lower = Image.new('RGBA', canvas.size)
            mark = logo.resize((108, 108), Image.Resampling.LANCZOS)
            lower.alpha_composite(mark, (306, 806))
            ld = ImageDraw.Draw(lower)
            ld.text((360, 947), cfg['brand'], font=brand_font, anchor='mm', fill='#'+cfg['text_color'])
            ld.text((360, 993), settings.get('series', 'Dino Adventures'), font=series_font, anchor='mm', fill='#'+cfg['secondary_color'])
            ld.rounded_rectangle((140, 1040, 580, 1101), radius=30, fill='#'+palette['blue_rim'])
            ld.rounded_rectangle((140, 1034, 580, 1094), radius=30, fill='#'+palette['blue'])
            ld.text((360, 1064), cfg['website'], font=website_font, anchor='mm', fill='white')
            if v < 1:
                lower.putalpha(lower.getchannel('A').point([round(a*v) for a in range(256)]))
            canvas.alpha_composite(lower)
            proc.stdin.write(canvas.convert('RGB').tobytes())
        proc.stdin.close()
        error = proc.stderr.read().decode(errors='replace')
        if proc.wait(timeout=180):
            raise ValueError('End-card encoder failed: '+error[-1000:])
    except BaseException:
        if proc.poll() is None:
            proc.terminate()
            proc.wait(timeout=10)
        raise
    info = dub.probe(target)
    if int(info['streams'][0]['nb_frames']) != frames:
        raise ValueError('End-card frame count mismatch.')
    dub.write_new(report, (json.dumps({'fingerprint': identity, 'sha256': hashlib.sha256(target.read_bytes()).hexdigest(), 'settings': settings, 'frames': frames, 'status': 'rendered_pending_owner_visual_review'}, indent=2)+'\n').encode())
    return target


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('settings')
    args = p.parse_args()
    print(render(dub.load(dub.relative(args.settings, True))))
