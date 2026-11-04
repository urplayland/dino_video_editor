#!/usr/bin/env python3
"""Generate independent Gemini TTS WAVs from an episode manifest; stdlib only."""
import argparse
import base64
import json
import os
from pathlib import Path
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent
URL = "https://generativelanguage.googleapis.com/v1beta/interactions"


def generate(key, model, voice, style, text):
    body = {
        "model": model,
        "input": [{"type": "user_input", "content": [{"type": "text", "text": text,
            "annotations": [{"type": "speech_metadata", "style": style}]}]}],
        "response_format": {"type": "audio"},
        "generation_config": {"speech_config": [{"voice": voice}]}
    }
    req = Request(URL, data=json.dumps(body).encode(), method="POST", headers={
        "Content-Type": "application/json", "x-goog-api-key": key})
    try:
        with urlopen(req, timeout=120) as response:
            result = json.load(response)
    except HTTPError as exc:
        raise RuntimeError(f"Gemini HTTP {exc.code}: check quota, billing and model access") from None
    except URLError as exc:
        raise RuntimeError(f"Connection error: {exc.reason}") from None
    for step in reversed(result.get("steps", [])):
        if step.get("type") == "model_output":
            for part in reversed(step.get("content", [])):
                if part.get("type") == "audio" and part.get("data"):
                    wav = base64.b64decode(part["data"], validate=True)
                    if wav[:4] != b"RIFF" or wav[8:12] != b"WAVE":
                        raise RuntimeError("Returned audio is not a standard WAV")
                    return wav
    raise RuntimeError("Gemini response contained no output audio")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--lang", choices=("en", "zh", "ms"), default="en")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--limit", type=int, default=0, help="Max API calls this run; 0=all")
    p.add_argument("--force", action="store_true", help="Overwrite existing generated WAVs")
    args = p.parse_args()
    config = json.loads((ROOT / "voices.json").read_text(encoding="utf8"))
    episode = json.loads((ROOT / "episode.json").read_text(encoding="utf8"))
    key = os.environ.get("GEMINI_API_KEY", "")
    if not args.dry_run and not key:
        p.error("Set GEMINI_API_KEY privately in your terminal first")
    destination = ROOT / "output" / "voices" / args.lang
    if not args.dry_run:
        destination.mkdir(parents=True, exist_ok=True)
    count = 0
    for line in episode["lines"]:
        name = line["id"]
        if not re.fullmatch(r"[a-zA-Z0-9_-]{1,80}", name):
            raise ValueError("Invalid dialogue line id")
        content = line.get("text", {}).get(args.lang, "").strip()
        if not content:
            continue
        actor = config["characters"][line["character"]]
        target = destination / f"{name}.wav"
        if target.exists() and not args.force:
            print(f"SKIP existing {target.relative_to(ROOT)}")
            continue
        print(f"{args.lang} / {name} / {actor['voice']} -> {target.relative_to(ROOT)}")
        if args.dry_run:
            continue
        if args.limit and count >= args.limit:
            break
        audio = generate(key, config["model"], actor["voice"], actor["style"][args.lang], content)
        target.write_bytes(audio)
        count += 1
    print(f"Done. New API calls: {count}")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, RuntimeError) as exc:
        sys.exit(str(exc))
