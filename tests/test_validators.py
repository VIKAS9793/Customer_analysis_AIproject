import pytest
from datetime import datetime
from core.validators import Validator, ResponseValidator
from typing import Dict, Any


class TestValidator:
    def test_base_validator_initialization(self):
        """Test base validator initialization."""
        rules = [
            {
                "name": "test_rule",
                "condition": lambda x: True,
                "action": lambda x: None,
                "severity": "info",
                "description": "Test rule description"
            }
        ]
        validator = Validator(rules)
        assert len(validator.rules) == 1

    def test_validation_result_structure(self):
        """Test validation result structure."""
        validator = Validator([])
        result = validator.validate("test")
        assert "valid" in result
        assert "issues" in result
        assert "timestamp" in result


class TestResponseValidator:
    def setup_method(self):
        """Setup response validator for tests."""
        self.validator = ResponseValidator()

    def test_valid_response(self):
        """Test validation of a valid response."""
        response = "Valid response with proper sources and confidence."
        result = self.validator.validate(response)
        assert result["valid"] is True
        assert len(result["issues"]) == 0

    def test_missing_sources(self, monkeypatch):
        """Test response missing valid sources."""
        def mock_has_valid_sources(response):
            return False
        
        monkeypatch.setattr(
            self.validator,
            "_has_valid_sources",
            mock_has_valid_sources
        )
        
        result = self.validator.validate("response")
        assert result["valid"] is False
        assert any(
            issue["rule"] == "source_verification"
            for issue in result["issues"]
        )

    def test_low_confidence(self, monkeypatch):
        """Test response with low confidence."""
        def mock_has_sufficient_confidence(response):
            return False
        
        monkeypatch.setattr(
            self.validator,
            "_has_sufficient_confidence",
            mock_has_sufficient_confidence
        )
        
        result = self.validator.validate("response")
        assert result["valid"] is False
        assert any(
            issue["rule"] == "confidence_check"
            for issue in result["issues"]
        )

    def test_data_inconsistency(self, monkeypatch):
        """Test response inconsistent with data."""
        def mock_is_consistent_with_data(response):
            return False
        
        monkeypatch.setattr(
            self.validator,
            "_is_consistent_with_data",
            mock_is_consistent_with_data
        )
        
        result = self.validator.validate("response")
        assert result["valid"] is False
        assert any(
            issue["rule"] == "data_consistency"
            for issue in result["issues"]
        )

    def test_validation_history(self):
        """Test validation history tracking."""
        response = "Test response"
        result = self.validator.validate(response)
        assert "timestamp" in result
        assert isinstance(result["timestamp"], str)

    def test_severity_levels(self, monkeypatch):
        """Test different severity levels."""
        def mock_validate(response):
            return {
                "valid": False,
                "issues": [
                    {
                        "rule": "test_rule",
                        "severity": "critical",
                        "description": "Test issue"
                    },
                    {
                        "rule": "test_rule2",
                        "severity": "warning",
                        "description": "Test warning"
                    }
                ]
            }
        
        monkeypatch.setattr(
            self.validator,
            "validate",
            mock_validate
        )
        
        result = self.validator.validate("response")
        critical_issues = [i for i in result["issues"] if i["severity"] == "critical"]
        assert len(critical_issues) > 0

    def test_error_handling(self, monkeypatch):
        """Test error handling in validation."""
        def mock_validate(response):
            raise ValueError("Test error")
        
        monkeypatch.setattr(
            self.validator,
            "validate",
            mock_validate
        )
        
        result = self.validator.validate("response")
        assert result["valid"] is False
        assert any(
            "Test error" in issue["description"]
            for issue in result["issues"]
        )
