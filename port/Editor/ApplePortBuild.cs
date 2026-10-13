using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.Build.Reporting;
using UnityEngine;
using UnityEngine.Rendering;

public static class ApplePortBuild
{
    [Serializable] private class Result
    {
        public string result, architecture, backend, elapsed;
        public int errors, warnings;
        public ulong bytes;
    }

    private static string[] Scenes()
    {
        var scenes = EditorBuildSettings.scenes.Where(s => s.enabled).Select(s => s.path).ToArray();
        if (scenes.Length == 0) throw new InvalidOperationException("Enable game scenes in Build Settings first.");
        return scenes;
    }

    private static void Configure(NamedBuildTarget named, BuildTarget target)
    {
        PlayerSettings.SetScriptingBackend(named, ScriptingImplementation.IL2CPP);
        PlayerSettings.SetManagedStrippingLevel(named, ManagedStrippingLevel.Minimal);
        PlayerSettings.SetUseDefaultGraphicsAPIs(target, false);
        PlayerSettings.SetGraphicsAPIs(target, new[] { GraphicsDeviceType.Metal });
        PlayerSettings.colorSpace = ColorSpace.Gamma;
    }

    private static void Record(BuildReport report, string filename)
    {
        var summary = report.summary;
        File.WriteAllText(ApplePortPaths.Report(filename), JsonUtility.ToJson(new Result {
            result = summary.result.ToString(), architecture = "ARM64", backend = "IL2CPP",
            errors = summary.totalErrors, warnings = summary.totalWarnings,
            bytes = summary.totalSize, elapsed = summary.totalTime.ToString()
        }, true));
        if (summary.result != BuildResult.Succeeded) throw new Exception("Build failed; inspect the local report and Editor log.");
    }

    [MenuItem("Cuphead Port/Build macOS ARM64 development player")]
    public static void BuildMac()
    {
        string[] scenes = Scenes();
        Configure(NamedBuildTarget.Standalone, BuildTarget.StandaloneOSX);
        UnityEditor.OSXStandalone.UserBuildSettings.architecture = OSArchitecture.ARM64;
        PlayerSettings.defaultScreenWidth = 1280;
        PlayerSettings.defaultScreenHeight = 720;
        PlayerSettings.fullScreenMode = FullScreenMode.Windowed;
        PlayerSettings.runInBackground = true;
        AssetDatabase.SaveAssets();
        string output = Path.Combine(ApplePortPaths.Root, "builds/macos-arm64/Cuphead Apple Port.app");
        Directory.CreateDirectory(Path.GetDirectoryName(output));
        Record(BuildPipeline.BuildPlayer(new BuildPlayerOptions {
            scenes = scenes, target = BuildTarget.StandaloneOSX,
            locationPathName = output, options = BuildOptions.Development
        }), "macos-build-result.json");
    }

    [MenuItem("Cuphead Port/Build Apple TV development player")]
    public static void BuildTV()
    {
        string[] scenes = Scenes();
        string team = Environment.GetEnvironmentVariable("APPLE_DEVELOPMENT_TEAM");
        string bundle = Environment.GetEnvironmentVariable("CUPHEAD_BUNDLE_ID");
        if (string.IsNullOrWhiteSpace(team) || string.IsNullOrWhiteSpace(bundle))
            throw new InvalidOperationException("Set APPLE_DEVELOPMENT_TEAM and CUPHEAD_BUNDLE_ID before starting Unity. No signing identity is bundled.");
        Configure(NamedBuildTarget.tvOS, BuildTarget.tvOS);
        PlayerSettings.SetApplicationIdentifier(NamedBuildTarget.tvOS, bundle);
        PlayerSettings.productName = "Cuphead Apple Port";
        PlayerSettings.tvOS.sdkVersion = tvOSSdkVersion.Device;
        PlayerSettings.tvOS.targetOSVersionString = "15.0";
        PlayerSettings.tvOS.requireExtendedGameController = true;
        PlayerSettings.iOS.appleEnableAutomaticSigning = true;
        PlayerSettings.iOS.appleDeveloperTeamID = team;
        TvOsSaveStoreChecks.Run();
        AssetDatabase.SaveAssets();
        string output = Path.Combine(ApplePortPaths.Root, "builds/tvos-xcode");
        Directory.CreateDirectory(output);
        Record(BuildPipeline.BuildPlayer(new BuildPlayerOptions {
            scenes = scenes, target = BuildTarget.tvOS,
            locationPathName = output, options = BuildOptions.Development
        }), "tvos-unity-build-result.json");
    }
}
