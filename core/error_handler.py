"""
Error Handler - Provides error handling functionality for the FinConnectAI framework.

This module implements error handling mechanisms to ensure graceful degradation
and proper error reporting throughout the application.
"""

import functools
import logging
import traceback
from enum import Enum
from typing import Any, Callable, Dict, Optional, Type

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Enum for error severity levels."""

    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class FinConnectAIError(Exception):
    """
    Base exception class for FinConnectAI framework.

    All custom exceptions in the framework should inherit from this class.
    """

    def __init__(
        self,
        message: str,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ):
        """
        Initialize a FinConnectAI error.

        Args:
            message: Error message
            severity: Error severity level
            details: Additional error details
            cause: Original exception that caused this error
        """
        self.message = message
        self.severity = severity
        self.details = details or {}
        self.cause = cause

        # Include cause in the message if available
        if cause:
            message = f"{message} (Caused by: {str(cause)})"

        super().__init__(message)


class ConfigurationError(FinConnectAIError):
    """Exception raised for configuration errors."""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ):
        """Initialize a configuration error."""
        super().__init__(message, ErrorSeverity.ERROR, details, cause)


class ValidationError(FinConnectAIError):
    """Exception raised for validation errors."""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ):
        """Initialize a validation error."""
        super().__init__(message, ErrorSeverity.WARNING, details, cause)


class AuthenticationError(FinConnectAIError):
    """Exception raised for authentication errors."""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ):
        """Initialize an authentication error."""
        super().__init__(message, ErrorSeverity.ERROR, details, cause)


class AuthorizationError(FinConnectAIError):
    """Exception raised for authorization errors."""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ):
        """Initialize an authorization error."""
        super().__init__(message, ErrorSeverity.ERROR, details, cause)


class ModelError(FinConnectAIError):
    """Exception raised for model-related errors."""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ):
        """Initialize a model error."""
        super().__init__(message, ErrorSeverity.ERROR, details, cause)


class MemoryError(FinConnectAIError):
    """Exception raised for memory-related errors."""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ):
        """Initialize a memory error."""
        super().__init__(message, ErrorSeverity.ERROR, details, cause)


class KnowledgeError(FinConnectAIError):
    """Exception raised for knowledge-related errors."""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ):
        """Initialize a knowledge error."""
        super().__init__(message, ErrorSeverity.ERROR, details, cause)


class ActionError(FinConnectAIError):
    """Exception raised for action-related errors."""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ):
        """Initialize an action error."""
        super().__init__(message, ErrorSeverity.ERROR, details, cause)


class ErrorHandler:
    """
    Handler for error management.

    This class provides methods for handling errors, logging them,
    and generating appropriate responses.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize an error handler.

        Args:
            config: Configuration for the error handler
        """
        self.config = config
        self.debug_mode = config.get("debug", False)
        self.log_errors = config.get("log_errors", True)
        self.include_traceback = config.get("include_traceback", False)
        self.fallback_message = config.get(
            "fallback_message", "An error occurred. Please try again later."
        )

        # Map of exception types to handlers
        self.exception_handlers = {}

        # Register default handlers
        self._register_default_handlers()

        logger.info("Initialized error handler")

    def _register_default_handlers(self) -> None:
        """Register default exception handlers."""
        # Register handlers for custom exceptions
        self.register_handler(ConfigurationError, self._handle_configuration_error)
        self.register_handler(ValidationError, self._handle_validation_error)
        self.register_handler(AuthenticationError, self._handle_authentication_error)
        self.register_handler(AuthorizationError, self._handle_authorization_error)
        self.register_handler(ModelError, self._handle_model_error)
        self.register_handler(MemoryError, self._handle_memory_error)
        self.register_handler(KnowledgeError, self._handle_knowledge_error)
        self.register_handler(ActionError, self._handle_action_error)

        # Register handler for base FinConnectAI error
        self.register_handler(FinConnectAIError, self._handle_finconnectai_error)

        # Register handler for all other exceptions
        self.register_handler(Exception, self._handle_generic_error)

    def register_handler(
        self, exception_type: Type[Exception], handler: Callable[[Exception], Dict[str, Any]]
    ) -> None:
        """
        Register a handler for an exception type.

        Args:
            exception_type: The exception type to handle
            handler: The handler function
        """
        self.exception_handlers[exception_type] = handler

    def handle_exception(self, exception: Exception) -> Dict[str, Any]:
        """
        Handle an exception.

        Args:
            exception: The exception to handle

        Returns:
            Error response
        """
        # Find the most specific handler for the exception
        handler = self._find_handler(exception.__class__)

        # Log the error
        if self.log_errors:
            self._log_exception(exception)

        # Call the handler
        return handler(exception)

    def _find_handler(
        self, exception_type: Type[Exception]
    ) -> Callable[[Exception], Dict[str, Any]]:
        """
        Find the most specific handler for an exception type.

        Args:
            exception_type: The exception type

        Returns:
            Handler function
        """
        # Check if there's a direct handler
        if exception_type in self.exception_handlers:
            return self.exception_handlers[exception_type]

        # Check parent classes
        for base in exception_type.__bases__:
            if base in self.exception_handlers:
                return self.exception_handlers[base]

        # Fall back to generic handler
        return self.exception_handlers.get(Exception, self._handle_generic_error)

    def _log_exception(self, exception: Exception) -> None:
        """
        Log an exception.

        Args:
            exception: The exception to log
        """
        if isinstance(exception, FinConnectAIError):
            if exception.severity == ErrorSeverity.CRITICAL:
                logger.critical(str(exception), exc_info=True)
            elif exception.severity == ErrorSeverity.ERROR:
                logger.error(str(exception), exc_info=True)
            elif exception.severity == ErrorSeverity.WARNING:
                logger.warning(str(exception), exc_info=True)
            else:
                logger.info(str(exception), exc_info=True)
        else:
            logger.error(f"Unexpected error: {str(exception)}", exc_info=True)

    def _handle_finconnectai_error(self, exception: FinConnectAIError) -> Dict[str, Any]:
        """
        Handle a FinConnectAI error.

        Args:
            exception: The exception to handle

        Returns:
            Error response
        """
        response = {
            "status": "error",
            "error": {
                "type": exception.__class__.__name__,
                "message": exception.message,
                "severity": exception.severity.value,
            },
        }

        # Include details if available
        if exception.details:
            response["error"]["details"] = exception.details

        # Include traceback in debug mode
        if self.debug_mode and self.include_traceback:
            response["error"]["traceback"] = traceback.format_exc()

        return response

    def _handle_configuration_error(self, exception: ConfigurationError) -> Dict[str, Any]:
        """
        Handle a configuration error.

        Args:
            exception: The exception to handle

        Returns:
            Error response
        """
        return self._handle_finconnectai_error(exception)

    def _handle_validation_error(self, exception: ValidationError) -> Dict[str, Any]:
        """
        Handle a validation error.

        Args:
            exception: The exception to handle

        Returns:
            Error response
        """
        return self._handle_finconnectai_error(exception)

    def _handle_authentication_error(self, exception: AuthenticationError) -> Dict[str, Any]:
        """
        Handle an authentication error.

        Args:
            exception: The exception to handle

        Returns:
            Error response
        """
        return self._handle_finconnectai_error(exception)

    def _handle_authorization_error(self, exception: AuthorizationError) -> Dict[str, Any]:
        """
        Handle an authorization error.

        Args:
            exception: The exception to handle

        Returns:
            Error response
        """
        return self._handle_finconnectai_error(exception)

    def _handle_model_error(self, exception: ModelError) -> Dict[str, Any]:
        """
        Handle a model error.

        Args:
            exception: The exception to handle

        Returns:
            Error response
        """
        return self._handle_finconnectai_error(exception)

    def _handle_memory_error(self, exception: MemoryError) -> Dict[str, Any]:
        """
        Handle a memory error.

        Args:
            exception: The exception to handle

        Returns:
            Error response
        """
        return self._handle_finconnectai_error(exception)

    def _handle_knowledge_error(self, exception: KnowledgeError) -> Dict[str, Any]:
        """
        Handle a knowledge error.

        Args:
            exception: The exception to handle

        Returns:
            Error response
        """
        return self._handle_finconnectai_error(exception)

    def _handle_action_error(self, exception: ActionError) -> Dict[str, Any]:
        """
        Handle an action error.

        Args:
            exception: The exception to handle

        Returns:
            Error response
        """
        return self._handle_finconnectai_error(exception)

    def _handle_generic_error(self, exception: Exception) -> Dict[str, Any]:
        """
        Handle a generic error.

        Args:
            exception: The exception to handle

        Returns:
            Error response
        """
        response = {
            "status": "error",
            "error": {
                "type": "InternalError",
                "message": self.fallback_message,
                "severity": ErrorSeverity.ERROR.value,
            },
        }

        # Include actual error message in debug mode
        if self.debug_mode:
            response["error"]["actual_message"] = str(exception)

            # Include traceback in debug mode
            if self.include_traceback:
                response["error"]["traceback"] = traceback.format_exc()

        return response


def handle_errors(error_handler: Optional[ErrorHandler] = None):
    """
    Decorator for handling errors in functions.

    Args:
        error_handler: Optional error handler to use

    Returns:
        Decorator function
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if error_handler:
                    return error_handler.handle_exception(e)
                else:
                    # If no error handler, re-raise the exception
                    raise

        return wrapper

    return decorator
