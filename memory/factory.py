"""
Memory Factory - Factory for creating memory implementations.

This module provides a factory function for creating memory implementations
based on configuration.
"""

import logging
from typing import Any, Dict, Optional

from core.model_provider import ModelProvider
from memory.base import MemoryInterface, ShortTermMemory
from memory.long_term import LongTermMemory

logger = logging.getLogger(__name__)


def create_memory(
    config: Dict[str, Any], model_provider: Optional[ModelProvider] = None
) -> MemoryInterface:
    """
    Create a memory implementation based on configuration.

    Args:
        config: Configuration for the memory
        model_provider: Optional model provider for generating embeddings

    Returns:
        A MemoryInterface implementation
    """
    memory_type = config.get("type", "mock")

    logger.info(f"Creating memory implementation: {memory_type}")

    if memory_type == "short_term":
        return ShortTermMemory(config)
    elif memory_type == "long_term":
        return LongTermMemory(config, model_provider)
    elif memory_type == "mock":
        return ShortTermMemory(config)  # Use ShortTermMemory as mock
    else:
        logger.warning(f"Unknown memory type: {memory_type}, using mock")
        return ShortTermMemory(config)  # Use ShortTermMemory as mock
