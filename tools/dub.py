#!/usr/bin/env python3
"""Dependency-free, explicit Gemini TTS and FFmpeg prototype workflow."""
import argparse
from array import array
import base64
from datetime import datetime, timezone
import hashlib
import io
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from urllib import request, error
import wave

from dino import ROOT, find_tool

LANGUAGES = ('en', 'zh', 'ms')
STATES = ('sample', 'draft', 'verified', 'approved')


def load_env(path=None, key_name="GEMINI_API_KEY"):
    """Read only the explicitly selected Gemini key; never execute shell text."""
    path = path or ROOT / '.env'
    if not re.fullmatch(r'GEMINI_API_KEY(?:_[A-Z0-9]+)?', key_name):
        raise ValueError('Invalid Gemini dotenv key variable name.')
    if (os.environ.get('GEMINI_API_KEY') and key_name == 'GEMINI_API_KEY') or not path.is_file():
        return
    for line in path.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if line.startswith('export '):
            line = line[7:].lstrip()
        key, sep, value = line.partition('=')
        if not sep or key.strip() != key_name:
            continue
        value = value.strip()
        if value.startswith(('"', "'")):
            quote = value[0]
            end = value.find(quote, 1)
            if end < 0 or (value[end+1:].strip() and not value[end+1:].strip().startswith('#')):
                raise ValueError('Invalid GEMINI_API_KEY quoting in .env.')
            value = value[1:end]
        else:
            value = value.split(' #', 1)[0].rstrip()
        if value:
            os.environ['GEMINI_API_KEY'] = value
        return


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def relative(value, exists=False):
    if not isinstance(value, str) or not value:
        raise ValueError('A nonempty repository-relative path is required.')
    p = Path(value)
    result = ROOT / p
    if p.is_absolute() or '..' in p.parts or not result.resolve().is_relative_to(ROOT):
        raise ValueError('Paths must remain inside the workspace.')
    if any(x.is_symlink() for x in (result, *result.parents) if x != ROOT):
        raise ValueError('Symlinks are not supported.')
    if exists and not result.is_file():
        raise ValueError(f'Missing file: {value}')
    return result


def number(value, name, low=0, high=1e8):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not low <= value <= high:
        raise ValueError(f'{name} must be a finite number in [{low}, {high}].')
    return value


def validate(m, voices):
    """Validate the versioned manifest contract without third-party packages."""
    if m.get('schema_version') != 1 or m.get('kind') not in ('dubbing_poc', 'dubbing_production'):
        raise ValueError('Expected dubbing_poc or dubbing_production manifest schema_version 1.')
    if m.get('status') not in STATES or m.get('language') not in LANGUAGES:
        raise ValueError('Invalid manifest status or language.')
    relative(m.get('source_video'))
    number(m.get('source_start_s'), 'source_start_s')
    production = m['kind'] == 'dubbing_production'
    duration = number(m.get('duration_s'), 'duration_s', .1 if production else 8, 36000 if production else 10)
    if production and m.get('source_start_s') != 0:
        raise ValueError('Full production must begin at the start of the picture master.')
    relative(m.get('output_dir'))
    if not re.fullmatch(r'episodes/[a-z0-9-]+/media/derived/[a-zA-Z0-9_/-]+', m['output_dir']):
        raise ValueError('output_dir must be under episode media/derived/.')
    if m.get('original_audio') != 'replace':
        raise ValueError('POC requires replacing original audio to prevent duplicate dialogue.')
    mix = m.get('mix', {})
    number(mix.get('integrated_lufs'), 'integrated_lufs', -30, -12)
    number(mix.get('true_peak_db'), 'true_peak_db', -6, -1)
    if not isinstance(m.get('dialogue'), list) or not m['dialogue']:
        raise ValueError('At least one dialogue cue is required; do not invent film dialogue.')
    if not isinstance(m.get('beds'), list) or not isinstance(m.get('sfx'), list):
        raise ValueError('beds and sfx must be lists.')
    seen, ordered = set(), []
    for cue in m['dialogue']:
        cid = cue.get('id', '')
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', cid) or cid in seen:
            raise ValueError('Dialogue IDs must be unique lowercase slugs.')
        seen.add(cid)
        char = voices.get('characters', {}).get(cue.get('character'))
        if not char or char.get('approval_status') != 'voice_selection_approved':
            raise ValueError('Character needs an approved voice selection.')
        if cue.get('voice_version') != char.get('preset_version'):
            raise ValueError('Cue voice_version does not match selected registry version.')
        if not re.fullmatch(r'[a-zA-Z0-9._-]+', char.get('model', '')):
            raise ValueError('Invalid model ID.')
        if not char.get('voice') or not char.get('style', {}).get(m['language']):
            raise ValueError('Missing preset voice or language style.')
        if cue.get('status') not in STATES or not isinstance(cue.get('text'), str) or not cue['text'].strip():
            raise ValueError('Cue needs text and an explicit review status.')
        start = number(cue.get('start_s'), 'start_s', 0, duration)
        end = number(cue.get('end_s'), 'end_s', 0, duration)
        if end <= start:
            raise ValueError('Cue end must follow start.')
        number(cue.get('gain_db', 0), 'gain_db', -60, 12)
        ordered.append((start, end))
    ordered.sort()
    if any(b[0] < a[1] for a, b in zip(ordered, ordered[1:])):
        raise ValueError('Overlapping dialogue cue windows need editorial resolution.')
    for cue in m['beds'] + m['sfx']:
        relative(cue.get('path'))
        number(cue.get('start_s'), 'asset start_s', 0, duration)
        number(cue.get('duration_s'), 'asset duration_s', .01, duration)
        if cue['start_s'] + cue['duration_s'] > duration:
            raise ValueError('Audio cue extends beyond the prototype.')
        number(cue.get('gain_db'), 'asset gain_db', -60, 12)
        if cue.get('status') not in ('verified', 'approved') or cue.get('dialogue_free') is not True:
            raise ValueError('Background and SFX assets must be reviewed and confirmed dialogue-free.')
    return m


