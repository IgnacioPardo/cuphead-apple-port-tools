using System.Collections;
using UnityEngine;
using UnityEngine.SceneManagement;

// Development-player evidence only. Does not change game state or input.
public sealed class ApplePortRuntimeDiagnostics : MonoBehaviour
{
#if (UNITY_STANDALONE_OSX || UNITY_TVOS) && !UNITY_EDITOR && DEVELOPMENT_BUILD
    private string controllerDescription;
    private float nextControllerSample;
    private float nextAxisSample;
    private float demoFpsUntil;
    private float fpsSampleStart;
    private int fpsSampleFrames;
    private float measuredFps;
    private GUIStyle fpsStyle;
    private bool animationEvidence;
    private float nextAnimationSample;
    [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.BeforeSceneLoad)]
    private static void Install()
    {
        var root = new GameObject("Apple port development diagnostics");
        DontDestroyOnLoad(root);
        root.AddComponent<ApplePortRuntimeDiagnostics>();
    }

    private void Awake()
    {
        UnityEngine.Debug.developerConsoleVisible = false;
        UnityEngine.Debug.developerConsoleEnabled = false;
        int demoSeconds;
        if (int.TryParse(System.Environment.GetEnvironmentVariable("CUPHEAD_DEMO_FPS_SECONDS"), out demoSeconds))
            demoFpsUntil = Time.realtimeSinceStartup + Mathf.Clamp(demoSeconds, 0, 120);
        fpsSampleStart = Time.realtimeSinceStartup;
        animationEvidence = System.Environment.GetEnvironmentVariable("CUPHEAD_ANIMATION_DIAGNOSTICS") == "1";
#if UNITY_TVOS
        UnityEngine.tvOS.Remote.allowExitToHome = false;
#endif
        UnityEngine.Debug.Log("APPLE_PORT_START unity=" + Application.unityVersion +
            " platform=" + Application.platform + " graphics=" + SystemInfo.graphicsDeviceType +
            " processor=" + SystemInfo.processorType + " screen=" + Screen.width + "x" + Screen.height +
            " desktopResolutions=" + Screen.resolutions.Length +
            " developerConsole=" + UnityEngine.Debug.developerConsoleEnabled +
            " demoFPSUntil=" + demoFpsUntil);
        SceneManager.sceneLoaded += OnSceneLoaded;
        StartCoroutine(ObserveFrames());
    }

    private void OnSceneLoaded(Scene scene, LoadSceneMode mode)
    {
        UnityEngine.Debug.Log("APPLE_PORT_SCENE name=" + scene.name + " frame=" + Time.frameCount);
    }

    private IEnumerator ObserveFrames()
    {
        for (int sample = 0; ; sample++)
        {
            yield return new WaitForSecondsRealtime(sample < 12 ? 5f : 30f);
            UnityEngine.Debug.Log("APPLE_PORT_FRAME scene=" + SceneManager.GetActiveScene().name +
                " frame=" + Time.frameCount + " realtime=" + Time.realtimeSinceStartup);
        }
    }

    private void Update()
    {
        fpsSampleFrames++;
        float now = Time.realtimeSinceStartup;
        if (now - fpsSampleStart >= 0.5f)
        {
            measuredFps = fpsSampleFrames / (now - fpsSampleStart);
            fpsSampleFrames = 0;
            fpsSampleStart = now;
        }
        if (!Rewired.ReInput.isReady) return;
        if (animationEvidence && now >= nextAnimationSample)
        {
            nextAnimationSample = now + 1.137f;
            SampleAnimations();
        }
        if (Time.unscaledTime >= nextControllerSample)
        {
            nextControllerSample = Time.unscaledTime + 1f;
            string description = string.Join(";", Input.GetJoystickNames());
            foreach (var joystick in Rewired.ReInput.controllers.Joysticks)
                description += " | rewired=" + joystick.id + ":" + joystick.name + ":" + joystick.hardwareIdentifier;
            if (controllerDescription != description)
            {
                controllerDescription = description;
                UnityEngine.Debug.Log("APPLE_PORT_CONTROLLERS " + description);
            }
        }
        foreach (var player in Rewired.ReInput.players.AllPlayers)
        {
            foreach (int action in new[] { 2, 3, 4, 5, 6, 7, 8, 11, 12, 13, 14, 15, 16, 18, 19, 20 })
                if (player.GetButtonDown(action))
                    UnityEngine.Debug.Log("APPLE_PORT_BUTTON player=" + player.id + " action=" + action);
            if (Time.unscaledTime >= nextAxisSample)
            {
                float x = player.GetAxis(0), y = player.GetAxis(1);
                if (Mathf.Abs(x) > 0.25f || Mathf.Abs(y) > 0.25f)
                    UnityEngine.Debug.Log("APPLE_PORT_AXIS player=" + player.id + " x=" + x + " y=" + y);
            }
        }
        if (Time.unscaledTime >= nextAxisSample) nextAxisSample = Time.unscaledTime + 0.5f;
    }

    private void OnGUI()
    {
        if (demoFpsUntil <= 0f || Time.realtimeSinceStartup >= demoFpsUntil) return;
        float scale = Mathf.Max(1f, Screen.height / 1080f);
        if (fpsStyle == null) fpsStyle = new GUIStyle(GUI.skin.label) { fontStyle = FontStyle.Bold };
        fpsStyle.fontSize = Mathf.RoundToInt(24f * scale);
        fpsStyle.normal.textColor = Color.white;
        Rect area = new Rect(Screen.safeArea.x + 24f * scale,
            Screen.height - Screen.safeArea.yMax + 24f * scale, 172f * scale, 48f * scale);
        Color color = GUI.color;
        GUI.color = new Color(0f, 0f, 0f, 0.75f);
        GUI.DrawTexture(area, Texture2D.whiteTexture);
        GUI.color = color;
        GUI.Label(new Rect(area.x + 12f * scale, area.y + 7f * scale, area.width, area.height),
            "FPS  " + measuredFps.ToString("F1"), fpsStyle);
    }

    private static string ObjectPath(Transform item)
    {
        return item.parent == null ? item.name : ObjectPath(item.parent) + "/" + item.name;
    }

    private static void SampleAnimations()
    {
        foreach (var animator in UnityEngine.Object.FindObjectsByType<Animator>(FindObjectsInactive.Exclude, FindObjectsSortMode.None))
        {
            if (animator.runtimeAnimatorController == null) continue;
            string sprites = "";
            foreach (var renderer in animator.GetComponentsInChildren<SpriteRenderer>())
                if (renderer.enabled && renderer.isVisible)
                    sprites += " " + renderer.name + "=" + (renderer.sprite == null ? "null" : renderer.sprite.name);
            if (sprites.Length == 0) continue;
            string states = "";
            if (animator.isInitialized)
                for (int layer = 0; layer < animator.layerCount; layer++)
                {
                    var state = animator.GetCurrentAnimatorStateInfo(layer);
                    states += " layer=" + layer + ":" + animator.GetLayerWeight(layer).ToString("F2") +
                        ":" + state.fullPathHash + ":" + state.normalizedTime.ToString("F3");
                }
            UnityEngine.Debug.Log("APPLE_PORT_ANIMATION object=" + ObjectPath(animator.transform) +
                " enabled=" + animator.enabled + " speed=" + animator.speed + states + " sprites=" + sprites);
        }
    }

    private void OnDestroy()
    {
        SceneManager.sceneLoaded -= OnSceneLoaded;
    }
#endif
}
