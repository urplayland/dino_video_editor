#!/usr/bin/env python3
"""Build FLH channel-art layouts from supplied artwork, fonts and episode stills.

Font outlines and native SVG layouts preserve exact logos and lettering; FFmpeg's
librsvg decoder exports upload files. No artwork or animation is regenerated.
"""
import argparse
import base64
import html
import json
from pathlib import Path
import subprocess

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont
import dub


def build(config_path):
    cfg = dub.load(dub.relative(config_path, True))
    root = dub.relative(cfg['output_dir'])
    out = root/'01_Channel_Branding'
    covers = root/'02_Episode_Covers'
    source = root/'05_Editable_Source'
    review = root/'03_Previews'
    for folder in (out, covers, source, review):
        folder.mkdir(parents=True, exist_ok=True)
    faces = {}
    for name, item in cfg['fonts'].items():
        font = TTFont(dub.relative(item['path'], True), fontNumber=item.get('index', 0))
        faces[name] = (font, font.getGlyphSet(), font.getBestCmap(), font['head'].unitsPerEm)
    cream, ink, blue = '#FFFDF9', '#4B4B4B', '#1CB0F6'
    def glyphs(text, face='heading'):
        result = []
        for char in text:
            key = face if ord(char) in faces[face][2] else 'chinese'
            font, glyphset, cmap, upm = faces[key]
            if ord(char) not in cmap:
                raise ValueError('Missing glyph: '+char)
            name = cmap[ord(char)]
            result.append((glyphset[name], font['hmtx'][name][0], upm))
        return result
    def width(text, size, face='heading'):
        return sum(advance/upm*size for _, advance, upm in glyphs(text, face))
    def text(value, x, y, size, color=ink, face='heading', maximum=None):
        if maximum:
            size = min(size, size*maximum/max(1, width(value, size, face)))
        paths = []
        cursor = x
        for glyph, advance, upm in glyphs(value, face):
            pen = SVGPathPen(None)
            glyph.draw(pen)
            paths.append(f'<path d="{pen.getCommands()}" transform="translate({cursor} {y}) scale({size/upm} {-size/upm})"/>')
            cursor += advance/upm*size
        return f'<g fill="{color}" aria-label="{html.escape(value, quote=True)}">'+''.join(paths)+'</g>'
    def image(path, x, y, w, h, fit='xMidYMid meet'):
        p = dub.relative(path, True)
        mime = 'image/jpeg' if p.suffix in ('.jpg', '.jpeg') else 'image/png'
        data = base64.b64encode(p.read_bytes()).decode()
        return f'<image x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="{fit}" href="data:{mime};base64,{data}"/>'
    def rect(x, y, w, h, radius, color):
        return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{color}"/>'
    def svg(w, h, body):
        return f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{body}</svg>'
    def render(name, document, target, max_bytes=None):
        editable = source/(name+'.svg')
        editable.write_text(document, encoding='utf-8')
        if target.exists():
            raise ValueError('Refusing to overwrite artwork: '+str(target))
        args = [dub.tool('ffmpeg'), '-v', 'error', '-nostdin', '-n', '-i', str(editable), '-frames:v', '1']
        if target.suffix == '.jpg':
            args += ['-q:v', '4']
        dub.run(args+[str(target)], timeout=180)
        if max_bytes and target.stat().st_size > max_bytes:
            raise ValueError('Artwork exceeds upload size target: '+str(target))
        return target
    logo = cfg['logo']
    background = cfg['background']
    still = cfg['episode_still']
    banner = rect(0, 0, 2560, 1440, 0, cream)+image(background, 0, 0, 2560, 1440, 'xMidYMid slice')
    banner += image(logo, 565, 567, 290, 290)
    banner += text('Family Learning Hub', 910, 643, 86, maximum=1080)
    banner += text('Stories, learning & little adventures', 914, 713, 45, face='body', maximum=1055)
    banner += text('English · 中文 · Bahasa Melayu', 916, 772, 35, face='body', maximum=1030)
    banner += rect(912, 804, 660, 63, 31, '#1899D6')+rect(912, 798, 660, 63, 31, blue)
    banner += text('familylearninghub.com', 960, 841, 38, '#FFFFFF', 'body', maximum=565)
    render('channel-banner-2560x1440', svg(2560, 1440, banner), out/'channel-banner-2560x1440.png', 6_000_000)
    profile = rect(0, 0, 800, 800, 0, cream)+image(logo, 120, 120, 560, 560)
    render('channel-avatar-800', svg(800, 800, profile), out/'channel-avatar-800.png', 2_000_000)
    render('optional-watermark-150', svg(150, 150, image(logo, 0, 0, 150, 150)), out/'optional-watermark-150.png', 1_000_000)
    for lang, localized in cfg['languages'].items():
        body = rect(0, 0, 3840, 2160, 0, cream)
        body += image(background, 0, 0, 3840, 2160, 'xMidYMid slice')
        body += rect(120, 300, 2110, 1430, 120, cream)
        body += image(logo, 155, 150, 235, 235)
        body += text('Family Learning Hub', 425, 306, 90, maximum=1560)
        body += text('Dino Adventures', 210, 610, 96, '#8549BA', maximum=1830)
        for index, line in enumerate(localized['landscape_lines']):
            body += text(line, 205, 930+index*280, 242, maximum=1880)
        body += rect(210, 1550, 940, 116, 58, blue)
        body += text(localized['label'], 270, 1629, 62, '#FFFFFF', 'body', maximum=800)
        body += rect(2400, 102, 1280, 1960, 100, '#E5D8BB')+rect(2385, 82, 1280, 1960, 100, '#FFFFFF')
        body += image(still, 2420, 116, 1210, 1892)
        render('episode-cover-'+lang+'-3840x2160', svg(3840, 2160, body), covers/('episode-cover-'+lang+'-3840x2160.jpg'), 2_000_000)
        portrait = image(still, 0, 0, 2160, 3840)
        portrait += rect(80, 80, 1950, 250, 125, cream)+image(logo, 110, 104, 200, 200)
        portrait += text('Dino Adventures', 365, 254, 118, maximum=1510)
        portrait += rect(60, 3210, 2040, 560, 100, cream)
        for index, line in enumerate(localized['portrait_lines']):
            portrait += text(line, 150, 3420+index*200, 175, maximum=1850)
        render('episode-cover-'+lang+'-2160x3840', svg(2160, 3840, portrait), covers/('episode-cover-'+lang+'-2160x3840.jpg'), 2_000_000)
    # Crop previews use the same exported banner. Guides are never upload assets.
    input_banner = out/'channel-banner-2560x1440.png'
    for name, graph in [('banner-mobile-safe-preview', 'crop=1544:422:508:509'), ('banner-desktop-preview', 'crop=2560:422:0:509')]:
        target = review/(name+'.png')
        dub.run([dub.tool('ffmpeg'), '-v', 'error', '-n', '-i', str(input_banner), '-vf', graph, '-frames:v', '1', str(target)], timeout=120)
    report = {'schema_version': 1, 'config': config_path, 'banner_upload_size': [2560, 1440],
              'conservative_safe_region': {'x': 508, 'y': 509, 'width': 1544, 'height': 422},
              'essential_content_bounds': [565, 555, 1995, 870],
              'logo': 'Existing owner-approved H/star logo, unmodified',
              'font_export': 'Real Outfit/Nunito/Noto SC glyph outlines; no generated lettering',
              'episode_art': 'Actual original silent-master frame index 1440; not regenerated characters',
              'production_method': 'Generated background + native SVG logo/type layouts + FFmpeg exports',
              'files': [str(p.relative_to(root)) for p in sorted(out.glob('*'))]+[str(p.relative_to(root)) for p in sorted(covers.glob('*'))]}
    (review/'art-validation.json').write_text(json.dumps(report, indent=2)+'\n')
    print('Built', len(report['files']), 'upload assets and editable SVG sources.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('config')
    build(parser.parse_args().config)
