#!/usr/bin/env python3
"""Link verified dialogue exports and reviewed beds into a shared mix manifest."""
import argparse
import json

import audio_production
import dub
import production
import sfx


def link(episode_path, mix_path):
    episode=dub.load(episode_path)
    mix=dub.load(mix_path)
    mix['source_video']=episode['source_video']
    mix['source_video_sha256']=sfx.digest(dub.relative(episode['source_video'],True))
    mix['duration_s']=episode['duration_s']
    for lang in ('en','zh','ms'):
        if not production.verified_export(episode,lang):
            raise ValueError('Verified full dialogue export missing: '+lang)
        report_path=dub.relative(episode['exports'][lang],True).with_suffix('.json')
        report=dub.load(report_path)
        stem=report['stems']['dialogue']
        mix['dialogue'][lang].update(path=stem,sha256=sfx.digest(dub.relative(stem,True)),
            status='verified',provenance='Gemini dialogue with per-line generation metadata and automated transcript checks; '+str(report_path.relative_to(dub.ROOT)),
            license='Gemini-generated dialogue; provider terms apply. No third-party recording imported.',
            provenance_report=str(report_path.relative_to(dub.ROOT)))
    for spec in mix['music']+mix.get('ambience',[]):
        spec['sha256']=sfx.digest(dub.relative(spec['path'],True))
    mix['status']='verified'
    audio_production.validate(mix,True)
    # Validation above precedes the manifest mutation; media is never touched.
    mix_path.write_text(json.dumps(mix,indent=2,ensure_ascii=False)+'\n')
    print('Linked three verified dialogue stems:',mix_path.relative_to(dub.ROOT))
    return mix


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('episode')
    p.add_argument('mix')
    args=p.parse_args()
    try:
        link(dub.relative(args.episode,True),dub.relative(args.mix,True))
    except (ValueError,OSError,KeyError,TypeError) as error:
        p.exit(1,'Error: '+str(error)+'\n')
