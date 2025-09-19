using System.Collections;
using System.Collections.Generic;
using UnityEngine;

/// <summary>
/// Manages the overall playtest environment and game state.
/// </summary>
public class PlaytestManager : MonoBehaviour
{
    [Header("Environment Configuration")]
    [SerializeField] private Transform[] spawnPoints;
    [SerializeField] private GameObject playerPrefab;
    [SerializeField] private bool autoResetOnExploit = false;
    [SerializeField] private float maxEpisodeTime = 300f;
    
    [Header("Game State Tracking")]
    [SerializeField] private int initialPlayerHealth = 100;
    [SerializeField] private int initialPlayerScore = 0;
    [SerializeField] private bool enableTimeLimit = false;
    
    private float episodeStartTime;
    private bool debugMode = false;
    private GameStateData currentGameState;
    private List<ExploitSequenceData> pendingExploitTests = new List<ExploitSequenceData>();
    
    // Game objects tracking
    private List<GameObject> enemies = new List<GameObject>();
    private List<GameObject> collectibles = new List<GameObject>();
    private List<GameObject> dynamicObjects = new List<GameObject>();

    void Start()
    {
        InitializeEnvironment();
        ResetEnvironment();
    }

    void Update()
    {
        UpdateGameState();
        ProcessPendingExploitTests();
        
        if (debugMode)
        {
            DisplayDebugInfo();
        }
    }

    public void InitializeEnvironment()
    {
        episodeStartTime = Time.time;
        
        // Find and catalog game objects
        RefreshObjectLists();
        
        // Initialize game state
        currentGameState = new GameStateData
        {
            playerHealth = initialPlayerHealth,
            playerScore = initialPlayerScore,
            gameTime = 0f,
            enemyCount = enemies.Count,
            collectibleCount = collectibles.Count
        };
        
        Debug.Log("PlaytestManager environment initialized");
    }

    public void ResetEnvironment()
    {
        episodeStartTime = Time.time;
        
        // Reset player state
        var player = FindObjectOfType<PlaytestAgent>();
        if (player != null)
        {
            player.transform.position = GetSpawnPoint();
            var rb = player.GetComponent<Rigidbody>();
            if (rb != null)
            {
                rb.velocity = Vector3.zero;
                rb.angularVelocity = Vector3.zero;
            }
        }
        
        // Reset game objects
        ResetGameObjects();
        
        // Reset game state
        currentGameState.playerHealth = initialPlayerHealth;
        currentGameState.playerScore = initialPlayerScore;
        currentGameState.gameTime = 0f;
        
        RefreshObjectLists();
        currentGameState.enemyCount = enemies.Count;
        currentGameState.collectibleCount = collectibles.Count;
        
        Debug.Log("Environment reset completed");
    }

    public Vector3 GetSpawnPoint()
    {
        if (spawnPoints != null && spawnPoints.Length > 0)
        {
            return spawnPoints[Random.Range(0, spawnPoints.Length)].position;
        }
        return Vector3.zero;
    }

    public GameStateData GetCurrentGameState()
    {
        return currentGameState;
    }

    public float CalculateGameSpecificReward(Vector3 agentPosition, Vector3 agentVelocity)
    {
        float reward = 0f;
        
        // Distance-based exploration reward
        float explorationReward = CalculateExplorationReward(agentPosition);
        reward += explorationReward;
        
        // Interaction rewards
        reward += CalculateInteractionReward();
        
        // Performance-based rewards
        reward += CalculatePerformanceReward();
        
        // Novelty rewards
        reward += CalculateNoveltyReward(agentPosition, agentVelocity);
        
        return reward;
    }

    public bool ShouldTerminateEpisode()
    {
        // Time limit check
        if (enableTimeLimit && Time.time - episodeStartTime > maxEpisodeTime)
            return true;
            
        // Health check
        if (currentGameState.playerHealth <= 0)
            return true;
            
        // Game-specific termination conditions
        if (currentGameState.collectibleCount <= 0) // All collectibles gathered
            return true;
            
        return false;
    }

    public void ConfigureFromParameters(CommandParameters parameters)
    {
        if (parameters.performanceReportInterval > 0)
        {
            // Configure performance reporting interval
        }
        
        autoResetOnExploit = parameters.enablePerformanceReporting;
        debugMode = parameters.enableLogging;
    }

    public void InjectExploitTest(ExploitSequenceData[] exploitSequence)
    {
        if (exploitSequence != null)
        {
            pendingExploitTests.AddRange(exploitSequence);
            Debug.Log($"Injected {exploitSequence.Length} exploit test actions");
        }
    }

    public void SetDebugMode(bool enabled)
    {
        debugMode = enabled;
        Debug.Log($"Debug mode {(enabled ? "enabled" : "disabled")}");
    }

