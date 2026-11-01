#!/usr/bin/env python3
"""Package a reviewed release as individual files, never as an archive."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tempfile

import dub


def export(manifest):
    if manifest.get('schema_version')!=1 or not manifest.get('review_status'):
        raise ValueError('Release needs a version and explicit review status.')
    target=dub.relative(manifest['output_dir'])
    if not str(target.relative_to(dub.ROOT)).startswith('episodes/') or '/exports/' not in str(target.relative_to(dub.ROOT)):
        raise ValueError('Release packaging must remain in episode exports.')
    records=[];seen=set()
    for entry in manifest['files']:
        name=entry['destination'];relative=Path(name)
        if not name or relative.is_absolute() or '..' in relative.parts or name in seen or name=='FILE_MANIFEST.json':
            raise ValueError('Invalid or duplicate release destination.')
        seen.add(name)
        source=dub.relative(entry['source'],True)
        records.append(dict(entry,bytes=source.stat().st_size,sha256=hashlib.sha256(source.read_bytes()).hexdigest()))
    result={'schema_version':1,'review_status':manifest['review_status'],'files':records,'archive_created':False}
    if target.exists():
        stamp=target/'FILE_MANIFEST.json'
        if not stamp.is_file() or dub.load(stamp)!=result:
            raise ValueError('Release inputs changed; use a new release version.')
        for record in records:
            out=dub.relative(str((target/record['destination']).relative_to(dub.ROOT)),True)
            if hashlib.sha256(out.read_bytes()).hexdigest()!=record['sha256']:
                raise ValueError('Existing packaged file changed; preserve it and use a new version.')
        return result
    target.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='release-',dir=target.parent) as tmp:
        folder=Path(tmp)
        for record in records:
            source=dub.relative(record['source'],True)
            out=folder/record['destination'];out.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(source,out)
            if hashlib.sha256(out.read_bytes()).hexdigest()!=record['sha256']:
                raise ValueError('Release source changed while copying.')
        (folder/'FILE_MANIFEST.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
        folder.replace(target)
    print('Packaged',len(records),'individual files:',manifest['output_dir'])
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('manifest');args=p.parse_args()
    try:export(dub.load(dub.relative(args.manifest,True)))
    except (ValueError,OSError,KeyError,TypeError) as error:p.exit(1,'Error: '+str(error)+'\n')
