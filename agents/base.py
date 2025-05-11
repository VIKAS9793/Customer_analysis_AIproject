"""
Base Agent - Base class for all agents in the FinConnectAI framework.

This module defines the base agent class that all specific agent implementations
should inherit from.
"""

import logging
from typing import Any, Dict, Optional

from core.agent_manager import Agent

logger = logging.getLogger(__name__)


class BaseAgent(Agent):
    """
    Base class for all agents in the FinConnectAI framework.

    This class extends the Agent class from core.agent_manager and provides
    additional functionality common to all agents.
    """

    def __init__(self, name: str, description: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize a base agent.

        Args:
            name: The name of the agent
            description: A description of the agent's role
            config: Optional configuration for the agent
        """
        super().__init__(name, description)
        self.config = config or {}
        logger.info(f"Initialized agent: {name}")

    def can_handle_task(self, task: Dict[str, Any]) -> bool:
        """
        Determine if this agent can handle the given task.

        Args:
            task: The task to check

        Returns:
            True if the agent can handle the task, False otherwise
        """
        # Default implementation always returns False
        # Subclasses should override this method
        return False

    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the given task.

        Args:
            task: The task to execute

        Returns:
            The result of the task execution
        """
        # Default implementation raises NotImplementedError
        # Subclasses should override this method
        raise NotImplementedError("Subclasses must implement this method")

    def _validate_task(self, task: Dict[str, Any]) -> bool:
        """
        Validate that a task has the required fields.

        Args:
            task: The task to validate

        Returns:
            True if the task is valid, False otherwise
        """
        required_fields = ["type"]

        for field in required_fields:
            if field not in task:
                logger.warning(f"Task missing required field: {field}")
                return False

        return True

    def _get_model_provider(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get the model provider configuration for a task.

        Args:
            task: The task to get the model provider for

        Returns:
            The model provider configuration
        """
        # Get the provider from the task or use the default
        provider_name = task.get("provider", self.config.get("default_provider", "openai"))

        # Get the provider configuration
        providers = self.config.get("model_providers", {})
        provider = providers.get(provider_name, {})

        if not provider:
            logger.warning(f"Unknown provider: {provider_name}, using default")
            provider = providers.get(providers.get("default", "openai"), {})

        return provider

    def _log_task_execution(self, task: Dict[str, Any], result: Dict[str, Any]) -> None:
        """
        Log task execution details.

        Args:
            task: The executed task
            result: The result of the task execution
        """
        task_type = task.get("type", "unknown")
        status = result.get("status", "unknown")

        logger.info(f"Task execution: type={task_type}, status={status}")

        # Log detailed information at debug level
        logger.debug(f"Task details: {task}")
        logger.debug(f"Result details: {result}")

    def _create_error_response(self, task: Dict[str, Any], error_message: str) -> Dict[str, Any]:
        """
        Create an error response for a task.

        Args:
            task: The task that failed
            error_message: The error message

        Returns:
            An error response
        """
        return {"status": "error", "message": error_message, "original_task": task}
