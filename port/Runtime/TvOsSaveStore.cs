using System;
using System.Collections.Generic;
using System.Text;
using UnityEngine;

// tvOS has no persistentDataPath. Keep small save JSON in the platform preferences
// store, with a previous snapshot and a combined 256 KiB application budget.
public sealed class TvOsSaveStore
{
    [Serializable] private sealed class Entry { public string key; public string value; }
    [Serializable] private sealed class Envelope { public int version = 1; public Entry[] entries; }
    private readonly string prefix;
    private const int MaximumSaveBytes = 256 * 1024;
    private Dictionary<string, string> slots;
    private string snapshot;

    public TvOsSaveStore(string prefix = "cuphead.freshport.tvos.saves") { this.prefix = prefix; }

    private static void ValidateKey(string key)
    {
        if (string.IsNullOrEmpty(key) || key.Length > 128) throw new ArgumentException("Invalid save key.");
        foreach (char c in key)
            if (!(c >= 'a' && c <= 'z') && !(c >= 'A' && c <= 'Z') &&
                !(c >= '0' && c <= '9') && c != '_' && c != '-')
                throw new ArgumentException("Invalid save key.");
    }

    private static Dictionary<string, string> Decode(string text)
    {
        var envelope = JsonUtility.FromJson<Envelope>(text);
        if (envelope == null || envelope.version != 1 || envelope.entries == null)
            throw new FormatException("Invalid tvOS save envelope.");
        var result = new Dictionary<string, string>();
        foreach (var entry in envelope.entries)
        {
            if (entry == null || entry.value == null) throw new FormatException("Invalid tvOS save entry.");
            ValidateKey(entry.key);
            result.Add(entry.key, entry.value);
        }
        return result;
    }

    public void Initialize()
    {
        if (slots != null) return;
        bool found = false;
        foreach (string suffix in new[] { ".current", ".previous" })
        {
            if (!PlayerPrefs.HasKey(prefix + suffix)) continue;
            found = true;
            string candidate = PlayerPrefs.GetString(prefix + suffix);
            try
            {
                slots = Decode(candidate);
                snapshot = candidate;
                if (suffix == ".previous") UnityEngine.Debug.LogWarning("Recovered tvOS saves from the previous snapshot.");
                return;
            }
            catch (Exception exception) { UnityEngine.Debug.LogWarning("Invalid tvOS save snapshot: " + exception.Message); }
        }
        if (found) throw new FormatException("Both tvOS save snapshots are invalid; refusing to overwrite them.");
        slots = new Dictionary<string, string>();
        snapshot = "";
    }

    public void Save(IDictionary<string, string> data)
    {
        Initialize();
        var next = new Dictionary<string, string>(slots);
        foreach (var entry in data)
        {
            ValidateKey(entry.Key);
            if (entry.Value == null) throw new ArgumentException("Null save contents.");
            next[entry.Key] = entry.Value;
        }
        var entries = new List<Entry>();
        foreach (var entry in next) entries.Add(new Entry { key = entry.Key, value = entry.Value });
        entries.Sort((a, b) => string.CompareOrdinal(a.key, b.key));
        string encoded = JsonUtility.ToJson(new Envelope { entries = entries.ToArray() });
        if (Encoding.UTF8.GetByteCount(encoded) + Encoding.UTF8.GetByteCount(snapshot) > MaximumSaveBytes)
            throw new InvalidOperationException("tvOS save snapshots exceed the reserved 256 KiB storage budget.");
        // Validate the complete replacement before updating either preference.
        if (snapshot.Length != 0) PlayerPrefs.SetString(prefix + ".previous", snapshot);
        PlayerPrefs.SetString(prefix + ".current", encoded);
        PlayerPrefs.Save();
        slots = next;
        snapshot = encoded;
    }

    public string[] Load(string[] keys, out bool anyData)
    {
        Initialize();
        var result = new string[keys.Length];
        anyData = false;
        for (int i = 0; i < keys.Length; i++)
        {
            ValidateKey(keys[i]);
            if (slots.TryGetValue(keys[i], out result[i])) anyData = true;
        }
        return result;
    }
}
