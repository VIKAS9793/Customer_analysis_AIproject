"""
Environment Utilities - Utilities for handling environment variables.

This module provides utilities for loading and accessing environment variables
and configuration settings.
"""

import logging
import os
from typing import Any, Dict, Optional

from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class EnvironmentManager:
    """
    Manager for environment variables and configuration.

    This class provides methods for loading and accessing environment variables
    and configuration settings.
    """

    def __init__(self, env_file: Optional[str] = None):
        """
        Initialize an environment manager.

        Args:
            env_file: Optional path to .env file
        """
        self.env_file = env_file or os.path.join(os.getcwd(), ".env")
        self.env_loaded = False
        self.env_vars = {}

        # Load environment variables
        self.load_env()

        logger.info("Initialized environment manager")

    def load_env(self) -> bool:
        """
        Load environment variables from .env file.

        Returns:
            True if environment variables were loaded, False otherwise
        """
        try:
            # Check if .env file exists
            if os.path.exists(self.env_file):
                # Load environment variables from .env file
                load_dotenv(self.env_file)
                self.env_loaded = True
                logger.info(f"Loaded environment variables from {self.env_file}")
            else:
                logger.warning(f"Environment file not found: {self.env_file}")

            # Store environment variables in dictionary
            self.env_vars = dict(os.environ)

            return self.env_loaded
        except Exception as e:
            logger.error(f"Error loading environment variables: {e}")
            return False

    def get_env(self, key: str, default: Any = None) -> Any:
        """
        Get an environment variable.

        Args:
            key: The environment variable key
            default: Default value if key is not found

        Returns:
            The environment variable value, or default if not found
        """
        return os.environ.get(key, default)

    def get_bool_env(self, key: str, default: bool = False) -> bool:
        """
        Get a boolean environment variable.

        Args:
            key: The environment variable key
            default: Default value if key is not found

        Returns:
            The environment variable value as a boolean, or default if not found
        """
        value = self.get_env(key)
        if value is None:
            return default

        return value.lower() in ["true", "yes", "y", "1", "on"]

    def get_int_env(self, key: str, default: int = 0) -> int:
        """
        Get an integer environment variable.

        Args:
            key: The environment variable key
            default: Default value if key is not found or not an integer

        Returns:
            The environment variable value as an integer, or default if not found or not an integer
        """
        value = self.get_env(key)
        if value is None:
            return default

        try:
            return int(value)
        except ValueError:
            logger.warning(f"Environment variable {key} is not an integer: {value}")
            return default

    def get_float_env(self, key: str, default: float = 0.0) -> float:
        """
        Get a float environment variable.

        Args:
            key: The environment variable key
            default: Default value if key is not found or not a float

        Returns:
            The environment variable value as a float, or default if not found or not a float
        """
        value = self.get_env(key)
        if value is None:
            return default

        try:
            return float(value)
        except ValueError:
            logger.warning(f"Environment variable {key} is not a float: {value}")
            return default

    def get_list_env(self, key: str, default: Optional[list] = None, separator: str = ",") -> list:
        """
        Get a list environment variable.

        Args:
            key: The environment variable key
            default: Default value if key is not found
            separator: Separator for list items

        Returns:
            The environment variable value as a list, or default if not found
        """
        value = self.get_env(key)
        if value is None:
            return default or []

        return [item.strip() for item in value.split(separator)]

    def get_dict_env(self, prefix: str) -> Dict[str, str]:
        """
        Get environment variables with a specific prefix as a dictionary.

        Args:
            prefix: The prefix for environment variables

        Returns:
            Dictionary of environment variables with the prefix
        """
        result = {}
        prefix_upper = prefix.upper()

        for key, value in self.env_vars.items():
            if key.startswith(prefix_upper):
                # Remove prefix and convert to lowercase
                dict_key = key[len(prefix_upper) :].lower()
                result[dict_key] = value

        return result

    def set_env(self, key: str, value: str) -> None:
        """
        Set an environment variable.

        Args:
            key: The environment variable key
            value: The environment variable value
        """
        os.environ[key] = value
        self.env_vars[key] = value

    def is_production(self) -> bool:
        """
        Check if the environment is production.

        Returns:
            True if the environment is production, False otherwise
        """
        env = self.get_env("ENV", "development").lower()
        return env in ["production", "prod"]

    def is_development(self) -> bool:
        """
        Check if the environment is development.

        Returns:
            True if the environment is development, False otherwise
        """
        env = self.get_env("ENV", "development").lower()
        return env in ["development", "dev"]

    def is_test(self) -> bool:
        """
        Check if the environment is test.

        Returns:
            True if the environment is test, False otherwise
        """
        env = self.get_env("ENV", "development").lower()
        return env in ["test", "testing"]


# Create a global instance for convenience
env_manager = EnvironmentManager()


def get_env(key: str, default: Any = None) -> Any:
    """
    Get an environment variable.

    Args:
        key: The environment variable key
        default: Default value if key is not found

    Returns:
        The environment variable value, or default if not found
    """
    return env_manager.get_env(key, default)


def get_bool_env(key: str, default: bool = False) -> bool:
    """
    Get a boolean environment variable.

    Args:
        key: The environment variable key
        default: Default value if key is not found

    Returns:
        The environment variable value as a boolean, or default if not found
    """
    return env_manager.get_bool_env(key, default)


def get_int_env(key: str, default: int = 0) -> int:
    """
    Get an integer environment variable.

    Args:
        key: The environment variable key
        default: Default value if key is not found or not an integer

    Returns:
        The environment variable value as an integer, or default if not found or not an integer
    """
    return env_manager.get_int_env(key, default)


def get_float_env(key: str, default: float = 0.0) -> float:
    """
    Get a float environment variable.

    Args:
        key: The environment variable key
        default: Default value if key is not found or not a float

    Returns:
        The environment variable value as a float, or default if not found or not a float
    """
    return env_manager.get_float_env(key, default)


def get_list_env(key: str, default: Optional[list] = None, separator: str = ",") -> list:
    """
    Get a list environment variable.

    Args:
        key: The environment variable key
        default: Default value if key is not found
        separator: Separator for list items

    Returns:
        The environment variable value as a list, or default if not found
    """
    return env_manager.get_list_env(key, default, separator)


def is_production() -> bool:
    """
    Check if the environment is production.

    Returns:
        True if the environment is production, False otherwise
    """
    return env_manager.is_production()


def is_development() -> bool:
    """
    Check if the environment is development.

    Returns:
        True if the environment is development, False otherwise
    """
    return env_manager.is_development()


def is_test() -> bool:
    """
    Check if the environment is test.

    Returns:
        True if the environment is test, False otherwise
    """
    return env_manager.is_test()
