using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Unity.MLAgents.SideChannels;
using System.Text;

/// <summary>
/// Custom side channel for communication between Unity and Python.
/// Handles exploit reports, performance data, and configuration commands.
/// </summary>
public class PlaytestSideChannel : SideChannel
{
    [Header("Configuration")]
    [SerializeField] private bool enableLogging = true;
    [SerializeField] private bool enablePerformanceReporting = true;
    [SerializeField] private float performanceReportInterval = 1.0f;
    
    private PlaytestManager playtestManager;
    private float lastPerformanceReport = 0f;
    
    // Performance tracking
    private float[] frameTimeHistory = new float[60];
    private int frameTimeIndex = 0;
    private int totalFrames = 0;

    public PlaytestSideChannel()
    {
        ChannelId = new System.Guid("621f0a70-4f87-11ea-a6bf-784f4387d1f7");
    }

    void Start()
    {
        playtestManager = GameObject.FindAnyObjectByType<PlaytestManager>();
        
        if (enableLogging)
            Debug.Log("PlaytestSideChannel initialized");
    }

    void Update()
    {
        // Track performance metrics
        if (enablePerformanceReporting)
        {
            TrackPerformance();
            
            if (Time.time - lastPerformanceReport > performanceReportInterval)
            {
                SendPerformanceData();
                lastPerformanceReport = Time.time;
            }
        }
    }

    protected override void OnMessageReceived(IncomingMessage msg)
    {
        string command = msg.ReadString();
        string parametersJson = msg.ReadString();
        
        if (enableLogging)
            Debug.Log($"Received command: {command} with parameters: {parametersJson}");
        
        ProcessCommand(command, parametersJson);
    }

    private void ProcessCommand(string command, string parametersJson)
    {
        try
        {
            var parameters = JsonUtility.FromJson<CommandParameters>(parametersJson);
            
            switch (command)
            {
                case "CONFIGURE_TESTING":
                    ConfigureTesting(parameters);
                    break;
                    
                case "START_RECORDING":
                    StartRecording(parameters);
                    break;
                    
                case "STOP_RECORDING":
                    StopRecording();
                    break;
                    
                case "INJECT_EXPLOIT_TEST":
                    InjectExploitTest(parameters);
                    break;
                    
                case "RESET_ENVIRONMENT":
                    ResetEnvironment();
                    break;
                    
                case "SET_GAME_SPEED":
                    SetGameSpeed(parameters);
                    break;
                    
                case "ENABLE_DEBUG_MODE":
                    EnableDebugMode(parameters);
                    break;
                    
                default:
                    Debug.LogWarning($"Unknown command: {command}");
                    break;
            }
        }
        catch (System.Exception e)
        {
            Debug.LogError($"Error processing command {command}: {e.Message}");
        }
    }

    public void SendExploitReport(string exploitType, string severity, Vector3 position, string description, int frame)
    {
        using (var msg = new OutgoingMessage())
        {
            msg.WriteString("EXPLOIT_DETECTED");
            msg.WriteString(exploitType);
            msg.WriteString(severity);
            msg.WriteFloat32(position.x);
            msg.WriteFloat32(position.y);
            msg.WriteFloat32(position.z);
            msg.WriteString(description);
            msg.WriteInt32(frame);
            
            QueueMessageToSend(msg);
        }
        
        if (enableLogging)
            Debug.LogWarning($"Exploit reported: {exploitType} ({severity}) - {description}");
    }

    public void SendGameEvent(string eventName, string eventData)
    {
        using (var msg = new OutgoingMessage())
        {
            msg.WriteString("GAME_EVENT");
            msg.WriteString(eventName);
            msg.WriteString(eventData);
            msg.WriteFloat32(Time.time);
            
            QueueMessageToSend(msg);
        }
    }

    private void SendPerformanceData()
    {
        float avgFrameTime = 0f;
        int validFrames = 0;
        
        for (int i = 0; i < frameTimeHistory.Length; i++)
        {
            if (frameTimeHistory[i] > 0f)
            {
                avgFrameTime += frameTimeHistory[i];
                validFrames++;
            }
        }
        
        if (validFrames > 0)
        {
            avgFrameTime /= validFrames;
            float fps = 1.0f / avgFrameTime;
            
            using (var msg = new OutgoingMessage())
            {
                msg.WriteString("PERFORMANCE_DATA");
                msg.WriteFloat32(fps);
                msg.WriteFloat32(GetMemoryUsage());
                msg.WriteFloat32(GetCPUUsage());
                msg.WriteInt32(totalFrames);
                
                QueueMessageToSend(msg);
            }
        }
    }

    private void TrackPerformance()
    {
        frameTimeHistory[frameTimeIndex] = Time.deltaTime;
        frameTimeIndex = (frameTimeIndex + 1) % frameTimeHistory.Length;
        totalFrames++;
    }

    private float GetMemoryUsage()
    {
        // Unity memory usage in MB
        return UnityEngine.Profiling.Profiler.GetTotalAllocatedMemory(UnityEngine.Profiling.Profiler.Area.All) / (1024f * 1024f);
    }

    private float GetCPUUsage()
    {
        // Approximate CPU usage based on frame time
        float targetFrameTime = 1.0f / Application.targetFrameRate;
        return Mathf.Clamp01(Time.deltaTime / targetFrameTime) * 100f;
    }

    private void ConfigureTesting(CommandParameters parameters)
    {
        if (playtestManager != null)
        {
            playtestManager.ConfigureFromParameters(parameters);
        }
        
        // Configure performance reporting
        if (parameters.performanceReportInterval > 0)
        {
            performanceReportInterval = parameters.performanceReportInterval;
        }
        
        enablePerformanceReporting = parameters.enablePerformanceReporting;
        enableLogging = parameters.enableLogging;
    }

    private void StartRecording(CommandParameters parameters)
    {
        // PlaytestRecorder removed for ML-Agents 4.0.0 compatibility
        Debug.Log("Recording functionality temporarily disabled");
    }

    private void StopRecording()
    {
        // PlaytestRecorder removed for ML-Agents 4.0.0 compatibility
        Debug.Log("Recording functionality temporarily disabled");
    }

    private void InjectExploitTest(CommandParameters parameters)
    {
        if (playtestManager != null && parameters.exploitSequence != null)
        {
            playtestManager.InjectExploitTest(parameters.exploitSequence);
        }
    }

    private void ResetEnvironment()
    {
        if (playtestManager != null)
        {
            playtestManager.ResetEnvironment();
        }
    }

    private void SetGameSpeed(CommandParameters parameters)
    {
        if (parameters.gameSpeed > 0f)
        {
            Time.timeScale = parameters.gameSpeed;
        }
    }

    private void EnableDebugMode(CommandParameters parameters)
    {
        if (playtestManager != null)
        {
            playtestManager.SetDebugMode(parameters.enableDebugMode);
        }
    }
}

[System.Serializable]
public class CommandParameters
{
    public float performanceReportInterval = 1.0f;
    public bool enablePerformanceReporting = true;
    public bool enableLogging = true;
    public string outputPath = "";
    public ExploitSequenceData[] exploitSequence;
    public float gameSpeed = 1.0f;
    public bool enableDebugMode = false;
}

[System.Serializable]
public class ExploitSequenceData
{
    public float[] action;
    public float timestamp;
    public string actionType;
}
