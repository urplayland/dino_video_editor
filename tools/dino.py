#!/usr/bin/env python3
"""Create and inventory Dino Adventures episodes without modifying source media."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import uuid


ROOT = Path(__file__).resolve().parents[1]


def find_tool(name):
    """Use an explicit override, PATH, then conventional macOS installations."""
    override = os.environ.get(f"DINO_{name.upper()}")
    if override:
        resolved = shutil.which(override)
        if not resolved:
            raise ValueError(f"DINO_{name.upper()} does not name an executable.")
        return resolved
    return shutil.which(name) or next(
        (str(p) for p in (Path('/opt/homebrew/bin') / name, Path('/usr/local/bin') / name)
         if p.is_file() and os.access(p, os.X_OK)), None
    )


def episode_path(slug):
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
        raise ValueError("Episode slug must use lowercase words or numbers separated by hyphens.")
    path = ROOT / "episodes" / slug
    if path.is_symlink() or not path.resolve().is_relative_to(ROOT):
        raise ValueError("Episode path must stay inside this workspace.")
    return path


def init_episode(args):
    destination = episode_path(args.slug)
    if destination.exists():
        raise ValueError(f"Episode already exists: {args.slug}; nothing was overwritten.")
    shutil.copytree(ROOT / "templates" / "episode", destination)
    manifest_path = destination / "episode.json"
    manifest = json.loads(manifest_path.read_text())
    manifest.update(slug=args.slug, title=args.title)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    for folder in ("media/originals", "media/derived", "work", "exports", "reports"):
        (destination / folder).mkdir(parents=True, exist_ok=True)
    print(f"Created episodes/{args.slug}")


def inspect_file(path, probe):
    digest = hashlib.sha256()
    before = path.stat()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    result = {
        "path": path.relative_to(ROOT).as_posix(),
        "bytes": before.st_size,
        "sha256": digest.hexdigest(),
    }
    media_extensions = {'.mp4', '.mov', '.mkv', '.webm', '.wav', '.mp3', '.aac', '.m4a', '.flac', '.ogg', '.aiff'}
    if probe and path.suffix.lower() in media_extensions:
        try:
            response = subprocess.run(
                [probe, "-v", "error", "-show_format", "-show_streams", "-of", "json", str(path)],
                capture_output=True, text=True, timeout=60, check=False,
            )
            if response.returncode:
                result["probe_error"] = response.stderr.strip() or "ffprobe failed"
            else:
                result["media"] = json.loads(response.stdout)
                if "format" in result["media"]:
                    result["media"]["format"]["filename"] = result["path"]
        except (subprocess.TimeoutExpired, json.JSONDecodeError) as error:
            result["probe_error"] = str(error)
    after = path.stat()
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise ValueError(f"File changed during inventory; retry when idle: {path}")
    return result


def inventory(args):
    episode = episode_path(args.slug)
    if not (episode / "episode.json").is_file():
        raise ValueError(f"Episode does not exist: {args.slug}")
    probe = find_tool("ffprobe")
    files = []
    for base in (episode / "media", ROOT / "library" / "media"):
        if base.is_symlink() or not base.resolve().is_relative_to(ROOT):
            raise ValueError(f"Media directory must stay inside the workspace: {base}")
        for path in sorted(base.rglob("*")):
            if path.is_symlink():
                raise ValueError(f"Symlinks are not supported in media inventories: {path}")
            if path.is_file() and path.name not in ("README.md", ".DS_Store"):
                files.append(inspect_file(path, probe))
    now = datetime.now(timezone.utc)
    report = {
        "schema_version": 1,
        "episode": args.slug,
        "created_at": now.isoformat(),
        "ffprobe_available": bool(probe),
        "files": files,
    }
    reports = episode / "reports"
    if reports.is_symlink() or not reports.resolve().is_relative_to(ROOT):
        raise ValueError("Reports directory must stay inside the workspace.")
    reports.mkdir(exist_ok=True)
    output = reports / f"inventory-{now:%Y%m%dT%H%M%S%fZ}-{uuid.uuid4().hex[:8]}.json"
    with output.open("x") as destination:
        json.dump(report, destination, indent=2)
        destination.write("\n")
    print(f"Inventoried {len(files)} files: {output.relative_to(ROOT)}")
    if not probe:
        print("ffprobe unavailable: hashes recorded; media stream properties remain unverified.")
    errors = sum("probe_error" in item for item in files)
    if errors:
        print(f"Review {errors} probe error(s) in the report; non-media files may not be probeable.")


def doctor(_args):
    print(f"Workspace: {ROOT}")
    print(f"Python: {sys.version.split()[0]}")
    for name in ("ffprobe", "ffmpeg"):
        print(f"{name}: {find_tool(name) or 'not installed'}")


def verify(args):
    episode_path(args.slug)
    report = json.loads(Path(args.report).read_text(encoding="utf-8"))
    if report.get('schema_version') != 1 or report.get('episode') != args.slug:
        raise ValueError('Report version or episode does not match.')
    if not report.get('files'):
        raise ValueError('Report contains no files to verify.')
    failures = []
    for item in report['files']:
        relative = Path(item['path'])
        path = ROOT / relative
        if relative.is_absolute() or '..' in relative.parts or not path.resolve().is_relative_to(ROOT):
            raise ValueError('Report contains a path outside the workspace.')
        if any(parent.is_symlink() for parent in (path, *path.parents) if parent != ROOT):
            raise ValueError('Report paths must not contain symlinks.')
        if not path.is_file():
            failures.append(f"Missing: {relative}")
            continue
        current = inspect_file(path, None)
        if current['sha256'] != item['sha256'] or current['bytes'] != item['bytes']:
            failures.append(f"Changed: {relative}")
    if failures:
        raise ValueError('\n'.join(failures))
    print(f"Verified {len(report['files'])} files against {args.report}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser("init", help="Create an episode from the template")
    create.add_argument("slug")
    create.add_argument("--title", required=True)
    create.set_defaults(run=init_episode)
    scan = commands.add_parser("inventory", help="Hash episode and shared media; inspect using ffprobe if available")
    scan.add_argument("slug")
    scan.set_defaults(run=inventory)
    check = commands.add_parser("doctor", help="Check local media tool availability")
    check.set_defaults(run=doctor)
    verification = commands.add_parser('verify', help='Check recorded files against an inventory after a copy or restore')
    verification.add_argument('slug')
    verification.add_argument('--report', required=True)
    verification.set_defaults(run=verify)
    args = parser.parse_args()
    try:
        args.run(args)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Error: {error}\n")


if __name__ == "__main__":
    main()
