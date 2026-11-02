#!/usr/bin/env python3
"""Restore exact large-media bytes from authenticated Drive IDs without generation."""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile


def restore(manifest,root,remote='GDrive:',only=None):
    cfg=json.loads(Path(manifest).read_text());root=Path(root).resolve()
    if cfg.get('schema_version')!=1 or not re.fullmatch(r'[A-Za-z0-9_-]+:',remote):
        raise ValueError('Unsupported restore manifest or remote name.')
    selected=set(only or []);specs=[];seen=set()
    for spec in cfg['files']:
        rel=Path(spec['path'])
        if rel.is_absolute() or '..' in rel.parts or not rel.parts or any(x.startswith('.env') or x=='.git' for x in rel.parts):
            raise ValueError('Unsafe restore path.')
        if str(rel) in seen:raise ValueError('Duplicate restore destination.')
        seen.add(str(rel))
        dest=root/rel
        if any(p.is_symlink() for p in [dest,*[p for p in dest.parents if p.is_relative_to(root)]]):
            raise ValueError('Restore path must not contain symlinks.')
        if not dest.resolve().is_relative_to(root):raise ValueError('Restore path escapes root.')
        if not re.fullmatch(r'[A-Za-z0-9_-]+',spec['drive_file_id']) or not re.fullmatch(r'[a-f0-9]{64}',spec['sha256']):
            raise ValueError('Invalid backup ID/checksum.')
        if not isinstance(spec['bytes'],int) or spec['bytes']<0:raise ValueError('Invalid backup size.')
        if not selected or str(rel) in selected:specs.append((spec,dest))
    if selected-seen:raise ValueError('Requested asset is absent from restore manifest.')
    def verify(path,spec):
        if not path.is_file() or path.stat().st_size!=spec['bytes']:return False
        h=hashlib.sha256()
        with path.open('rb') as stream:
            for chunk in iter(lambda:stream.read(1024*1024),b''):h.update(chunk)
        return h.hexdigest()==spec['sha256']
    count=0
    for spec,dest in specs:
        if dest.exists():
            if not verify(dest,spec):raise ValueError('Existing file differs; refusing overwrite: '+spec['path'])
            continue
        if not shutil.which('rclone'):raise ValueError('rclone and the named authenticated remote are required.')
        dest.parent.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='.restore-',dir=dest.parent) as temp:
            staged=Path(temp)/'asset'
            subprocess.run(['rclone','backend','copyid',remote,spec['drive_file_id'],str(staged)],check=True,capture_output=True)
            if not verify(staged,spec):raise ValueError('Downloaded backup checksum/size differs: '+spec['path'])
            # Same-directory hard link installs atomically and refuses overwrite.
            os.link(staged,dest)
        count+=1
    return dict(status='verified',restored=count,selected=len(specs))
