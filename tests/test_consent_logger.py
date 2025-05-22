"""
Tests for the consent logging system
"""

import pytest

from auth.consent_logger import ConsentLogger


@pytest.fixture
def logger(tmp_path):
    log_file = tmp_path / "test_consent.json"
    return ConsentLogger(str(log_file))


def test_log_consent(logger):
    """Test basic consent logging."""
    logger.log_consent(
        user_id="user123", action="opt-in", feature="fraud_analysis", metadata={"source": "web"}
    )

    logs = logger._read_logs()
    assert len(logs) == 1
    assert logs[0]["user_id"] == "user123"
    assert logs[0]["action"] == "opt-in"
    assert logs[0]["feature"] == "fraud_analysis"
    assert logs[0]["metadata"]["source"] == "web"
    assert "timestamp" in logs[0]
    assert logs[0]["version"] == "2.1"


def test_get_consent_status(logger):
    """Test retrieving consent status."""
    # No consent yet
    assert not logger.get_user_consent_status("user123", "fraud_analysis")

    # Add opt-in
    logger.log_consent("user123", "opt-in", "fraud_analysis")
    assert logger.get_user_consent_status("user123", "fraud_analysis")

    # Revoke consent
    logger.log_consent("user123", "revoke", "fraud_analysis")
    assert not logger.get_user_consent_status("user123", "fraud_analysis")


def test_multiple_features(logger):
    """Test consent tracking for multiple features."""
    logger.log_consent("user123", "opt-in", "fraud_analysis")
    logger.log_consent("user123", "deny", "marketing")

    assert logger.get_user_consent_status("user123", "fraud_analysis")
    assert not logger.get_user_consent_status("user123", "marketing")


def test_multiple_users(logger):
    """Test consent tracking for multiple users."""
    logger.log_consent("user1", "opt-in", "fraud_analysis")
    logger.log_consent("user2", "deny", "fraud_analysis")

    assert logger.get_user_consent_status("user1", "fraud_analysis")
    assert not logger.get_user_consent_status("user2", "fraud_analysis")
