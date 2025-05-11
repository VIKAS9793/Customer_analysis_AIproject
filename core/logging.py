"""
Logging configuration for the FinConnectAI framework.

This module sets up logging for the FinConnectAI framework with appropriate
handlers and formatters.
"""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Dict, Optional


def setup_logging(config: Dict[str, Any]) -> None:
    """
    Set up logging for the FinConnectAI framework.

    Args:
        config: Logging configuration
    """
    # Get log level from config
    log_level_str = config.get("level", "INFO")
    log_level = getattr(logging, log_level_str.upper(), logging.INFO)

    # Get log format from config
    log_format = config.get("format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter(log_format)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # Create file handler if enabled
    if config.get("file_enabled", False):
        log_dir = config.get("log_dir", "logs")
        os.makedirs(log_dir, exist_ok=True)

        log_file = Path(log_dir) / "finconnectai.log"
        max_bytes = config.get("max_bytes", 10 * 1024 * 1024)  # 10 MB
        backup_count = config.get("backup_count", 5)

        file_handler = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count)
        file_handler.setLevel(log_level)
        file_formatter = logging.Formatter(log_format)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

    # Log startup message
    logging.info("FinConnectAI logging initialized")


class AuditLogger:
    """
    Logger for audit events in the FinConnectAI framework.

    This logger ensures all security-relevant events are properly logged
    with appropriate metadata for compliance and auditing purposes.
    """

    def __init__(self, name: str = "finconnectai.audit"):
        """
        Initialize the audit logger.

        Args:
            name: Logger name
        """
        self.logger = logging.getLogger(name)

    def log_access(self, user_id: str, resource: str, action: str, success: bool) -> None:
        """
        Log an access event.

        Args:
            user_id: ID of the user performing the action
            resource: Resource being accessed
            action: Action being performed
            success: Whether the access was successful
        """
        self.logger.info(
            f"ACCESS: user={user_id} resource={resource} action={action} success={success}"
        )

    def log_data_access(
        self, user_id: str, data_type: str, data_id: str, purpose: str, success: bool
    ) -> None:
        """
        Log a data access event.

        Args:
            user_id: ID of the user accessing the data
            data_type: Type of data being accessed
            data_id: ID of the data being accessed
            purpose: Purpose of the access
            success: Whether the access was successful
        """
        self.logger.info(
            f"DATA_ACCESS: user={user_id} data_type={data_type} data_id={data_id} "
            f"purpose={purpose} success={success}"
        )

    def log_model_invocation(
        self,
        model: str,
        prompt_id: str,
        user_id: Optional[str] = None,
        tokens: Optional[int] = None,
    ) -> None:
        """
        Log a model invocation event.

        Args:
            model: Model being invoked
            prompt_id: ID of the prompt
            user_id: Optional ID of the user
            tokens: Optional token count
        """
        user_info = f"user={user_id} " if user_id else ""
        token_info = f"tokens={tokens} " if tokens is not None else ""

        self.logger.info(
            f"MODEL_INVOCATION: {user_info}{token_info}model={model} prompt_id={prompt_id}"
        )

    def log_security_event(self, event_type: str, severity: str, details: Dict[str, Any]) -> None:
        """
        Log a security event.

        Args:
            event_type: Type of security event
            severity: Severity of the event
            details: Event details
        """
        self.logger.warning(
            f"SECURITY_EVENT: type={event_type} severity={severity} details={details}"
        )
