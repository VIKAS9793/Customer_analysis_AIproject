"""
KnowledgeBase - Plugin-based knowledge search interface.

This module defines the abstract interface for knowledge bases in the CustomerAI framework,
with implementations for different types of knowledge storage.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class KnowledgeBase(ABC):
    """
    Abstract base class for knowledge base implementations.

    This class defines the interface that all knowledge base implementations must follow.
    """

    @abstractmethod
    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search the knowledge base for relevant information.

        Args:
            query: The search query
            limit: Maximum number of results to return

        Returns:
            A list of relevant documents or information
        """
        pass

    @abstractmethod
    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific document from the knowledge base.

        Args:
            document_id: ID of the document to retrieve

        Returns:
            The document, or None if not found
        """
        pass

    @abstractmethod
    def add_document(self, document: Dict[str, Any]) -> str:
        """
        Add a document to the knowledge base.

        Args:
            document: The document to add

        Returns:
            The ID of the added document
        """
        pass

    @abstractmethod
    def update_document(self, document_id: str, document: Dict[str, Any]) -> bool:
        """
        Update a document in the knowledge base.

        Args:
            document_id: ID of the document to update
            document: The updated document

        Returns:
            True if the document was updated, False otherwise
        """
        pass

    @abstractmethod
    def delete_document(self, document_id: str) -> bool:
        """
        Delete a document from the knowledge base.

        Args:
            document_id: ID of the document to delete

        Returns:
            True if the document was deleted, False otherwise
        """
        pass


class VectorStoreKnowledge(KnowledgeBase):
    """
    Vector store implementation of a knowledge base.

    This class implements a knowledge base using a vector store for efficient
    semantic search.
    """

    def __init__(self, vector_store_type: str = "mock", **kwargs):
        """
        Initialize the vector store knowledge base.

        Args:
            vector_store_type: Type of vector store to use
            **kwargs: Additional arguments for the vector store
        """
        self.vector_store_type = vector_store_type
        self.vector_store = self._initialize_vector_store(vector_store_type, **kwargs)
        logger.info(f"Initialized vector store knowledge base with type={vector_store_type}")

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
                from knowledge.vector_stores.faiss_store import FAISSVectorStore

                return FAISSVectorStore(**kwargs)
            except ImportError:
                logger.error("FAISS not installed, falling back to mock vector store")
                return MockVectorStore()
        elif vector_store_type == "pinecone":
            try:
                from knowledge.vector_stores.pinecone_store import PineconeVectorStore

                return PineconeVectorStore(**kwargs)
            except ImportError:
                logger.error("Pinecone not installed, falling back to mock vector store")
                return MockVectorStore()
        else:
            logger.warning(f"Unknown vector store type: {vector_store_type}, using mock")
            return MockVectorStore()

    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search the knowledge base for relevant information.

        Args:
            query: The search query
            limit: Maximum number of results to return

        Returns:
            A list of relevant documents or information
        """
        # Search the vector store
        results = self.vector_store.search(query, limit)

        # Format the results
        formatted_results = []
        for result in results:
            formatted_results.append(
                {
                    "id": result.get("id", ""),
                    "title": result.get("metadata", {}).get("title", ""),
                    "content": result.get("text", ""),
                    "content_snippet": result.get("text", "")[:200] + "...",
                    "url": result.get("metadata", {}).get("url", ""),
                    "source": result.get("metadata", {}).get("source", ""),
                    "relevance_score": result.get("score", 0.0),
                }
            )

        return formatted_results

    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific document from the knowledge base.

        Args:
            document_id: ID of the document to retrieve

        Returns:
            The document, or None if not found
        """
        # Get the document from the vector store
        result = self.vector_store.get_item(document_id)

        if not result:
            return None

        # Format the result
        return {
            "id": document_id,
            "title": result.get("metadata", {}).get("title", ""),
            "content": result.get("text", ""),
            "url": result.get("metadata", {}).get("url", ""),
            "source": result.get("metadata", {}).get("source", ""),
            "metadata": result.get("metadata", {}),
        }

    def add_document(self, document: Dict[str, Any]) -> str:
        """
        Add a document to the knowledge base.

        Args:
            document: The document to add

        Returns:
            The ID of the added document
        """
        # Extract document fields
        document_id = document.get("id", f"doc-{len(self.vector_store.items) + 1}")
        title = document.get("title", "")
        content = document.get("content", "")
        url = document.get("url", "")
        source = document.get("source", "")
        metadata = document.get("metadata", {})

        # Combine metadata
        combined_metadata = {"title": title, "url": url, "source": source, **metadata}

        # Add to vector store
        self.vector_store.add_item(document_id, content, combined_metadata)

        return document_id

    def update_document(self, document_id: str, document: Dict[str, Any]) -> bool:
        """
        Update a document in the knowledge base.

        Args:
            document_id: ID of the document to update
            document: The updated document

        Returns:
            True if the document was updated, False otherwise
        """
        # Check if document exists
        if not self.vector_store.get_item(document_id):
            return False

        # Delete the existing document
        self.vector_store.delete_item(document_id)

        # Add the updated document
        title = document.get("title", "")
        content = document.get("content", "")
        url = document.get("url", "")
        source = document.get("source", "")
        metadata = document.get("metadata", {})

        # Combine metadata
        combined_metadata = {"title": title, "url": url, "source": source, **metadata}

        # Add to vector store
        self.vector_store.add_item(document_id, content, combined_metadata)

        return True

    def delete_document(self, document_id: str) -> bool:
        """
        Delete a document from the knowledge base.

        Args:
            document_id: ID of the document to delete

        Returns:
            True if the document was deleted, False otherwise
        """
        return self.vector_store.delete_item(document_id)


class GraphKnowledge(KnowledgeBase):
    """
    Graph database implementation of a knowledge base.

    This class implements a knowledge base using a graph database for
    relationship-based knowledge representation.
    """

    def __init__(self, graph_db_type: str = "mock", **kwargs):
        """
        Initialize the graph knowledge base.

        Args:
            graph_db_type: Type of graph database to use
            **kwargs: Additional arguments for the graph database
        """
        self.graph_db_type = graph_db_type
        self.graph_db = self._initialize_graph_db(graph_db_type, **kwargs)
        logger.info(f"Initialized graph knowledge base with type={graph_db_type}")

    def _initialize_graph_db(self, graph_db_type: str, **kwargs) -> Any:
        """
        Initialize the graph database.

        Args:
            graph_db_type: Type of graph database to use
            **kwargs: Additional arguments for the graph database

        Returns:
            The initialized graph database
        """
        if graph_db_type == "mock":
            return MockGraphDB()
        elif graph_db_type == "neo4j":
            try:
                from knowledge.graph_dbs.neo4j_db import Neo4jGraphDB

                return Neo4jGraphDB(**kwargs)
            except ImportError:
                logger.error("Neo4j not installed, falling back to mock graph DB")
                return MockGraphDB()
        else:
            logger.warning(f"Unknown graph DB type: {graph_db_type}, using mock")
            return MockGraphDB()

    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search the knowledge base for relevant information.

        Args:
            query: The search query
            limit: Maximum number of results to return

        Returns:
            A list of relevant documents or information
        """
        # Search the graph database
        results = self.graph_db.search(query, limit)

        # Format the results
        formatted_results = []
        for result in results:
            formatted_results.append(
                {
                    "id": result.get("id", ""),
                    "title": result.get("properties", {}).get("title", ""),
                    "content": result.get("properties", {}).get("content", ""),
                    "content_snippet": result.get("properties", {}).get("content", "")[:200]
                    + "...",
                    "url": result.get("properties", {}).get("url", ""),
                    "source": result.get("properties", {}).get("source", ""),
                    "relevance_score": result.get("score", 0.0),
                    "relationships": result.get("relationships", []),
                }
            )

        return formatted_results

    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific document from the knowledge base.

        Args:
            document_id: ID of the document to retrieve

        Returns:
            The document, or None if not found
        """
        # Get the document from the graph database
        result = self.graph_db.get_node(document_id)

        if not result:
            return None

        # Format the result
        return {
            "id": document_id,
            "title": result.get("properties", {}).get("title", ""),
            "content": result.get("properties", {}).get("content", ""),
            "url": result.get("properties", {}).get("url", ""),
            "source": result.get("properties", {}).get("source", ""),
            "metadata": result.get("properties", {}),
            "relationships": result.get("relationships", []),
        }

    def add_document(self, document: Dict[str, Any]) -> str:
        """
        Add a document to the knowledge base.

        Args:
            document: The document to add

        Returns:
            The ID of the added document
        """
        # Extract document fields
        document_id = document.get("id", f"doc-{self.graph_db.get_node_count() + 1}")
        title = document.get("title", "")
        content = document.get("content", "")
        url = document.get("url", "")
        source = document.get("source", "")
        metadata = document.get("metadata", {})
        relationships = document.get("relationships", [])

        # Combine properties
        properties = {"title": title, "content": content, "url": url, "source": source, **metadata}

        # Add to graph database
        self.graph_db.add_node(document_id, "Document", properties)

        # Add relationships
        for relationship in relationships:
            target_id = relationship.get("target_id")
            rel_type = relationship.get("type")
            rel_properties = relationship.get("properties", {})

            if target_id and rel_type:
                self.graph_db.add_relationship(document_id, target_id, rel_type, rel_properties)

        return document_id

    def update_document(self, document_id: str, document: Dict[str, Any]) -> bool:
        """
        Update a document in the knowledge base.

        Args:
            document_id: ID of the document to update
            document: The updated document

        Returns:
            True if the document was updated, False otherwise
        """
        # Check if document exists
        if not self.graph_db.get_node(document_id):
            return False

        # Extract document fields
        title = document.get("title", "")
        content = document.get("content", "")
        url = document.get("url", "")
        source = document.get("source", "")
        metadata = document.get("metadata", {})

        # Combine properties
        properties = {"title": title, "content": content, "url": url, "source": source, **metadata}

        # Update in graph database
        self.graph_db.update_node(document_id, properties)

        # Update relationships if provided
        if "relationships" in document:
            # First, remove existing relationships
            self.graph_db.delete_relationships(document_id)

            # Then add the new ones
            for relationship in document["relationships"]:
                target_id = relationship.get("target_id")
                rel_type = relationship.get("type")
                rel_properties = relationship.get("properties", {})

                if target_id and rel_type:
                    self.graph_db.add_relationship(document_id, target_id, rel_type, rel_properties)

        return True

    def delete_document(self, document_id: str) -> bool:
        """
        Delete a document from the knowledge base.

        Args:
            document_id: ID of the document to delete

        Returns:
            True if the document was deleted, False otherwise
        """
        return self.graph_db.delete_node(document_id)


class MockVectorStore:
    """
    Mock implementation of a vector store for testing.

    This class provides a simple in-memory implementation of a vector store
    for testing and development purposes.
    """

    def __init__(self):
        """Initialize the mock vector store."""
        self.items = {}

    def add_item(self, item_id: str, text: str, metadata: Dict[str, Any]) -> None:
        """
        Add an item to the store.

        Args:
            item_id: ID of the item
            text: Text to embed
            metadata: Additional metadata
        """
        self.items[item_id] = {"text": text, "metadata": metadata}

    def get_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        """
        Get an item from the store.

        Args:
            item_id: ID of the item

        Returns:
            The item, or None if not found
        """
        return self.items.get(item_id)

    def delete_item(self, item_id: str) -> bool:
        """
        Delete an item from the store.

        Args:
            item_id: ID of the item to delete

        Returns:
            True if the item was deleted, False otherwise
        """
        if item_id in self.items:
            del self.items[item_id]
            return True
        return False

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
                result = {
                    "id": item_id,
                    "text": item["text"],
                    "metadata": item["metadata"],
                    "score": 0.8,  # Mock relevance score
                }
                results.append(result)

            if len(results) >= limit:
                break

        return results


class MockGraphDB:
    """
    Mock implementation of a graph database for testing.

    This class provides a simple in-memory implementation of a graph database
    for testing and development purposes.
    """

    def __init__(self):
        """Initialize the mock graph database."""
        self.nodes = {}
        self.relationships = {}

    def add_node(self, node_id: str, node_type: str, properties: Dict[str, Any]) -> None:
        """
        Add a node to the database.

        Args:
            node_id: ID of the node
            node_type: Type of the node
            properties: Node properties
        """
        self.nodes[node_id] = {"type": node_type, "properties": properties}
        self.relationships[node_id] = []

    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a node from the database.

        Args:
            node_id: ID of the node

        Returns:
            The node, or None if not found
        """
        if node_id not in self.nodes:
            return None

        node = self.nodes[node_id]
        relationships = self.relationships.get(node_id, [])

        return {
            "id": node_id,
            "type": node["type"],
            "properties": node["properties"],
            "relationships": relationships,
        }

    def update_node(self, node_id: str, properties: Dict[str, Any]) -> bool:
        """
        Update a node in the database.

        Args:
            node_id: ID of the node to update
            properties: Updated properties

        Returns:
            True if the node was updated, False otherwise
        """
        if node_id not in self.nodes:
            return False

        self.nodes[node_id]["properties"] = properties
        return True

    def delete_node(self, node_id: str) -> bool:
        """
        Delete a node from the database.

        Args:
            node_id: ID of the node to delete

        Returns:
            True if the node was deleted, False otherwise
        """
        if node_id not in self.nodes:
            return False

        del self.nodes[node_id]
        del self.relationships[node_id]

        # Remove any relationships targeting this node
        for source_id, rels in self.relationships.items():
            self.relationships[source_id] = [r for r in rels if r["target_id"] != node_id]

        return True

    def add_relationship(
        self, source_id: str, target_id: str, rel_type: str, properties: Dict[str, Any]
    ) -> bool:
        """
        Add a relationship to the database.

        Args:
            source_id: ID of the source node
            target_id: ID of the target node
            rel_type: Type of the relationship
            properties: Relationship properties

        Returns:
            True if the relationship was added, False otherwise
        """
        if source_id not in self.nodes or target_id not in self.nodes:
            return False

        relationship = {
            "source_id": source_id,
            "target_id": target_id,
            "type": rel_type,
            "properties": properties,
        }

        self.relationships[source_id].append(relationship)
        return True

    def delete_relationships(self, node_id: str) -> bool:
        """
        Delete all relationships for a node.

        Args:
            node_id: ID of the node

        Returns:
            True if relationships were deleted, False otherwise
        """
        if node_id not in self.relationships:
            return False

        self.relationships[node_id] = []

        # Remove any relationships targeting this node
        for source_id, rels in self.relationships.items():
            if source_id != node_id:
                self.relationships[source_id] = [r for r in rels if r["target_id"] != node_id]

        return True

    def search(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """
        Search for nodes in the database.

        Args:
            query: The search query
            limit: Maximum number of nodes to retrieve

        Returns:
            A list of matching nodes
        """
        # Simple search implementation
        results = []

        for node_id, node in self.nodes.items():
            properties = node["properties"]
            content = properties.get("content", "")
            title = properties.get("title", "")

            if query.lower() in content.lower() or query.lower() in title.lower():
                result = {
                    "id": node_id,
                    "type": node["type"],
                    "properties": properties,
                    "relationships": self.relationships.get(node_id, []),
                    "score": 0.8,  # Mock relevance score
                }
                results.append(result)

            if len(results) >= limit:
                break

        return results

    def get_node_count(self) -> int:
        """
        Get the number of nodes in the database.

        Returns:
            The number of nodes
        """
        return len(self.nodes)
