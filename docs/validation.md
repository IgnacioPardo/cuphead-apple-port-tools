# Validation scope

## Checks performed for the initial tooling edition

- Twelve Python tests passed for workspace isolation, snapshot mismatches,
  unfetched LFS inputs, non-destructive helper installation, the narrow compiler
  repairs, and detection of staged/historical credentials and binary payloads.
- The standalone .NET file-store tests passed for first launch, Unicode, partially
  missing slots, reopening stores, repeated replacement, previous-save backups,
  invalid batches, and temporary-file cleanup.
- The recovery command ran against the locally supplied original game using
  ILSpy 9.1.0.7988. All five assemblies decompiled successfully.
- Preparation generated fresh compiler diagnostics and repaired the expected
  three iterator aliases and fifteen character-switch labels. All three baseline
  assemblies compiled against the original references with .NET SDK 8.0.131 and
  zero errors. Gameplay emitted 2,999 warnings.
- The eight standalone helpers installed into a fresh Unity 6000.6.5f1 project,
  compiled without C# errors, and ran `TvOsSaveStoreChecks.Run()` successfully.
  These tests exercised Editor PlayerPrefs, including snapshot bounds, partial
  updates, previous-snapshot recovery, and refusal of two corrupt snapshots.

The source installations, raw recovery, compiler logs, Unity project, reports,
and generated assemblies used for these checks remain in an external private
workspace. They are not test fixtures or repository artifacts.

## CI coverage

CI runs Python tests, the standalone .NET file-store tests, and the publication
scanner with full fetched Git history. The workflow uses pinned action revisions,
read-only repository permissions, and no artifact uploads. It needs no game files,
Unity license, signing identity, or hardware.

The scanner checks the current working files, the index, and every commit
reachable from local refs. It rejects paths outside the reviewed manifest,
private output directories, symlinks/submodules, binary/LFS payloads, oversized
files, and selected credential/personal-data patterns. It reports rule names
and locations without values. It does not establish ownership or licensing,
detect every possible secret encoding, or inspect remote artifacts and refs
that were not fetched.

## Claims these checks do not establish

- A complete playable reconstruction from this repository alone.
- Runtime equivalence between recovered C# and the original game.
- The optional integration adapters being activated correctly in a migrated game.
- AssetRipper export fidelity, repaired asset references, or reconstructed shaders.
- New macOS/tvOS native builds of the complete game from the tooling edition.
- Physical-device save progression after restart, tvOS suspend/resume,
  controller reconnection, two-player behavior, or full campaign coverage.

The historical private port's device observations are summarized in the README
and recovery guide. They are distinct from tests of this tooling edition.
