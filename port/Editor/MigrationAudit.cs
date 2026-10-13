using System;
using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

public static class MigrationAudit
{
    [Serializable] public class MissingScript { public string assetPath, objectPath; public int count; }
    [Serializable] public class Report
    {
        public int scenes, prefabs;
        public List<MissingScript> missingScripts = new List<MissingScript>();
    }

    private static string ObjectPath(Transform item)
    {
        return item.parent == null ? item.name : ObjectPath(item.parent) + "/" + item.name;
    }

    private static void Inspect(GameObject root, string path, Report report)
    {
        foreach (Transform child in root.GetComponentsInChildren<Transform>(true))
        {
            int count = GameObjectUtility.GetMonoBehavioursWithMissingScriptCount(child.gameObject);
            if (count > 0) report.missingScripts.Add(new MissingScript {
                assetPath = path, objectPath = ObjectPath(child), count = count
            });
        }
    }

    [MenuItem("Cuphead Port/Audit scene and prefab scripts")]
    public static void AuditScenesAndPrefabs()
    {
        if (EditorApplication.isPlaying) throw new InvalidOperationException("Exit play mode before auditing.");
        if (!EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo())
            throw new InvalidOperationException("Audit cancelled; unsaved scene changes were not approved for saving.");
        var setup = EditorSceneManager.GetSceneManagerSetup();
        var report = new Report();
        try
        {
            foreach (string guid in AssetDatabase.FindAssets("t:Scene", new[] { "Assets" }))
            {
                string path = AssetDatabase.GUIDToAssetPath(guid);
                var scene = EditorSceneManager.OpenScene(path, OpenSceneMode.Single);
                foreach (var root in scene.GetRootGameObjects()) Inspect(root, path, report);
                report.scenes++;
            }
            foreach (string guid in AssetDatabase.FindAssets("t:Prefab", new[] { "Assets" }))
            {
                string path = AssetDatabase.GUIDToAssetPath(guid);
                var root = AssetDatabase.LoadAssetAtPath<GameObject>(path);
                if (root == null) continue;
                Inspect(root, path, report);
                report.prefabs++;
            }
            File.WriteAllText(ApplePortPaths.Report("scene-prefab-script-audit.json"), JsonUtility.ToJson(report, true));
        }
        finally
        {
            if (setup.Length > 0) EditorSceneManager.RestoreSceneManagerSetup(setup);
            else EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
        }
        if (report.missingScripts.Count > 0)
            throw new InvalidOperationException("Missing scripts found; inspect the local audit. No components were deleted.");
    }
}
