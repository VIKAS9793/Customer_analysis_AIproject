"""
ActionExecutor - Unified interface for executing external or internal actions.

This module defines the abstract interface for action executors in the FinConnectAI framework,
with implementations for different types of actions.
"""

import logging
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional

from scripts.secure_subprocess import SecureSubprocess

logger = logging.getLogger(__name__)


class ActionExecutor(ABC):
    """
    Abstract base class for action executors.

    This class defines the interface that all action executors must follow.
    """

    @abstractmethod
    def execute_action(self, action_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an action.

        Args:
            action_type: Type of action to execute
            params: Parameters for the action

        Returns:
            The result of the action
        """
        pass

    @abstractmethod
    def list_available_actions(self) -> List[Dict[str, Any]]:
        """
        List all available actions.

        Returns:
            A list of available actions with their descriptions
        """
        pass

    @abstractmethod
    def get_action_details(self, action_type: str) -> Optional[Dict[str, Any]]:
        """
        Get details about a specific action.

        Args:
            action_type: Type of action

        Returns:
            Details about the action, or None if not found
        """
        pass


class MockActionExecutor(ActionExecutor):
    """
    Mock implementation of an action executor for testing.

    This class provides a simple implementation of an action executor
    that returns mock responses for testing and development purposes.
    """

    def __init__(self):
        """Initialize the mock action executor."""
        self.available_actions = {
            "send_email": {
                "description": "Send an email to a recipient",
                "params": {
                    "to": "Email address of the recipient",
                    "subject": "Subject of the email",
                    "body": "Body of the email",
                },
                "mock_response": {
                    "status": "success",
                    "message": "Email sent successfully",
                    "details": {"email_id": "mock-email-123"},
                },
            },
            "create_ticket": {
                "description": "Create a support ticket",
                "params": {
                    "title": "Title of the ticket",
                    "description": "Description of the ticket",
                    "priority": "Priority of the ticket (low, medium, high)",
                },
                "mock_response": {
                    "status": "success",
                    "message": "Ticket created successfully",
                    "details": {"ticket_id": "mock-ticket-456"},
                },
            },
            "update_customer": {
                "description": "Update customer information",
                "params": {
                    "customer_id": "ID of the customer",
                    "fields": "Fields to update (JSON object)",
                },
                "mock_response": {
                    "status": "success",
                    "message": "Customer updated successfully",
                    "details": {"customer_id": "mock-customer-789"},
                },
            },
        }

    def execute_action(self, action_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an action.

        Args:
            action_type: Type of action to execute
            params: Parameters for the action

        Returns:
            The result of the action
        """
        logger.info(f"Executing mock action: {action_type}")

        if action_type not in self.available_actions:
            return {"status": "error", "message": f"Unknown action type: {action_type}"}

        # Validate required parameters
        action_details = self.available_actions[action_type]
        required_params = action_details["params"].keys()

        for param in required_params:
            if param not in params:
                return {"status": "error", "message": f"Missing required parameter: {param}"}

        # Return mock response
        mock_response = action_details["mock_response"]

        # Add input parameters to the response for reference
        mock_response["input_params"] = params

        return mock_response

    def list_available_actions(self) -> List[Dict[str, Any]]:
        """
        List all available actions.

        Returns:
            A list of available actions with their descriptions
        """
        actions = []

        for action_type, details in self.available_actions.items():
            actions.append(
                {
                    "type": action_type,
                    "description": details["description"],
                    "params": details["params"],
                }
            )

        return actions

    def get_action_details(self, action_type: str) -> Optional[Dict[str, Any]]:
        """
        Get details about a specific action.

        Args:
            action_type: Type of action

        Returns:
            Details about the action, or None if not found
        """
        if action_type not in self.available_actions:
            return None

        details = self.available_actions[action_type]

        return {
            "type": action_type,
            "description": details["description"],
            "params": details["params"],
        }


class LiveActionExecutor(ActionExecutor):
    """
    Live implementation of an action executor.

    This class provides a real implementation of an action executor
    that executes actions using external services and APIs.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the live action executor.

        Args:
            config: Configuration for the action executor
        """
        self.config = config
        self.project_root = Path(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
        self.secure_subprocess = SecureSubprocess(self.project_root)

        # Initialize plugins
        self.plugins = self._initialize_plugins()

        logger.info("Initialized live action executor")

    def _initialize_plugins(self) -> Dict[str, Any]:
        """
        Initialize action plugins.

        Returns:
            A dictionary of initialized plugins
        """
        plugins = {}

        # Get plugin configurations
        plugin_configs = self.config.get("plugins", {})

        for plugin_name, plugin_config in plugin_configs.items():
            try:
                if plugin_name == "zendesk":
                    from actions.plugins.zendesk import ZendeskPlugin

                    plugins[plugin_name] = ZendeskPlugin(plugin_config)
                elif plugin_name == "email":
                    from actions.plugins.email import EmailPlugin

                    plugins[plugin_name] = EmailPlugin(plugin_config)
                elif plugin_name == "webhook":
                    from actions.plugins.webhook import WebhookPlugin

                    plugins[plugin_name] = WebhookPlugin(plugin_config)
                else:
                    logger.warning(f"Unknown plugin: {plugin_name}")
            except ImportError as e:
                logger.error(f"Failed to import plugin {plugin_name}: {e}")
            except Exception as e:
                logger.error(f"Failed to initialize plugin {plugin_name}: {e}")

        return plugins

    def execute_action(self, action_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an action.

        Args:
            action_type: Type of action to execute
            params: Parameters for the action

        Returns:
            The result of the action
        """
        logger.info(f"Executing live action: {action_type}")

        # Parse action type to determine plugin and action
        parts = action_type.split(".")

        if len(parts) != 2:
            return {
                "status": "error",
                "message": f"Invalid action type format: {action_type}. Expected format: plugin.action",
            }

        plugin_name, action_name = parts

        # Check if plugin exists
        if plugin_name not in self.plugins:
            return {"status": "error", "message": f"Unknown plugin: {plugin_name}"}

        plugin = self.plugins[plugin_name]

        # Check if action exists
        if not hasattr(plugin, action_name) or not callable(getattr(plugin, action_name)):
            return {
                "status": "error",
                "message": f"Unknown action: {action_name} for plugin: {plugin_name}",
            }

        # Execute the action
        try:
            action_method = getattr(plugin, action_name)
            result = action_method(**params)

            return {
                "status": "success",
                "message": f"Action {action_type} executed successfully",
                "details": result,
            }
        except Exception as e:
            logger.error(f"Error executing action {action_type}: {e}")

            return {
                "status": "error",
                "message": f"Error executing action: {str(e)}",
                "details": {"action_type": action_type, "params": params},
            }

    def list_available_actions(self) -> List[Dict[str, Any]]:
        """
        List all available actions.

        Returns:
            A list of available actions with their descriptions
        """
        actions = []

        for plugin_name, plugin in self.plugins.items():
            plugin_actions = plugin.get_available_actions()

            for action in plugin_actions:
                actions.append(
                    {
                        "type": f"{plugin_name}.{action['name']}",
                        "description": action["description"],
                        "params": action["params"],
                    }
                )

        return actions

    def get_action_details(self, action_type: str) -> Optional[Dict[str, Any]]:
        """
        Get details about a specific action.

        Args:
            action_type: Type of action

        Returns:
            Details about the action, or None if not found
        """
        # Parse action type to determine plugin and action
        parts = action_type.split(".")

        if len(parts) != 2:
            return None

        plugin_name, action_name = parts

        # Check if plugin exists
        if plugin_name not in self.plugins:
            return None

        plugin = self.plugins[plugin_name]

        # Get action details
        action_details = plugin.get_action_details(action_name)

        if not action_details:
            return None

        return {
            "type": action_type,
            "description": action_details["description"],
            "params": action_details["params"],
        }


def create_action_executor(config: Dict[str, Any]) -> ActionExecutor:
    """
    Create an action executor based on configuration.

    Args:
        config: Configuration for the action executor

    Returns:
        An initialized action executor
    """
    mode = config.get("mode", "mock")

    if mode == "mock":
        logger.info("Creating mock action executor")
        return MockActionExecutor()
    elif mode == "live":
        logger.info("Creating live action executor")
        return LiveActionExecutor(config)
    else:
        logger.warning(f"Unknown mode: {mode}, falling back to mock")
        return MockActionExecutor()
