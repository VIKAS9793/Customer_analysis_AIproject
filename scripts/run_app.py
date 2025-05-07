"""
Run App - Script to run the CustomerAI application in different modes.

This script provides a command-line interface for running the CustomerAI
application in different modes (API or UI).
"""

import argparse
import logging
import os
import sys
from typing import Any, Dict

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.action_agent import ActionAgent
from agents.chat_agent import ChatAgent
from agents.insight_agent import InsightAgent
from core.agent_manager import AgentManager
from core.config_manager import ConfigManager
from core.logging import setup_logging
from core.model_provider import create_model_provider
from interfaces.api import run_api
from interfaces.streamlit_ui import run_streamlit
from knowledge.factory import create_knowledge_base
from memory.factory import create_memory

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def setup_agent_manager(config: Dict[str, Any]) -> AgentManager:
    """
    Set up the agent manager with all required agents.

    Args:
        config: Application configuration

    Returns:
        Configured agent manager
    """
    logger.info("Setting up agent manager")

    # Create model provider
    model_provider = create_model_provider(config.get("model_providers", {}))

    # Create knowledge base
    knowledge_base = create_knowledge_base(config.get("knowledge", {}), model_provider)

    # Create memory store
    create_memory(config.get("memory", {}), model_provider)

    # Create agent manager
    agent_manager = AgentManager()

    # Create and register agents
    chat_agent = ChatAgent(config, knowledge_base)
    insight_agent = InsightAgent(config, knowledge_base)
    action_agent = ActionAgent(config)

    agent_manager.register_agent(chat_agent)
    agent_manager.register_agent(insight_agent)
    agent_manager.register_agent(action_agent)

    logger.info("Agent manager setup complete")

    return agent_manager


def main():
    """Main function to run the application."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Run CustomerAI application")
    parser.add_argument(
        "--mode",
        choices=["api", "ui"],
        default="api",
        help="Application mode: 'api' for FastAPI server, 'ui' for Streamlit UI",
    )
    parser.add_argument("--host", default=None, help="Host to run the server on (overrides config)")
    parser.add_argument(
        "--port", type=int, default=None, help="Port to run the server on (overrides config)"
    )
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")

    args = parser.parse_args()

    # Load configuration
    config_manager = ConfigManager()
    config = config_manager.load_config()

    # Override config with command-line arguments
    if args.host:
        config["api"]["host"] = args.host
    if args.port:
        config["api"]["port"] = args.port
    if args.debug:
        config["api"]["debug"] = True
        config["logging"]["level"] = "DEBUG"

    # Set up logging
    setup_logging(config)

    # Set up agent manager
    agent_manager = setup_agent_manager(config)

    # Run in specified mode
    if args.mode == "api":
        logger.info("Running in API mode")
        api_config = config.get("api", {})
        run_api(
            agent_manager=agent_manager,
            host=api_config.get("host", "0.0.0.0"),
            port=api_config.get("port", 8000),
            debug=api_config.get("debug", False),
        )
    elif args.mode == "ui":
        logger.info("Running in UI mode")
        run_streamlit(agent_manager=agent_manager)
    else:
        logger.error(f"Unknown mode: {args.mode}")
        sys.exit(1)


if __name__ == "__main__":
    main()
