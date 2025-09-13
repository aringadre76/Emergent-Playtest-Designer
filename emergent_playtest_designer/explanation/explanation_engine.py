"""Main explanation engine for generating exploit explanations."""

import asyncio
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from loguru import logger
from ..core.types import ExploitReport
from .llm_client import LLMClient
from .causal_analyzer import CausalAnalyzer, CausalChain


@dataclass
class ExplanationResult:
    """Represents the result of explanation generation."""
    exploit_id: str
    summary: str
    detailed_explanation: str
    causal_chain: CausalChain
    technical_details: Dict[str, Any]
    suggested_fixes: List[str]
    confidence: float
    generation_time: float


class ExplanationEngine:
    """Main engine for generating exploit explanations."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize explanation engine."""
        self.config = config
        self.llm_client = LLMClient(config.get("llm_config"))
        self.causal_analyzer = CausalAnalyzer(config.get("causal_config", {}))
        
    async def generate_explanation(self, exploit_report: ExploitReport) -> ExplanationResult:
        """Generate comprehensive explanation for exploit."""
        logger.info(f"Generating explanation for exploit {exploit_report.exploit_id}")
        
        start_time = asyncio.get_event_loop().time()
        
        causal_chain = self.causal_analyzer.analyze_causal_chain(exploit_report)
        
        exploit_data = {
            "exploit_id": exploit_report.exploit_id,
            "exploit_type": exploit_report.exploit_type.value,
            "severity": exploit_report.severity.value,
            "description": exploit_report.description,
            "confidence_score": exploit_report.confidence_score,
            "action_sequence": exploit_report.action_sequence.to_dict(),
            "game_states": [state.to_dict() for state in exploit_report.game_states],
            "reproduction_steps": exploit_report.reproduction_steps
        }
        
        detailed_explanation = await self.llm_client.generate_explanation(
            self._create_explanation_prompt(exploit_data),
            exploit_data
        )
        
        summary = self._generate_summary(exploit_report, causal_chain)
        technical_details = self._extract_technical_details(exploit_report, causal_chain)
        suggested_fixes = self._generate_suggested_fixes(exploit_report, causal_chain)
        
        generation_time = asyncio.get_event_loop().time() - start_time
        
        result = ExplanationResult(
            exploit_id=exploit_report.exploit_id,
            summary=summary,
            detailed_explanation=detailed_explanation.content,
            causal_chain=causal_chain,
            technical_details=technical_details,
            suggested_fixes=suggested_fixes,
            confidence=causal_chain.confidence,
            generation_time=generation_time
        )
        
        logger.info(f"Explanation generated in {generation_time:.2f}s")
        return result
    
    def _create_explanation_prompt(self, exploit_data: Dict[str, Any]) -> str:
        """Create prompt for explanation generation."""
        prompt = f"""
You are analyzing a game exploit discovered by an automated testing system. Please provide a comprehensive explanation of this exploit.

EXPLOIT INFORMATION:
- ID: {exploit_data['exploit_id']}
- Type: {exploit_data['exploit_type']}
- Severity: {exploit_data['severity']}
- Description: {exploit_data['description']}
- Confidence: {exploit_data['confidence_score']:.1%}

REPRODUCTION STEPS:
{self._format_reproduction_steps(exploit_data['reproduction_steps'])}

ACTION SEQUENCE:
{self._format_action_sequence(exploit_data['action_sequence'])}

GAME STATE ANALYSIS:
{self._format_game_states(exploit_data['game_states'])}

Please provide a detailed explanation that includes:

1. **EXECUTIVE SUMMARY**: Brief overview of what the exploit does and its impact
2. **TECHNICAL ANALYSIS**: Step-by-step breakdown of how the exploit works
3. **ROOT CAUSE**: What game mechanic or bug is being exploited
4. **IMPACT ASSESSMENT**: How this affects gameplay, balance, or player experience
5. **REPRODUCTION GUIDE**: Clear steps for developers to reproduce the issue
6. **SUGGESTED FIXES**: Specific recommendations for preventing or fixing this exploit
7. **PREVENTION STRATEGIES**: How to avoid similar exploits in the future

Focus on technical accuracy and provide actionable insights for game developers.
"""
        return prompt
    
    def _format_reproduction_steps(self, steps: List[str]) -> str:
        """Format reproduction steps for prompt."""
        if not steps:
            return "No reproduction steps provided"
        
        formatted = "Steps to reproduce:\n"
        for i, step in enumerate(steps, 1):
            formatted += f"{i}. {step}\n"
        
        return formatted
    
    def _format_action_sequence(self, action_sequence: Dict[str, Any]) -> str:
        """Format action sequence for prompt."""
        if not action_sequence or not action_sequence.get('actions'):
            return "No action sequence available"
        
        formatted = f"Action sequence (Duration: {action_sequence.get('total_duration', 0):.2f}s):\n"
        
        for i, action in enumerate(action_sequence['actions']):
            formatted += f"{i+1}. {action.get('timestamp', 0):.2f}s: {action.get('action_type', 'unknown')}"
            
            if action.get('parameters'):
                params = action['parameters']
                if 'key' in params:
                    formatted += f" (Key: {params['key']})"
                elif 'button' in params:
                    formatted += f" (Button: {params['button']})"
                elif 'axis' in params:
                    formatted += f" (Axis: {params['axis']}, Value: {params.get('value', 0):.2f})"
            
            formatted += f" (Duration: {action.get('duration', 0):.2f}s)\n"
        
        return formatted
    
    def _format_game_states(self, game_states: List[Dict[str, Any]]) -> str:
        """Format game states for prompt."""
        if not game_states:
            return "No game states available"
        
        formatted = f"Game state analysis ({len(game_states)} states):\n"
        
        for i, state in enumerate(game_states[:5]):
            formatted += f"\nState {i+1} (t={state.get('timestamp', 0):.2f}s):\n"
            formatted += f"  Position: {state.get('player_position', [0,0,0])}\n"
            formatted += f"  Health: {state.get('player_health', 0)}\n"
            
            resources = state.get('player_resources', {})
            if resources:
                formatted += f"  Resources: {resources}\n"
            
            physics = state.get('physics_state', {})
            if physics:
                formatted += f"  Physics: {physics}\n"
        
        if len(game_states) > 5:
            formatted += f"\n... and {len(game_states) - 5} more states\n"
        
        return formatted
    
    def _generate_summary(self, exploit_report: ExploitReport, causal_chain: CausalChain) -> str:
        """Generate executive summary."""
        summary = f"Exploit {exploit_report.exploit_id}: {exploit_report.description}\n\n"
        
        summary += f"This {exploit_report.exploit_type.value} exploit has {exploit_report.severity.value} severity "
        summary += f"and was discovered with {exploit_report.confidence_score:.1%} confidence. "
        
        summary += f"The exploit involves {len(causal_chain.events)} causal events "
        summary += f"over {exploit_report.action_sequence.total_duration:.2f} seconds. "
        
        summary += f"Root cause: {causal_chain.root_cause}. "
        summary += f"Mechanism: {causal_chain.exploit_mechanism}."
        
        return summary
    
    def _extract_technical_details(self, exploit_report: ExploitReport, 
                                 causal_chain: CausalChain) -> Dict[str, Any]:
        """Extract technical details from exploit."""
        return {
            "exploit_type": exploit_report.exploit_type.value,
            "severity": exploit_report.severity.value,
            "confidence": exploit_report.confidence_score,
            "duration": exploit_report.action_sequence.total_duration,
            "action_count": len(exploit_report.action_sequence.actions),
            "state_count": len(exploit_report.game_states),
            "causal_events": len(causal_chain.events),
            "root_cause": causal_chain.root_cause,
            "mechanism": causal_chain.exploit_mechanism,
            "causal_confidence": causal_chain.confidence
        }
    
    def _generate_suggested_fixes(self, exploit_report: ExploitReport, 
                                causal_chain: CausalChain) -> List[str]:
        """Generate suggested fixes based on exploit type."""
        fixes = []
        
        if exploit_report.exploit_type.value == "out_of_bounds":
            fixes.extend([
                "Add boundary checks in player movement code",
                "Implement collision detection for world boundaries",
                "Add teleportation prevention mechanisms",
                "Validate player position after movement calculations"
            ])
        
        elif exploit_report.exploit_type.value == "infinite_resources":
            fixes.extend([
                "Add resource gain rate limiting",
                "Implement resource validation checks",
                "Add cooldown periods for resource generation",
                "Validate resource values before applying changes"
            ])
        
        elif exploit_report.exploit_type.value == "stuck_state":
            fixes.extend([
                "Add stuck state detection and recovery",
                "Implement automatic respawn mechanisms",
                "Add state validation checks",
                "Implement timeout mechanisms for stuck states"
            ])
        
        elif exploit_report.exploit_type.value == "infinite_loop":
            fixes.extend([
                "Add loop detection mechanisms",
                "Implement maximum iteration limits",
                "Add state change validation",
                "Implement automatic loop breaking"
            ])
        
        else:
            fixes.extend([
                "Review and validate game state transitions",
                "Add comprehensive input validation",
                "Implement anomaly detection systems",
                "Add automated testing for edge cases"
            ])
        
        return fixes
    
    def generate_explanation_report(self, result: ExplanationResult) -> str:
        """Generate formatted explanation report."""
        report = f"""
EXPLOIT EXPLANATION REPORT
==========================

Exploit ID: {result.exploit_id}
Generated: {result.generation_time:.2f}s
Confidence: {result.confidence:.1%}

EXECUTIVE SUMMARY
-----------------
{result.summary}

DETAILED EXPLANATION
--------------------
{result.detailed_explanation}

TECHNICAL DETAILS
-----------------
"""
        
        for key, value in result.technical_details.items():
            report += f"- {key}: {value}\n"
        
        report += f"""
CAUSAL CHAIN ANALYSIS
--------------------
Root Cause: {result.causal_chain.root_cause}
Mechanism: {result.causal_chain.exploit_mechanism}
Events: {len(result.causal_chain.events)}

SUGGESTED FIXES
---------------
"""
        
        for i, fix in enumerate(result.suggested_fixes, 1):
            report += f"{i}. {fix}\n"
        
        return report
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get explanation engine statistics."""
        return {
            "llm_provider": self.llm_client.config.provider,
            "llm_model": self.llm_client.config.model,
            "causal_min_correlation": self.causal_analyzer.min_correlation,
            "causal_max_distance": self.causal_analyzer.max_causal_distance
        }
