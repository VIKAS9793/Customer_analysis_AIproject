"""
Tests for the mock core banking API connector
"""

import json

import pytest

from connectors.mock_core_api import CoreBankingConnector


@pytest.fixture
def connector(tmp_path):
    return CoreBankingConnector(log_dir=str(tmp_path))


def test_get_account_info_success(connector):
    """Test successful account info retrieval."""
    response = connector.get_account_info("1001")
    assert "account_id" in response
    assert "balance" in response
    assert "status" in response
    assert "timestamp" in response


def test_get_account_info_error(connector):
    """Test error handling for invalid account."""
    with pytest.raises(ValueError):
        connector.get_account_info("9999")


def test_check_transaction_history(connector):
    """Test transaction history retrieval."""
    response = connector.check_transaction_history("1001")
    assert "account_id" in response
    assert "transaction_count" in response
    assert "total_debit" in response
    assert "total_credit" in response
    assert "timestamp" in response


def test_response_logging(connector, tmp_path):
    """Test that responses are properly logged."""
    # Generate some activity
    try:
        connector.get_account_info("1001")
        connector.check_transaction_history("1001")
        connector.get_account_info("9999")  # This will fail
    except ValueError:
        pass  # Expected for invalid account

    # Check log file
    log_file = tmp_path / "integration_test_log.json"
    assert log_file.exists()

    with open(log_file) as f:
        logs = json.load(f)

    # Verify log structure
    assert len(logs) >= 3  # Should have at least 3 log entries
    for entry in logs:
        assert "timestamp" in entry
        assert "operation" in entry
        assert "status" in entry
        assert "data" in entry
        assert entry["status"] in ["success", "error", "timeout"]
