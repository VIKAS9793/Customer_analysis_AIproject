"""
Validation and Sanitization - Utilities for data validation and sanitization.

This module provides utilities for validating and sanitizing user input
to prevent security issues such as injection attacks.
"""

import logging
import re
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class InputValidator:
    """
    Validator for user input.

    This class provides methods for validating user input to ensure it
    meets required constraints and is safe to process.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize an input validator.

        Args:
            config: Optional configuration for the validator
        """
        self.config = config or {}
        self.max_input_length = self.config.get("max_input_length", 4096)
        self.allowed_html_tags = self.config.get(
            "allowed_html_tags", ["p", "br", "b", "i", "ul", "ol", "li"]
        )

        logger.info("Initialized input validator")

    def validate_text_input(self, text: str) -> Dict[str, Any]:
        """
        Validate text input.

        Args:
            text: The text to validate

        Returns:
            Validation result with status and errors
        """
        logger.debug("Validating text input")

        result = {"valid": True, "errors": []}

        # Check if input is empty
        if not text or text.strip() == "":
            result["valid"] = False
            result["errors"].append("Input cannot be empty")

        # Check input length
        if len(text) > self.max_input_length:
            result["valid"] = False
            result["errors"].append(
                f"Input exceeds maximum length of {self.max_input_length} characters"
            )

        # Check for potentially malicious patterns
        if self._contains_script_tags(text):
            result["valid"] = False
            result["errors"].append("Input contains potentially malicious script tags")

        # Check for SQL injection patterns
        if self._contains_sql_injection(text):
            result["valid"] = False
            result["errors"].append("Input contains potential SQL injection patterns")

        return result

    def validate_json_input(self, data: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate JSON input against a schema.

        Args:
            data: The JSON data to validate
            schema: The schema to validate against

        Returns:
            Validation result with status and errors
        """
        logger.debug("Validating JSON input")

        result = {"valid": True, "errors": []}

        # Check required fields
        for field, field_schema in schema.items():
            if field_schema.get("required", False) and field not in data:
                result["valid"] = False
                result["errors"].append(f"Missing required field: {field}")

        # Validate field types and values
        for field, value in data.items():
            if field in schema:
                field_schema = schema[field]
                field_type = field_schema.get("type")

                # Validate type
                if field_type and not self._validate_type(value, field_type):
                    result["valid"] = False
                    result["errors"].append(
                        f"Invalid type for field '{field}': expected {field_type}"
                    )

                # Validate string length
                if field_type == "string" and "max_length" in field_schema:
                    max_length = field_schema["max_length"]
                    if len(value) > max_length:
                        result["valid"] = False
                        result["errors"].append(
                            f"Field '{field}' exceeds maximum length of {max_length} characters"
                        )

                # Validate numeric range
                if field_type in ["integer", "number"] and (
                    "min" in field_schema or "max" in field_schema
                ):
                    if "min" in field_schema and value < field_schema["min"]:
                        result["valid"] = False
                        result["errors"].append(
                            f"Field '{field}' is less than minimum value of {field_schema['min']}"
                        )

                    if "max" in field_schema and value > field_schema["max"]:
                        result["valid"] = False
                        result["errors"].append(
                            f"Field '{field}' is greater than maximum value of {field_schema['max']}"
                        )

                # Validate enum values
                if "enum" in field_schema and value not in field_schema["enum"]:
                    result["valid"] = False
                    result["errors"].append(
                        f"Field '{field}' has invalid value: must be one of {field_schema['enum']}"
                    )

                # Validate pattern
                if field_type == "string" and "pattern" in field_schema:
                    pattern = field_schema["pattern"]
                    if not re.match(pattern, value):
                        result["valid"] = False
                        result["errors"].append(f"Field '{field}' does not match required pattern")
            else:
                # Unknown field
                if not schema.get("allow_unknown_fields", False):
                    result["valid"] = False
                    result["errors"].append(f"Unknown field: {field}")

        return result

    def sanitize_text(self, text: str) -> str:
        """
        Sanitize text input.

        Args:
            text: The text to sanitize

        Returns:
            Sanitized text
        """
        logger.debug("Sanitizing text input")

        # Remove script tags
        sanitized = self._remove_script_tags(text)

        # Remove HTML tags except allowed ones
        sanitized = self._sanitize_html(sanitized)

        # Trim whitespace
        sanitized = sanitized.strip()

        return sanitized

    def sanitize_json(self, data: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize JSON input.

        Args:
            data: The JSON data to sanitize
            schema: The schema to sanitize against

        Returns:
            Sanitized JSON data
        """
        logger.debug("Sanitizing JSON input")

        sanitized = {}

        # Only include fields in schema
        for field, value in data.items():
            if field in schema or schema.get("allow_unknown_fields", False):
                # Sanitize string values
                if isinstance(value, str):
                    sanitized[field] = self.sanitize_text(value)
                # Recursively sanitize nested objects
                elif isinstance(value, dict) and "properties" in schema.get(field, {}):
                    sanitized[field] = self.sanitize_json(value, schema[field]["properties"])
                # Sanitize array items
                elif isinstance(value, list) and "items" in schema.get(field, {}):
                    item_schema = schema[field]["items"]
                    if (
                        "type" in item_schema
                        and item_schema["type"] == "object"
                        and "properties" in item_schema
                    ):
                        sanitized[field] = [
                            self.sanitize_json(item, item_schema["properties"])
                            for item in value
                            if isinstance(item, dict)
                        ]
                    elif "type" in item_schema and item_schema["type"] == "string":
                        sanitized[field] = [
                            self.sanitize_text(item) for item in value if isinstance(item, str)
                        ]
                    else:
                        sanitized[field] = value
                else:
                    sanitized[field] = value

        return sanitized

    def _validate_type(self, value: Any, expected_type: str) -> bool:
        """
        Validate that a value is of the expected type.

        Args:
            value: The value to validate
            expected_type: The expected type

        Returns:
            True if the value is of the expected type, False otherwise
        """
        if expected_type == "string":
            return isinstance(value, str)
        elif expected_type == "integer":
            return isinstance(value, int) and not isinstance(value, bool)
        elif expected_type == "number":
            return isinstance(value, (int, float)) and not isinstance(value, bool)
        elif expected_type == "boolean":
            return isinstance(value, bool)
        elif expected_type == "array":
            return isinstance(value, list)
        elif expected_type == "object":
            return isinstance(value, dict)
        elif expected_type == "null":
            return value is None
        else:
            return True

    def _contains_script_tags(self, text: str) -> bool:
        """
        Check if text contains script tags.

        Args:
            text: The text to check

        Returns:
            True if the text contains script tags, False otherwise
        """
        script_pattern = re.compile(
            r"<\s*script.*?>.*?<\s*/\s*script\s*>", re.IGNORECASE | re.DOTALL
        )
        return bool(script_pattern.search(text))

    def _contains_sql_injection(self, text: str) -> bool:
        """
        Check if text contains SQL injection patterns.

        Args:
            text: The text to check

        Returns:
            True if the text contains SQL injection patterns, False otherwise
        """
        # Simple SQL injection patterns
        sql_patterns = [
            r'(\b|\'|")SELECT(\b|\'|")',
            r'(\b|\'|")INSERT(\b|\'|")',
            r'(\b|\'|")UPDATE(\b|\'|")',
            r'(\b|\'|")DELETE(\b|\'|")',
            r'(\b|\'|")DROP(\b|\'|")',
            r'(\b|\'|")UNION(\b|\'|")',
            r'(\b|\'|")OR\s+1\s*=\s*1(\b|\'|")',
            r'(\b|\'|")AND\s+1\s*=\s*1(\b|\'|")',
            r"--\s*$",
        ]

        for pattern in sql_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True

        return False

    def _remove_script_tags(self, text: str) -> str:
        """
        Remove script tags from text.

        Args:
            text: The text to process

        Returns:
            Text with script tags removed
        """
        script_pattern = re.compile(
            r"<\s*script.*?>.*?<\s*/\s*script\s*>", re.IGNORECASE | re.DOTALL
        )
        return script_pattern.sub("", text)

    def _sanitize_html(self, text: str) -> str:
        """
        Sanitize HTML in text, keeping only allowed tags.

        Args:
            text: The text to sanitize

        Returns:
            Sanitized text
        """
        # If no HTML tags are allowed, remove all tags
        if not self.allowed_html_tags:
            tag_pattern = re.compile(r"<[^>]*>")
            return tag_pattern.sub("", text)

        # Otherwise, remove disallowed tags
        allowed_tags_str = "|".join(self.allowed_html_tags)
        allowed_pattern = re.compile(f"</?({allowed_tags_str})(?:\s[^>]*)?>", re.IGNORECASE)
        tag_pattern = re.compile(r"<[^>]*>")

        # Find all tags
        tags = tag_pattern.findall(text)

        # Replace disallowed tags with empty string
        for tag in tags:
            if not allowed_pattern.match(tag):
                text = text.replace(tag, "")

        return text
