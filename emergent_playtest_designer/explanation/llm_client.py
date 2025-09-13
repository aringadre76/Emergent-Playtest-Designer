"""LLM client for generating explanations."""

import asyncio
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from loguru import logger
from ..core.config import LLMConfig


@dataclass
class LLMResponse:
    """Represents an LLM response."""
    content: str
    usage: Dict[str, int]
    model: str
    finish_reason: str


class LLMClient:
    """Client for interacting with LLM APIs."""
    
    def __init__(self, config: LLMConfig):
        """Initialize LLM client."""
        self.config = config
        self.client = self._create_client()
        
    def _create_client(self):
        """Create LLM client based on provider."""
        if self.config.provider == "openai":
            return self._create_openai_client()
        elif self.config.provider == "anthropic":
            return self._create_anthropic_client()
        else:
            raise ValueError(f"Unsupported LLM provider: {self.config.provider}")
    
    def _create_openai_client(self):
        """Create OpenAI client."""
        try:
            import openai
            return openai.OpenAI(api_key=self.config.api_key)
        except ImportError:
            logger.error("OpenAI library not installed")
            raise
    
    def _create_anthropic_client(self):
        """Create Anthropic client."""
        try:
            import anthropic
            return anthropic.Anthropic(api_key=self.config.api_key)
        except ImportError:
            logger.error("Anthropic library not installed")
            raise
    
    async def generate_explanation(self, prompt: str, context: Dict[str, Any]) -> LLMResponse:
        """Generate explanation using LLM."""
        try:
            if self.config.provider == "openai":
                return await self._generate_openai_explanation(prompt, context)
            elif self.config.provider == "anthropic":
                return await self._generate_anthropic_explanation(prompt, context)
            else:
                raise ValueError(f"Unsupported provider: {self.config.provider}")
                
        except Exception as e:
            logger.error(f"Failed to generate explanation: {e}")
            return LLMResponse(
                content="Failed to generate explanation due to API error.",
                usage={"prompt_tokens": 0, "completion_tokens": 0},
                model=self.config.model,
                finish_reason="error"
            )
    
    async def _generate_openai_explanation(self, prompt: str, context: Dict[str, Any]) -> LLMResponse:
        """Generate explanation using OpenAI."""
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.config.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                timeout=self.config.timeout
            )
            
            return LLMResponse(
                content=response.choices[0].message.content,
                usage=response.usage.__dict__,
                model=response.model,
                finish_reason=response.choices[0].finish_reason
            )
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    async def _generate_anthropic_explanation(self, prompt: str, context: Dict[str, Any]) -> LLMResponse:
        """Generate explanation using Anthropic."""
        try:
            response = await asyncio.to_thread(
                self.client.messages.create,
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                system=self._get_system_prompt(),
                messages=[{"role": "user", "content": prompt}]
            )
            
            return LLMResponse(
                content=response.content[0].text,
                usage={
                    "prompt_tokens": response.usage.input_tokens,
                    "completion_tokens": response.usage.output_tokens
                },
                model=response.model,
                finish_reason=response.stop_reason
            )
            
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for LLM."""
        return """You are an expert game developer and QA analyst specializing in identifying and explaining game exploits and bugs. Your task is to analyze game state data, action sequences, and exploit reports to provide clear, technical explanations of how exploits work.

Key responsibilities:
1. Analyze game state transitions and action sequences
2. Identify the root cause of exploits
3. Explain the mechanics behind the exploit
4. Provide clear, actionable insights for developers
5. Suggest potential fixes or prevention strategies

Guidelines:
- Be precise and technical in your explanations
- Focus on the causal relationship between actions and outcomes
- Use game development terminology appropriately
- Provide specific frame numbers, coordinates, or values when relevant
- Explain both what happened and why it happened
- Suggest concrete steps for reproduction and fixing

Format your responses clearly with:
- Summary of the exploit
- Step-by-step explanation of the mechanics
- Root cause analysis
- Suggested fixes or prevention measures"""
    
    def generate_causal_analysis(self, exploit_data: Dict[str, Any]) -> str:
        """Generate causal analysis of exploit."""
        prompt = self._create_causal_analysis_prompt(exploit_data)
        
        try:
            response = asyncio.run(self.generate_explanation(prompt, exploit_data))
            return response.content
        except Exception as e:
            logger.error(f"Failed to generate causal analysis: {e}")
            return "Failed to generate causal analysis."
    
    def _create_causal_analysis_prompt(self, exploit_data: Dict[str, Any]) -> str:
        """Create prompt for causal analysis."""
        prompt = f"""
Analyze the following game exploit and provide a detailed causal explanation:

EXPLOIT DETAILS:
- Type: {exploit_data.get('exploit_type', 'Unknown')}
- Severity: {exploit_data.get('severity', 'Unknown')}
- Description: {exploit_data.get('description', 'No description')}
- Confidence: {exploit_data.get('confidence_score', 0.0)}

ACTION SEQUENCE:
{self._format_action_sequence(exploit_data.get('action_sequence', {}))}

GAME STATES:
{self._format_game_states(exploit_data.get('game_states', []))}

Please provide:
1. A clear summary of what the exploit does
2. Step-by-step explanation of how it works
3. Root cause analysis (what game mechanic is being exploited)
4. Specific frame numbers or timestamps where key events occur
5. Suggested fixes or prevention strategies
6. Impact assessment (how this affects gameplay)

Focus on the technical details and causal relationships between the actions and the exploit outcome.
"""
        return prompt
    
    def _format_action_sequence(self, action_sequence: Dict[str, Any]) -> str:
        """Format action sequence for prompt."""
        if not action_sequence or not action_sequence.get('actions'):
            return "No action sequence available"
        
        formatted = "Actions performed:\n"
        for i, action in enumerate(action_sequence['actions']):
            formatted += f"{i+1}. Frame {action.get('timestamp', 0):.2f}s: {action.get('action_type', 'unknown')}"
            if action.get('parameters'):
                formatted += f" - {action['parameters']}"
            formatted += f" (Duration: {action.get('duration', 0):.2f}s)\n"
        
        return formatted
    
    def _format_game_states(self, game_states: List[Dict[str, Any]]) -> str:
        """Format game states for prompt."""
        if not game_states:
            return "No game states available"
        
        formatted = "Key game states:\n"
        for i, state in enumerate(game_states[:10]):
            formatted += f"State {i+1} (t={state.get('timestamp', 0):.2f}s):\n"
            formatted += f"  Position: {state.get('player_position', [0,0,0])}\n"
            formatted += f"  Health: {state.get('player_health', 0)}\n"
            formatted += f"  Resources: {state.get('player_resources', {})}\n"
            if state.get('physics_state'):
                formatted += f"  Physics: {state['physics_state']}\n"
            formatted += "\n"
        
        if len(game_states) > 10:
            formatted += f"... and {len(game_states) - 10} more states\n"
        
        return formatted
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get LLM client statistics."""
        return {
            "provider": self.config.provider,
            "model": self.config.model,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "timeout": self.config.timeout
        }
