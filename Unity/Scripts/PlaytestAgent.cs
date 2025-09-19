using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Unity.MLAgents;
using Unity.MLAgents.Actuators;
using Unity.MLAgents.Sensors;
using Unity.MLAgents.SideChannels;

/// <summary>
/// Main ML-Agents agent for automated playtesting and exploit discovery.
/// </summary>
public class PlaytestAgent : Agent
{
    [Header("Agent Configuration")]
    [SerializeField] private float movementSpeed = 5f;
    [SerializeField] private float jumpForce = 10f;
    [SerializeField] private bool enableContinuousMovement = true;
    [SerializeField] private bool enableDiscreteActions = false;
    
    [Header("Observation Configuration")]
    [SerializeField] private Camera observationCamera;
    [SerializeField] private bool useVisualObservations = false;
    [SerializeField] private bool useRaycastObservations = true;
    [SerializeField] private int raycastCount = 16;
    [SerializeField] private float raycastDistance = 10f;
    
    [Header("Exploit Detection")]
    [SerializeField] private ExploitDetector exploitDetector;
    [SerializeField] private PlaytestRecorder recorder;
    
    // Components
    private Rigidbody rb;
    private PlaytestSideChannel sideChannel;
    private PlaytestManager playtestManager;
    
    // State tracking
    private Vector3 lastPosition;
    private float stuckTimer = 0f;
    private int actionSequenceCount = 0;
    private List<int> lastActions = new List<int>();
    
    // Performance tracking
    private float episodeStartTime;
    private int totalSteps = 0;
    private float totalReward = 0f;

    public override void Initialize()
    {
        rb = GetComponent<Rigidbody>();
        if (rb == null)
            rb = gameObject.AddComponent<Rigidbody>();
            
        sideChannel = GameObject.FindObjectOfType<PlaytestSideChannel>();
        playtestManager = GameObject.FindObjectOfType<PlaytestManager>();
        
        if (exploitDetector == null)
            exploitDetector = GetComponent<ExploitDetector>();
            
        if (recorder == null)
            recorder = GetComponent<PlaytestRecorder>();
            
        if (observationCamera == null)
            observationCamera = Camera.main;
            
        lastPosition = transform.position;
        episodeStartTime = Time.time;
        
        Debug.Log("PlaytestAgent initialized");
    }

    public override void OnEpisodeBegin()
    {
        // Reset agent state
        ResetAgent();
        
        // Reset environment state
        if (playtestManager != null)
            playtestManager.ResetEnvironment();
            
        // Clear action history
        lastActions.Clear();
        actionSequenceCount = 0;
        stuckTimer = 0f;
        
        // Reset timers
        episodeStartTime = Time.time;
        totalSteps = 0;
        totalReward = 0f;
        
        Debug.Log("Episode began");
    }

    public override void CollectObservations(VectorSensor sensor)
    {
        // Agent position and velocity
        sensor.AddObservation(transform.position);
        sensor.AddObservation(rb.velocity);
        sensor.AddObservation(transform.rotation);
        
        // Ground check
        bool isGrounded = Physics.CheckSphere(transform.position + Vector3.down * 0.1f, 0.1f);
        sensor.AddObservation(isGrounded);
        
        // Raycast observations for spatial awareness
        if (useRaycastObservations)
        {
            for (int i = 0; i < raycastCount; i++)
            {
                float angle = i * (360f / raycastCount);
                Vector3 direction = Quaternion.Euler(0, angle, 0) * transform.forward;
                
                RaycastHit hit;
                float distance = Physics.Raycast(transform.position, direction, out hit, raycastDistance) ? 
                    hit.distance : raycastDistance;
                    
                sensor.AddObservation(distance / raycastDistance); // Normalized distance
                
                // Add object type information if hit
                if (hit.collider != null)
                {
                    sensor.AddObservation(GetObjectTypeEncoding(hit.collider.gameObject));
                }
                else
                {
                    sensor.AddObservation(0f); // No object
                }
            }
        }
        
        // Game state observations
        if (playtestManager != null)
        {
            var gameState = playtestManager.GetCurrentGameState();
            sensor.AddObservation(gameState.playerHealth);
            sensor.AddObservation(gameState.playerScore);
            sensor.AddObservation(gameState.gameTime);
            sensor.AddObservation(gameState.enemyCount);
            sensor.AddObservation(gameState.collectibleCount);
        }
        
        // Performance observations
        sensor.AddObservation(Time.deltaTime);
        sensor.AddObservation(Application.targetFrameRate);
        
        // Recent action history
        int historyLength = Mathf.Min(5, lastActions.Count);
        for (int i = 0; i < 5; i++)
        {
            if (i < historyLength)
                sensor.AddObservation(lastActions[lastActions.Count - 1 - i]);
            else
                sensor.AddObservation(0);
        }
    }

