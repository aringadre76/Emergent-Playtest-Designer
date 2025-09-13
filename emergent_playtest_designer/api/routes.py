"""API routes for the Emergent Playtest Designer."""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from loguru import logger
from ..core.orchestrator import PlaytestOrchestrator, TestingConfig
from ..core.types import ExploitReport


router = APIRouter()


class TestingSessionRequest(BaseModel):
    """Request model for starting testing session."""
    game_path: str
    max_duration: int = 3600
    max_episodes: int = 1000
    agent_type: str = "novelty_search"
    exploit_detection_enabled: bool = True
    reproduction_enabled: bool = True
    explanation_enabled: bool = True


class TestingSessionResponse(BaseModel):
    """Response model for testing session."""
    session_id: str
    status: str
    message: str


class ExploitResponse(BaseModel):
    """Response model for exploit."""
    exploit_id: str
    exploit_type: str
    severity: str
    description: str
    confidence_score: float
    reproduction_steps: List[str]
    video_path: Optional[str] = None
    screenshots: List[str] = []
    explanation: Optional[str] = None


class SessionStatusResponse(BaseModel):
    """Response model for session status."""
    session_id: str
    game_path: str
    start_time: float
    end_time: Optional[float]
    is_running: bool
    exploits_found: int
    total_actions: int
    total_states: int


def get_orchestrator(request) -> PlaytestOrchestrator:
    """Get orchestrator from request state."""
    return request.app.state.orchestrator


@router.post("/testing/start", response_model=TestingSessionResponse)
async def start_testing_session(
    request: TestingSessionRequest,
    background_tasks: BackgroundTasks,
    orchestrator: PlaytestOrchestrator = Depends(get_orchestrator)
):
    """Start a new testing session."""
    try:
        testing_config = TestingConfig(
            game_path=request.game_path,
            max_duration=request.max_duration,
            max_episodes=request.max_episodes,
            agent_type=request.agent_type,
            exploit_detection_enabled=request.exploit_detection_enabled,
            reproduction_enabled=request.reproduction_enabled,
            explanation_enabled=request.explanation_enabled
        )
        
        session_id = await orchestrator.start_testing_session(testing_config)
        
        return TestingSessionResponse(
            session_id=session_id,
            status="started",
            message=f"Testing session {session_id} started successfully"
        )
        
    except Exception as e:
        logger.error(f"Failed to start testing session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/testing/stop")
async def stop_testing_session(
    orchestrator: PlaytestOrchestrator = Depends(get_orchestrator)
):
    """Stop current testing session."""
    try:
        orchestrator.stop_testing()
        
        return {
            "status": "stopped",
            "message": "Testing session stopped successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to stop testing session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/testing/status", response_model=SessionStatusResponse)
async def get_session_status(
    orchestrator: PlaytestOrchestrator = Depends(get_orchestrator)
):
    """Get current session status."""
    try:
        status = orchestrator.get_session_status()
        
        if status["status"] == "no_session":
            raise HTTPException(status_code=404, detail="No active session")
        
        return SessionStatusResponse(**status)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get session status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/exploits", response_model=List[ExploitResponse])
async def get_exploits(
    orchestrator: PlaytestOrchestrator = Depends(get_orchestrator)
):
    """Get all discovered exploits."""
    try:
        status = orchestrator.get_session_status()
        
        if status["status"] == "no_session":
            return []
        
        exploits = []
        if orchestrator.current_session:
            for exploit in orchestrator.current_session.exploits_found:
                exploits.append(ExploitResponse(
                    exploit_id=exploit.exploit_id,
                    exploit_type=exploit.exploit_type.value,
                    severity=exploit.severity.value,
                    description=exploit.description,
                    confidence_score=exploit.confidence_score,
                    reproduction_steps=exploit.reproduction_steps,
                    video_path=exploit.video_path,
                    screenshots=exploit.screenshots or [],
                    explanation=exploit.explanation
                ))
        
        return exploits
        
    except Exception as e:
        logger.error(f"Failed to get exploits: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/exploits/{exploit_id}", response_model=ExploitResponse)
async def get_exploit(
    exploit_id: str,
    orchestrator: PlaytestOrchestrator = Depends(get_orchestrator)
):
    """Get specific exploit by ID."""
    try:
        if not orchestrator.current_session:
            raise HTTPException(status_code=404, detail="No active session")
        
        for exploit in orchestrator.current_session.exploits_found:
            if exploit.exploit_id == exploit_id:
                return ExploitResponse(
                    exploit_id=exploit.exploit_id,
                    exploit_type=exploit.exploit_type.value,
                    severity=exploit.severity.value,
                    description=exploit.description,
                    confidence_score=exploit.confidence_score,
                    reproduction_steps=exploit.reproduction_steps,
                    video_path=exploit.video_path,
                    screenshots=exploit.screenshots or [],
                    explanation=exploit.explanation
                )
        
        raise HTTPException(status_code=404, detail="Exploit not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get exploit: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics")
async def get_statistics(
    orchestrator: PlaytestOrchestrator = Depends(get_orchestrator)
):
    """Get system statistics."""
    try:
        stats = orchestrator.get_statistics()
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/exploits/{exploit_id}/reproduce")
async def reproduce_exploit(
    exploit_id: str,
    orchestrator: PlaytestOrchestrator = Depends(get_orchestrator)
):
    """Reproduce specific exploit."""
    try:
        if not orchestrator.current_session:
            raise HTTPException(status_code=404, detail="No active session")
        
        exploit = None
        for e in orchestrator.current_session.exploits_found:
            if e.exploit_id == exploit_id:
                exploit = e
                break
        
        if not exploit:
            raise HTTPException(status_code=404, detail="Exploit not found")
        
        reproduction_data = orchestrator.reproduction_generator.generate_reproduction(exploit)
        
        return {
            "status": "success",
            "message": f"Exploit {exploit_id} reproduced successfully",
            "reproduction_data": {
                "video_path": reproduction_data.video_path,
                "screenshots": reproduction_data.screenshots,
                "test_case_path": f"exploit_{exploit_id}_test_case.py"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to reproduce exploit: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents")
async def get_available_agents():
    """Get list of available AI agents."""
    return {
        "agents": [
            {
                "type": "novelty_search",
                "name": "Novelty Search Agent",
                "description": "Explores game mechanics to discover novel behaviors"
            },
            {
                "type": "evolutionary",
                "name": "Evolutionary Agent",
                "description": "Uses genetic algorithms to evolve exploit strategies"
            },
            {
                "type": "reinforcement",
                "name": "Reinforcement Learning Agent",
                "description": "Learns optimal actions through trial and error"
            }
        ]
    }


@router.get("/exploit-types")
async def get_exploit_types():
    """Get list of detectable exploit types."""
    return {
        "exploit_types": [
            {
                "type": "out_of_bounds",
                "name": "Out of Bounds",
                "description": "Player moves outside intended game boundaries"
            },
            {
                "type": "infinite_resources",
                "name": "Infinite Resources",
                "description": "Player gains unlimited resources or items"
            },
            {
                "type": "stuck_state",
                "name": "Stuck State",
                "description": "Player becomes unresponsive or stuck"
            },
            {
                "type": "infinite_loop",
                "name": "Infinite Loop",
                "description": "Game enters an endless loop state"
            },
            {
                "type": "clipping",
                "name": "Clipping",
                "description": "Player passes through solid objects"
            },
            {
                "type": "sequence_break",
                "name": "Sequence Break",
                "description": "Game sequence is broken or skipped"
            }
        ]
    }
