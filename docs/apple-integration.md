# Apple helper integration

Install the helpers into a separate Unity 6000.6.5f1 project using `install_port.py`.
They are original code, but the optional integration adapters reference interfaces
provided by a user's locally recovered project.

| Helper | Dependency and behavior |
| --- | --- |
| `LocalSaveStore` | Standard .NET file APIs; validates slot keys, replaces each slot atomically, retains the previous file; no transaction across multiple slots |
| `TvOsSaveStore` | Unity PlayerPrefs/JsonUtility; current and previous snapshots share a 256 KiB budget; can recover a valid previous snapshot |
| `CupheadLegacyGuiTexture` | Unity GUI compatibility for a dynamically created legacy fade helper |
| `OnlineInterfaceLocal` | Requires local game interfaces; adapts the game's cloud-shaped API to local saves without online achievements or rich presence |
| `ApplePortRuntimeDiagnostics` | Requires local Rewired APIs; development-player logging, optional temporary FPS and animation sampling |

The installer alone does not activate the local provider or change platform
detection. Those game-specific transformations, Unity API repairs, script GUID
rebinding, and shader reconstruction remain separate migration work. Existing
Wine saves are not imported. No cloud synchronization is provided.

## Audits and builds

In the **Cuphead Port** menu:

1. **Audit scene and prefab scripts** checks scene and prefab objects for missing
   scripts and records a report. It does not delete components or repair references.
2. **Compile recovered shaders on current GPU** compiles the project's shaders
   using default and material keyword sets. Run with a graphics device and check
   that the report identifies Metal. This does not compare visuals.
3. **Build macOS ARM64 development player** selects ARM64, IL2CPP, and Metal.
4. **Build Apple TV development player** selects IL2CPP/Metal for a physical device
   and runs the isolated PlayerPrefs save tests before exporting Xcode.

Reports go to `evidence/` beside the consumer's project folder. Builds go to the
adjacent `builds/` directory. Keep both outside the public tooling repository.

For a batch macOS build, close the project in Unity first:

```sh
"/path/to/6000.6.5f1/Unity.app/Contents/MacOS/Unity" \
  -batchmode -quit -buildTarget StandaloneOSX \
  -projectPath "/path/to/your/unity-project" \
  -executeMethod ApplePortBuild.BuildMac \
  -logFile "/path/to/private-workspace/evidence/macos-build.log"
```

For tvOS, set `APPLE_DEVELOPMENT_TEAM` to your own team and `CUPHEAD_BUNDLE_ID`
to your own stable bundle identifier **before launching Unity**. Do not put them
in tracked files. Export using `-buildTarget tvOS -executeMethod ApplePortBuild.BuildTV`.
Open the resulting Xcode project, choose your paired device and signing team,
then build/install the `Unity-iPhone` scheme. Supply your own permitted artwork.

Keep your chosen bundle identifier consistent across updates if you need to
retain the app's local save identity. tvOS requires an extended controller;
the presence of a build or input map is not proof of controller or lifecycle behavior.

## Native player inspection

On macOS with Xcode command-line tools, inspect a locally built app:

```sh
python3 scripts/verify_native_player.py \
  --app "/path/to/your/built.app" \
  --log "/path/to/private-workspace/evidence/player.log" \
  --output "/path/to/private-workspace/evidence/player-verification.json"
```

`--log` is optional. Without it, the report provides architecture evidence only.
The command exits with failure for a non-ARM64 binary or recognized runtime error
lines. Advancing frames and clean logs still require separate observation of
picture, sound, input, gameplay, persistence, and suspend/resume.
