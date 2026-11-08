# Family Learning Hub — video production

Shared post-production workspace for Dino Stories and Milo, with English, Mandarin Chinese and Malaysian Bahasa Melayu releases.

| Location | Contents |
|---|---|
| `series/dino/` | Dino tools, presets, episode plans and selected small reusable assets |
| `series/milo/episodes/learn-shapes/` | Milo EP01 editing code, plans and release handoff |
| `shared/Production_Guidelines.md` | Common production and future uncompressed-final requirements |
| `tools/publishing/` | Restricted YouTube connection and channel helpers |
| `config/publishing/` | Non-secret channel policy and playlist references |
| `secrets/`, `.env` | Private credentials; local only and ignored by Git |
| `local/`, `backups/` | Local diagnostics and restructuring backups; ignored by Git |

Read the [shared guideline](shared/Production_Guidelines.md) first. Its shared Drive location is [Videos/Production_Guidelines.md](https://drive.google.com/file/d/1mfEJlUVYEakgr9LQ2Zs200RG9WFLil8M/view). Future final exports use uncompressed video and PCM audio directly from the timeline. Existing Milo EP01 files are exempt and remain unchanged.

## Production entrypoints

Run Dino commands from `series/dino`, following [its production guide](series/dino/docs/production.md). The existing workspace environment remains at `/srv/video_editor/.venv`:

```sh
cd /srv/video_editor/series/dino
../../.venv/bin/python -m unittest discover -s tests -v
../../.venv/bin/python tools/check_git_assets.py
```

Milo EP01 instructions: [episode README](series/milo/episodes/learn-shapes/README.md), [edit plan](series/milo/episodes/learn-shapes/edit-plan.md), [release handoff](series/milo/episodes/learn-shapes/release-handoff-v001.md). Its scripts resolve shared resources independently of the shell's current directory. Existing MP4 renderers are historical EP01 implementations; adapt them before future final delivery.

Read-only YouTube verification:

```sh
cd /srv/video_editor
.venv/bin/python tools/publishing/youtube-manager.py status
```

YouTube policy stays in `config/publishing/youtube-policy.json`; OAuth clients/tokens stay private in `secrets/`. The Gemini environment file remains `.env`. No credential values belong in Git.

## Storage and recovery

Drive keeps episode originals, full videos, audio, subtitles and large dependencies under `Videos/{Dino_Stories,Milo}`. Approved local outputs remain under each episode's `exports`; earlier Milo reviews are under `archive/reviews`. Scratch/model caches may be recreated in `work` when needed. Original media and all final deliverables were checksum-verified during cleanup.

The repository was expanded from the existing Dino repository without replacing its history. Its existing GitHub remote remains `urplayland/dino_video_editor`; the workspace now covers both series. See [the reorganization record](docs/workspace-reorganization.md) for path migration and cleanup details.

Codex boot startup and the existing video-workspace Claude service are documented in [remote service operations](tools/remote-access/README.md).

Future Dino editing runs on another environment; see [the retirement and media recovery handoff](docs/dino-environment-handoff.md).
