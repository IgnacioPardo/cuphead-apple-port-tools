using System;
using System.Collections.Generic;
using System.IO;
using System.Text;

// New port code. Stores the original game's JSON strings without conversion.
public sealed class LocalSaveStore
{
    private readonly string directory;

    public LocalSaveStore(string directory)
    {
        if (string.IsNullOrEmpty(directory) || !Path.IsPathRooted(directory))
            throw new ArgumentException("An absolute save directory is required.", "directory");
        this.directory = directory;
    }

    public void Initialize() { Directory.CreateDirectory(directory); }

    private string FilePath(string key)
    {
        if (string.IsNullOrEmpty(key)) throw new ArgumentException("Empty save key.");
        foreach (char c in key)
            if (!(c >= 'a' && c <= 'z') && !(c >= 'A' && c <= 'Z') &&
                !(c >= '0' && c <= '9') && c != '_' && c != '-')
                throw new ArgumentException("Invalid save key: " + key);
        return Path.Combine(directory, key + ".sav");
    }

    public void Save(IDictionary<string, string> data)
    {
        // Validate every entry before touching any existing slot.
        foreach (var entry in data)
        {
            FilePath(entry.Key);
            if (entry.Value == null) throw new ArgumentException("Null save contents.");
        }
        Initialize();
        foreach (var entry in data)
        {
            string destination = FilePath(entry.Key);
            string temporary = destination + ".tmp-" + Guid.NewGuid().ToString("N");
            try
            {
                byte[] bytes = new UTF8Encoding(false).GetBytes(entry.Value);
                using (var stream = new FileStream(temporary, FileMode.CreateNew, FileAccess.Write))
                {
                    stream.Write(bytes, 0, bytes.Length);
                    stream.Flush();
                }
                // Atomic per slot, not a transaction spanning all three slots.
                if (File.Exists(destination)) File.Replace(temporary, destination, destination + ".previous");
                else File.Move(temporary, destination);
            }
            finally
            {
                if (File.Exists(temporary)) File.Delete(temporary);
            }
        }
    }

    public string[] Load(string[] keys, out bool anyData)
    {
        var result = new string[keys.Length];
        anyData = false;
        for (int i = 0; i < keys.Length; i++)
        {
            string path = FilePath(keys[i]);
            // Missing slots stay null; PlayerData already initializes them to defaults.
            if (!File.Exists(path)) continue;
            result[i] = File.ReadAllText(path);
            anyData = true;
        }
        return result;
    }
}
