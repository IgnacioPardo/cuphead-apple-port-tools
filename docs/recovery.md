# Local recovery workflow

The supported source is the GOG Windows Mono build using Unity 5.6.2p1. The original
experiment received it inside a Wineskin wrapper. The wrapper is just a container
for recovery: no Wine or game executable is run by these tools.

The game logic is managed CIL, so ILSpy can produce C#. This does not recover the
original authored project, comments, or guarantees of behavioral equivalence.
Unity scenes, prefabs, media, and native middleware are separate migration concerns.

## Prerequisites

- A user-supplied supported installation with `Cuphead_Data/Managed/`.
- Python 3.9+, .NET SDK 8, and ILSpy 9.1.0.7988.
- AssetRipper 2.0.0 if exporting assets. Install it separately from its upstream
  release; this repository neither bundles nor automatically downloads it.
- Substantial free disk space for extracted content and eventual Unity caches.

Follow the README's recovery commands. `recover.py` creates an external private
workspace with this layout:

```text
private-workspace/
  .gitignore                    # excludes all workspace contents
  .cuphead-private-workspace.json
  input/Managed/                # original assembly snapshot
  recovered/                    # raw ILSpy output
  src/                          # repaired working sources, after preparation
  evidence/                     # local paths, hashes, diagnostics, and reports
  builds/                       # recompiled managed DLLs and later native builds
  exports/                      # optional raw AssetRipper reconstruction
```

Treat everything in this workspace as private. Recovered source may include
service credentials embedded by the original publisher. The tooling does not
print source snippets or credentials, but external tools can write them into
local output and logs. Do not commit or upload those files.

`recover.py` verifies an existing snapshot before reuse and refuses a different
build. A partial decompilation is kept for diagnosis; repeat it in a new workspace
instead of deleting the failure evidence automatically.

## Managed compilation

```sh
python3 scripts/prepare_sources.py --workspace "$HOME/cuphead-private-workspace"
python3 scripts/compile_managed.py --workspace "$HOME/cuphead-private-workspace"
```

Preparation compiles raw recovery, identifies the expected 15 numeric character
switch labels from compiler diagnostics, and inlines three invalid iterator
reference aliases. It validates all expected matches before creating the working
tree. A different game/compiler output may be rejected; do not bypass the checks
without inspecting the private diagnostics.

The compiler selects an installed .NET SDK 8 Roslyn and uses the input game's
original Unity reference assemblies. It compiles gameplay, first-pass, and Galaxy
wrapper source. Rewired's recovered obfuscated source is inspection-only and is
not part of this compilation check.

## Raw asset export

```sh
python3 scripts/export_assets.py \
  --workspace "$HOME/cuphead-private-workspace" \
  --assetripper "/path/to/AssetRipper.GUI.Free"
```

The wrapper starts the exporter locally, supplies the source path from the private
manifest, requests a Unity export, and stops its server afterward. It refuses an
existing export directory because the exporter can delete output contents.

Successful export is not a functioning migrated project. In the private
experiment, AssetRipper produced placeholder shaders and omitted some component
fields and synchronized animation motions. The complete repair pipeline is
listed as follow-on work in `PUBLICATION_PLAN.md`.

## What the private experiment established

The historical input yielded 2,104 recovered C# files across five assemblies.
The repaired three-assembly baseline compiled without errors. Its separately
reconstructed Unity project reached native ARM64 macOS and Apple TV gameplay,
with audited scene/prefab scripts and Metal shader compilation.

Those observations describe the private experiment. They do not establish that
this tooling edition rebuilds that complete project, or that full campaign,
save/restart, controller reconnection, or two-player behavior has been validated.
