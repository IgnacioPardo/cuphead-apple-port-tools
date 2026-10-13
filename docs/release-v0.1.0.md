# v0.1.0 — Experimental Apple port tooling

First release of the original tooling developed during a Cuphead Apple Silicon
macOS and Apple TV port experiment.

## Included

- Local managed-code recovery through separately installed ILSpy.
- Compiler-checked repairs for the supported Unity 5.6.2p1 Mono build.
- A wrapper for a separately installed AssetRipper.
- Original file/preference save backends and optional game integration adapters.
- Unity 6000.6.5f1 ARM64 IL2CPP/Metal build and audit helpers.
- Synthetic tests, documentation, and publication checks covering working files,
  staged content, and Git history.

The original code is MIT-licensed. Users provide their own game installation,
development tools, and any required middleware. Game source, assets, DLLs,
reconstructed shaders, and compiled players are excluded from this release.

## Validation

Twelve Python tests and the standalone .NET file-store tests pass. Local checks
decompiled all five source assemblies, compiled the repaired three-assembly
baseline with zero errors, and ran the standalone helpers and PlayerPrefs tests
in a fresh Unity project. CI runs without game files or signing credentials.

See [validation scope](https://github.com/IgnacioPardo/cuphead-apple-port-tools/blob/v0.1.0/docs/validation.md)
for the limits of these checks.

## Current limits

This is an experimental tooling release. A complete migration from a purchased
game to a playable Unity 6 build is not yet automated. Shader reconstruction,
asset-reference repairs, and game-specific integration remain follow-on work.
The private experiment's working native players are not distributed here.

## Credits and resources

- [REA](https://github.com/morluto/rea) supported managed assembly and native-import
  inspection during the original recovery.
- [Apple Game Porting Toolkit](https://developer.apple.com/games/game-porting-toolkit/)
  provides related porting guidance and Metal resources; this repository's build
  workflow uses Unity IL2CPP and Metal.

Start with the [README](https://github.com/IgnacioPardo/cuphead-apple-port-tools/tree/v0.1.0#readme)
and [migration plan](https://github.com/IgnacioPardo/cuphead-apple-port-tools/blob/v0.1.0/PUBLICATION_PLAN.md).
