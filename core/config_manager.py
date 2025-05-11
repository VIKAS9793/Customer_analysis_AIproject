"""
ConfigManager - Handles loading and validating configuration for the FinConnectAI framework.

This module implements a configuration manager that loads configuration from
various sources and validates it against the expected schema.
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class ConfigManager:
    """
    Handles loading and validating configuration for the FinConnectAI framework.
    """

    def __init__(self, config_path: Optional[str] = None, env_file: Optional[str] = None):
        """
        Initialize the configuration manager.

        Args:
            config_path: Path to the configuration file
            env_file: Path to the environment file
        """
        self.config_path = config_path or os.environ.get(
            "FINCONNECTAI_CONFIG", "configs/default.yaml"
        )
        self.env_file = env_file or os.environ.get("FINCONNECTAI_ENV", ".env")

        # Load environment variables
        self._load_env_vars()

    def _load_env_vars(self) -> None:
        """Load environment variables from the .env file."""
        env_path = Path(self.env_file)
        if env_path.exists():
            logger.info(f"Loading environment variables from {env_path}")
            load_dotenv(env_path)
        else:
            logger.warning(f"Environment file not found: {env_path}")

    def load_config(self) -> Dict[str, Any]:
        """
        Load the configuration from the specified file.

        Returns:
            The loaded configuration
        """
        config_path = Path(self.config_path)
        if not config_path.exists():
            logger.warning(f"Configuration file not found: {config_path}")
            return self._get_default_config()

        logger.info(f"Loading configuration from {config_path}")
        try:
            with open(config_path, "r") as f:
                config = yaml.safe_load(f)

            # Validate the configuration
            self._validate_config(config)

            # Apply environment variable overrides
            config = self._apply_env_overrides(config)

            return config
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """
        Get the default configuration.

        Returns:
            The default configuration
        """
        logger.info("Using default configuration")
        return {
            "api": {"host": "0.0.0.0", "port": 8000, "debug": False, "cors_origins": ["*"]},
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
            "safety": {
                "anti_hallucination": True,
                "source_verification": True,
                "bias_filter": True,
                "fallback_message": "I do not have enough data to answer accurately.",
            },
            "memory": {
                "type": "mock",
                "vector_db": {
                    "type": "faiss",
                    "dimension": 1536,
                    "index_path": "data/vector_index",
                },
            },
            "knowledge": {"type": "mock", "sources": []},
            "model_providers": {
                "default": "openai",
                "openai": {"api_key_env": "OPENAI_API_KEY", "model": "gpt-4"},
            },
            "mode": {"type": "mock", "production_ready": False},
        }

    def _validate_config(self, config: Dict[str, Any]) -> None:
        """
        Validate the configuration against the expected schema.

        Args:
            config: The configuration to validate
        """
        # Ensure required sections exist
        required_sections = ["api", "logging", "safety", "memory", "knowledge"]
        for section in required_sections:
            if section not in config:
                logger.warning(f"Missing required configuration section: {section}")
                config[section] = self._get_default_config()[section]

        # Validate safety settings
        safety = config.get("safety", {})
        if not isinstance(safety, dict):
            logger.warning("Safety configuration is not a dictionary")
            config["safety"] = self._get_default_config()["safety"]
        else:
            # Ensure required safety settings
            for key in ["anti_hallucination", "source_verification", "bias_filter"]:
                if key not in safety:
                    logger.warning(f"Missing required safety setting: {key}")
                    safety[key] = self._get_default_config()["safety"][key]

    def _apply_env_overrides(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply environment variable overrides to the configuration.

        Args:
            config: The configuration to override

        Returns:
            The configuration with environment overrides applied
        """
        # API settings
        if "API_HOST" in os.environ:
            config["api"]["host"] = os.environ["API_HOST"]
        if "API_PORT" in os.environ:
            config["api"]["port"] = int(os.environ["API_PORT"])
        if "API_DEBUG" in os.environ:
            config["api"]["debug"] = os.environ["API_DEBUG"].lower() == "true"

        # Logging settings
        if "LOG_LEVEL" in os.environ:
            config["logging"]["level"] = os.environ["LOG_LEVEL"]

        # Mode settings
        if "FINCONNECTAI_MODE_TYPE" in os.environ:
            if "mode" not in config:
                config["mode"] = {}
            config["mode"]["type"] = os.environ["FINCONNECTAI_MODE_TYPE"]
        if "FINCONNECTAI_PRODUCTION_READY" in os.environ:
            if "mode" not in config:
                config["mode"] = {}
            config["mode"]["production_ready"] = (
                os.environ["FINCONNECTAI_PRODUCTION_READY"].lower() == "true"
            )

        return config
