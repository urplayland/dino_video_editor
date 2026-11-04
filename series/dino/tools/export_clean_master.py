#!/usr/bin/env python3
"""Export a silent, uncaptioned FLH picture master matching selected deliveries."""
import argparse
import hashlib
import json
from pathlib import Path
import tempfile

import dub


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest() if hasattr(hashlib, 'file_digest') else hashlib.sha256(stream.read()).hexdigest()


def export(manifest_path):
    manifest = dub.load(dub.relative(manifest_path, True))
    if manifest.get('schema_version') != 1:
        raise ValueError('Unsupported clean master manifest.')
    episode = dub.load(dub.relative(manifest['episode_manifest'], True))
    branding = dub.load(dub.relative(manifest['branding_manifest'], True))
    cfg = dub.load(dub.relative(branding['brand_config'], True))
    selection = dub.load(dub.relative(manifest['selection_manifest'], True))
    source = dub.relative(episode['picture_master'], True)
    expected = next(x['sha256'] for x in episode['sources'] if x['path'] == episode['picture_master'])
    if sha(source) != expected:
        raise ValueError('Silent picture source changed.')
    bumpers = dub.relative(cfg['bumper_media_dir'])
    provenance = dub.load(bumpers/'provenance.json')
    for name in ('intro.mp4', 'outro.mp4'):
        if sha(bumpers/name) != provenance['clips'][name]:
            raise ValueError('Approved bumper changed: '+name)
    inputs = [bumpers/'intro.mp4', source, bumpers/'outro.mp4']
    output = dub.relative(manifest['output'])
    report_path = dub.relative(manifest['report'])
    if output.exists() or report_path.exists():
        raise ValueError('Output or report already exists; choose a new version.')
    infos = [dub.probe(p) for p in inputs]
    if any(s['codec_type'] != 'video' for s in infos[1]['streams']):
        raise ValueError('Expected a video-only original master.')
    expected_frames = sum(int(next(s for s in info['streams'] if s['codec_type'] == 'video')['nb_frames']) for info in infos)
    total = branding['source_duration_s'] + cfg['intro_duration_s'] + cfg['outro_duration_s']
    output.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    graph = ';'.join([
        f'[{i}:v]format=yuv420p,setsar=1,settb=AVTB,setpts=PTS-STARTPTS[v{i}]' for i in range(3)
    ] + ['[v0][v1][v2]concat=n=3:v=1:a=0[video]'])
    with tempfile.TemporaryDirectory(prefix='clean-master-', dir=output.parent) as temp:
        staged = Path(temp)/'picture.mp4'
        args = [dub.tool('ffmpeg'), '-v', 'error', '-nostdin', '-n']
        for path in inputs:
            args += ['-i', str(path)]
        args += ['-filter_complex', graph, '-map', '[video]', '-an', '-sn', '-dn', '-t', str(total),
                 '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-threads', '4',
                 '-pix_fmt', 'yuv420p', '-fps_mode:v', 'passthrough', '-enc_time_base:v', '1:15360',
                 '-movflags', '+faststart', str(staged)]
        dub.run(args, timeout=1800)
        info = dub.probe(staged)
        streams = info['streams']
        if len(streams) != 1 or streams[0]['codec_type'] != 'video':
            raise ValueError('Clean master must contain exactly one video stream.')
        if int(streams[0]['nb_frames']) != expected_frames or abs(float(info['format']['duration'])-total) > .001:
            raise ValueError('Unexpected clean master frames/duration.')
        dub.run([dub.tool('ffmpeg'), '-v', 'error', '-xerror', '-i', str(staged), '-f', 'null', '-'], timeout=600)
        def pts(path):
            data = dub.run([dub.tool('ffprobe'), '-v', 'error', '-select_streams', 'v:0',
                            '-show_entries', 'packet=pts_time', '-of', 'json', str(path)], timeout=120)
            return sorted(float(p['pts_time']) for p in json.loads(data.stdout)['packets'])
        picture_pts = pts(staged)
        alignments = {}
        for language, selected in selection['media'].items():
            reference = dub.relative(selected['file'], True)
            if sha(reference) != selected['sha256']:
                raise ValueError('Selected delivery changed: '+language)
            reference_pts = pts(reference)
            if len(reference_pts) != len(picture_pts):
                raise ValueError('Selected frame count differs: '+language)
            drift = max(abs(a-b) for a,b in zip(picture_pts, reference_pts))
            if drift > .001:
                raise ValueError('Picture timing differs: '+language)
            alignments[language] = {'selected_video': selected['file'], 'maximum_frame_timestamp_drift_s': drift}
        staged.replace(output)
    report = {'status': 'decode_frame_count_stream_and_selected_timing_checks_passed', 'manifest': manifest,
              'output_sha256': sha(output), 'duration_s': float(info['format']['duration']),
              'expected_frames': expected_frames, 'actual_frames': int(streams[0]['nb_frames']),
              'audio_streams': 0, 'subtitle_streams': 0, 'burned_subtitles_applied': False,
              'source_inputs': [{'path': p.relative_to(dub.ROOT).as_posix(), 'sha256': sha(p)} for p in inputs],
              'selected_timing_checks': alignments, 'api_calls': 0,
              'picture_processing': 'Derived H264 encode to join approved bumpers with entire original silent story; originals unchanged.'}
    dub.write_new(report_path, (json.dumps(report, indent=2)+'\n').encode())
    print(json.dumps(report, indent=2))