    public override void OnActionReceived(ActionBuffers actionBuffers)
    {
        totalSteps++;
        
        // Process continuous actions
        if (enableContinuousMovement && actionBuffers.ContinuousActions.Length >= 3)
        {
            float moveX = actionBuffers.ContinuousActions[0];
            float moveZ = actionBuffers.ContinuousActions[1];
            float jump = actionBuffers.ContinuousActions[2];
            
            // Apply movement
            Vector3 movement = new Vector3(moveX, 0, moveZ) * movementSpeed;
            rb.AddForce(movement, ForceMode.VelocityChange);
            
            // Apply jump if grounded
            if (jump > 0.5f && Physics.CheckSphere(transform.position + Vector3.down * 0.1f, 0.1f))
            {
                rb.AddForce(Vector3.up * jumpForce, ForceMode.Impulse);
            }
            
            // Record actions for pattern detection
            RecordAction(Mathf.RoundToInt(moveX * 10) + Mathf.RoundToInt(moveZ * 10) + (jump > 0.5f ? 100 : 0));
        }
        
        // Process discrete actions
        if (enableDiscreteActions && actionBuffers.DiscreteActions.Length > 0)
        {
            int action = actionBuffers.DiscreteActions[0];
            ProcessDiscreteAction(action);
            RecordAction(action);
        }
        
        // Calculate rewards
        float reward = CalculateReward();
        AddReward(reward);
        totalReward += reward;
        
        // Check for exploits
        CheckForExploits();
        
        // Check termination conditions
        CheckTerminationConditions();
        
        // Update position tracking
        lastPosition = transform.position;
    }

    public override void Heuristic(in ActionBuffers actionsOut)
    {
        // Manual control for testing
        var continuousActionsOut = actionsOut.ContinuousActions;
        continuousActionsOut[0] = Input.GetAxis("Horizontal");
        continuousActionsOut[1] = Input.GetAxis("Vertical");
        continuousActionsOut[2] = Input.GetKey(KeyCode.Space) ? 1.0f : 0.0f;
    }

    private void ProcessDiscreteAction(int action)
    {
        switch (action)
        {
            case 0: // No action
                break;
            case 1: // Move forward
                rb.AddForce(transform.forward * movementSpeed, ForceMode.VelocityChange);
                break;
            case 2: // Move backward
                rb.AddForce(-transform.forward * movementSpeed, ForceMode.VelocityChange);
                break;
            case 3: // Turn left
                transform.Rotate(0, -90f * Time.deltaTime, 0);
                break;
            case 4: // Turn right
                transform.Rotate(0, 90f * Time.deltaTime, 0);
                break;
            case 5: // Jump
                if (Physics.CheckSphere(transform.position + Vector3.down * 0.1f, 0.1f))
                    rb.AddForce(Vector3.up * jumpForce, ForceMode.Impulse);
                break;
        }
    }

    private float CalculateReward()
    {
        float reward = 0f;
        
        // Exploration reward - reward for moving to new areas
        float distanceMoved = Vector3.Distance(transform.position, lastPosition);
        reward += distanceMoved * 0.1f;
        
        // Survival reward
        reward += 0.01f;
        
        // Game-specific rewards from PlaytestManager
        if (playtestManager != null)
        {
            reward += playtestManager.CalculateGameSpecificReward(transform.position, rb.velocity);
        }
        
        // Penalty for being stuck
        if (distanceMoved < 0.1f)
        {
            stuckTimer += Time.deltaTime;
            if (stuckTimer > 5f)
                reward -= 0.1f;
        }
        else
        {
            stuckTimer = 0f;
        }
        
        return reward;
    }

