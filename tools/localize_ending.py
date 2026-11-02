#!/usr/bin/env python3
"""Replace a final's ending card; preserve audio and copy the preceding closed GOPs."""
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path

import dub
import end_card
from review_audio import immutable_json, sha


def packet_info(path, stream='v:0'):
    return json.loads(dub.run([dub.tool('ffprobe'),'-v','error','-select_streams',stream,
        '-show_packets','-show_entries','packet=pts,dts,flags','-of','json',str(path)]).stdout)['packets']


def prefix_hash(path, frames):
    if not frames:return None
    output=dub.run([dub.tool('ffmpeg'),'-v','error','-nostdin','-i',str(path),'-map','0:v:0',
        '-frames:v',str(frames),'-an','-f','framemd5','-'],timeout=900).stdout
    lines=[x for x in output.splitlines() if x and not x.startswith('#')]
    if len(lines)!=frames:raise ValueError('Copied picture prefix is incomplete.')
    return hashlib.sha256('\n'.join(lines).encode()).hexdigest()


def audio_hash(path):
    return dub.run([dub.tool('ffmpeg'),'-v','error','-i',str(path),'-map','0:a:0',
        '-c:a','copy','-f','hash','-hash','sha256','-']).stdout.strip()


def replace(config_path):
    cfg=dub.load(config_path)
    source=dub.relative(cfg['source_final']['path'],True)
    if sha(source)!=cfg['source_final']['sha256']:raise ValueError('Source final changed.')
    settings=dub.load(dub.relative(cfg['ending_settings'],True))
    card=end_card.render(settings)
    out=dub.relative(cfg['output']);out.parent.mkdir(parents=True,exist_ok=True)
    work=dub.relative(cfg['work_dir']);work.mkdir(parents=True,exist_ok=True)
    immutable_json(work/'inputs.json',dict(config=sha(config_path),source=sha(source),card=sha(card),tool=sha(Path(__file__))))
    info=dub.probe(source);v=next(x for x in info['streams'] if x['codec_type']=='video')
    tb=Fraction(v['time_base']);fps=Fraction(v['r_frame_rate'])
    if fps!=24:raise ValueError('Expected the approved24fps picture.')
    story=Fraction(str(cfg['story_end_s']));card_duration=Fraction(str(settings['duration_s']))
    total=story+card_duration;packets=packet_info(source)
    keys=[p for p in packets if 'K' in p.get('flags','') and Fraction(p['pts'])*tb<story]
    if not keys:raise ValueError('No random-access boundary before ending.')
    key=max(keys,key=lambda p:p['pts']);cut=Fraction(key['pts'])*tb;cut_dts=Fraction(key['dts'])*tb
    lead_frames=round((story-cut)*fps);tail_frames=lead_frames+round(card_duration*fps)
    tail=work/'localized-tail.mp4'
    if not tail.exists():
        graph=(f'[0:v]trim=end_frame={lead_frames},setpts=PTS-STARTPTS[a];'
               f'[1:v]trim=end_frame={round(card_duration*fps)},setpts=PTS-STARTPTS[b];'
               '[a][b]concat=n=2:v=1:a=0[v]')
        dub.run([dub.tool('ffmpeg'),'-v','error','-nostdin','-n','-ss',str(float(cut)),'-i',str(source),
            '-i',str(card),'-f','lavfi','-i','anullsrc=r=48000:cl=stereo','-filter_complex',graph,
            '-map','[v]','-map','2:a:0','-t',str(float(total-cut)),'-frames:v',str(tail_frames),
            '-c:v','libx264','-preset','fast','-crf','18','-threads','2','-pix_fmt','yuv420p',
            '-video_track_timescale',str(tb.denominator),'-c:a','aac','-b:a','192k','-ar','48000','-ac','2',str(tail)],timeout=300)
    # concat's outpoint is exclusive DTS, not display time. Explicit duration
    # retains the original frame clock despite B-frame decoding delay.
    # https://ffmpeg.org/ffmpeg-formats.html#concat-1
    def quoted(path):return "'"+str(path.resolve()).replace("'","'\\''")+"'"
    content='ffconcat version 1.0\n'
    # Floor to the concat demuxer's microsecond precision: rounding upward can
    # accidentally retain the first packet of the GOP being replaced.
    outpoint_us=(cut_dts*1000000).__floor__()
    if cut>0:content+=f'file {quoted(source)}\noutpoint {outpoint_us/1000000:.6f}\nduration {float(cut):.9f}\n'
    content+=f'file {quoted(tail)}\nduration {float(total-cut):.9f}\n'
    listing=work/'picture.ffconcat'
    if not listing.exists():dub.write_new(listing,content.encode())
    elif listing.read_text()!=content:raise ValueError('Existing splice decisions differ.')
    if not out.exists():
        dub.run([dub.tool('ffmpeg'),'-v','error','-nostdin','-n','-copyts','-f','concat','-safe','0','-i',str(listing),
            '-i',str(source),'-map','0:v:0','-map','1:a:0','-t',str(float(total)),
            '-c:v','copy','-c:a','copy','-avoid_negative_ts','disabled','-movflags','+faststart',str(out)],timeout=300)
    result=dub.probe(out);video=next(x for x in result['streams'] if x['codec_type']=='video')
    if int(video['nb_frames'])!=round(total*fps) or abs(float(video['duration'])-float(total))>.001:
        raise ValueError('Localized final changed the frame count/duration.')
    if (v['width'],v['height'])!=(video['width'],video['height']):raise ValueError('Picture geometry changed.')
    new_tb=Fraction(video['time_base']);new_packets=packet_info(out)
    old_pts=sorted(Fraction(p['pts'])*tb for p in packets)
    new_pts=sorted(Fraction(p['pts'])*new_tb for p in new_packets)
    if old_pts!=new_pts:raise ValueError('Localized final changed picture timestamps.')
    if audio_hash(source)!=audio_hash(out):raise ValueError('Approved audio packets changed.')
    a,b=packet_info(source,'a:0'),packet_info(out,'a:0')
    if [(p['pts'],p['dts']) for p in a]!=[(p['pts'],p['dts']) for p in b]:
        raise ValueError('Approved audio timestamps changed.')
    copied_frames=round(cut*fps)
    if prefix_hash(source,copied_frames)!=prefix_hash(out,copied_frames):
        raise ValueError('Story picture changed before the ending splice GOP.')
    dub.run([dub.tool('ffmpeg'),'-v','error','-nostdin','-threads','2','-i',str(out),'-f','null','-'],timeout=900)
    record=dict(status='verified',language=cfg['language'],source_sha256=sha(source),output_sha256=sha(out),
        output_bytes=out.stat().st_size,story_end_s=float(story),duration_s=float(total),frames=round(total*fps),
        title=settings['title'],series=settings['series'],audio_packets_and_timestamps_unchanged=True,
        video_timestamps_unchanged=True,copied_story_frames=copied_frames,tail_reencode_start_s=float(cut),
        note='Only the short final GOP is re-encoded to insert the translated card; the earlier decoded story frames match exactly. No speech, subtitle timing, music or effects changed.')
    immutable_json(dub.relative(cfg['report']),record)
    print(json.dumps(record,ensure_ascii=False),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('config');a=p.parse_args()
    try:replace(dub.relative(a.config,True))
    except (ValueError,OSError,KeyError) as exc:p.exit(1,f'Error: {exc}\n')
