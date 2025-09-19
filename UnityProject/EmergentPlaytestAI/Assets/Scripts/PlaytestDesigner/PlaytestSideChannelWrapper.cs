using UnityEngine;
using Unity.MLAgents;
using Unity.MLAgents.SideChannels;

/// <summary>
/// MonoBehaviour wrapper for PlaytestSideChannel to enable FindObjectOfType usage
/// </summary>
public class PlaytestSideChannelWrapper : MonoBehaviour
{
    private PlaytestSideChannel sideChannel;

    void Awake()
    {
        // Create and register the side channel
        sideChannel = new PlaytestSideChannel();
        sideChannel.Initialize();
        SideChannelManager.RegisterSideChannel(sideChannel);
    }

    void Update()
    {
        // Update performance tracking
        if (sideChannel != null)
        {
            sideChannel.UpdatePerformanceTracking();
        }
    }

    void OnDestroy()
    {
        // Unregister the side channel when destroyed
        if (sideChannel != null)
        {
            SideChannelManager.UnregisterSideChannel(sideChannel);
        }
    }

    public PlaytestSideChannel GetSideChannel()
    {
        return sideChannel;
    }
}
