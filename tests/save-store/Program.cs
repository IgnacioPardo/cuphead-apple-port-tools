using System;
using System.Collections.Generic;
using System.IO;

class Program
{
    static void Check(bool condition, string message)
    {
        if (!condition) throw new Exception(message);
    }
    static void Main()
    {
        string root = Path.Combine(Path.GetTempPath(), "cuphead-save-test-" + Guid.NewGuid().ToString("N"));
        try
        {
            var store = new LocalSaveStore(root);
            var keys = new[] { "cuphead_player_data_v1_slot_0", "cuphead_player_data_v1_slot_1" };
            bool any;
            var empty = store.Load(keys, out any);
            Check(!any && empty[0] == null, "First launch must report no data.");
            store.Save(new Dictionary<string, string> { { keys[0], "{\"name\":\"ñ☕\",\"progress\":1}" } });
            var restarted = new LocalSaveStore(root).Load(keys, out any);
            Check(any && restarted[0].Contains("ñ☕") && restarted[1] == null, "Partial slots or Unicode lost.");
            store.Save(new Dictionary<string, string> { { keys[0], "second" } });
            Check(File.ReadAllText(Path.Combine(root, keys[0] + ".sav.previous")).Contains("progress"), "Previous version missing.");
            store.Save(new Dictionary<string, string> { { keys[0], "third" } });
            Check(store.Load(keys, out any)[0] == "third", "Repeated atomic replacement failed.");
            Check(File.ReadAllText(Path.Combine(root, keys[0] + ".sav.previous")) == "second", "Backup did not rotate.");
            try
            {
                store.Save(new Dictionary<string, string> { { keys[0], "bad" }, { "../escape", "bad" } });
                throw new Exception("Invalid key accepted.");
            }
            catch (ArgumentException) { }
            Check(store.Load(keys, out any)[0] == "third", "Invalid batch partially modified a slot.");
            Check(Directory.GetFiles(root, "*.tmp-*").Length == 0, "Temporary file leaked.");
            Console.WriteLine("PASS: first launch, Unicode, partial slots, restart, repeated replacement, previous-save backup, invalid batch, temporary-file cleanup.");
        }
        finally { if (Directory.Exists(root)) Directory.Delete(root, true); }
    }
}
