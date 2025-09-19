"""
Simplified CLI for the Emergent Playtest Designer that works with mock implementations.
This allows shipping a working product without heavy dependencies.
"""

import asyncio
import typer
import json
import time
from typing import Optional
from pathlib import Path
from loguru import logger

# Import mock implementations
from emergent_playtest_designer.mocks import MockUnityController, MockLLMClient, MockDatabase
from examples.demo_game import DemoGame

app = typer.Typer(help="Emergent Playtest Designer - Simple CLI")

@app.command()
def demo(
    duration: int = typer.Option(60, help="Demo duration in seconds"),
    verbose: bool = typer.Option(False, help="Enable verbose logging")
):
    """Run a demo of the playtest designer with simulated game."""
    
    if verbose:
        logger.add("demo.log", level="DEBUG")
    
    logger.info("Starting Emergent Playtest Designer Demo")
    
    async def run_demo():
        # Initialize components
        game = DemoGame()
        llm_client = MockLLMClient()
        database = MockDatabase()
        
        # Start game
        await game.start_game()
        session_id = f"demo_session_{int(time.time())}"
        
        logger.info(f"Demo session started: {session_id}")
        
        # Save session to database
        database.save_session(session_id, "demo_game", {
            "duration": duration,
            "agent_type": "demo",
            "timestamp": time.time()
        })
        
        # Simulate gameplay with random actions
        actions = [
            ("move_right", 1.0),
            ("move_left", 1.0),
            ("jump", 1.0),
            ("attack", 1.0),
        ]
        
        start_time = time.time()
        frame_count = 0
        
        while time.time() - start_time < duration:
            # Random action every few frames
            if frame_count % 10 == 0:
                import random
                action, value = random.choice(actions)
                await game.process_input(action, value)
            
            # Update game
            state = await game.update()
            frame_count += 1
            
            # Check for exploits
            exploits = game.get_exploits()
            if exploits:
                latest_exploit = exploits[-1]
                if len(exploits) == 1 or exploits[-1]["id"] != exploits[-2]["id"]:
                    logger.info(f"EXPLOIT DETECTED: {latest_exploit['type']}")
                    
                    # Generate explanation using LLM
                    explanation = await llm_client.generate_explanation(latest_exploit)
                    
                    # Save exploit to database
                    database.save_exploit(
                        latest_exploit["id"],
                        session_id,
                        {
                            "type": latest_exploit["type"],
                            "severity": latest_exploit["severity"],
                            "description": latest_exploit["description"],
                            "explanation": explanation,
                            "frame": latest_exploit["frame"]
                        }
                    )
                    
                    typer.echo(f"🚨 EXPLOIT FOUND: {latest_exploit['type']}")
                    typer.echo(f"   Description: {latest_exploit['description']}")
                    typer.echo(f"   Explanation: {explanation}")
                    typer.echo()
            
            # Print status every 5 seconds
            if frame_count % 300 == 0:  # ~5 seconds at 60fps
                typer.echo(f"Frame {frame_count}: Player at ({state['player']['x']:.1f}, {state['player']['y']:.1f}), "
                          f"Health: {state['player']['health']}, Score: {state['player']['score']}")
            
            await asyncio.sleep(0.016)  # ~60 FPS
        
        # Stop game
        await game.stop_game()
        
        # Final results
        final_exploits = game.get_exploits()
        typer.echo(f"\n🎮 Demo completed!")
        typer.echo(f"   Duration: {duration} seconds")
        typer.echo(f"   Frames processed: {frame_count}")
        typer.echo(f"   Final score: {state['player']['score']}")
        typer.echo(f"   Exploits found: {len(final_exploits)}")
        
        if final_exploits:
            typer.echo(f"\n📊 Exploit Summary:")
            for i, exploit in enumerate(final_exploits, 1):
                typer.echo(f"   {i}. {exploit['type']} ({exploit['severity']}) - Frame {exploit['frame']}")
        
        logger.info(f"Demo completed with {len(final_exploits)} exploits found")
    
    asyncio.run(run_demo())

