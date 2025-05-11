"""
MemoryInterface - Abstract memory layer with short- and long-term implementations.

This module defines the abstract interface for memory in the FinConnectAI framework,
with implementations for both short-term and long-term memory.
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class MemoryInterface(ABC):
    """
    Abstract base class for memory implementations.

    This class defines the interface that all memory implementations must follow.
    """

    @abstractmethod
    def store_interaction(self, query: Dict[str, Any], response: Dict[str, Any]) -> str:
        """
        Store an interaction in memory.

        Args:
            query: The query from the user
            response: The response from the system

        Returns:
            The ID of the stored interaction
        """
        pass

    @abstractmethod
    def retrieve_interaction(self, interaction_id: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Retrieve an interaction from memory.

        Args:
            interaction_id: The ID of the interaction to retrieve

        Returns:
            The query and response for the interaction
        """
        pass

    @abstractmethod
    def retrieve_recent_interactions(
        self, limit: int = 10
    ) -> List[Tuple[Dict[str, Any], Dict[str, Any]]]:
        """
        Retrieve recent interactions from memory.

        Args:
            limit: Maximum number of interactions to retrieve

        Returns:
            A list of query-response pairs
        """
        pass

    @abstractmethod
    def search_interactions(
        self, query: str, limit: int = 5
    ) -> List[Tuple[Dict[str, Any], Dict[str, Any]]]:
        """
        Search for interactions in memory.

        Args:
            query: The search query
            limit: Maximum number of interactions to retrieve

        Returns:
            A list of query-response pairs matching the search
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all interactions from memory."""
        pass


