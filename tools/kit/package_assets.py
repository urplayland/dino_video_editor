#!/usr/bin/env python3
"""Bundle generated stems, manifests and edit cue sheet for a handoff."""
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parent


def main():
    episode = json.loads((ROOT / "episode.json").read_text(encoding="utf8"))
    missing_timing = any(c.get("start") is None or c.get("end") is None for c in episode["lines"])
    if missing_timing:
        print("WARNING: Dialogue cue times are incomplete. Editor must verify alignment.")
    archive = ROOT / "dino_audio_handoff.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for filename in ("README.md", "episode.json", "voices.json", "sfx_presets.json"):
            z.write(ROOT / filename, filename)
        for file in sorted((ROOT / "output").rglob("*.wav")) if (ROOT / "output").exists() else []:
            z.write(file, file.relative_to(ROOT).as_posix())
    print(f"Wrote {archive}")


if __name__ == "__main__":
    main()
