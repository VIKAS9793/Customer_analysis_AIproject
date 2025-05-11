"""
Long-Term Memory - Implementation of long-term memory for FinConnectAI.

This module implements a long-term memory store for the FinConnectAI framework
using vector embeddings for semantic search.
"""

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from core.model_provider import ModelProvider, create_model_provider
from memory.base import MemoryInterface

logger = logging.getLogger(__name__)


class LongTermMemory(MemoryInterface):
    """
    Long-term memory implementation.

    This class implements the MemoryInterface for long-term storage of
    interactions using vector embeddings for semantic search.
    """

    def __init__(self, config: Dict[str, Any], model_provider: Optional[ModelProvider] = None):
        """
        Initialize a long-term memory store.

        Args:
            config: Configuration for the memory store
            model_provider: Optional model provider for generating embeddings
        """
        super().__init__()
        self.config = config
        self.vector_db_type = config.get("vector_db", {}).get("type", "faiss")
        self.dimension = config.get("vector_db", {}).get("dimension", 1536)
        self.index_path = config.get("vector_db", {}).get("index_path", "data/vector_index")
        self.similarity_threshold = config.get("vector_db", {}).get("similarity_threshold", 0.7)

        # Create model provider if not provided
        if model_provider is None:
            model_provider_config = config.get("model_providers", {})
            self.model_provider = create_model_provider(model_provider_config)
        else:
            self.model_provider = model_provider

        # Initialize vector store
        self._initialize_vector_store()

        logger.info(f"Initialized long-term memory with vector store: {self.vector_db_type}")

    def _initialize_vector_store(self) -> None:
        """
        Initialize the vector store.

        In a real implementation, this would initialize the vector store
        (FAISS, Pinecone, etc.) and load existing indices.
        """
        # In a real implementation, this would initialize the vector store
        # For now, we'll use a mock implementation with a JSON file

        # Create index directory if it doesn't exist
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)

        # Check if index exists
        index_file = f"{self.index_path}.json"
        if os.path.exists(index_file):
            logger.info(f"Loading existing memory from {index_file}")
            try:
                with open(index_file, "r") as f:
                    self.memories = json.load(f)
            except Exception as e:
                logger.error(f"Error loading memories: {e}")
                self.memories = []
        else:
            logger.info("Initializing empty memory store")
            self.memories = []

            # Save empty index
            self._save_vector_store()

    def _save_vector_store(self) -> None:
        """
        Save the vector store to disk.
        """
        # In a real implementation, this would save the vector store
        # For now, we'll use a mock implementation with a JSON file

        # Save memories to JSON file
        index_file = f"{self.index_path}.json"
        try:
            with open(index_file, "w") as f:
                json.dump(self.memories, f)
            logger.info(f"Saved memories to {index_file}")
        except Exception as e:
            logger.error(f"Error saving memories: {e}")

    def store_interaction(self, query: Dict[str, Any], response: Dict[str, Any]) -> str:
        """
        Store an interaction in memory.

        Args:
            query: The user query
            response: The system response

        Returns:
            The ID of the stored interaction
        """
        logger.info("Storing interaction in long-term memory")

        try:
            # Create memory entry
            memory_id = f"mem-{len(self.memories) + 1}"
            timestamp = datetime.now().isoformat()

            # Extract content from query and response
            query_content = query.get("content", "")
            response_content = response.get("content", "")

            # Combine query and response for embedding
            combined_content = f"Query: {query_content}\nResponse: {response_content}"

            # Generate embedding
            # In a real implementation, this would be used for semantic search
            # embedding = self.model_provider.generate_embeddings([combined_content])[0]

            # Create memory object
            memory = {
                "id": memory_id,
                "timestamp": timestamp,
                "query": query,
                "response": response,
                "combined_content": combined_content,
                # "embedding": embedding,
                "metadata": {
                    "user_id": query.get("user_id"),
                    "conversation_id": query.get("conversation_id"),
                    "tags": query.get("tags", []),
                },
            }

            # Add memory to store
            self.memories.append(memory)

            # Save vector store
            self._save_vector_store()

            return memory_id
        except Exception as e:
            logger.error(f"Error storing interaction: {e}")
            raise

    def retrieve_by_id(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a memory by ID.

        Args:
            memory_id: The ID of the memory to retrieve

        Returns:
            The memory, or None if not found
        """
        logger.info(f"Retrieving memory by ID: {memory_id}")

        try:
            # Find memory by ID
            for memory in self.memories:
                if memory.get("id") == memory_id:
                    return memory

            logger.warning(f"Memory not found: {memory_id}")
            return None
        except Exception as e:
            logger.error(f"Error retrieving memory: {e}")
            return None

    def search(
        self, query: str, limit: int = 5, filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for memories similar to a query.

        Args:
            query: The search query
            limit: Maximum number of results to return
            filters: Optional filters to apply to the search

        Returns:
            List of matching memories
        """
        logger.info(f"Searching memories for: {query}")

        try:
            # In a real implementation, this would use the vector store for semantic search
            # For now, we'll use a simple keyword search

            # Generate query embedding
            # In a real implementation, this would be used for semantic search
            # query_embedding = self.model_provider.generate_embeddings([query])[0]

            # Simple keyword search
            results = []
            query_terms = query.lower().split()

            for memory in self.memories:
                # Apply filters if provided
                if filters and not self._apply_filters(memory, filters):
                    continue

                # Calculate a simple relevance score based on term frequency
                score = 0
                combined_content = memory.get("combined_content", "").lower()

                for term in query_terms:
                    if term in combined_content:
                        score += combined_content.count(term)

                # Add memory to results if it has a non-zero score
                if score > 0:
                    results.append(
                        {
                            "id": memory.get("id"),
                            "timestamp": memory.get("timestamp"),
                            "query": memory.get("query"),
                            "response": memory.get("response"),
                            "score": score,
                            "metadata": memory.get("metadata", {}),
                        }
                    )

            # Sort results by score and limit
            results = sorted(results, key=lambda x: x["score"], reverse=True)[:limit]

            logger.info(f"Found {len(results)} memories for query: {query}")

            return results
        except Exception as e:
            logger.error(f"Error searching memories: {e}")
            return []

    def _apply_filters(self, memory: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """
        Apply filters to a memory.

        Args:
            memory: The memory to filter
            filters: The filters to apply

        Returns:
            True if the memory passes all filters, False otherwise
        """
        # Apply user_id filter
        if "user_id" in filters and memory.get("metadata", {}).get("user_id") != filters["user_id"]:
            return False

        # Apply conversation_id filter
        if (
            "conversation_id" in filters
            and memory.get("metadata", {}).get("conversation_id") != filters["conversation_id"]
        ):
            return False

        # Apply tags filter
        if "tags" in filters:
            memory_tags = memory.get("metadata", {}).get("tags", [])
            for tag in filters["tags"]:
                if tag not in memory_tags:
                    return False

        # Apply date range filter
        if "start_date" in filters or "end_date" in filters:
            memory_date = datetime.fromisoformat(memory.get("timestamp"))

            if "start_date" in filters and memory_date < datetime.fromisoformat(
                filters["start_date"]
            ):
                return False

            if "end_date" in filters and memory_date > datetime.fromisoformat(filters["end_date"]):
                return False

        return True

    def delete(self, memory_id: str) -> bool:
        """
        Delete a memory.

        Args:
            memory_id: The ID of the memory to delete

        Returns:
            True if the memory was deleted, False otherwise
        """
        logger.info(f"Deleting memory: {memory_id}")

        try:
            # Find memory by ID
            for i, memory in enumerate(self.memories):
                if memory.get("id") == memory_id:
                    # Delete memory
                    del self.memories[i]

                    # Save vector store
                    self._save_vector_store()

                    return True

            logger.warning(f"Memory not found for deletion: {memory_id}")
            return False
        except Exception as e:
            logger.error(f"Error deleting memory: {e}")
            return False

    def clear(self, filters: Optional[Dict[str, Any]] = None) -> bool:
        """
        Clear memories, optionally filtered.

        Args:
            filters: Optional filters to apply

        Returns:
            True if memories were cleared, False otherwise
        """
        logger.info("Clearing memories")

        try:
            if filters:
                # Filter memories
                self.memories = [m for m in self.memories if not self._apply_filters(m, filters)]
            else:
                # Clear all memories
                self.memories = []

            # Save vector store
            self._save_vector_store()

            return True
        except Exception as e:
            logger.error(f"Error clearing memories: {e}")
            return False
