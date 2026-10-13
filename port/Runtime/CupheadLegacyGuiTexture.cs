using UnityEngine;

// Compatibility for Dialoguer's optional camera-fade helper. No GUITexture
// components were found in the source assets; this is created dynamically.
public sealed class CupheadLegacyGuiTexture : MonoBehaviour
{
    public Texture texture;
    public Color color = new Color(0.5f, 0.5f, 0.5f, 0.5f);

    private void OnGUI()
    {
        if (texture == null || Event.current.type != EventType.Repaint) return;
        Color previousColor = GUI.color;
        int previousDepth = GUI.depth;
        Vector3 position = transform.position;
        Vector3 scale = transform.lossyScale;
        try
        {
            GUI.depth = -(int)position.z;
            GUI.color = color * 2f;
            GUI.DrawTexture(new Rect((position.x - scale.x * 0.5f) * Screen.width,
                                     (1f - position.y - scale.y * 0.5f) * Screen.height,
                                     scale.x * Screen.width, scale.y * Screen.height), texture);
        }
        finally { GUI.color = previousColor; GUI.depth = previousDepth; }
    }
}