    private void CheckForExploits()
    {
        if (exploitDetector != null)
        {
            exploitDetector.CheckExploits(transform.position, rb.velocity, lastActions);
        }
        
        // Built-in exploit checks
        
        // Out of bounds check
        if (transform.position.y < -50f || transform.position.y > 100f ||
            Mathf.Abs(transform.position.x) > 1000f || Mathf.Abs(transform.position.z) > 1000f)
        {
            SendExploitReport("out_of_bounds", "critical", transform.position, "Agent went out of game boundaries");
            AddReward(-1f);
        }
        
        // Infinite loop detection
        if (lastActions.Count >= 10)
        {
            if (IsRepeatingPattern(lastActions, 3))
            {
                SendExploitReport("infinite_loop", "high", transform.position, "Repeating action pattern detected");
                AddReward(-0.5f);
            }
        }
        
        // Velocity exploit check
        if (rb.velocity.magnitude > 50f)
        {
            SendExploitReport("velocity_exploit", "high", transform.position, "Excessive velocity detected");
            AddReward(-0.3f);
        }
    }

    private void CheckTerminationConditions()
    {
        // Episode too long
        if (Time.time - episodeStartTime > 300f) // 5 minutes max
        {
            EndEpisode();
        }
        
        // Agent fell out of world
        if (transform.position.y < -100f)
        {
            AddReward(-1f);
            EndEpisode();
        }
        
        // Game-specific termination
        if (playtestManager != null && playtestManager.ShouldTerminateEpisode())
        {
            EndEpisode();
        }
    }

    private void RecordAction(int action)
    {
        lastActions.Add(action);
        actionSequenceCount++;
        
        // Keep only recent actions
        if (lastActions.Count > 50)
            lastActions.RemoveAt(0);
    }

    private bool IsRepeatingPattern(List<int> actions, int patternLength)
    {
        if (actions.Count < patternLength * 3) return false;
        
        var recent = actions.GetRange(actions.Count - patternLength, patternLength);
        var previous = actions.GetRange(actions.Count - patternLength * 2, patternLength);
        
        for (int i = 0; i < patternLength; i++)
        {
            if (recent[i] != previous[i]) return false;
        }
        
        return true;
    }

    private void SendExploitReport(string exploitType, string severity, Vector3 position, string description)
    {
        if (sideChannel != null)
        {
            sideChannel.SendExploitReport(exploitType, severity, position, description, totalSteps);
        }
        
        Debug.LogWarning($"Exploit detected: {exploitType} - {description}");
    }

    private float GetObjectTypeEncoding(GameObject obj)
    {
        // Simple object type encoding based on tags
        switch (obj.tag)
        {
            case "Player": return 0.1f;
            case "Enemy": return 0.2f;
            case "Wall": return 0.3f;
            case "Platform": return 0.4f;
            case "Collectible": return 0.5f;
            case "Hazard": return 0.6f;
            default: return 0.0f;
        }
    }

    private void ResetAgent()
    {
        // Reset position to spawn point
        if (playtestManager != null)
        {
            transform.position = playtestManager.GetSpawnPoint();
        }
        
        // Reset physics
        rb.velocity = Vector3.zero;
        rb.angularVelocity = Vector3.zero;
        
        // Reset state
        lastPosition = transform.position;
        stuckTimer = 0f;
    }

    void OnTriggerEnter(Collider other)
    {
        // Reward system for triggers
        if (other.CompareTag("Collectible"))
        {
            AddReward(0.1f);
        }
        else if (other.CompareTag("Goal"))
        {
            AddReward(1.0f);
            EndEpisode();
        }
        else if (other.CompareTag("Hazard"))
        {
            AddReward(-0.5f);
            EndEpisode();
        }
    }

    void OnCollisionEnter(Collision collision)
    {
        // Collision-based rewards and exploits
        if (collision.gameObject.CompareTag("Enemy"))
        {
            AddReward(-0.2f);
        }
        
        // Check for clipping exploits
        if (collision.gameObject.CompareTag("Wall") && rb.velocity.magnitude > 10f)
        {
            SendExploitReport("potential_clipping", "medium", transform.position, "High-speed wall collision");
        }
    }
}