def package_primary(manifest_path):
    """Attach an existing selected mix without re-encoding picture or audio."""
    manifest = dub.load(dub.relative(manifest_path, True))
    if not manifest.get('primary_output'):
        return
    clean = dub.relative(manifest['output'], True)
    clean_report = dub.load(dub.relative(manifest['report'], True))
    if sha(clean) != clean_report['output_sha256']:
        raise ValueError('Clean master changed.')
    selection = dub.load(dub.relative(manifest['selection_manifest'], True))
    selected = selection['media'][manifest['primary_language']]
    audio_source = dub.relative(selected['file'], True)
    if sha(audio_source) != selected['sha256']:
        raise ValueError('Selected primary audio source changed.')
    output = dub.relative(manifest['primary_output'])
    report_path = output.with_suffix('.json')
    if output.exists() or report_path.exists():
        raise ValueError('Primary output exists; choose a new version.')
    def packets(path, stream):
        return dub.run([dub.tool('ffmpeg'), '-v', 'error', '-i', str(path), '-map', stream,
                        '-c', 'copy', '-f', 'hash', '-hash', 'sha256', '-'], timeout=120).stdout.strip()
    with tempfile.TemporaryDirectory(prefix='primary-', dir=output.parent) as temp:
        staged = Path(temp)/'primary.mp4'
        dub.run([dub.tool('ffmpeg'), '-v', 'error', '-nostdin', '-n', '-i', str(clean),
                 '-i', str(audio_source), '-map', '0:v:0', '-map', '1:a:0', '-c', 'copy',
                 '-sn', '-dn', '-movflags', '+faststart', str(staged)], timeout=120)
        info = dub.probe(staged)
        if sorted(s['codec_type'] for s in info['streams']) != ['audio', 'video']:
            raise ValueError('Primary file must contain one video and one audio stream.')
        if packets(staged, '0:v:0') != packets(clean, '0:v:0'):
            raise ValueError('Clean picture packet identity changed.')
        if packets(staged, '0:a:0') != packets(audio_source, '0:a:0'):
            raise ValueError('Selected audio packet identity changed.')
        dub.run([dub.tool('ffmpeg'), '-v', 'error', '-xerror', '-i', str(staged),
                 '-f', 'null', '-'], timeout=600)
        staged.replace(output)
    report = {'status': 'full_decode_and_picture_audio_packet_identity_checks_passed',
              'output_sha256': sha(output), 'picture_master': manifest['output'],
              'selected_audio_source': selected['file'], 'language': manifest['primary_language'],
              'duration_s': float(info['format']['duration']), 'burned_subtitles_applied': False,
              'api_calls': 0, 'encoding': 'Video and audio stream copy; no re-encoding.'}
    dub.write_new(report_path, (json.dumps(report, indent=2)+'\n').encode())
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest')
    parser.add_argument('--package-primary-only', action='store_true',
                        help='Attach primary audio to an already verified clean master.')
    args = parser.parse_args()
    if not args.package_primary_only:
        export(args.manifest)
    package_primary(args.manifest)
