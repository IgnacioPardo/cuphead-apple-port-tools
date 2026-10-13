# Included-file provenance

This repository was prepared by selecting original tooling from a private Apple
port experiment and writing portable replacements. No game source or assets were
copied from the recovery trees, migrated Unity Assets directory, managed input
snapshot, shader reconstruction output, branding directory, or evidence archive.
No private Git commits were imported.

| Group | Origin and review |
| --- | --- |
| `port/Runtime/` | Original file/preference save implementations and GUI compatibility helper authored for the port |
| `port/Integration/` | Original local-service adapter and runtime diagnostics; references to external interfaces are API dependencies, whose implementations are excluded |
| `port/Editor/` | Original build/audit/test utilities, revised to remove personal signing configuration, branding dependencies, and asset-specific deletion lists |
| `scripts/recover.py`, `compile_managed.py`, `export_assets.py` | Portable replacements for original recovery orchestration; invoke separately obtained tools against private inputs |
| `scripts/prepare_sources.py` | Narrow syntax transformations over local ILSpy output, validated against freshly produced compiler diagnostics; no recovered method bodies are distributed |
| `scripts/verify_native_player.py` | Original architecture/log inspector with explicit local input and output paths |
| Other scripts and tests | Newly written workspace, installation, publication checks, and synthetic tests |
| Documentation, license, and CI | Written for this tooling edition; private evidence is summarized rather than copied |

The private experiment's reconstructed game shaders and large patch files were
excluded pending a separate rights/provenance review. Tooling that extracts local
content is not a claim that the extracted content can be redistributed.

`public-files.json` identifies every reviewed file. Additions require review of
both their origin and their contents; passing a pattern scanner alone is insufficient.
