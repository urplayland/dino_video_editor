#!/usr/bin/env python3
"""Review the real shared-background releases using existing dialogue checks."""
import argparse
from pathlib import Path

import dub
import production


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('episode')
    p.add_argument('--lang',choices=('en','zh','ms','all'),default='all')
    p.add_argument('--model',help='Independent CPU recognizer model; defaults to small/small.en')
    p.add_argument('--by-cue',action='store_true')
    args=p.parse_args()
    try:
        episode=dub.load(dub.relative(args.episode,True))
        common=dub.load(dub.relative(episode['shared_audio_manifest'],True))
        episode['exports']=common['exports']
        episode['report_dir']=str(Path(episode['report_dir']).parent/'final-mix-v001')
        dub.relative(episode['report_dir']).mkdir(parents=True,exist_ok=True)
        for lang in episode['languages'] if args.lang=='all' else [args.lang]:
            production.verify_export_audio(episode,lang,args.model or ('small.en' if lang=='en' else 'small'),args.by_cue)
    except (ValueError,OSError,KeyError,TypeError) as error:p.exit(1,'Error: '+str(error)+'\n')


if __name__=='__main__':main()