@app.command()
def test_game(
    game_path: str = typer.Argument(..., help="Path to game (will use mock implementation)"),
    max_duration: int = typer.Option(3600, help="Maximum testing duration in seconds"),
    agent_type: str = typer.Option("novelty_search", help="AI agent type"),
    verbose: bool = typer.Option(False, help="Enable verbose logging")
):
    """Test a game using mock implementations."""
    
    if verbose:
        logger.add("test.log", level="DEBUG")
    
    logger.info(f"Starting playtesting session for {game_path}")
    
    async def run_test():
        # Initialize mock components
        unity_controller = MockUnityController(game_path)
        llm_client = MockLLMClient()
        database = MockDatabase()
        
        # Start Unity game (mock)
        await unity_controller.start_game()
        session_id = f"test_session_{int(time.time())}"
        
        logger.info(f"Testing session started: {session_id}")
        
        # Save session
        database.save_session(session_id, game_path, {
            "max_duration": max_duration,
            "agent_type": agent_type,
            "timestamp": time.time()
        })
        
        start_time = time.time()
        frame_count = 0
        exploits_found = []
        
        # Simulate testing with random inputs
        actions = ["move_right", "move_left", "jump", "attack"]
        
        while time.time() - start_time < max_duration:
            # Random action
            import random
            action = random.choice(actions)
            await unity_controller.inject_input(action, random.uniform(0.5, 1.0))
            
            # Get game state
            state = await unity_controller.get_game_state()
            frame_count += 1
            
            # Simulate exploit detection (random chance)
            if random.random() < 0.001:  # 0.1% chance per frame
                exploit_types = ["out_of_bounds", "infinite_resources", "stuck_state", "infinite_loop"]
                exploit_type = random.choice(exploit_types)
                
                exploit_data = {
                    "type": exploit_type,
                    "severity": random.choice(["low", "medium", "high", "critical"]),
                    "description": f"Mock {exploit_type} exploit detected",
                    "frame": frame_count,
                    "state": state
                }
                
                # Generate explanation
                explanation = await llm_client.generate_explanation(exploit_data)
                
                # Save exploit
                exploit_id = f"exploit_{len(exploits_found)}_{frame_count}"
                database.save_exploit(exploit_id, session_id, exploit_data)
                exploits_found.append(exploit_data)
                
                typer.echo(f"🚨 EXPLOIT FOUND: {exploit_type}")
                typer.echo(f"   Severity: {exploit_data['severity']}")
                typer.echo(f"   Frame: {frame_count}")
                typer.echo(f"   Explanation: {explanation}")
                typer.echo()
            
            # Status update every 30 seconds
            if frame_count % 1800 == 0:  # ~30 seconds at 60fps
                typer.echo(f"Testing progress: {frame_count} frames, {len(exploits_found)} exploits found")
            
            await asyncio.sleep(0.016)  # ~60 FPS
        
        # Stop game
        await unity_controller.stop_game()
        
        # Final results
        typer.echo(f"\n🎮 Testing completed!")
        typer.echo(f"   Game: {game_path}")
        typer.echo(f"   Duration: {max_duration} seconds")
        typer.echo(f"   Frames processed: {frame_count}")
        typer.echo(f"   Exploits found: {len(exploits_found)}")
        
        if exploits_found:
            typer.echo(f"\n📊 Exploit Summary:")
            for i, exploit in enumerate(exploits_found, 1):
                typer.echo(f"   {i}. {exploit['type']} ({exploit['severity']}) - Frame {exploit['frame']}")
        
        logger.info(f"Testing completed with {len(exploits_found)} exploits found")
    
    asyncio.run(run_test())

@app.command()
def server(
    host: str = typer.Option("0.0.0.0", help="Host to bind to"),
    port: int = typer.Option(8000, help="Port to bind to"),
    verbose: bool = typer.Option(False, help="Enable verbose logging")
):
    """Start a simple API server with mock implementations."""
    
    if verbose:
        logger.add("server.log", level="DEBUG")
    
    logger.info(f"Starting simple API server on {host}:{port}")
    
    try:
        import uvicorn
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware
        
        # Create FastAPI app
        app_fastapi = FastAPI(title="Emergent Playtest Designer API", version="1.0.0")
        
        # Add CORS middleware
        app_fastapi.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Initialize mock database
        db = MockDatabase()
        
        @app_fastapi.get("/")
        async def root():
            return {"message": "Emergent Playtest Designer API", "status": "running"}
        
        @app_fastapi.get("/api/v1/status")
        async def get_status():
            return {"status": "running", "version": "1.0.0", "mode": "mock"}
        
        @app_fastapi.post("/api/v1/testing/start")
        async def start_testing(request: dict):
            session_id = f"api_session_{int(time.time())}"
            game_path = request.get("game_path", "mock_game")
            max_duration = request.get("max_duration", 3600)
            agent_type = request.get("agent_type", "novelty_search")
            
            db.save_session(session_id, game_path, {
                "max_duration": max_duration,
                "agent_type": agent_type,
                "timestamp": time.time()
            })
            
            return {"session_id": session_id, "status": "started"}
        
        @app_fastapi.get("/api/v1/testing/status")
        async def get_testing_status():
            return {"status": "running", "active_sessions": 1}
        
        @app_fastapi.get("/api/v1/exploits")
        async def get_exploits():
            exploits = db.get_exploits()
            return {"exploits": exploits, "count": len(exploits)}
        
        @app_fastapi.get("/api/v1/exploits/{session_id}")
        async def get_exploits_by_session(session_id: str):
            exploits = db.get_exploits(session_id)
            return {"exploits": exploits, "count": len(exploits), "session_id": session_id}
        
        typer.echo(f"🚀 Starting API server on http://{host}:{port}")
        typer.echo(f"📖 API documentation available at http://{host}:{port}/docs")
        
        uvicorn.run(app_fastapi, host=host, port=port, log_level="info")
        
    except Exception as e:
        logger.error(f"Server startup failed: {e}")
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)

@app.command()
def validate():
    """Validate the installation and mock implementations."""
    
    typer.echo("🔍 Validating Emergent Playtest Designer installation...")
    
    try:
        # Test mock imports
        from emergent_playtest_designer.mocks import MockUnityController, MockLLMClient, MockDatabase
        typer.echo("✅ Mock implementations imported successfully")
        
        # Test demo game
        from examples.demo_game import DemoGame
        typer.echo("✅ Demo game imported successfully")
        
        # Test basic functionality
        async def test_basic():
            game = DemoGame()
            await game.start_game()
            await game.process_input("move_right", 1.0)
            state = await game.update()
            await game.stop_game()
            return True
        
        asyncio.run(test_basic())
        typer.echo("✅ Basic functionality test passed")
        
        # Test database
        db = MockDatabase()
        db.save_session("test", "test_game", {"test": True})
        exploits = db.get_exploits()
        typer.echo("✅ Database functionality test passed")
        
        typer.echo("\n🎉 All validation tests passed!")
        typer.echo("   The Emergent Playtest Designer is ready to use.")
        typer.echo("\n📋 Available commands:")
        typer.echo("   python cli_simple.py demo --help")
        typer.echo("   python cli_simple.py test-game --help")
        typer.echo("   python cli_simple.py server --help")
        
    except Exception as e:
        typer.echo(f"❌ Validation failed: {e}", err=True)
        raise typer.Exit(1)

def main():
    """Main CLI entry point."""
    app()

if __name__ == "__main__":
    main()
