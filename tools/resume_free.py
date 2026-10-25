#!/usr/bin/env python3
"""Resume an owner-authorized list of existing free-tier Gemini credentials."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import dub


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest')
    parser.add_argument('--env-file',required=True)
    parser.add_argument('--keys',nargs='+',required=True,help='Explicit existing variables authorized by the owner; values are never logged')
    args=parser.parse_args()
    try:
        episode=dub.load(dub.relative(args.manifest,True))
        preflight=episode.get('api_preflight',{})
        if not preflight.get('owner_authorized_free_key_pool') or not preflight.get('owner_confirmed_billing_disabled'):
            raise ValueError('This runner requires owner authorization for existing free-tier credentials; it never enables billing.')
        allowed=preflight.get('authorized_key_variables',[])
        if any(key not in allowed for key in args.keys):
            raise ValueError('A requested key variable is outside the recorded owner-authorized list.')
        seen=set()
        for name in args.keys:
            os.environ.pop('GEMINI_API_KEY',None)
            dub.load_env(Path(args.env_file),name)
            value=os.environ.get('GEMINI_API_KEY')
            if not value:
                print(f'{name}: not configured; skipped.',flush=True)
                continue
            fingerprint=hashlib.sha256(value.encode()).hexdigest()
            if fingerprint in seen:
                print(f'{name}: duplicate of a selected credential; skipped.',flush=True)
                continue
            seen.add(fingerprint)
            os.environ['DINO_CREDENTIAL_LABEL']='bursa-sim:'+name
            print(f'Resuming with owner-authorized free-tier variable {name}.',flush=True)
            command=[sys.executable,str(Path(__file__).parent/'production.py'),args.manifest,'build','--live']
            process=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1)
            daily_quota=False
            for line in process.stdout:
                print(line,end='',flush=True)
                if 'GenerateRequestsPerDayPerProjectPerModel-FreeTier' in line:
                    daily_quota=True
            code=process.wait()
            if code==0:
                print('All full language builds and encoded-dialogue checks finished.',flush=True)
                return
            if daily_quota:
                print(f'{name}: daily free-tier quota exhausted; retained outputs; next explicitly authorized credential.',flush=True)
                continue
            raise ValueError(f'Production stopped on a non-daily-quota error with {name}; inspect the reports before any further requests.')
        raise ValueError('Selected free-tier credentials exhausted or unavailable. Outputs are retained; no billing was enabled.')
    except (ValueError,OSError,KeyError) as exc:
        parser.exit(1,f'Error: {exc}\n')


if __name__=='__main__':
    main()
