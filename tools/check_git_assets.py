#!/usr/bin/env python3
"""Verify the deliberately small, versioned Git media allowlist without generation."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def validate(manifest,root=ROOT):
    cfg=json.loads(Path(manifest).read_text())
    if cfg.get('schema_version')!=1:raise ValueError('Unsupported Git asset policy.')
    seen=set();total=0
    for spec in cfg['files']:
        relative=Path(spec['path'])
        if relative.is_absolute() or '..' in relative.parts or not relative.parts:
            raise ValueError('Asset must use a repository-relative path.')
        name=relative.as_posix()
        allowed=name.startswith('library/media/') or name.startswith('episodes/') and '/media/derived/' in name
        if not allowed or any(p.startswith('.env') or p=='.git' for p in relative.parts):
            raise ValueError('Only selected media assets may enter this allowlist.')
        target=root/relative
        if any(p.is_symlink() for p in [target,*target.parents]) or not target.resolve().is_relative_to(root.resolve()):
            raise ValueError('Asset must stay in the repository without symlinks.')
        if relative.as_posix() in seen:raise ValueError('Duplicate Git asset.')
        seen.add(relative.as_posix())
        data=target.read_bytes();total+=len(data)
        if len(data)>cfg['max_file_bytes']:raise ValueError('Asset exceeds small-file policy: '+str(relative))
        if hashlib.sha256(data).hexdigest()!=spec['sha256']:raise ValueError('Pinned Git asset changed: '+str(relative))
    if total>cfg['max_total_bytes']:raise ValueError('Git asset set exceeds total budget.')
    return dict(status='verified',files=len(seen),bytes=total)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest',nargs='?',default='library/presets/git-assets-v001.json')
    args=parser.parse_args()
    try:print(json.dumps(validate(ROOT/args.manifest)))
    except (ValueError,OSError,KeyError) as exc:parser.exit(1,f'Error: {exc}\n')
