using System.IO;
using UnityEngine;

// Outputs stay with the consumer's local Unity project, never in this tooling repo.
public static class ApplePortPaths
{
    public static string Root { get { return Path.GetFullPath(Path.Combine(Application.dataPath, "../..")); } }
    public static string Report(string filename)
    {
        string directory = Path.Combine(Root, "evidence");
        Directory.CreateDirectory(directory);
        return Path.Combine(directory, filename);
    }
}
