"""
Knowledge Factory - Factory for creating knowledge base implementations.

This module provides a factory function for creating knowledge base implementations
based on configuration.
"""

import logging
from typing import Any, Dict, Optional

from core.model_provider import ModelProvider
from knowledge.base import KnowledgeBase, MockKnowledgeBase
from knowledge.vector_store import VectorStoreKnowledge

logger = logging.getLogger(__name__)


def create_knowledge_base(
    config: Dict[str, Any], model_provider: Optional[ModelProvider] = None
) -> KnowledgeBase:
    """
    Create a knowledge base implementation based on configuration.

    Args:
        config: Configuration for the knowledge base
        model_provider: Optional model provider for generating embeddings

    Returns:
        A KnowledgeBase implementation
    """
    knowledge_type = config.get("type", "mock")

    logger.info(f"Creating knowledge base implementation: {knowledge_type}")

    if knowledge_type == "vector_store":
        return VectorStoreKnowledge(config, model_provider)
    elif knowledge_type == "graph":
        # Not implemented yet, use mock
        logger.warning("Graph knowledge base not implemented yet, using mock")
        return MockKnowledgeBase()
    elif knowledge_type == "mock":
        return MockKnowledgeBase()
    else:
        logger.warning(f"Unknown knowledge base type: {knowledge_type}, using mock")
        return MockKnowledgeBase()
