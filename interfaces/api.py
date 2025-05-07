"""
API Server - FastAPI server for user input/output.

This module implements a FastAPI server that provides API endpoints for interacting
with the CustomerAI framework.
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from core.agent_manager import AgentManager
from core.config_manager import ConfigManager

logger = logging.getLogger(__name__)


# Define request and response models
class ChatRequest(BaseModel):
    """Request model for chat endpoint."""

    message: str = Field(..., description="User message")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for context")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""

    response: str = Field(..., description="AI response")
    conversation_id: str = Field(..., description="Conversation ID")
    sources: Optional[List[Dict[str, Any]]] = Field(None, description="Information sources")
    confidence: float = Field(..., description="Confidence score")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class InsightRequest(BaseModel):
    """Request model for insight endpoint."""

    query: str = Field(..., description="Insight query")
    data_sources: Optional[List[str]] = Field(None, description="Data sources to query")
    filters: Optional[Dict[str, Any]] = Field(None, description="Query filters")


class InsightResponse(BaseModel):
    """Response model for insight endpoint."""

    insights: List[Dict[str, Any]] = Field(..., description="Generated insights")
    sources: List[Dict[str, Any]] = Field(..., description="Information sources")
    query_id: str = Field(..., description="Query ID for reference")


class ActionRequest(BaseModel):
    """Request model for action endpoint."""

    action_type: str = Field(..., description="Type of action to execute")
    params: Dict[str, Any] = Field(..., description="Action parameters")
    context_id: Optional[str] = Field(None, description="Context ID for reference")


class ActionResponse(BaseModel):
    """Response model for action endpoint."""

    status: str = Field(..., description="Action status")
    message: str = Field(..., description="Status message")
    details: Optional[Dict[str, Any]] = Field(None, description="Action details")
    action_id: str = Field(..., description="Action ID for reference")


def create_app(agent_manager: Optional[AgentManager] = None) -> FastAPI:
    """
    Create and configure the FastAPI application.

    Args:
        agent_manager: Optional agent manager instance

    Returns:
        Configured FastAPI application
    """
    # Load configuration
    config_manager = ConfigManager()
    config = config_manager.load_config()

    # Create FastAPI app
    app = FastAPI(
        title="CustomerAI API", description="API for the CustomerAI framework", version="1.0.0"
    )

    # Configure CORS
    cors_origins = config.get("api", {}).get("cors_origins", ["*"])
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Create agent manager if not provided
    if agent_manager is None:
        from core.agent_manager import AgentManager

        agent_manager = AgentManager()

        # Initialize safety measures
        from core.safety import AntiHallucinationGuard

        safety_guard = AntiHallucinationGuard()
        agent_manager.register_safety_guard(safety_guard)

        # Initialize memory
        from memory.base import LongTermMemory, ShortTermMemory

        memory_config = config.get("memory", {})
        memory_type = memory_config.get("type", "short_term")

        if memory_type == "short_term":
            memory = ShortTermMemory()
        elif memory_type == "long_term":
            memory = LongTermMemory(
                vector_store_type=memory_config.get("vector_db", {}).get("type", "mock")
            )
        else:
            memory = ShortTermMemory()

        agent_manager.set_memory(memory)

    # Health check endpoint
    @app.get("/health")
    async def health_check() -> Dict[str, str]:
        """Health check endpoint."""
        return {"status": "healthy"}

    # Chat endpoint
    @app.post("/chat", response_model=ChatResponse)
    async def chat(request: ChatRequest) -> ChatResponse:
        """
        Chat with the AI.

        Args:
            request: Chat request

        Returns:
            AI response
        """
        logger.info(f"Chat request: {request.message[:50]}...")

        try:
            # Prepare task for agent
            task = {
                "type": "chat",
                "content": request.message,
                "conversation_id": request.conversation_id,
                "metadata": request.metadata or {},
            }

            # Run task
            result = agent_manager.run_task(task)

            # Extract response fields
            response = result.get("content", "I'm sorry, I couldn't generate a response.")
            conversation_id = result.get("conversation_id", "new_conversation")
            sources = result.get("sources", [])
            confidence = result.get("confidence", 0.0)
            metadata = result.get("metadata", {})

            return ChatResponse(
                response=response,
                conversation_id=conversation_id,
                sources=sources,
                confidence=confidence,
                metadata=metadata,
            )
        except Exception as e:
            logger.error(f"Error in chat endpoint: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error processing chat request: {str(e)}",
            )

    # Insight endpoint
    @app.post("/insight", response_model=InsightResponse)
    async def insight(request: InsightRequest) -> InsightResponse:
        """
        Generate insights from data.

        Args:
            request: Insight request

        Returns:
            Generated insights
        """
        logger.info(f"Insight request: {request.query[:50]}...")

        try:
            # Prepare task for agent
            task = {
                "type": "insight",
                "content": request.query,
                "data_sources": request.data_sources or [],
                "filters": request.filters or {},
            }

            # Run task
            result = agent_manager.run_task(task)

            # Extract response fields
            insights = result.get("insights", [])
            sources = result.get("sources", [])
            query_id = result.get("query_id", f"query-{len(request.query)}")

            return InsightResponse(insights=insights, sources=sources, query_id=query_id)
        except Exception as e:
            logger.error(f"Error in insight endpoint: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error processing insight request: {str(e)}",
            )

    # Action endpoint
    @app.post("/action", response_model=ActionResponse)
    async def action(request: ActionRequest) -> ActionResponse:
        """
        Execute an action.

        Args:
            request: Action request

        Returns:
            Action result
        """
        logger.info(f"Action request: {request.action_type}")

        try:
            # Prepare task for agent
            task = {
                "type": "action",
                "action_type": request.action_type,
                "params": request.params,
                "context_id": request.context_id,
            }

            # Run task
            result = agent_manager.run_task(task)

            # Extract response fields
            status_str = result.get("status", "error")
            message = result.get("message", "Action execution failed")
            details = result.get("details", {})
            action_id = result.get("action_id", f"action-{request.action_type}")

            return ActionResponse(
                status=status_str, message=message, details=details, action_id=action_id
            )
        except Exception as e:
            logger.error(f"Error in action endpoint: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error processing action request: {str(e)}",
            )

    # Error handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Global exception handler."""
        logger.error(f"Unhandled exception: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An unexpected error occurred"},
        )

    return app
