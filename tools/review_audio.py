#!/usr/bin/env python3
"""Offline, versioned dialogue edits and four-stem review mixes; no generation API.

Reuses the production timeline, score, subtitle and mastering engines. Source
stems and their generation records are immutable; edit decisions are separate.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import subprocess

import dub
import production
import scene_score
import sfx
import subtitles
from audio_production import timeline
from brand_video import caption_filter, decoded_audio
from review_mix_integrity import similarity

RATE = 48000


def review_options(cfg):
    version = cfg.get('output_version', 'v002')
    if not re.fullmatch(r'v\d{3}', version):
        raise ValueError('Review version must be v followed by three digits.')
    options = cfg.get('review_video', {})
    width = options.get('width', 720)
    if width not in (360, 540, 720):
        raise ValueError('Review width must be360,540 or720.')
    crf = options.get('crf', 23)
    if not isinstance(crf, int) or not 18 <= crf <= 32:
        raise ValueError('Review CRF must be an integer from18 to32.')
    preset = options.get('preset', 'fast')
    if preset not in ('fast', 'veryfast'):
        raise ValueError('Unsupported review encoding preset.')
    return version, width, crf, preset


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_pcm(path):
    import numpy as np
    result = subprocess.run([dub.tool('ffmpeg'), '-v', 'error', '-i', str(path),
        '-vn', '-ar', str(RATE), '-ac', '2', '-f', 'f32le', '-'], capture_output=True, check=True)
    return np.frombuffer(result.stdout, dtype='<f4').reshape(-1, 2).copy()


def take_pcm(spec, expected_text, voices, nonverbal=False):
    """Load a newly generated take only with matching voice/transcript provenance."""
    path = dub.relative(spec['path'], True)
    if sha(path) != spec['sha256']:
        raise ValueError('Replacement take checksum changed.')
    record = dub.load(path.with_suffix('.json'))
    check = dub.load(dub.relative(spec['verification_report'], True))
    state = 'passed_technical_nonverbal' if nonverbal else 'passed_automated'
    char = voices['characters'][spec['character']]
    if (char.get('approval_status') != 'voice_selection_approved'
            or check.get('status') != state or check.get('sha256') != spec['sha256']
            or check.get('expected_text') != expected_text or record.get('sha256') != spec['sha256']
            or record.get('character') != spec['character'] or record.get('language') != 'en'
            or record.get('model') != char['model'] or record.get('voice_version') != char['preset_version']
            or record['request']['generationConfig']['speechConfig']['voiceConfig']['voice'] != char['voice']
            or record['request']['contents'][0]['parts'][0]['text'] != expected_text):
        raise ValueError('Replacement take voice/text verification is missing or stale.')
    identity = {k:record[k] for k in ('model','voice_version','request')}
    if record['fingerprint'] != hashlib.sha256(json.dumps(identity,sort_keys=True,ensure_ascii=False).encode()).hexdigest():
        raise ValueError('Replacement take generation identity changed.')
    lo, hi = dub.speech_bounds(path.read_bytes())
    return read_pcm(path)[round(lo*RATE):round(hi*RATE)]


def write_pcm(path, pcm):
    path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([dub.tool('ffmpeg'), '-v', 'error', '-nostdin', '-n',
        '-f', 'f32le', '-ar', str(RATE), '-ac', '2', '-i', '-',
        '-c:a', 'pcm_s24le', str(path)], input=pcm.astype('<f4').tobytes(), check=True)


def active_bounds(pcm, rate=RATE):
    """Conservative energy edges, not word alignment; preserve quiet consonants."""
    import numpy as np
    peaks = np.max(np.abs(pcm), axis=1)
    active = np.flatnonzero(peaks > max(0.0003, float(peaks.max()) * .003))
    if not len(active):
        raise ValueError('No detectable speech in selected cue.')
    return max(0, active[0] / rate - .025), min(len(pcm) / rate, (active[-1] + 1) / rate + .045)


def duck_envelope(count, intervals, reduction_db, attack=.15, release=.3, rate=RATE):
    """Phrase-level automation, minimum of overlapping ramps (no syllable pumping)."""
    import numpy as np
    dub.number(reduction_db, 'duck reduction', 0, 24)
    if attack <= 0 or release <= 0:
        raise ValueError('Ducking ramps must be positive.')
    env = np.ones(count, dtype='float32')
    floor = 10 ** (-reduction_db / 20)
    for start, end in intervals:
        if start < 0 or end <= start or end > count / rate + 1e-6:
            raise ValueError('Speech interval exceeds stem.')
        lo, hi = round(start * rate), min(count, round(end * rate))
        a, b = max(0, lo - round(attack * rate)), min(count, hi + round(release * rate))
        env[a:lo] = np.minimum(env[a:lo], np.linspace(1, floor, lo-a, endpoint=False))
        env[lo:hi] = np.minimum(env[lo:hi], floor)
        env[hi:b] = np.minimum(env[hi:b], np.linspace(floor, 1, b-hi))
    return env


def immutable_json(path, value):
    data = (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError('Existing review metadata differs; use a new version: ' + str(path))
    else:
        dub.write_new(path, data)


def build(config_path):
    import numpy as np
    cfg = dub.load(config_path)
    if cfg.get('schema_version') != 1 or cfg.get('language') != 'en':
        raise ValueError('This review is explicitly English only.')
    version, width, crf, preset = review_options(cfg)
    episode = dub.load(dub.relative(cfg['episode'], True))
    voices = dub.load(dub.relative(episode['voice_registry'], True))
    selected = production.language_manifest(episode, 'en')
    source = dub.relative(cfg['dialogue_source']['path'], True)
    if sha(source) != cfg['dialogue_source']['sha256']:
        raise ValueError('Dialogue source checksum changed.')
    work, dest = dub.relative(cfg['work_dir']), dub.relative(cfg['delivery_dir'])
    work.mkdir(parents=True, exist_ok=True); dest.mkdir(parents=True, exist_ok=True)
    identity = sha(config_path)
    stamp = work / 'inputs.json'
    dependencies = [config_path, dub.relative(cfg['episode'], True), source,
        dub.relative(cfg['score'], True), dub.relative(cfg['sfx_plan'], True),
        dub.relative(cfg['ambience'], True), dub.relative(cfg['original_music'], True),
        dub.relative(episode['source_video'], True), Path(__file__),
        Path(scene_score.__file__), Path(subtitles.__file__)]
    dependencies.extend([dub.relative(cfg['sfx_registry'], True),
        Path(sfx.__file__), Path(dub.__file__), dub.relative(cfg['subtitle_settings'], True),
        dub.relative(episode['voice_registry'], True)])
    take_specs = [e['source_take'] for e in cfg['dialogue_edits'].values() if e.get('source_take')]
    take_specs += [r['source_take'] for r in cfg.get('vocal_reactions', [])]
    for spec in take_specs:
        path = dub.relative(spec['path'], True)
        dependencies += [path, path.with_suffix('.json'), dub.relative(spec['verification_report'], True)]
    inputs = {str(p.relative_to(dub.ROOT)): sha(p) for p in dependencies}
    immutable_json(stamp, {'config_sha256': identity, 'inputs': inputs})
    original = read_pcm(source); count = round(episode['duration_s'] * RATE)
    if len(original) != count:
        raise ValueError('Dialogue stem sample count differs from picture.')
    rows, tracks = [], []
    for cue in selected['dialogue']:
        edit = cfg['dialogue_edits'][cue['id']]
        if edit.get('source_take') and edit['source_take']['character'] != cue['character']:
            raise ValueError('Replacement take belongs to a different character.')
        tempo = dub.number(edit.get('tempo', 1), 'dialogue tempo', .95, 1.10)
        start = dub.number(edit.get('start_s', cue['start_s']), 'dialogue start', 0, episode['duration_s'])
        gain = dub.number(edit.get('gain_db', 0), 'dialogue edit gain', -24 if edit.get('source_take') else -6, 6)
        pcm = (take_pcm(edit['source_take'], cue['text'], voices) if edit.get('source_take') else
               original[round(cue['start_s'] * RATE):round(cue['end_s'] * RATE)])
        clip = work / (cue['id'] + '.wav')
        if not clip.exists():
            raw = work / (cue['id'] + '.source.wav')
            if not raw.exists(): write_pcm(raw, pcm)
            dub.run([dub.tool('ffmpeg'), '-v', 'error', '-nostdin', '-n', '-i', str(raw),
                '-af', f'atempo={tempo},volume={gain}dB,afade=t=in:d=0.005',
                '-ar', str(RATE), '-ac', '2', '-c:a', 'pcm_s24le', str(clip)])
        rendered = read_pcm(clip)
        lead, tail = active_bounds(rendered)
        rows.append(dict(id=cue['id'], character=cue['character'], text=cue['text'],
            old_start_s=cue['start_s'], old_end_s=cue['end_s'], start_s=round(start + lead, 4),
            end_s=round(start + tail, 4), placement_s=start, tempo=tempo, gain_db=gain,
            reason=edit['reason'], emotion=edit['emotion'], sha256=sha(clip)))
        if edit.get('source_take'): rows[-1]['source_take'] = edit['source_take']
        tracks.append(dict(path=clip.relative_to(dub.ROOT).as_posix(), timestamp_s=start,
            duration_s=len(rendered)/RATE, gain_db=0))
    for a, b in zip(rows, rows[1:]):
        if a['end_s'] > b['start_s']:
            raise ValueError('Revised speech overlaps: ' + a['id'])
    reactions = []
    cue_ids = {r['id'] for r in rows}
    for reaction in cfg.get('vocal_reactions', []):
        if reaction['id'] in cue_ids:
            raise ValueError('Duplicate dialogue/reaction ID.')
        cue_ids.add(reaction['id'])
        start = dub.number(reaction['start_s'], 'reaction start', 0, episode['duration_s'])
        pcm = take_pcm(reaction['source_take'], reaction['phonation'], voices, nonverbal=True)
        end = start + len(pcm)/RATE
        if end > episode['duration_s'] or any(start < row['end_s'] and end > row['start_s'] for row in rows):
            raise ValueError('Vocal reaction overlaps spoken dialogue or ending.')
        clip = work/(reaction['id']+'.wav')
        if not clip.exists(): write_pcm(clip, pcm)
        gain = dub.number(reaction.get('gain_db',0), 'reaction gain', -30, 6)
        reactions.append(dict(reaction, end_s=round(end,4), path=clip.relative_to(dub.ROOT).as_posix(),
            timestamp_s=start, duration_s=len(pcm)/RATE, gain_db=gain))
    dialogue = dest / f'Dino_EP2_EN_Dialogue_Only_{version}.wav'
    if not dialogue.exists(): timeline(tracks+reactions, dialogue, episode['duration_s'])
    # Subtitle edges are remeasured from the final assembled audio, not old windows.
    final_dialogue = read_pcm(dialogue)
    for row, track in zip(rows, tracks):
        lo = round(track['timestamp_s'] * RATE); hi = lo + round(track['duration_s'] * RATE)
        lead, tail = active_bounds(final_dialogue[lo:hi])
        row.update(start_s=round(lo/RATE+lead, 4), end_s=round(lo/RATE+tail, 4))
    revised = copy.deepcopy(episode)
    revised['languages'] = ['en']
    for cue, row in zip(revised['dialogue'], rows):
        cue['audio']['en'].update(start_s=row['start_s'], end_s=row['end_s'])
    settings = dub.load(dub.relative(cfg['subtitle_settings'], True))
    settings.update(ass_path=(dest/f'Dino_EP2_EN_{version}.ass').relative_to(dub.ROOT).as_posix(),
        story_srt_path=(dest/f'Dino_EP2_EN_{version}.srt').relative_to(dub.ROOT).as_posix(),
        packaged_srt_path=(dest/f'Dino_EP2_EN_{version}.srt').relative_to(dub.ROOT).as_posix(),
        report_path=(work/'subtitles.json').relative_to(dub.ROOT).as_posix())
    subtitles.generate(revised, settings)
    immutable_json(work/'subtitle-settings.json', settings)
    immutable_json(dest/f'Dino_EP2_EN_Dialogue_Timeline_{version}.json', {
        'source_audio_sha256': sha(dialogue), 'timing_authority': 'Final dialogue PCM energy bounds, 25ms lead /45ms tail; not word-level forced alignment.',
        'generation': 'Existing Puck/Leda takes plus explicitly selected, verified retakes/reactions if configured. This renderer makes no generation calls.',
        'vocal_reactions':reactions, 'cues': rows})
    md = [f'# EP2 English dialogue {version}', '', 'Full-film clock, existing 2s opening included once. Final spoken-audio bounds. Vocal reactions are separately listed in the JSON, not new story dialogue.', '',
        '| Cue | Voice | In | Out | Spoken words |', '|---|---|---|---|---|']
    for row in rows:
        md.append(f'| {row["id"]} | {row["character"]} | {subtitles.stamp(row["start_s"])} | {subtitles.stamp(row["end_s"])} | {row["text"]} |')
    md += ['', 'All 27 speaker assignments checked against actual picture samples. Triangle discovery intentionally speaks over the stone cutaway. Acting/accent remain subject to human listening; tempo/gain edits do not create a newly acted performance.']
    text = '\n'.join(md)+'\n'
    target = dest/f'Dino_EP2_EN_Dialogue_Timeline_{version}.md'
    if not target.exists(): dub.write_new(target, text.encode())
    scene_score.render(dub.relative(cfg['score'], True))
    plan = dub.load(dub.relative(cfg['score'], True))
    music = read_pcm(dub.relative(plan['output'], True))
    original_music = read_pcm(dub.relative(cfg['original_music'], True))
    # Preserve the familiar opening and accepted closing music, with short joins.
    n = round(.08*RATE)
    blend = np.linspace(0, 1, n, dtype='float32')[:, None]
    music[:2*RATE] = original_music[:2*RATE]
    music[2*RATE:2*RATE+n] = original_music[2*RATE:2*RATE+n]*(1-blend) + music[2*RATE:2*RATE+n]*blend
    lo = 162*RATE-n
    music[lo:162*RATE] = music[lo:162*RATE]*(1-blend) + original_music[lo:162*RATE]*blend
    music[162*RATE:] = original_music[162*RATE:]
    intervals = [(r['start_s'], r['end_s']) for r in rows] + [(r['start_s'],r['end_s']) for r in reactions]
    automation = dict(cfg['automation'])
    music *= duck_envelope(count, intervals, automation['music_duck_db'])[:,None]
    ambience = read_pcm(dub.relative(cfg['ambience'], True))
    ambience *= duck_envelope(count, intervals, automation['ambience_duck_db'])[:,None]
    registry = dub.load(dub.relative(cfg['sfx_registry'], True))
    effect_plan = dub.load(dub.relative(cfg['sfx_plan'], True))
    cues = sfx.validate_plan(effect_plan, registry, production=True)
    for cue in cues:
        effect = registry['effects'][cue['preset_id']]
        sfx.ensure_asset(effect, sfx.select_variation(effect, cue))
    raw_sfx = work/'sfx.raw.wav'
    if not raw_sfx.exists(): timeline(cues, raw_sfx, episode['duration_s'])
    effects = read_pcm(raw_sfx)
    effects *= duck_envelope(count, intervals, automation['sfx_duck_db'])[:,None]
    stems = {'BGM':music, 'Ambience':ambience, 'SFX':effects}
    for name, samples in stems.items():
        path = dest/f'Dino_EP2_EN_{name}_{version}.wav'
        if not path.exists(): write_pcm(path, samples)
    immutable_json(dest/f'Dino_EP2_EN_Music_Automation_{version}.json', {
        'schema_version':1, 'duration_s':episode['duration_s'], 'language':'en',
        'roadmap':cfg['roadmap'], 'score_plan':plan, 'speech_intervals':intervals,
        'automation':automation, 'attack_s':.15, 'release_s':.3,
        'stems':'BGM, ambience and SFX files include their own automation; do not apply ducking twice.',
        'localized_exports':'Reuse musical composition and SFX marks; recalculate ducking from each final localized dialogue, never blindly copy EN duck envelope.',
        'resolved_sfx':cues, 'inputs':inputs})
    premix = work/'premix.wav'
    if not premix.exists():
        timeline([dict(path=p.relative_to(dub.ROOT).as_posix(),timestamp_s=0,duration_s=episode['duration_s'],gain_db=0)
            for p in [dialogue]+[dest/f'Dino_EP2_EN_{k}_{version}.wav' for k in stems]], premix, episode['duration_s'], float_output=True)
    clean = work/f'clean-{version}.mp4'
    direct = cfg.get('direct_review_master', False)
    movie = dest/f'Dino_EP2_EN_Integrated_Review_{version}.mp4'
    graph = caption_filter({'subtitles':(work/'subtitle-settings.json').relative_to(dub.ROOT).as_posix()})
    if width != 720:
        graph += f',scale={width}:{width*16//9}'
    if direct and not movie.exists():
        info, analysis, measurement, picture_hash = dub.master_audio(selected,
            dub.relative(episode['source_video'],True), premix, movie, video_filter=graph,
            video_options=['-preset',preset,'-crf',str(crf),'-threads','2'])
        immutable_json(work/'mastering.json',dict(analysis=analysis,measurement=measurement,
            source_picture_hash=picture_hash,mode='direct_captioned_compact_review_no_full_resolution_intermediate'))
    elif not direct and not clean.exists():
        info, analysis, measurement, picture_hash = dub.master_audio(selected,
            dub.relative(episode['source_video'],True), premix, clean)
        immutable_json(work/'mastering.json',dict(analysis=analysis, measurement=measurement,picture_hash=picture_hash))
    if not movie.exists():
        dub.run([dub.tool('ffmpeg'),'-v','error','-nostdin','-n','-i',str(clean),'-vf',graph,
            '-c:v','libx264','-preset',preset,'-crf',str(crf),'-threads','2','-pix_fmt','yuv420p',
            '-c:a','copy','-movflags','+faststart',str(movie)],timeout=1800)
    dub.run([dub.tool('ffmpeg'),'-v','error','-nostdin','-threads','2','-i',str(movie),'-f','null','-'],timeout=900)
    info = dub.probe(movie)
    video = next(s for s in info['streams'] if s['codec_type']=='video')
    if (int(video['nb_frames']) != 3996 or abs(float(video['duration'])-166.5)>.001
            or video['width'] != width or video['height'] != width*16//9):
        raise ValueError('Picture duration/frame count changed.')
    a,b = decoded_audio(dialogue,0,episode['duration_s']),decoded_audio(movie,0,episode['duration_s'])
    checks = [dict(id=r['id'],**similarity(a[round(r['start_s']*8000):round(r['end_s']*8000)],
        b[round(r['start_s']*8000):round(r['end_s']*8000)])) for r in rows]
    reaction_checks = [dict(id=r['id'],**similarity(a[round(r['start_s']*8000):round(r['end_s']*8000)],
        b[round(r['start_s']*8000):round(r['end_s']*8000)])) for r in reactions]
    measured = dub.loudness_info(movie)
    immutable_json(dest/f'QUALITY_REVIEW_{version}.json',{
        'status':'technical_pass_creative_listening_pending' if min(r['correlation'] for r in checks)>=.95 else 'needs_dialogue_balance_review',
        'dialogue_checks':checks, 'vocal_reaction_checks':reaction_checks, 'loudness':measured, 'frame_count':3996,'duration_s':166.5,
        'picture':'Original picture timeline retained; full-frame captions and configured review scaling only.',
        'review_encoding':dict(width=width,height=width*16//9,crf=crf,preset=preset),
        'limitations':'Offline frame/ASR/waveform checks do not establish human acting, accent or music taste approval. Generated performance requests are retained with selected takes; renderer never calls TTS.',
        'files':{p.name:dict(bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(dest.iterdir()) if p.is_file() and p.name!=f'QUALITY_REVIEW_{version}.json'}})
    print('English review rendered:', movie, flush=True)


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('config')
    args=parser.parse_args()
    try: build(dub.relative(args.config, True))
    except (ValueError, OSError, KeyError) as exc: parser.exit(1, f'Error: {exc}\n')
