# Cuphead Apple Port Tools

[![Validate tooling](https://github.com/IgnacioPardo/cuphead-apple-port-tools/actions/workflows/validate.yml/badge.svg)](https://github.com/IgnacioPardo/cuphead-apple-port-tools/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Original recovery tooling and Apple platform helpers developed while rebuilding
a local Cuphead installation for Apple Silicon macOS and Apple TV. This repository
contains Python tools, C# adapters, tests, and documentation. Supply your own game
installation and development tools; generated game content stays in a separate
private workspace.

**Status: experimental tooling.** The private migration has produced working
ARM64 IL2CPP/Metal players on macOS and physical Apple TV hardware. This tooling
edition supports local C# recovery, the known managed compilation repairs, helper
installation, and validation. It does **not** yet automate the complete migration
from a purchased game to a playable Unity 6 build. See the
[publication and migration plan](PUBLICATION_PLAN.md).

Start with the [v0.1.0 experimental tooling release](https://github.com/IgnacioPardo/cuphead-apple-port-tools/releases/tag/v0.1.0)
and [validation notes](docs/validation.md).

## What is included

- Recovery from a local GOG Windows Mono installation or its Wineskin wrapper.
- ILSpy invocation and compilation of locally recovered C# using .NET SDK 8.
- Narrow, compiler-checked repairs for the known ILSpy output from Unity 5.6.2p1.
- A wrapper for a separately installed AssetRipper 2.0.0.
- Original macOS file saves, bounded tvOS preference saves, and a legacy GUI helper.
- Optional local-service and diagnostics adapters requiring locally recovered APIs.
- Unity 6000.6.5f1 Editor utilities for ARM64 builds, script audits, and shader checks.
- A publication check covering reviewed paths, staged content, and all local Git refs.

Game source, DLLs, textures, music, scenes, prefabs, logos, recovered shader programs,
reconstructed game shaders, private logs, signing identities, and device records
are excluded. The repository has new history; no commits from the development
archive were imported. There are no Git LFS objects or compiled game releases.

## Quick start

Clone the repository with Git:

```sh
git clone https://github.com/IgnacioPardo/cuphead-apple-port-tools.git
cd cuphead-apple-port-tools
```

Use Python 3.9+ and .NET SDK 8. Install ILSpy separately:

```sh
dotnet tool install ilspycmd --tool-path "$HOME/.local/share/cuphead-port-tools/ilspy" --version 9.1.0.7988
```

From this repository, choose a **new workspace outside the repository** and the
directory containing your game's `Cuphead_Data` folder:

```sh
python3 scripts/recover.py \
  --game-dir "/path/to/your/Cuphead" \
  --workspace "$HOME/cuphead-private-workspace" \
  --ilspy "$HOME/.local/share/cuphead-port-tools/ilspy/ilspycmd"
python3 scripts/prepare_sources.py --workspace "$HOME/cuphead-private-workspace"
```

For the original Wineskin layout, replace `--game-dir` with
`--app "/path/to/your/Cuphead.app"`. Native macOS installations and IL2CPP game
builds are not supported by this recovery command. Omit `--ilspy` to snapshot
assemblies without decompiling. Inputs are read without executing the game.

The second command compiles raw recovery to obtain diagnostics, repairs a separate
`src/` tree, and compiles it again. It refuses an existing working source tree or
an unexpected recovery layout. The resulting managed DLLs are a source validation
checkpoint, not a game build. Reports and compiler logs stay in the workspace.

See [the recovery guide](docs/recovery.md) for asset export and the remaining
Unity migration steps.

## Install Apple helpers

For a **separate Unity 6000.6.5f1 project**, close Unity and run:

```sh
python3 scripts/install_port.py --project "/path/to/your/unity-project"
```

This installs standalone save/GUI helpers and Editor utilities. Use
`--game-adapters` only after your local project provides the recovered game
interfaces and Rewired dependencies. Installation preserves modified files and
does not patch the game or perform its Unity API migration.

In Unity, use the **Cuphead Port** menu to audit scenes/prefabs and compile
shaders on Metal. The build utilities require an already functioning migrated
project, enabled scenes, and the matching macOS IL2CPP or Apple TV module.
tvOS exports also require your own `APPLE_DEVELOPMENT_TEAM` and `CUPHEAD_BUNDLE_ID`
environment variables. No default signing identity or branded artwork is included.
See [Apple integration](docs/apple-integration.md).

## Development checks

```sh
python3 -m unittest discover -s tests -v
dotnet run --project tests/save-store/SaveStoreTests.csproj --configuration Release
python3 scripts/check_publication.py
```

CI runs these checks without game files, Unity, or signing credentials. Read
[validation scope](docs/validation.md) before interpreting test results. Changes
use [Conventional Commits](CONTRIBUTING.md).

## Tools and resources

- [REA — Reverse Engineer Anything](https://github.com/morluto/rea): used in the
  original recovery to inspect managed assembly metadata, CIL portability, and
  declared native dependencies. The private analysis used REA 6.4.0; the recovery
  scripts in this tooling edition do not currently invoke it.
- [Apple Game Porting Toolkit](https://developer.apple.com/games/game-porting-toolkit/):
  Apple's game-porting guidance, Windows game evaluation tools, and Metal shader
  conversion resources. It is a related resource rather than a required dependency
  of this repository's Unity IL2CPP/Metal build workflow.

## License and scope

The original code and documentation here use the [MIT license](LICENSE).
It grants no rights to Cuphead, Unity, Rewired, GOG, or other external content.
This is an unofficial project; Cuphead belongs to Studio MDHR.
[Third-party dependencies](THIRD_PARTY.md) are obtained separately under their
own terms. A local extraction workflow is not permission to redistribute its output.