def payload(cue, char, language):
    # Gemini 3.8 REST contract: style metadata is separate from spoken text.
    style = char['style'][language]
    if cue.get('delivery_style'):
        if not isinstance(cue['delivery_style'],str):
            raise ValueError('Per-cue delivery style must be text.')
        style += ' ' + cue['delivery_style']
    return {'contents': [{'role': 'user', 'parts': [{
        'text': cue['text'], 'speech_metadata': {'style': style}
    }]}], 'generationConfig': {'responseModalities': ['AUDIO'],
        'speechConfig': {'voiceConfig': {'voice': char['voice']}}}}


def wav_info(data):
    with wave.open(io.BytesIO(data), 'rb') as w:
        if w.getcomptype() != 'NONE' or w.getsampwidth() != 2 or w.getnchannels() != 1 or w.getframerate() != 24000 or not w.getnframes():
            raise ValueError('Expected nonempty 24 kHz mono 16-bit PCM WAV; review provider output.')
        frames = w.getnframes()
        if len(w.readframes(frames)) != frames * 2:
            raise ValueError('Truncated WAV data.')
        return {'duration_s': frames / 24000, 'sample_rate': 24000, 'channels': 1, 'sample_width': 2}



def speech_bounds(data):
    """Trim only near-silent edges, retaining 60 ms lead and 80 ms tail."""
    wav_info(data)
    with wave.open(io.BytesIO(data), 'rb') as w:
        pcm = array('h', w.readframes(w.getnframes()))
    if sys.byteorder != 'little':
        pcm.byteswap()
    threshold = max(35, max(abs(x) for x in pcm)*.006)
    active = [i for i, value in enumerate(pcm) if abs(value) > threshold]
    if not active:
        raise ValueError('Generated WAV has no detectable speech energy.')
    return max(0, active[0]/24000-.06), min(len(pcm)/24000, active[-1]/24000+.08)


def decode_audio(response):
    parts = response.get('candidates', [{}])[0].get('content', {}).get('parts', [])
    audio = [p['inlineData'] for p in parts if 'inlineData' in p]
    if len(audio) != 1:
        raise ValueError('Expected exactly one audio response; no output saved.')
    try:
        data = base64.b64decode(audio[0]['data'], validate=True)
    except (ValueError, TypeError):
        raise ValueError('Malformed base64 audio response.') from None
    mime = audio[0].get('mimeType', '').lower()
    if mime in ('audio/wav', 'audio/x-wav'):
        wav_info(data)
        return data
    # Explicit legacy raw PCM compatibility. Never double-wrap a WAV response.
    if re.fullmatch(r'audio/l16;\s*codec=pcm;\s*rate=24000', mime):
        if not data or len(data) % 2:
            raise ValueError('Malformed raw PCM.')
        out = io.BytesIO()
        with wave.open(out, 'wb') as w:
            w.setparams((1, 2, 24000, 0, 'NONE', 'not compressed'))
            w.writeframes(data)
        return out.getvalue()
    raise ValueError('Unsupported audio MIME type; inspect provider contract.')


