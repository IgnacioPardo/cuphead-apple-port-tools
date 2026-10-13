using System;
using System.Collections.Generic;
using UnityEngine;

// New macOS port provider. The legacy "Cloud" API also carries local save slots.
public sealed class OnlineInterfaceLocal : OnlineInterface
{
#if UNITY_TVOS && !UNITY_EDITOR
    private TvOsSaveStore store;
#else
    private LocalSaveStore store;
#endif
    public OnlineUser MainUser { get { return null; } }
    public OnlineUser SecondaryUser { get { return null; } }
    public bool CloudStorageInitialized { get; private set; }
    public bool SupportsMultipleUsers { get { return false; } }
    public bool SupportsUserSignIn { get { return false; } }
    public event SignInEventHandler OnUserSignedIn;
    public event SignOutEventHandler OnUserSignedOut { add { } remove { } }

    public void Init() { }
    public void Reset() { }
    public void SignInUser(bool silent, PlayerId player, ulong controllerId)
    {
        if (OnUserSignedIn != null) OnUserSignedIn(null);
    }
    public void SwitchUser(PlayerId player, ulong controllerId) { }
    public OnlineUser GetUserForController(ulong id) { return null; }
    public List<ulong> GetControllersForUser(PlayerId player) { return new List<ulong>(); }
    public bool IsUserSignedIn(PlayerId player) { return false; }
    public OnlineUser GetUser(PlayerId player) { return null; }
    public void SetUser(PlayerId player, OnlineUser user) { }
    public Texture2D GetProfilePic(PlayerId player) { return null; }
    public void GetAchievement(PlayerId player, string id, AchievementEventHandler handler)
    {
        if (handler != null) handler(null);
    }
    // Service achievements and rich presence are unavailable in the local provider.
    public void UnlockAchievement(PlayerId player, string id) { }
    public void SyncAchievementsAndStats() { }
    public void SetStat(PlayerId player, string id, int value) { }
    public void SetStat(PlayerId player, string id, float value) { }
    public void SetStat(PlayerId player, string id, string value) { }
    public void IncrementStat(PlayerId player, string id, int value) { }
    public void SetRichPresence(PlayerId player, string id, bool active) { }
    public void SetRichPresenceActive(PlayerId player, bool active) { }

    public void InitializeCloudStorage(PlayerId player, InitializeCloudStoreHandler handler)
    {
        CloudStorageInitialized = false;
        try
        {
#if UNITY_TVOS && !UNITY_EDITOR
            store = new TvOsSaveStore();
#else
            store = new LocalSaveStore(Application.persistentDataPath);
#endif
            store.Initialize();
            CloudStorageInitialized = true;
        }
        catch (Exception exception) { Debug.LogException(exception); }
        if (handler != null) handler(CloudStorageInitialized);
    }
    public void UninitializeCloudStorage() { store = null; CloudStorageInitialized = false; }

    public void SaveCloudData(IDictionary<string, string> data, SaveCloudDataHandler handler)
    {
        bool success = false;
        try
        {
            if (store == null) throw new InvalidOperationException("Save storage is not initialized.");
            store.Save(data);
            success = true;
        }
        catch (Exception exception) { Debug.LogException(exception); }
        if (handler != null) handler(success);
    }

    public void LoadCloudData(string[] keys, LoadCloudDataHandler handler)
    {
        string[] data = new string[keys.Length];
        CloudLoadResult result = CloudLoadResult.Failed;
        try
        {
            if (store == null) throw new InvalidOperationException("Save storage is not initialized.");
            bool anyData;
            data = store.Load(keys, out anyData);
            result = anyData ? CloudLoadResult.Success : CloudLoadResult.NoData;
        }
        catch (Exception exception) { Debug.LogException(exception); }
        if (handler != null) handler(data, result);
    }
    public void UpdateControllerMapping() { }
    public bool ControllerMappingChanged() { return false; }
}
