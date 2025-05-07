"""
AntiHallucinationGuard - Applies strict prompt filters, source validation, and fallback responses.

This module implements safety measures to prevent hallucinations and ensure
that all responses are grounded in verifiable data.
"""

import logging
from typing import Any, Dict, List, Optional

from knowledge.base import KnowledgeBase

logger = logging.getLogger(__name__)


class AntiHallucinationGuard:
    """
    Applies strict prompt filters, source validation, and fallback responses.

    This class implements various safety measures to prevent hallucinations
    and ensure that all responses are properly sourced and verified.
    """

    def __init__(self, knowledge_base: Optional[KnowledgeBase] = None):
        """
        Initialize the anti-hallucination guard.

        Args:
            knowledge_base: Optional knowledge base for source verification
        """
        self.knowledge_base = knowledge_base
        self.fallback_message = "I do not have enough data to answer accurately."

    def apply_prompt_filters(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply prompt filters to prevent hallucinations.

        Args:
            task: The task to filter

        Returns:
            The filtered task
        """
        logger.info("Applying prompt filters")

        # Add anti-hallucination instructions to the prompt
        if "prompt" in task:
            task["prompt"] = self._add_anti_hallucination_instructions(task["prompt"])

        # Add source verification requirements
        task["require_sources"] = True

        # Add confidence threshold
        task["confidence_threshold"] = 0.85

        return task

    def _add_anti_hallucination_instructions(self, prompt: str) -> str:
        """
        Add anti-hallucination instructions to a prompt.

        Args:
            prompt: The original prompt

        Returns:
            The prompt with anti-hallucination instructions
        """
        anti_hallucination_prefix = (
            "Respond only with verifiable data. Do not assume or speculate. "
            "If you are uncertain, acknowledge the limitations of your knowledge. "
            "Always cite your sources when providing information. "
        )

        return f"{anti_hallucination_prefix}\n\n{prompt}"

    def verify_response_with_sources(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify that a response includes proper sources.

        Args:
            response: The response to verify

        Returns:
            The verified response, or a fallback response if verification fails
        """
        logger.info("Verifying response with sources")

        # Check if the response has sources
        sources = response.get("sources", [])
        content = response.get("content", "")

        # If no sources and not a fallback response already
        if not sources and not self._is_fallback_response(content):
            confidence = response.get("confidence", 0.0)

            # If confidence is too low or no sources provided
            if confidence < 0.85:
                logger.warning("Response failed verification: low confidence or missing sources")
                return self._create_fallback_response(response)

            # If knowledge base is available, try to find sources
            if self.knowledge_base:
                verified_sources = self._find_sources_for_response(content)

                if verified_sources:
                    response["sources"] = verified_sources
                    response["source_verified"] = True
                    return response
                else:
                    logger.warning(
                        "Response failed verification: no sources found in knowledge base"
                    )
                    return self._create_fallback_response(response)

        # Response has sources or is already a fallback
        return response

    def _is_fallback_response(self, content: str) -> bool:
        """
        Check if a response is already a fallback response.

        Args:
            content: The response content

        Returns:
            True if the response is a fallback, False otherwise
        """
        return self.fallback_message in content

    def _create_fallback_response(self, original_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a fallback response.

        Args:
            original_response: The original response

        Returns:
            A fallback response
        """
        return {
            "status": "fallback",
            "content": self.fallback_message,
            "confidence": 1.0,
            "sources": [],
            "original_query": original_response.get("original_query", ""),
            "fallback_triggered": True,
        }

    def _find_sources_for_response(self, content: str) -> List[Dict[str, Any]]:
        """
        Find sources for a response in the knowledge base.

        Args:
            content: The response content

        Returns:
            A list of sources
        """
        if not self.knowledge_base:
            return []

        # Query the knowledge base for relevant sources
        sources = self.knowledge_base.search(content, limit=3)

        # Format the sources
        formatted_sources = []
        for source in sources:
            formatted_sources.append(
                {
                    "id": source.get("id", ""),
                    "title": source.get("title", ""),
                    "url": source.get("url", ""),
                    "content_snippet": source.get("content_snippet", ""),
                    "relevance_score": source.get("relevance_score", 0.0),
                }
            )

        return formatted_sources
