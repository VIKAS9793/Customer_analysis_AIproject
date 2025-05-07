"""
ActionAgent - Agent for executing actions.

This module implements an agent that executes actions based on user requests.
"""

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from actions.base import create_action_executor
from agents.base import BaseAgent

logger = logging.getLogger(__name__)


class ActionAgent(BaseAgent):
    """
    Agent for executing actions.

    This agent is responsible for executing actions based on user requests,
    such as sending emails, creating tickets, or updating customer information.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize an action agent.

        Args:
            config: Optional configuration for the agent
        """
        super().__init__(
            name="ActionAgent", description="Executes actions based on user requests", config=config
        )

        # Create action executor
        action_config = config.get("actions", {}) if config else {}
        self.action_executor = create_action_executor(action_config)

    def can_handle_task(self, task: Dict[str, Any]) -> bool:
        """
        Determine if this agent can handle the given task.

        Args:
            task: The task to check

        Returns:
            True if the agent can handle the task, False otherwise
        """
        # Check if the task is valid
        if not self._validate_task(task):
            return False

        # Check if the task type is "action" or "list_actions"
        return task.get("type") in ["action", "list_actions"]

    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the given task.

        Args:
            task: The task to execute

        Returns:
            The result of the task execution
        """
        logger.info(f"ActionAgent executing task: {task.get('type')}")

        try:
            # Handle different task types
            task_type = task.get("type")

            if task_type == "list_actions":
                return self._list_actions()
            elif task_type == "action":
                return self._execute_action(task)
            else:
                return self._create_error_response(task, f"Unknown task type: {task_type}")
        except Exception as e:
            logger.error(f"Error executing action task: {e}")
            return self._create_error_response(task, f"Error executing action task: {str(e)}")

    def _list_actions(self) -> Dict[str, Any]:
        """
        List available actions.

        Returns:
            A list of available actions
        """
        # Get available actions from the executor
        available_actions = self.action_executor.list_available_actions()

        # Create result
        result = {
            "status": "success",
            "actions": available_actions,
            "timestamp": datetime.now().isoformat(),
        }

        return result

    def _execute_action(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an action.

        Args:
            task: The task containing action details

        Returns:
            The result of the action execution
        """
        # Extract task fields
        action_type = task.get("action_type")
        params = task.get("params", {})
        context_id = task.get("context_id")

        if not action_type:
            return self._create_error_response(task, "Missing action_type")

        # Validate action type
        action_details = self.action_executor.get_action_details(action_type)
        if not action_details:
            return self._create_error_response(task, f"Unknown action type: {action_type}")

        # Execute the action
        action_result = self.action_executor.execute_action(action_type, params)

        # Create result
        result = {
            "status": action_result.get("status", "error"),
            "message": action_result.get("message", "Action execution failed"),
            "details": action_result.get("details", {}),
            "action_id": f"action-{uuid.uuid4()}",
            "timestamp": datetime.now().isoformat(),
            "action_type": action_type,
            "context_id": context_id,
        }

        # Log task execution
        self._log_task_execution(task, result)

        return result
