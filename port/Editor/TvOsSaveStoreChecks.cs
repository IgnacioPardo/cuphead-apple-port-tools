using System;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

public static class TvOsSaveStoreChecks
{
    private static void Require(bool condition, string message)
    {
        if (!condition) throw new Exception("tvOS save test failed: " + message);
    }

    public static void Run()
    {
        string prefix = "cuphead.port.tests." + Guid.NewGuid().ToString("N");
        try
        {
            bool any;
            var store = new TvOsSaveStore(prefix);
            var keys = new[] { "slot_0", "slot_1" };
            Require(store.Load(keys, out any)[0] == null && !any, "first launch");
            store.Save(new Dictionary<string, string> { { keys[0], "{\"name\":\"ñ☕\",\"progress\":1}" } });
            var restarted = new TvOsSaveStore(prefix);
            Require(restarted.Load(keys, out any)[0].Contains("ñ☕") && any, "restart / Unicode");
            restarted.Save(new Dictionary<string, string> { { keys[1], "second-slot" } });
            Require(new TvOsSaveStore(prefix).Load(keys, out any)[0].Contains("progress"), "partial save preserves other slots");
            string before = PlayerPrefs.GetString(prefix + ".current");
            try { restarted.Save(new Dictionary<string, string> { { keys[0], "changed" }, { "../bad", "bad" } }); throw new Exception("Invalid key accepted"); }
            catch (ArgumentException) { }
            Require(PlayerPrefs.GetString(prefix + ".current") == before, "invalid batch did not overwrite");
            try { restarted.Save(new Dictionary<string, string> { { keys[0], new string('x', 300000) } }); throw new Exception("Oversize save accepted"); }
            catch (InvalidOperationException) { }
            Require(PlayerPrefs.GetString(prefix + ".current") == before, "oversize did not overwrite");
            PlayerPrefs.SetString(prefix + ".current", "broken");
            var recovered = new TvOsSaveStore(prefix);
            Require(recovered.Load(keys, out any)[0].Contains("progress"), "corrupt current recovered previous");
            recovered.Save(new Dictionary<string, string> { { keys[1], "recovered-slot" } });
            Require(new TvOsSaveStore(prefix).Load(keys, out any)[1] == "recovered-slot", "save after recovery");
            PlayerPrefs.SetString(prefix + ".current", "broken");
            PlayerPrefs.SetString(prefix + ".previous", "broken");
            try { new TvOsSaveStore(prefix).Initialize(); throw new Exception("Corrupt snapshots accepted"); }
            catch (FormatException) { }
            File.WriteAllText(ApplePortPaths.Report("tvos-save-store-tests.txt"),
                "PASS: first launch, Unicode, partial slots, recreated store, invalid batch, size bound, previous-snapshot recovery, save after recovery, corrupt-data refusal.\nBackend exercised: Editor PlayerPrefs; device restart persistence requires separate validation.\n");
        }
        finally
        {
            PlayerPrefs.DeleteKey(prefix + ".current");
            PlayerPrefs.DeleteKey(prefix + ".previous");
            PlayerPrefs.Save();
        }
    }
}