class ShortTermMemory(MemoryInterface):
    """
    Short-term memory implementation.

    This class implements short-term memory that holds temporary context
    for immediate tasks. It stores interactions in memory without persistence.
    """

    def __init__(self, max_interactions: int = 100):
        """
        Initialize short-term memory.

        Args:
            max_interactions: Maximum number of interactions to store
        """
        self.interactions: List[Tuple[str, Dict[str, Any], Dict[str, Any], datetime]] = []
        self.max_interactions = max_interactions
        logger.info(f"Initialized short-term memory with max_interactions={max_interactions}")

    def store_interaction(self, query: Dict[str, Any], response: Dict[str, Any]) -> str:
        """
        Store an interaction in short-term memory.

        Args:
            query: The query from the user
            response: The response from the system

        Returns:
            The ID of the stored interaction
        """
        # Generate a unique ID for the interaction
        interaction_id = f"st-{len(self.interactions)}-{datetime.now().timestamp()}"

        # Store the interaction
        self.interactions.append((interaction_id, query, response, datetime.now()))

        # Trim if needed
        if len(self.interactions) > self.max_interactions:
            self.interactions = self.interactions[-self.max_interactions :]

        logger.debug(f"Stored interaction {interaction_id} in short-term memory")
        return interaction_id

    def retrieve_interaction(self, interaction_id: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Retrieve an interaction from short-term memory.

        Args:
            interaction_id: The ID of the interaction to retrieve

        Returns:
            The query and response for the interaction
        """
        for stored_id, query, response, _ in self.interactions:
            if stored_id == interaction_id:
                return query, response

        logger.warning(f"Interaction {interaction_id} not found in short-term memory")
        return {}, {}

    def retrieve_recent_interactions(
        self, limit: int = 10
    ) -> List[Tuple[Dict[str, Any], Dict[str, Any]]]:
        """
        Retrieve recent interactions from short-term memory.

        Args:
            limit: Maximum number of interactions to retrieve

        Returns:
            A list of query-response pairs
        """
        # Get the most recent interactions
        recent = self.interactions[-limit:]

        # Return as list of query-response pairs
        return [(query, response) for _, query, response, _ in recent]

    def search_interactions(
        self, query: str, limit: int = 5
    ) -> List[Tuple[Dict[str, Any], Dict[str, Any]]]:
        """
        Search for interactions in short-term memory.

        Args:
            query: The search query
            limit: Maximum number of interactions to retrieve

        Returns:
            A list of query-response pairs matching the search
        """
        # Simple search implementation
        results = []

        for _, q, r, _ in self.interactions:
            # Check if query appears in the interaction
            q_content = q.get("content", "")
            r_content = r.get("content", "")

            if query.lower() in q_content.lower() or query.lower() in r_content.lower():
                results.append((q, r))

            if len(results) >= limit:
                break

        return results

    def clear(self) -> None:
        """Clear all interactions from short-term memory."""
        self.interactions = []
        logger.info("Cleared short-term memory")


class LongTermMemory(MemoryInterface):
    """
    Long-term memory implementation.

    This class implements long-term memory that stores past interactions and facts
    for better recall and continuity. It uses a vector database for efficient retrieval.
    """

    def __init__(self, vector_store_type: str = "mock", **kwargs):
        """
        Initialize long-term memory.

        Args:
            vector_store_type: Type of vector store to use
            **kwargs: Additional arguments for the vector store
        """
        self.vector_store_type = vector_store_type
        self.vector_store = self._initialize_vector_store(vector_store_type, **kwargs)
        logger.info(f"Initialized long-term memory with vector_store_type={vector_store_type}")

    def _initialize_vector_store(self, vector_store_type: str, **kwargs) -> Any:
        """
        Initialize the vector store.

        Args:
            vector_store_type: Type of vector store to use
            **kwargs: Additional arguments for the vector store

        Returns:
            The initialized vector store
        """
        if vector_store_type == "mock":
            return MockVectorStore()
        elif vector_store_type == "faiss":
            try:
                from memory.vector_stores.faiss_store import FAISSVectorStore

                return FAISSVectorStore(**kwargs)
            except ImportError:
                logger.error("FAISS not installed, falling back to mock vector store")
                return MockVectorStore()
        elif vector_store_type == "pinecone":
            try:
                from memory.vector_stores.pinecone_store import PineconeVectorStore

                return PineconeVectorStore(**kwargs)
            except ImportError:
                logger.error("Pinecone not installed, falling back to mock vector store")
                return MockVectorStore()
        else:
            logger.warning(f"Unknown vector store type: {vector_store_type}, using mock")
            return MockVectorStore()

    def store_interaction(self, query: Dict[str, Any], response: Dict[str, Any]) -> str:
        """
        Store an interaction in long-term memory.

        Args:
            query: The query from the user
            response: The response from the system

        Returns:
            The ID of the stored interaction
        """
        # Generate a unique ID for the interaction
        interaction_id = f"lt-{datetime.now().timestamp()}"

        # Combine query and response for embedding
        combined_text = self._prepare_text_for_embedding(query, response)

        # Store in vector database
        self.vector_store.add_item(
            interaction_id,
            combined_text,
            {"query": query, "response": response, "timestamp": datetime.now().isoformat()},
        )

        logger.debug(f"Stored interaction {interaction_id} in long-term memory")
        return interaction_id

    def _prepare_text_for_embedding(self, query: Dict[str, Any], response: Dict[str, Any]) -> str:
        """
        Prepare text for embedding.

        Args:
            query: The query from the user
            response: The response from the system

        Returns:
            The prepared text
        """
        query_text = query.get("content", "")
        response_text = response.get("content", "")

        return f"Query: {query_text}\nResponse: {response_text}"

    def retrieve_interaction(self, interaction_id: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Retrieve an interaction from long-term memory.

        Args:
            interaction_id: The ID of the interaction to retrieve

        Returns:
            The query and response for the interaction
        """
        item = self.vector_store.get_item(interaction_id)

        if item:
            metadata = item.get("metadata", {})
            return metadata.get("query", {}), metadata.get("response", {})

        logger.warning(f"Interaction {interaction_id} not found in long-term memory")
        return {}, {}

    def retrieve_recent_interactions(
        self, limit: int = 10
    ) -> List[Tuple[Dict[str, Any], Dict[str, Any]]]:
        """
        Retrieve recent interactions from long-term memory.

        Args:
            limit: Maximum number of interactions to retrieve

        Returns:
            A list of query-response pairs
        """
        # Get recent items from vector store
        items = self.vector_store.get_recent_items(limit)

        # Extract query-response pairs
        results = []
        for item in items:
            metadata = item.get("metadata", {})
            query = metadata.get("query", {})
            response = metadata.get("response", {})
            results.append((query, response))

        return results

    def search_interactions(
        self, query: str, limit: int = 5
    ) -> List[Tuple[Dict[str, Any], Dict[str, Any]]]:
        """
        Search for interactions in long-term memory.

        Args:
            query: The search query
            limit: Maximum number of interactions to retrieve

        Returns:
            A list of query-response pairs matching the search
        """
        # Search the vector store
        items = self.vector_store.search(query, limit)

        # Extract query-response pairs
        results = []
        for item in items:
            metadata = item.get("metadata", {})
            query = metadata.get("query", {})
            response = metadata.get("response", {})
            results.append((query, response))

        return results

    def clear(self) -> None:
        """Clear all interactions from long-term memory."""
        self.vector_store.clear()
        logger.info("Cleared long-term memory")


class MockVectorStore:
    """
    Mock implementation of a vector store for testing.

    This class provides a simple in-memory implementation of a vector store
    for testing and development purposes.
    """

    def __init__(self):
        """Initialize the mock vector store."""
        self.items = {}
        self.timestamps = {}

    def add_item(self, item_id: str, text: str, metadata: Dict[str, Any]) -> None:
        """
        Add an item to the store.

        Args:
            item_id: ID of the item
            text: Text to embed
            metadata: Additional metadata
        """
        self.items[item_id] = {"text": text, "metadata": metadata}
        self.timestamps[item_id] = datetime.now()

    def get_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        """
        Get an item from the store.

        Args:
            item_id: ID of the item

        Returns:
            The item, or None if not found
        """
        return self.items.get(item_id)

    def get_recent_items(self, limit: int) -> List[Dict[str, Any]]:
        """
        Get recent items from the store.

        Args:
            limit: Maximum number of items to retrieve

        Returns:
            A list of recent items
        """
        # Sort items by timestamp
        sorted_ids = sorted(self.timestamps.keys(), key=lambda x: self.timestamps[x], reverse=True)

        # Get the most recent items
        recent_ids = sorted_ids[:limit]

        # Return the items
        return [self.items[item_id] for item_id in recent_ids]

    def search(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """
        Search for items in the store.

        Args:
            query: The search query
            limit: Maximum number of items to retrieve

        Returns:
            A list of matching items
        """
        # Simple search implementation
        results = []

        for item_id, item in self.items.items():
            if query.lower() in item["text"].lower():
                results.append(item)

            if len(results) >= limit:
                break

        return results

    def clear(self) -> None:
        """Clear all items from the store."""
        self.items = {}
        self.timestamps = {}
