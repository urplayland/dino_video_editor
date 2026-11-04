"""Resolve workspace resources from this episode without depending on the shell cwd."""
from pathlib import Path

EPISODE = Path(__file__).resolve().parent
WORKSPACE = EPISODE.parents[3]
DINO = WORKSPACE / 'series' / 'dino'
