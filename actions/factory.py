"""
Action Factory - Factory for creating action executor implementations.

This module provides a factory function for creating action executor implementations
based on configuration.
"""

import logging
from typing import Any, Dict

from actions.base import ActionExecutor, MockActionExecutor
from actions.email import EmailActionExecutor
from actions.webhook import WebhookActionExecutor
from actions.zendesk import ZendeskActionExecutor

logger = logging.getLogger(__name__)


def create_action_executor(config: Dict[str, Any]) -> ActionExecutor:
    """
    Create an action executor implementation based on configuration.

    Args:
        config: Configuration for the action executor

    Returns:
        An ActionExecutor implementation
    """
    action_mode = config.get("mode", "mock")

    logger.info(f"Creating action executor implementation: {action_mode}")

    if action_mode == "live":
        # Create a composite executor with all available executors
        executors = []

        # Add Zendesk executor if configured
        if "zendesk" in config.get("plugins", {}):
            logger.info("Adding Zendesk action executor")
            zendesk_config = config.get("plugins", {}).get("zendesk", {})
            executors.append(ZendeskActionExecutor(zendesk_config))

        # Add Email executor if configured
        if "email" in config.get("plugins", {}):
            logger.info("Adding Email action executor")
            email_config = config.get("plugins", {}).get("email", {})
            executors.append(EmailActionExecutor(email_config))

        # Add Webhook executor if configured
        if "webhook" in config.get("plugins", {}):
            logger.info("Adding Webhook action executor")
            webhook_config = config.get("plugins", {}).get("webhook", {})
            executors.append(WebhookActionExecutor(webhook_config))

        # If no executors were added, use mock
        if not executors:
            logger.warning("No action executors configured, using mock")
            return MockActionExecutor()

        # Create composite executor
        return CompositeActionExecutor(executors)
    elif action_mode == "mock":
        return MockActionExecutor()
    else:
        logger.warning(f"Unknown action mode: {action_mode}, using mock")
        return MockActionExecutor()


class CompositeActionExecutor(ActionExecutor):
    """
    Composite action executor that delegates to multiple executors.

    This class implements the ActionExecutor interface by delegating to
    multiple executors based on the action type.
    """

    def __init__(self, executors: list[ActionExecutor]):
        """
        Initialize a composite action executor.

        Args:
            executors: List of executors to delegate to
        """
        self.executors = executors
        self._action_map = {}

        # Build action map
        for executor in executors:
            actions = executor.list_available_actions()
            for action in actions:
                action_type = action.get("type")
                if action_type:
                    self._action_map[action_type] = executor

        logger.info(f"Initialized composite action executor with {len(executors)} executors")
        logger.info(f"Available actions: {list(self._action_map.keys())}")

    def execute_action(self, action_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an action.

        Args:
            action_type: The type of action to execute
            params: Parameters for the action

        Returns:
            The result of the action execution
        """
        # Find executor for action type
        executor = self._action_map.get(action_type)

        if executor:
            logger.info(f"Delegating action {action_type} to {executor.__class__.__name__}")
            return executor.execute_action(action_type, params)
        else:
            logger.warning(f"No executor found for action type: {action_type}")
            return {
                "status": "error",
                "message": f"No executor found for action type: {action_type}",
            }

    def list_available_actions(self) -> list[Dict[str, Any]]:
        """
        List available actions.

        Returns:
            List of available actions
        """
        # Collect actions from all executors
        all_actions = []
        for executor in self.executors:
            all_actions.extend(executor.list_available_actions())

        return all_actions

    def get_action_details(self, action_type: str) -> Dict[str, Any]:
        """
        Get details for an action.

        Args:
            action_type: The type of action to get details for

        Returns:
            Details for the action
        """
        # Find executor for action type
        executor = self._action_map.get(action_type)

        if executor:
            return executor.get_action_details(action_type)
        else:
            logger.warning(f"No executor found for action type: {action_type}")
            return {}
