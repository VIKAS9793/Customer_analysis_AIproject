"""
AgentManager - Central controller that routes tasks to role-specific agents.

This module implements the central controller for the FinConnectAI framework,
responsible for managing and coordinating different agents.
"""

import logging
from typing import Any, Dict, List, Optional

from core.safety import AntiHallucinationGuard
from memory.base import MemoryInterface

logger = logging.getLogger(__name__)


class Agent:
    """Base class for all agents in the system."""

    def __init__(self, name: str, description: str):
        """Initialize an agent.

        Args:
            name: The name of the agent
            description: A description of the agent's role
        """
        self.name = name
        self.description = description

    def can_handle_task(self, task: Dict[str, Any]) -> bool:
        """Determine if this agent can handle the given task.

        Args:
            task: The task to check

        Returns:
            True if the agent can handle the task, False otherwise
        """
        raise NotImplementedError("Subclasses must implement this method")

    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the given task.

        Args:
            task: The task to execute

        Returns:
            The result of the task execution
        """
        raise NotImplementedError("Subclasses must implement this method")


class AgentManager:
    """Central controller that routes tasks to role-specific agents."""

    def __init__(self):
        """Initialize the agent manager."""
        self.agents: List[Agent] = []
        self.safety_guards: List[AntiHallucinationGuard] = []
        self.memory: Optional[MemoryInterface] = None

    def register_agent(self, agent: Agent) -> None:
        """Register an agent with the manager.

        Args:
            agent: The agent to register
        """
        logger.info(f"Registering agent: {agent.name}")
        self.agents.append(agent)

    def register_safety_guard(self, guard: AntiHallucinationGuard) -> None:
        """Register a safety guard with the manager.

        Args:
            guard: The safety guard to register
        """
        logger.info("Registering safety guard")
        self.safety_guards.append(guard)

    def set_memory(self, memory: MemoryInterface) -> None:
        """Set the memory interface for the agent manager.

        Args:
            memory: The memory interface to use
        """
        logger.info("Setting memory interface")
        self.memory = memory

    def run_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Run a task using the appropriate agent.

        Args:
            task: The task to run

        Returns:
            The result of the task execution
        """
        logger.info(f"Running task: {task.get('type', 'unknown')}")

        # Apply prompt filters from safety guards
        for guard in self.safety_guards:
            task = guard.apply_prompt_filters(task)

        # Find an agent that can handle the task
        for agent in self.agents:
            if agent.can_handle_task(task):
                logger.info(f"Agent {agent.name} will handle the task")

                # Execute the task
                result = agent.execute_task(task)

                # Verify the response with safety guards
                for guard in self.safety_guards:
                    result = guard.verify_response_with_sources(result)

                # Store the interaction in memory if available
                if self.memory:
                    self.memory.store_interaction(task, result)

                return result

        # No agent could handle the task
        logger.warning(f"No agent could handle task: {task.get('type', 'unknown')}")
        return {
            "status": "error",
            "message": "No agent available to handle this task",
            "task": task,
        }
