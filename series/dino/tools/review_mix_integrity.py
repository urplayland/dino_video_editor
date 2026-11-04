#!/usr/bin/env python3
"""Check each verified speech waveform remains audible in the encoded mix."""
import argparse
import json
import math
from pathlib import Path

import dub
import production
from brand_video import decoded_audio,digest


def similarity(reference,mixed):
    try:
        import numpy as np
    except ImportError:
        raise ValueError('Install requirements-transcription.txt for optional waveform QA.') from None
    a=np.asarray(reference,dtype=np.float64);b=np.asarray(mixed,dtype=np.float64)
    best=(-1,0,0)
    # At8kHz this allows only0.5ms codec/resampler alignment, not editorial drift.
    for lag in range(-4,5):
        x=a[4:-4];y=b[4+lag:len(b)-4+lag]
        if len(x)!=len(y) or not len(x):continue
        x=x-x.mean();y=y-y.mean();xx=float((x*x).sum());yy=float((y*y).sum())
        dot=float((x*y).sum());corr=dot/math.sqrt(xx*yy) if xx and yy else 0
        if corr>best[0]:best=(corr,lag,dot/xx if xx else 0)
    return {'correlation':best[0],'alignment_ms':best[1]/8,'level_ratio':best[2]}


def review(path):
    episode=dub.load(path);common=dub.load(dub.relative(episode['shared_audio_manifest'],True))
    selected=dict(episode,exports=common['exports'])
    results={}
    for lang in episode['languages']:
        if not production.verified_export(selected,lang):raise ValueError('Unverified shared export: '+lang)
        movie=dub.relative(common['exports'][lang],True)
        stem=dub.relative(common['dialogue'][lang]['path'],True)
        a=decoded_audio(stem,0,episode['duration_s']);b=decoded_audio(movie,0,episode['duration_s'])
        rows=[]
        for cue in production.language_manifest(episode,lang)['dialogue']:
            lo=round(cue['start_s']*8000);hi=round(cue['end_s']*8000)
            result=similarity(a[lo:hi],b[lo:hi])
            rows.append(dict(id=cue['id'],start_s=cue['start_s'],end_s=cue['end_s'],**result))
        passed=all(r['correlation']>=.95 and r['level_ratio']>0 for r in rows)
        record={'status':'passed_automated' if passed else 'needs_review','source':str(movie.relative_to(dub.ROOT)),
            'output_sha256':digest(movie),'verified_dialogue_stem_sha256':digest(stem),'cues':rows,
            'minimum_correlation':min(r['correlation'] for r in rows),
            'method':'Every cue from the independently ASR-verified speech stem is compared against actual mastered AAC including background music/SFX. Gain-invariant correlation>=0.95; maximum alignment allowance0.5ms.',
            'limits':'Waveform integrity verifies known speech is present and foregrounded; it does not establish human accent, acting, musical taste or voice identity approval. Short-line ASR orthography diagnostics remain separate.'}
        out=dub.relative(episode['report_dir']).parent/'final-mix-v001'/f'{lang}-waveform-integrity.json'
        out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(json.dumps(record,indent=2)+'\n');results[lang]=record
        print(lang,record['status'],record['minimum_correlation'],flush=True)
    if any(r['status']!='passed_automated' for r in results.values()):raise ValueError('Encoded dialogue waveform needs review.')
    return results


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('episode');args=p.parse_args()
    try:review(dub.relative(args.episode,True))
    except (ValueError,OSError,KeyError,TypeError) as error:p.exit(1,'Error: '+str(error)+'\n')
