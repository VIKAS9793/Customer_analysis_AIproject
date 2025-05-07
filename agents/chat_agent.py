"""
ChatAgent - Agent for handling chat interactions.

This module implements an agent that handles chat interactions with users.
"""

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from agents.base import BaseAgent
from knowledge.base import KnowledgeBase

logger = logging.getLogger(__name__)


class ChatAgent(BaseAgent):
    """
    Agent for handling chat interactions.

    This agent is responsible for processing chat messages from users and
    generating appropriate responses.
    """

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        knowledge_base: Optional[KnowledgeBase] = None,
    ):
        """
        Initialize a chat agent.

        Args:
            config: Optional configuration for the agent
            knowledge_base: Optional knowledge base for retrieving information
        """
        super().__init__(
            name="ChatAgent", description="Handles chat interactions with users", config=config
        )
        self.knowledge_base = knowledge_base

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

        # Check if the task type is "chat"
        return task.get("type") == "chat"

    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the given task.

        Args:
            task: The task to execute

        Returns:
            The result of the task execution
        """
        logger.info("ChatAgent executing task")

        try:
            # Extract task fields
            content = task.get("content", "")
            conversation_id = task.get("conversation_id")
            metadata = task.get("metadata", {})

            if not content:
                return self._create_error_response(task, "Empty message content")

            # Generate a new conversation ID if not provided
            if not conversation_id:
                conversation_id = f"conv-{uuid.uuid4()}"

            # Retrieve relevant information from knowledge base
            sources = []
            if self.knowledge_base:
                search_results = self.knowledge_base.search(content, limit=3)
                sources = search_results

            # Generate response
            response = self._generate_response(content, sources, metadata)

            # Create result
            result = {
                "status": "success",
                "content": response,
                "conversation_id": conversation_id,
                "timestamp": datetime.now().isoformat(),
                "sources": sources,
                "confidence": 0.95,  # Mock confidence score
                "metadata": metadata,
            }

            # Log task execution
            self._log_task_execution(task, result)

            return result
        except Exception as e:
            logger.error(f"Error executing chat task: {e}")
            return self._create_error_response(task, f"Error executing chat task: {str(e)}")

    def _generate_response(
        self, message: str, sources: List[Dict[str, Any]], metadata: Dict[str, Any]
    ) -> str:
        """
        Generate a response to a user message.

        Args:
            message: The user message
            sources: Information sources
            metadata: Additional metadata

        Returns:
            The generated response
        """
        # In a real implementation, this would call a language model
        # For now, we'll use a mock implementation

        # Get model provider configuration
        provider = self._get_model_provider({"type": "chat", "provider": metadata.get("provider")})

        # Log provider information
        logger.debug(f"Using provider: {provider.get('name', 'unknown')}")

        # Generate mock response based on the message
        if "hello" in message.lower() or "hi" in message.lower():
            return "Hello! How can I assist you today?"
        elif "help" in message.lower():
            return "I'm here to help! You can ask me questions, and I'll do my best to provide accurate information."
        elif "thank" in message.lower():
            return "You're welcome! Is there anything else I can help you with?"
        elif any(keyword in message.lower() for keyword in ["bye", "goodbye", "see you"]):
            return "Goodbye! Feel free to come back if you have more questions."
        elif "?" in message:
            # If sources are available, use them in the response
            if sources:
                source_info = sources[0]
                return f"Based on my information, {source_info.get('content_snippet', '')} Would you like to know more about this topic?"
            else:
                return "That's an interesting question. Let me provide you with the information you're looking for..."
        else:
            return "I understand your message. Is there anything specific you'd like to know more about?"