    private void UpdateGameState()
    {
        currentGameState.gameTime = Time.time - episodeStartTime;
        
        // Update object counts
        RefreshObjectLists();
        currentGameState.enemyCount = enemies.Count;
        currentGameState.collectibleCount = collectibles.Count;
        
        // Update player-specific state
        var player = FindObjectOfType<PlaytestAgent>();
        if (player != null)
        {
            // Health and score updates would come from game-specific components
            var healthComponent = player.GetComponent<HealthComponent>();
            if (healthComponent != null)
                currentGameState.playerHealth = healthComponent.GetHealth();
                
            var scoreComponent = player.GetComponent<ScoreComponent>();
            if (scoreComponent != null)
                currentGameState.playerScore = scoreComponent.GetScore();
        }
    }

    private void RefreshObjectLists()
    {
        enemies.Clear();
        enemies.AddRange(GameObject.FindGameObjectsWithTag("Enemy"));
        
        collectibles.Clear();
        collectibles.AddRange(GameObject.FindGameObjectsWithTag("Collectible"));
        
        dynamicObjects.Clear();
        dynamicObjects.AddRange(GameObject.FindGameObjectsWithTag("Dynamic"));
    }

    private void ResetGameObjects()
    {
        // Reset enemies to original positions and state
        foreach (var enemy in enemies)
        {
            if (enemy != null)
            {
                var resetComponent = enemy.GetComponent<IResettable>();
                if (resetComponent != null)
                    resetComponent.ResetToInitialState();
            }
        }
        
        // Reset collectibles
        foreach (var collectible in collectibles)
        {
            if (collectible != null)
            {
                collectible.SetActive(true);
                var resetComponent = collectible.GetComponent<IResettable>();
                if (resetComponent != null)
                    resetComponent.ResetToInitialState();
            }
        }
        
        // Reset dynamic objects
        foreach (var obj in dynamicObjects)
        {
            if (obj != null)
            {
                var resetComponent = obj.GetComponent<IResettable>();
                if (resetComponent != null)
                    resetComponent.ResetToInitialState();
            }
        }
    }

    private float CalculateExplorationReward(Vector3 position)
    {
        // Simple exploration reward based on distance from spawn
        float distanceFromSpawn = Vector3.Distance(position, GetSpawnPoint());
        return Mathf.Clamp(distanceFromSpawn * 0.01f, 0f, 0.1f);
    }

    private float CalculateInteractionReward()
    {
        // Reward for interacting with game objects
        float reward = 0f;
        
        // Check for recent object interactions
        var player = FindObjectOfType<PlaytestAgent>();
        if (player != null)
        {
            var interactionTracker = player.GetComponent<InteractionTracker>();
            if (interactionTracker != null)
            {
                reward += interactionTracker.GetRecentInteractionReward();
            }
        }
        
        return reward;
    }

    private float CalculatePerformanceReward()
    {
        // Reward for maintaining good performance
        float frameRate = 1.0f / Time.deltaTime;
        float targetFrameRate = Application.targetFrameRate;
        
        if (frameRate >= targetFrameRate * 0.9f)
            return 0.01f; // Small reward for good performance
        else if (frameRate < targetFrameRate * 0.5f)
            return -0.01f; // Small penalty for poor performance
            
        return 0f;
    }

    private float CalculateNoveltyReward(Vector3 position, Vector3 velocity)
    {
        // Reward for novel behaviors - this would be more sophisticated in practice
        float noveltyScore = 0f;
        
        // Velocity-based novelty
        if (velocity.magnitude > 10f && velocity.magnitude < 20f) // Interesting but not exploitative
            noveltyScore += 0.02f;
            
        // Position-based novelty (areas rarely visited)
        // This would typically use a more sophisticated spatial grid system
        
        return noveltyScore;
    }

    private void ProcessPendingExploitTests()
    {
        if (pendingExploitTests.Count > 0)
        {
            var currentTime = Time.time - episodeStartTime;
            
            for (int i = pendingExploitTests.Count - 1; i >= 0; i--)
            {
                var test = pendingExploitTests[i];
                if (currentTime >= test.timestamp)
                {
                    // Execute the exploit test action
                    ExecuteExploitTestAction(test);
                    pendingExploitTests.RemoveAt(i);
                }
            }
        }
    }

    private void ExecuteExploitTestAction(ExploitSequenceData testData)
    {
        var player = FindObjectOfType<PlaytestAgent>();
        if (player != null)
        {
            // This would inject the specific action into the agent
            Debug.Log($"Executing exploit test action: {testData.actionType} at {testData.timestamp}");
            // Implementation would depend on specific action types
        }
    }

    private void DisplayDebugInfo()
    {
        // Display debug information on screen or in console
        if (Time.frameCount % 60 == 0) // Update every second at 60fps
        {
            Debug.Log($"Game State - Time: {currentGameState.gameTime:F1}, " +
                     $"Health: {currentGameState.playerHealth}, " +
                     $"Score: {currentGameState.playerScore}, " +
                     $"Enemies: {currentGameState.enemyCount}, " +
                     $"Collectibles: {currentGameState.collectibleCount}");
        }
    }
}

[System.Serializable]
public class GameStateData
{
    public float playerHealth = 100f;
    public int playerScore = 0;
    public float gameTime = 0f;
    public int enemyCount = 0;
    public int collectibleCount = 0;
}

// Interface for resettable game objects
public interface IResettable
{
    void ResetToInitialState();
}
