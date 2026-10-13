# Publication and migration plan

The first release is a tooling repository. The working game reconstruction
remains in a separate private archive. Publishing a complete recovered Unity
project is outside this release's scope.

## Phase 1 — isolate the publishable material

- Start a new repository with no inherited Git history or LFS objects.
- Include only original tooling, platform helpers, synthetic tests, and written
  documentation. Record each included file in `public-files.json`.
- Exclude recovered C#, binaries, serialized assets, graphics, audio, logos,
  shader bytecode, reconstructed game shaders, game-derived repair manifests,
  raw evidence, and full source diffs.
- Apply MIT to the original code, with an explicit exclusion of external content.

Implementation: the reviewed file list, provenance notes, MIT license, and
third-party inventory are included in this repository.

## Phase 2 — make local tooling portable

- Require explicit input and output paths; remove machine-specific defaults.
- Keep source installations read-only and all generated output outside this repo.
- Recover and compile C# from the user's own installation.
- Derive compiler repairs from newly generated diagnostics instead of old logs.
- Install optional Apple adapters into an existing local Unity project without
  overwriting edits. Require user-supplied Apple signing configuration.

Implementation: the recovery, compilation, installation, and native verification
commands use explicit paths. AssetRipper remains a separately installed tool.

## Phase 3 — validate the repository boundary

- Test workspace isolation, assembly snapshot mismatches, helper installation,
  compiler transformations, and rejection of staged/historical credentials.
- Run file-store tests against synthetic data.
- Scan the working tree, Git index, and every commit reachable from local refs;
  reject non-reviewed paths, binary/LFS payloads, private output directories,
  common credentials, personal paths, and Apple identifiers.
- Run these checks in CI using read-only permissions. Do not upload recovered
  content, local reports, Unity logs, or private-workspace artifacts to Actions.

The automated check is a conservative guard, not a complete secret detector or
a legal determination. Human provenance review remains necessary when adding files.

## Phase 4 — private GitHub review, then public release

1. Create the new GitHub repository as **private** and push only its fresh history.
2. Verify CI and a fresh clone; confirm no source archive history, LFS objects,
   release assets, signing data, or private evidence came along.
3. Review the included-file provenance and license scope. Confirm the README
   describes the tooling's actual limits.
4. Obtain the owner's explicit decision to change visibility. Creation of the
   private review repository does not itself authorize a public release.

Visibility changes and game distribution are not automated by this repository.

## Follow-on work: a complete local migration pipeline

These items are deliberately outstanding; the current tools do not implement
an end-to-end playable port from a fresh purchase:

- Prepare an AssetRipper project while preserving script GUIDs; quarantine
  generated framework sources and resolve retained middleware through legitimate
  local dependencies.
- Review and implement the Unity 5.6 → 6000.6 API transformations, Apple startup
  selection, input fallback, bounded save initialization, and tvOS Options changes.
- Regenerate script-reference mappings, the debug InputField repair, and
  synchronized-layer animation assignments from the user's own input.
- Resolve shader reconstruction and dependency licensing before selecting a
  public implementation. Recovered shader programs, generated shader bodies, and
  Unity-supplied TextMeshPro resources are not included here.
- Validate a fresh local reconstruction through import, Metal audits, native
  builds, gameplay, restart persistence, two-player input, controller reconnection,
  and tvOS lifecycle handling.

Each new stage should include a provenance review, focused tests, and a
Conventional Commit. It must not depend on copies of the private archive's assets
or on previously generated private reports.
