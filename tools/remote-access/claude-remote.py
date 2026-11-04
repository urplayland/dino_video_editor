#!/usr/bin/env python3
"""Run one authenticated Claude remote server in a configured workspace."""
import os
from pathlib import Path

workspace = Path(os.environ['CLAUDE_WORKSPACE'])
if not workspace.is_absolute() or not workspace.is_dir():
    raise SystemExit('Configured workspace does not exist.')
cli = Path.home() / '.local/bin/claude'
os.chdir(workspace)
os.execv(str(cli), [str(cli), 'remote-control', '--name', os.environ['CLAUDE_REMOTE_NAME'],
                    '--spawn', 'same-dir', '--capacity', '1', '--permission-mode', 'default'])
