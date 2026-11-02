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


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_pcm(path):
    import numpy as np
    result = subprocess.run([dub.tool('ffmpeg'), '-v', 'error', '-i', str(path),
        '-vn', '-ar', str(RATE), '-ac', '2', '-f', 'f32le', '-'], capture_output=True, check=True)
    return np.frombuffer(result.stdout, dtype='<f4').reshape(-1, 2).copy()


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
    episode = dub.load(dub.relative(cfg['episode'], True))
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
    inputs = {str(p.relative_to(dub.ROOT)): sha(p) for p in dependencies}
    immutable_json(stamp, {'config_sha256': identity, 'inputs': inputs})
    original = read_pcm(source); count = round(episode['duration_s'] * RATE)
    if len(original) != count:
        raise ValueError('Dialogue stem sample count differs from picture.')
    rows, tracks = [], []
    for cue in selected['dialogue']:
        edit = cfg['dialogue_edits'][cue['id']]
        tempo = dub.number(edit.get('tempo', 1), 'dialogue tempo', .95, 1.10)
        start = dub.number(edit.get('start_s', cue['start_s']), 'dialogue start', 0, episode['duration_s'])
        gain = dub.number(edit.get('gain_db', 0), 'dialogue edit gain', -6, 6)
        pcm = original[round(cue['start_s'] * RATE):round(cue['end_s'] * RATE)]
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
        tracks.append(dict(path=clip.relative_to(dub.ROOT).as_posix(), timestamp_s=start,
            duration_s=len(rendered)/RATE, gain_db=0))
    for a, b in zip(rows, rows[1:]):
        if a['end_s'] > b['start_s']:
            raise ValueError('Revised speech overlaps: ' + a['id'])
    dialogue = dest / 'Dino_EP2_EN_Dialogue_Only_v002.wav'
    if not dialogue.exists(): timeline(tracks, dialogue, episode['duration_s'])
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
    settings.update(ass_path=(dest/'Dino_EP2_EN_v002.ass').relative_to(dub.ROOT).as_posix(),
        story_srt_path=(dest/'Dino_EP2_EN_v002.srt').relative_to(dub.ROOT).as_posix(),
        packaged_srt_path=(dest/'Dino_EP2_EN_v002.srt').relative_to(dub.ROOT).as_posix(),
        report_path=(work/'subtitles.json').relative_to(dub.ROOT).as_posix())
    subtitles.generate(revised, settings)
    immutable_json(work/'subtitle-settings.json', settings)
    immutable_json(dest/'Dino_EP2_EN_Dialogue_Timeline_v002.json', {
        'source_audio_sha256': sha(dialogue), 'timing_authority': 'Final dialogue PCM energy bounds, 25ms lead /45ms tail; not word-level forced alignment.',
        'generation': 'No new generation; pitch-preserving pacing edits to existing Puck/Leda takes.', 'cues': rows})
    md = ['# EP2 English dialogue v002', '', 'Full-film clock, existing 2s opening included once. Final spoken-audio bounds; no generation calls.', '',
        '| Cue | Voice | In | Out | Spoken words |', '|---|---|---|---|---|']
    for row in rows:
        md.append(f'| {row["id"]} | {row["character"]} | {subtitles.stamp(row["start_s"])} | {subtitles.stamp(row["end_s"])} | {row["text"]} |')
    md += ['', 'All 27 speaker assignments checked against actual picture samples. Triangle discovery intentionally speaks over the stone cutaway. Acting/accent remain subject to human listening; tempo/gain edits do not create a newly acted performance.']
    text = '\n'.join(md)+'\n'
    target = dest/'Dino_EP2_EN_Dialogue_Timeline_v002.md'
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
    intervals = [(r['start_s'], r['end_s']) for r in rows]
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
        path = dest/f'Dino_EP2_EN_{name}_v002.wav'
        if not path.exists(): write_pcm(path, samples)
    immutable_json(dest/'Dino_EP2_EN_Music_Automation_v002.json', {
        'schema_version':1, 'duration_s':episode['duration_s'], 'language':'en',
        'roadmap':cfg['roadmap'], 'score_plan':plan, 'speech_intervals':intervals,
        'automation':automation, 'attack_s':.15, 'release_s':.3,
        'stems':'BGM, ambience and SFX files include their own automation; do not apply ducking twice.',
        'localized_exports':'Reuse musical composition and SFX marks; recalculate ducking from each final localized dialogue, never blindly copy EN duck envelope.',
        'resolved_sfx':cues, 'inputs':inputs})
    premix = work/'premix.wav'
    if not premix.exists():
        timeline([dict(path=p.relative_to(dub.ROOT).as_posix(),timestamp_s=0,duration_s=episode['duration_s'],gain_db=0)
            for p in [dialogue]+[dest/f'Dino_EP2_EN_{k}_v002.wav' for k in stems]], premix, episode['duration_s'], float_output=True)
    clean = work/'clean-v002.mp4'
    if not clean.exists():
        info, analysis, measurement, picture_hash = dub.master_audio(selected,
            dub.relative(episode['source_video'],True), premix, clean)
        immutable_json(work/'mastering.json',dict(analysis=analysis, measurement=measurement,picture_hash=picture_hash))
    movie = dest/'Dino_EP2_EN_Integrated_Review_v002.mp4'
    if not movie.exists():
        graph = caption_filter({'subtitles':(work/'subtitle-settings.json').relative_to(dub.ROOT).as_posix()})
        dub.run([dub.tool('ffmpeg'),'-v','error','-nostdin','-n','-i',str(clean),'-vf',graph,
            '-c:v','libx264','-preset','fast','-crf','23','-threads','2','-pix_fmt','yuv420p',
            '-c:a','copy','-movflags','+faststart',str(movie)],timeout=1800)
    dub.run([dub.tool('ffmpeg'),'-v','error','-nostdin','-threads','2','-i',str(movie),'-f','null','-'],timeout=900)
    info = dub.probe(movie)
    video = next(s for s in info['streams'] if s['codec_type']=='video')
    if int(video['nb_frames']) != 3996 or abs(float(video['duration'])-166.5)>.001:
        raise ValueError('Picture duration/frame count changed.')
    a,b = decoded_audio(dialogue,0,episode['duration_s']),decoded_audio(movie,0,episode['duration_s'])
    checks = [dict(id=r['id'],**similarity(a[round(r['start_s']*8000):round(r['end_s']*8000)],
        b[round(r['start_s']*8000):round(r['end_s']*8000)])) for r in rows]
    measured = dub.loudness_info(movie)
    immutable_json(dest/'QUALITY_REVIEW_v002.json',{
        'status':'technical_pass_creative_listening_pending' if min(r['correlation'] for r in checks)>=.95 else 'needs_dialogue_balance_review',
        'dialogue_checks':checks, 'loudness':measured, 'frame_count':3996,'duration_s':166.5,
        'picture':'Source video packets unchanged before subtitle burn; full-frame caption overlay only.',
        'limitations':'Offline frame/ASR/waveform checks do not establish human acting, accent or music taste approval. No new TTS acting generated.',
        'files':{p.name:dict(bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(dest.iterdir()) if p.is_file() and p.name!='QUALITY_REVIEW_v002.json'}})
    print('English review rendered:', movie, flush=True)


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('config')
    args=parser.parse_args()
    try: build(dub.relative(args.config, True))
    except (ValueError, OSError, KeyError) as exc: parser.exit(1, f'Error: {exc}\n')