def write_new(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as f:
        f.write(data)


def generate(m, voices, line=None, live=False, regenerate=False):
    selected = [c for c in m['dialogue'] if line is None or c['id'] == line]
    if not selected:
        raise ValueError('Unknown line ID.')
    for cue in selected:
        char = voices['characters'][cue['character']]
        body = payload(cue, char, m['language'])
        identity = {'model': char['model'], 'voice_version': char['preset_version'], 'request': body}
        fingerprint = hashlib.sha256(json.dumps(identity, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        folder = relative(m['output_dir'] + '/' + m['language'])
        stem = folder / cue['id']
        wav_path = relative(cue['audio_path']) if cue.get('audio_path') and not regenerate else stem.with_suffix('.wav')
        record_path = wav_path.with_suffix('.json')
        if wav_path.exists() or record_path.exists():
            valid = wav_path.exists() and record_path.exists()
            if valid:
                record = load(record_path)
                valid = record.get('fingerprint') == fingerprint and record.get('sha256') == hashlib.sha256(wav_path.read_bytes()).hexdigest()
            if valid and not regenerate:
                print(f'Skip existing verified output: {cue["id"]}')
                continue
            if not regenerate:
                raise ValueError('Existing output is incomplete or configuration changed; use --regenerate for a new take.')
            folder = folder / ('take-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
            wav_path, record_path = folder / (cue['id'] + '.wav'), folder / (cue['id'] + '.json')
        if not live:
            print(json.dumps({'line': cue['id'], 'model': char['model'], 'output': str(wav_path.relative_to(ROOT)), 'request': body}, ensure_ascii=False))
            continue
        key = os.environ.get('GEMINI_API_KEY')
        if not key:
            raise ValueError('GEMINI_API_KEY is not set. No API call made.')
        req = request.Request(f'https://generativelanguage.googleapis.com/v1beta/models/{char["model"]}:generateContent',
            data=json.dumps(body).encode(), headers={'Content-Type': 'application/json', 'x-goog-api-key': key}, method='POST')
        try:
            with request.urlopen(req, timeout=120) as response:
                data = decode_audio(json.load(response))
        except error.HTTPError as exc:
            # Keep only quota diagnostics; never echo provider body or request headers.
            details = []
            try:
                provider = json.loads(exc.read()).get('error', {})
                for item in provider.get('details', []):
                    if item.get('@type', '').endswith('QuotaFailure'):
                        for violation in item.get('violations', []):
                            details.append({k: violation[k] for k in ('quotaMetric','quotaId','quotaValue') if k in violation})
                    if item.get('@type', '').endswith('RetryInfo'):
                        details.append({'retryDelay': item.get('retryDelay')})
            except (ValueError, OSError):
                pass
            diagnostic = json.dumps(details).replace(key, '[REDACTED]') if details else 'No quota details supplied.'
            raise ValueError(f'Gemini HTTP {exc.code}; generation stopped. Quota details: {diagnostic}') from None
        except (error.URLError, TimeoutError):
            raise ValueError('Gemini network failure; no automatic retry. Check for a completed request before repeating.') from None
        info = wav_info(data)
        record = dict(identity, fingerprint=fingerprint, sha256=hashlib.sha256(data).hexdigest(),
            character=cue['character'], language=m['language'], status='generated_pending_listening_review',
            output=wav_path.relative_to(ROOT).as_posix(), credential_label=os.environ.get('DINO_CREDENTIAL_LABEL','runtime-or-project-env'), created_at=datetime.now(timezone.utc).isoformat(), **info)
        write_new(wav_path, data)
        write_new(record_path, (json.dumps(record, indent=2, ensure_ascii=False)+'\n').encode())
        print(f'Generated {wav_path.relative_to(ROOT)} ({info["duration_s"]:.3f}s); listening review required.')


def run(args, timeout=180):
    try:
        result = subprocess.run(args, capture_output=True, text=True, check=False, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise ValueError(f'{Path(args[0]).name} exceeded its {timeout}-second processing limit.') from None
    if result.returncode:
        raise ValueError(f'{Path(args[0]).name} failed: {result.stderr[-2000:]}')
    return result


def tool(name):
    value = find_tool(name)
    if not value:
        raise ValueError(f'{name} is required; see docs/dubbing.md.')
    return value


def probe(path):
    return json.loads(run([tool('ffprobe'), '-v', 'error', '-show_format', '-show_streams', '-of', 'json', str(path)]).stdout)



def video_hash(path):
    return run([tool('ffmpeg'), '-v', 'error', '-nostdin', '-i', str(path), '-map', '0:v:0', '-c', 'copy', '-f', 'hash', '-hash', 'sha256', '-'], timeout=900).stdout.strip()


def loudness_info(path):
    result = run([tool('ffmpeg'), '-hide_banner', '-nostdin', '-i', str(path), '-vn', '-af',
                  'loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'], timeout=900).stderr
    return json.loads(result[result.rfind('{'):])


def master_audio(m, source, mix, movie):
    """Master/mux an already assembled mix using the established production checks."""
    ffmpeg = tool('ffmpeg')
    duration = m['duration_s']
    production = m.get('kind') == 'dubbing_production'
    loudness = f'loudnorm=I={m["mix"]["integrated_lufs"]}:TP={m["mix"]["true_peak_db"]}:LRA=11'
    analysis = run([ffmpeg, '-hide_banner', '-nostdin', '-i', str(mix), '-af', loudness+':print_format=json', '-f', 'null', '-']).stderr
    measured = json.loads(analysis[analysis.rfind('{'):])
    if any(not math.isfinite(float(measured[k])) for k in ('input_i', 'input_tp', 'input_lra', 'input_thresh', 'target_offset')):
        raise ValueError('Cannot normalize silent or invalid audio.')
    norm = loudness + ':linear=true:' + ':'.join(f'{k}={measured[v]}' for k,v in [('measured_I','input_i'),('measured_TP','input_tp'),('measured_LRA','input_lra'),('measured_thresh','input_thresh'),('offset','target_offset')])
    video_codec = ['-c:v', 'copy'] if production else ['-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p']
    run([ffmpeg, '-v', 'error', '-nostdin', '-n', '-ss', str(m['source_start_s']), '-i', str(source), '-i', str(mix),
         '-t', str(duration), '-map', '0:v:0', '-map', '1:a:0', '-af', norm, *video_codec,
         '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-ac', '2', '-movflags', '+faststart', str(movie)], timeout=900)
    info = probe(movie)
    if abs(float(info['format']['duration'])-duration) > .15 or not any(s['codec_type']=='audio' for s in info['streams']):
        raise ValueError('Export stream/duration validation failed.')
    run([ffmpeg, '-v', 'error', '-nostdin', '-i', str(movie), '-f', 'null', '-'], timeout=900)
    final_measurement = loudness_info(movie)
    if not math.isfinite(float(final_measurement['input_i'])) or float(final_measurement['input_tp']) > -.8:
        raise ValueError('Encoded audio is silent or exceeds the production peak margin.')
    if production and abs(float(final_measurement['input_i']) - m['mix']['integrated_lufs']) > 1:
        raise ValueError('Encoded integrated loudness differs from the target by over 1 LU.')
    picture_hash = None
    if production:
        picture_hash = video_hash(source)
        if video_hash(movie) != picture_hash:
            raise ValueError('Encoded animation differs from the supplied silent picture master.')
    return info, measured, final_measurement, picture_hash


def render(m, voices, output):
    if m['status'] not in ('verified', 'approved') or any(c['status'] not in ('verified', 'approved') for c in m['dialogue']):
        raise ValueError('Render needs a verified transcript, timing, and manifest.')
    source = relative(m['source_video'], True)
    source_info = probe(source)
    production = m.get('kind') == 'dubbing_production'
    if production and any(s['codec_type'] == 'audio' for s in source_info['streams']):
        raise ValueError('Production picture master must have no audio stream.')
    if production and abs(float(source_info['format']['duration']) - m['duration_s']) > .05:
        raise ValueError('Production manifest must cover the entire silent master.')
    if float(source_info['format']['duration']) + .001 < m['source_start_s'] + m['duration_s']:
        raise ValueError('Selected scene exceeds source duration.')
    target = relative(output)
    if not re.fullmatch(r'episodes/[a-z0-9-]+/exports/[^/]+\.mp4', output):
        raise ValueError('Review MP4 must be under episode exports/.')
    if target.exists() or target.with_suffix('.json').exists():
        raise ValueError('Output already exists; increment review version.')
    target.parent.mkdir(parents=True, exist_ok=True)
    ffmpeg = tool('ffmpeg')
    duration = m['duration_s']
    inputs, filters, tracks, records, groups = [], [], [], [], []
    for cue in m['dialogue']:
        path = relative(cue.get('audio_path') or f'{m["output_dir"]}/{m["language"]}/{cue["id"]}.wav', True)
        record = load(path.with_suffix('.json'))
        char = voices['characters'][cue['character']]
        expected = {'model': char['model'], 'voice_version': char['preset_version'], 'request': payload(cue, char, m['language'])}
        fingerprint = hashlib.sha256(json.dumps(expected, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        if record.get('fingerprint') != fingerprint or record.get('sha256') != hashlib.sha256(path.read_bytes()).hexdigest():
            raise ValueError('Audio provenance does not match cue/preset; regenerate or relink the correct take.')
        if cue.get('audio_review_status') not in ('approved', 'verified_automated'):
            raise ValueError('Each dialogue WAV needs audio review or a recorded automated verification.')
        if cue.get('audio_review_status') == 'verified_automated' and not cue.get('audio_verification_report'):
            raise ValueError('Automated audio verification requires a report path.')
        if cue.get('audio_verification_report'):
            check = load(relative(cue['audio_verification_report'], True))
            if check.get('status') != 'passed_automated' or check.get('sha256') != record['sha256'] or check.get('expected_text') != cue.get('spoken_text',cue['text']):
                raise ValueError('Audio verification is stale or failed; repeat the local verification.')
            if cue.get('required_names') and (check.get('required_names')!=cue['required_names'] or check.get('name_checks_passed') is not True or check.get('name_asr_aliases',{})!=cue.get('name_asr_aliases',{})):
                raise ValueError('Required character-name pronunciation check is missing or failed.')
        raw_audio = path.read_bytes()
        original_duration = wav_info(raw_audio)['duration_s']
        lead, tail = speech_bounds(raw_audio) if production else (0, original_duration)
        actual = tail - lead
        speed = max(1, actual / (cue['end_s'] - cue['start_s']))
        if speed > 1.10:
            raise ValueError(f'{cue["id"]} needs more than 10% speedup; revise delivery/text/timing.')
        records.append({'cue': cue['id'], 'path': path.relative_to(ROOT).as_posix(), 'sha256': record['sha256'], 'tempo': speed, 'trim_start_s': lead, 'trim_end_s': tail})
        tracks.append((path, cue['start_s'], actual/speed, cue.get('gain_db', 0), speed, lead, tail))
        groups.append('dialogue')
    for cue in m['beds'] + m['sfx']:
        path = relative(cue['path'], True)
        actual = float(probe(path)['format']['duration'])
        if actual + .01 < cue['duration_s']:
            raise ValueError('Background asset is shorter than its cue; supply a continuous prepared bed.')
        tracks.append((path, cue['start_s'], cue['duration_s'], cue['gain_db'], 1, 0, cue['duration_s']))
        groups.append(cue.get('category', 'sfx'))
        records.append({'path': cue['path'], 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
    for i, (path, start, length, gain, tempo, lead, tail) in enumerate(tracks):
        inputs += ['-i', str(path)]
        fade = min(.01, length/4)
        filters.append(f'[{i}:a]atrim=start={lead}:end={tail},asetpts=N/SR/TB,aresample=48000,atempo={tempo},atrim=duration={length},asetpts=N/SR/TB,volume={gain}dB,afade=t=in:d={fade},afade=t=out:st={length-fade}:d={fade},adelay={round(start*48000)}S:all=1,asetpts=N/SR/TB[a{i}]')
    group_names = sorted(set(groups))
    if any(name not in ('dialogue', 'music', 'ambience', 'sfx') for name in group_names):
        raise ValueError('Unknown audio bus category.')
    final_labels = []
    for group in group_names:
        indices = [i for i, name in enumerate(groups) if name == group]
        labels = ''.join(f'[a{i}]' for i in indices)
        bus = f'{labels}amix=inputs={len(indices)}:normalize=0,apad=whole_dur={duration},asetpts=N/SR/TB,atrim=duration={duration},aformat=sample_rates=48000:channel_layouts=stereo'
        if group == 'dialogue' and 'music' in group_names:
            filters.append(bus+',asplit=3[stem_dialogue][mix_dialogue][dialogue_key]')
        else:
            filters.append(bus+f',asplit=2[stem_{group}][mix_{group}]')
        final_labels.append('[ducked_music]' if group == 'music' else f'[mix_{group}]')
    if 'music' in group_names:
        filters.append('[mix_music][dialogue_key]sidechaincompress=threshold=0.02:ratio=4:attack=20:release=400[ducked_music]')
    filters.append(''.join(final_labels)+f'amix=inputs={len(final_labels)}:normalize=0[mix]')
    stem_targets = {group: target.with_suffix(f'.{group}.wav') for group in group_names}
    if any(path.exists() for path in stem_targets.values()):
        raise ValueError('Bus stem already exists; increment review version.')
    with tempfile.TemporaryDirectory(prefix='dino-dub-', dir=target.parent) as tmp:
        mix = Path(tmp)/'mix.wav'
        mixed_outputs = ['-map', '[mix]', '-t', str(duration), '-c:a', 'pcm_f32le', str(mix)]
        for group in group_names:
            mixed_outputs += ['-map', f'[stem_{group}]', '-t', str(duration), '-c:a', 'pcm_s24le', str(Path(tmp)/(group+'.wav'))]
        run([ffmpeg, '-v', 'error', '-nostdin', '-n', *inputs, '-filter_complex', ';'.join(filters), *mixed_outputs], timeout=900)
        movie = Path(tmp)/'review.mp4'
        info, measured, final_measurement, picture_hash = master_audio(m, source, mix, movie)
        info['format']['filename'] = output
        # Persist the editable mixed stem and reproducibility report alongside the render.
        stem_target = target.with_suffix('.mix.wav')
        if stem_target.exists():
            raise ValueError('Mixed stem exists; increment review version.')
        for group, destination in stem_targets.items():
            write_new(destination, (Path(tmp)/(group+'.wav')).read_bytes())
        write_new(stem_target, mix.read_bytes())
        write_new(target, movie.read_bytes())
        report = {'status': 'technical_checks_passed_pending_full_listening_and_visual_review', 'manifest': m,
            'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(), 'audio_inputs': records,
            'stems': {group:path.relative_to(ROOT).as_posix() for group,path in stem_targets.items()},
            'music_ducking': 'sidechaincompress threshold=0.02 ratio=4 attack=20ms release=400ms' if 'music' in group_names else None,
            'loudness_measurement_before_normalization': measured, 'encoded_audio_measurement': final_measurement,
            'picture_packet_hash': picture_hash, 'output_sha256': hashlib.sha256(movie.read_bytes()).hexdigest(), 'output_metadata': info,
            'ffmpeg_version': run([ffmpeg, '-version']).stdout.splitlines()[0]}
        write_new(target.with_suffix('.json'), (json.dumps(report, indent=2, ensure_ascii=False)+'\n').encode())
    print(f'Rendered {output}; full visual and listening review required.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--voices', default='config/voices.json')
    sub = parser.add_subparsers(dest='command', required=True)
    for command in ('validate', 'generate', 'render'):
        p = sub.add_parser(command)
        p.add_argument('manifest')
        if command == 'generate':
            p.add_argument('--line')
            p.add_argument('--live', action='store_true', help='Explicitly authorize API calls for selected lines; may incur charges')
            p.add_argument('--regenerate', action='store_true', help='Generate a separate take; preserve previous WAVs')
        elif command == 'render':
            p.add_argument('--output', required=True)
    inspect = sub.add_parser('inspect')
    inspect.add_argument('source')
    args = parser.parse_args()
    try:
        load_env()
        if args.command == 'inspect':
            print(json.dumps(probe(relative(args.source, True)), indent=2))
            return
        voices = load(relative(args.voices, True))
        m = validate(load(relative(args.manifest, True)), voices)
        if args.command == 'validate':
            print('Manifest structurally valid; this does not establish editorial approval or file availability.')
        elif args.command == 'generate':
            generate(m, voices, args.line, args.live, args.regenerate)
        else:
            render(m, voices, args.output)
    except (ValueError, OSError, KeyError, TypeError, IndexError, wave.Error) as exc:
        parser.exit(1, f'Error: {exc}\n')


if __name__ == '__main__':
    main()
