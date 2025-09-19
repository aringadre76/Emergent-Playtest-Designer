"""
Ollama client for local LLM integration with Llama 3.2 3B.
This provides real AI-powered explanations for exploit discovery.
"""

import requests
import json
import time
from typing import Dict, Any, Optional, List
from loguru import logger


class OllamaClient:
    """
    Client for Ollama local LLM integration.
    Uses Llama 3.2 3B for generating real AI explanations.
    """
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.2:3b"):
        """Initialize Ollama client."""
        self.base_url = base_url
        self.model = model
        self.session = requests.Session()
        self.session.timeout = 30
        
        # Test connection
        self._test_connection()
        
        logger.info(f"OllamaClient initialized with model: {model}")
    
    def _test_connection(self) -> bool:
        """Test connection to Ollama server."""
        try:
            response = self.session.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [model["name"] for model in models]
                
                if self.model in model_names:
                    logger.info(f"✅ Ollama connection successful, model {self.model} available")
                    return True
                else:
                    logger.warning(f"⚠️ Model {self.model} not found. Available models: {model_names}")
                    # Try to use the first available model
                    if model_names:
                        self.model = model_names[0]
                        logger.info(f"Using available model: {self.model}")
                        return True
                    else:
                        logger.error("❌ No models available in Ollama")
                        return False
            else:
                logger.error(f"❌ Ollama server not responding: {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            logger.error("❌ Cannot connect to Ollama server. Make sure Ollama is running on localhost:11434")
            return False
        except Exception as e:
            logger.error(f"❌ Error testing Ollama connection: {e}")
            return False
    
    def generate_explanation(self, exploit_data: Dict[str, Any]) -> str:
        """
        Generate AI explanation for an exploit using Llama 3.2 3B.
        """
        try:
            # Create prompt for exploit explanation
            prompt = self._create_exploit_explanation_prompt(exploit_data)
            
            # Call Ollama API
            response = self._call_ollama(prompt)
            
            if response:
                logger.debug(f"Generated explanation for {exploit_data.get('exploit_type', 'unknown')} exploit")
                return response
            else:
                return self._fallback_explanation(exploit_data)
                
        except Exception as e:
            logger.error(f"Error generating explanation: {e}")
            return self._fallback_explanation(exploit_data)
    
    def generate_exploit_explanation(self, exploit_data: Dict[str, Any]) -> str:
        """Generate detailed exploit explanation."""
        return self.generate_explanation(exploit_data)
    
    def analyze_game_behavior(self, behavior_data: Dict[str, Any]) -> str:
        """
        Analyze game behavior patterns using AI.
        """
        try:
            prompt = self._create_behavior_analysis_prompt(behavior_data)
            response = self._call_ollama(prompt)
            
            if response:
                return response
            else:
                return "Behavior analysis unavailable - using fallback analysis."
                
        except Exception as e:
            logger.error(f"Error analyzing behavior: {e}")
            return "Behavior analysis failed."
    
    def generate_reproduction_guide(self, exploit_data: Dict[str, Any]) -> str:
        """
        Generate step-by-step reproduction guide for an exploit.
        """
        try:
            prompt = self._create_reproduction_prompt(exploit_data)
            response = self._call_ollama(prompt)
            
            if response:
                return response
            else:
                return self._fallback_reproduction_guide(exploit_data)
                
        except Exception as e:
            logger.error(f"Error generating reproduction guide: {e}")
            return self._fallback_reproduction_guide(exploit_data)
    
    def _call_ollama(self, prompt: str) -> Optional[str]:
        """Call Ollama API with the given prompt."""
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 500
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
            else:
                logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error("Ollama API timeout")
            return None
        except Exception as e:
            logger.error(f"Error calling Ollama API: {e}")
            return None
    
    def _create_exploit_explanation_prompt(self, exploit_data: Dict[str, Any]) -> str:
        """Create prompt for exploit explanation."""
        exploit_type = exploit_data.get("exploit_type", "unknown")
        description = exploit_data.get("description", "No description available")
        severity = exploit_data.get("severity", "unknown")
        confidence = exploit_data.get("confidence", 0.0)
        
        prompt = f"""You are an expert game developer and QA engineer analyzing a game exploit. 

EXPLOIT DETAILS:
- Type: {exploit_type}
- Severity: {severity}
- Confidence: {confidence:.2f}
- Description: {description}

Please provide a clear, technical explanation of:
1. What this exploit does
2. Why it's problematic for the game
3. How it likely occurs in the game code
4. Potential impact on players
5. Recommended fix approach

Keep the explanation concise but informative, suitable for developers and QA teams."""

        return prompt
    
    def _create_behavior_analysis_prompt(self, behavior_data: Dict[str, Any]) -> str:
        """Create prompt for behavior analysis."""
        prompt = f"""You are analyzing unusual game behavior patterns. 

BEHAVIOR DATA:
{json.dumps(behavior_data, indent=2)}

Please analyze this behavior and explain:
1. What unusual patterns you observe
2. Why these patterns might indicate a problem
3. What the root cause could be
4. How this affects gameplay

Provide insights that would help game developers understand and fix the issue."""

        return prompt
    
    def _create_reproduction_prompt(self, exploit_data: Dict[str, Any]) -> str:
        """Create prompt for reproduction guide."""
        exploit_type = exploit_data.get("exploit_type", "unknown")
        description = exploit_data.get("description", "No description available")
        
        prompt = f"""You are creating a step-by-step reproduction guide for a game exploit.

EXPLOIT DETAILS:
- Type: {exploit_type}
- Description: {description}

Create a clear, numbered list of steps that QA testers can follow to reproduce this exploit. Include:
1. Prerequisites (game state, player position, etc.)
2. Exact actions to perform
3. Expected result
4. How to verify the exploit occurred

Make it simple enough for any tester to follow."""

        return prompt
    
    def _fallback_explanation(self, exploit_data: Dict[str, Any]) -> str:
        """Fallback explanation when Ollama is unavailable."""
        exploit_type = exploit_data.get("exploit_type", "unknown")
        severity = exploit_data.get("severity", "unknown")
        
        explanations = {
            "out_of_bounds": f"This exploit allows the player to move outside the intended game boundaries. This is a {severity} severity issue that can break game logic and cause crashes.",
            "infinite_resources": f"This exploit allows unlimited resource accumulation. This is a {severity} severity issue that breaks game balance and progression.",
            "stuck_state": f"The player becomes stuck and cannot move despite taking movement actions. This is a {severity} severity issue that prevents normal gameplay.",
            "infinite_loop": f"The game enters an infinite loop, likely due to improper loop termination conditions. This is a {severity} severity issue that can freeze the game.",
            "clipping": f"The player clips through solid objects, indicating collision detection issues. This is a {severity} severity issue that breaks game physics.",
            "sequence_break": f"The game sequence is broken, allowing invalid game states to persist. This is a {severity} severity issue that can cause unpredictable behavior."
        }
        
        return explanations.get(exploit_type, f"This is a {severity} severity {exploit_type} exploit that needs investigation.")
    
    def _fallback_reproduction_guide(self, exploit_data: Dict[str, Any]) -> str:
        """Fallback reproduction guide when Ollama is unavailable."""
        exploit_type = exploit_data.get("exploit_type", "unknown")
        
        guides = {
            "out_of_bounds": [
                "1. Start the game",
                "2. Move player to edge of map",
                "3. Continue moving in same direction",
                "4. Player will move outside intended boundaries"
            ],
            "infinite_resources": [
                "1. Start the game",
                "2. Find resource collection point",
                "3. Rapidly collect resources",
                "4. Resources will accumulate beyond normal limits"
            ],
            "stuck_state": [
                "1. Start the game",
                "2. Move to specific location",
                "3. Attempt to move in any direction",
                "4. Player will become stuck and unresponsive"
            ],
            "infinite_loop": [
                "1. Start the game",
                "2. Perform specific action sequence",
                "3. Repeat the sequence",
                "4. Game will enter infinite loop"
            ],
            "clipping": [
                "1. Start the game",
                "2. Move towards solid object",
                "3. Perform specific movement",
                "4. Player will pass through solid object"
            ],
            "sequence_break": [
                "1. Start the game",
                "2. Perform actions that break game logic",
                "3. Game will continue in invalid state",
                "4. Sequence will be broken"
            ]
        }
        
        steps = guides.get(exploit_type, [
            "1. Start the game",
            "2. Perform actions that trigger the exploit",
            "3. Observe the problematic behavior",
            "4. Document the steps for developers"
        ])
        
        return "\n".join(steps)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model."""
        try:
            response = self.session.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                for model in models:
                    if model["name"] == self.model:
                        return {
                            "name": model["name"],
                            "size": model.get("size", "unknown"),
                            "modified_at": model.get("modified_at", "unknown"),
                            "available": True
                        }
            
            return {
                "name": self.model,
                "available": False,
                "error": "Model not found"
            }
            
        except Exception as e:
            return {
                "name": self.model,
                "available": False,
                "error": str(e)
            }
    
    def test_generation(self) -> bool:
        """Test if the model can generate text."""
        try:
            test_prompt = "Say 'Hello, I am working correctly!' if you can process this request."
            response = self._call_ollama(test_prompt)
            
            if response and "working correctly" in response.lower():
                logger.info("✅ Ollama model test successful")
                return True
            else:
                logger.warning("⚠️ Ollama model test failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Ollama model test error: {e}")
            return False
