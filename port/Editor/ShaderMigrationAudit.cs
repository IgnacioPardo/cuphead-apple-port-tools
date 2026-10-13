using System;
using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;

public static class ShaderMigrationAudit
{
    [Serializable] public class Message
    {
        public string severity;
        public string message;
        public string platform;
        public string file;
        public int line;
    }
    [Serializable] public class Entry
    {
        public string path;
        public string name;
        public bool supported;
        public int passes;
        public int variants;
        public List<Message> messages = new List<Message>();
    }
    [Serializable] public class Report
    {
        public string graphicsDevice;
        public string graphicsVersion;
        public string scope = "Default and recovered material keyword sets; not exhaustive shader variants or visual equivalence.";
        public List<Entry> shaders = new List<Entry>();
    }

    [MenuItem("Cuphead Port/Compile recovered shaders on current GPU")]
    public static void CompileRecoveredShaders()
    {
        if (SystemInfo.graphicsDeviceType == GraphicsDeviceType.Null)
            throw new InvalidOperationException("Shader validation needs an Editor with a graphics device.");
        var report = new Report {
            graphicsDevice = SystemInfo.graphicsDeviceType.ToString(),
            graphicsVersion = SystemInfo.graphicsDeviceVersion
        };
        var materials = new List<Material>();
        foreach (string guid in AssetDatabase.FindAssets("t:Material", new[] { "Assets" }))
        {
            var material = AssetDatabase.LoadAssetAtPath<Material>(AssetDatabase.GUIDToAssetPath(guid));
            if (material != null) materials.Add(material);
        }
        foreach (string guid in AssetDatabase.FindAssets("t:Shader", new[] { "Assets" }))
        {
            string path = AssetDatabase.GUIDToAssetPath(guid);
            var shader = AssetDatabase.LoadAssetAtPath<Shader>(path);
            if (shader == null) continue;
            var entry = new Entry { path = path, name = shader.name };
            var variants = new HashSet<string>();
            var temporary = new Material(shader);
            try
            {
                Compile(temporary, variants, entry);
                foreach (Material material in materials)
                    if (material.shader == shader) Compile(material, variants, entry);
                entry.supported = shader.isSupported;
                foreach (var message in ShaderUtil.GetShaderMessages(shader))
                    entry.messages.Add(new Message { severity = message.severity.ToString(), message = message.message,
                        platform = message.platform.ToString(), file = message.file, line = message.line });
            }
            finally { UnityEngine.Object.DestroyImmediate(temporary); }
            report.shaders.Add(entry);
        }
        string output = ApplePortPaths.Report("metal-shader-audit.json");
        File.WriteAllText(output, JsonUtility.ToJson(report, true));
        Debug.Log("Shader compilation audit written: " + output);
    }

    static void Compile(Material material, HashSet<string> seen, Entry entry)
    {
        string[] keywords = material.shaderKeywords;
        Array.Sort(keywords, StringComparer.Ordinal);
        if (!seen.Add(string.Join(" ", keywords))) return;
        entry.variants++;
        entry.passes = material.passCount;
        for (int pass = 0; pass < material.passCount; pass++) ShaderUtil.CompilePass(material, pass, true);
    }
}
