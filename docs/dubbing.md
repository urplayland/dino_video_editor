# Dubbing implementation

The active workflow is [full episode production](production.md). The owner cancelled the earlier 8–10-second prototype stopping requirement.

`tools/dub.py` supplies safe dotenv loading, Gemini REST generation, immutable takes/provenance, timeline checks and FFmpeg mixing/rendering. It retains backward compatibility with the original `dubbing_poc` contract and also supports full-length `dubbing_production` manifests. `tools/production.py` orchestrates the multilingual production manifest, registry/schema validation, reusable assets, local transcript verification, timing fitting, generation and full renders.

The original handover scripts are preserved under `tools/kit/` and with episode originals. Production reuses the kit SFX implementation and its unchanged voice/style presets. The live-validated TTS path uses Google's `generateContent` REST contract, separate spoken text and style metadata, and complete WAV output. See [the official TTS guide](https://ai.google.dev/gemini-api/docs/generate-content/speech-generation). A successful generation does not establish final acting, pronunciation or mix approval.

See [production commands, current limitations and verification](production.md), and the [episode plan](../episodes/save-the-moon/edit-plan.md). No prototype-only gate remains.
