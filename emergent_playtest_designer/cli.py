"""Command-line interface for the Emergent Playtest Designer."""

import asyncio
import typer
from typing import Optional
from loguru import logger
from .core.config import Config
from .core.orchestrator import PlaytestOrchestrator, TestingConfig


app = typer.Typer(help="Emergent Playtest Designer CLI")


@app.command()
def run(
    game_path: str = typer.Argument(..., help="Path to Unity game executable"),
    max_duration: int = typer.Option(3600, help="Maximum testing duration in seconds"),
    max_episodes: int = typer.Option(1000, help="Maximum number of episodes"),
    agent_type: str = typer.Option("novelty_search", help="AI agent type"),
    config_file: Optional[str] = typer.Option(None, help="Configuration file path"),
    verbose: bool = typer.Option(False, help="Enable verbose logging")
):
    """Run automated playtesting session."""
    
    if verbose:
        logger.add("logs/cli.log", level="DEBUG")
    
    logger.info(f"Starting playtesting session for {game_path}")
    
    try:
        config = Config.from_env(config_file)
        config.validate()
        
        orchestrator = PlaytestOrchestrator(config)
        
        testing_config = TestingConfig(
            game_path=game_path,
            max_duration=max_duration,
            max_episodes=max_episodes,
            agent_type=agent_type
        )
        
        async def run_session():
            session_id = await orchestrator.start_testing_session(testing_config)
            logger.info(f"Session {session_id} completed")
        
        asyncio.run(run_session())
        
    except Exception as e:
        logger.error(f"Playtesting failed: {e}")
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def server(
    host: str = typer.Option("0.0.0.0", help="Host to bind to"),
    port: int = typer.Option(8000, help="Port to bind to"),
    workers: int = typer.Option(4, help="Number of worker processes"),
    config_file: Optional[str] = typer.Option(None, help="Configuration file path")
):
    """Start the API server."""
    
    logger.info(f"Starting API server on {host}:{port}")
    
    try:
        import uvicorn
        from .api.main import app
        
        uvicorn.run(
            app,
            host=host,
            port=port,
            workers=workers,
            log_level="info"
        )
        
    except Exception as e:
        logger.error(f"Server startup failed: {e}")
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def validate_config(
    config_file: Optional[str] = typer.Option(None, help="Configuration file path")
):
    """Validate configuration file."""
    
    try:
        config = Config.from_env(config_file)
        config.validate()
        
        typer.echo("Configuration is valid!")
        
        typer.echo("\nConfiguration summary:")
        config_dict = config.to_dict()
        for section, values in config_dict.items():
            typer.echo(f"\n{section.upper()}:")
            for key, value in values.items():
                typer.echo(f"  {key}: {value}")
        
    except Exception as e:
        typer.echo(f"Configuration validation failed: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def test_connection(
    config_file: Optional[str] = typer.Option(None, help="Configuration file path")
):
    """Test connections to external services."""
    
    try:
        config = Config.from_env(config_file)
        
        typer.echo("Testing connections...")
        
        # Test Unity connection
        typer.echo("Testing Unity connection...")
        from .unity_integration import UnityController
        controller = UnityController(config.unity)
        typer.echo(f"Unity executable: {config.unity.executable_path}")
        typer.echo(f"Unity project: {config.unity.project_path}")
        
        # Test LLM connection
        typer.echo("Testing LLM connection...")
        from .explanation import LLMClient
        llm_client = LLMClient(config.llm)
        typer.echo(f"LLM provider: {config.llm.provider}")
        typer.echo(f"LLM model: {config.llm.model}")
        
        typer.echo("All connections configured successfully!")
        
    except Exception as e:
        typer.echo(f"Connection test failed: {e}", err=True)
        raise typer.Exit(1)


def main():
    """Main CLI entry point."""
    app()


if __name__ == "__main__":
    main()
