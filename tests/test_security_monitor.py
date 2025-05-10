import pytest
from security.security_monitor import SecurityMonitor
from datetime import datetime
import logging
from unittest.mock import patch, MagicMock

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.fixture
def security_monitor():
    """Create a security monitor instance for testing."""
    config = {
        "alert_thresholds": {
            "high_severity": 0.9,
            "medium_severity": 0.7,
            "low_severity": 0.5
        },
        "notification_channels": ["email", "slack"],
        "compliance_standards": ["ISO_27001", "SOC_2"]
    }
    return SecurityMonitor(config)


def test_security_monitor_initialization(security_monitor):
    """Test security monitor initialization."""
    assert isinstance(security_monitor, SecurityMonitor)
    assert security_monitor.config["alert_thresholds"]["high_severity"] == 0.9
    assert len(security_monitor.config["notification_channels"]) == 2


def test_alert_generation(security_monitor):
    """Test alert generation based on real-world scenarios."""
    # Create a high severity event
    event = {
        "type": "authentication_failure",
        "description": "Multiple failed login attempts",
        "count": 15
    }
    
    # Generate alerts
    alerts = security_monitor.detect_security_events([event])
    
    # Verify alert generation
    assert len(alerts) == 1
    assert alerts[0]["severity"] >= 0.9
    assert alerts[0]["type"] == "authentication_failure"


def test_notification_channels(security_monitor):
    """Test notification channel integration."""
    # Mock notification methods
    with patch.object(security_monitor, "_send_email") as mock_email, \
         patch.object(security_monitor, "_send_slack_message") as mock_slack:
        
        # Create an alert
        alert = {
            "type": "authentication_failure",
            "severity": 0.9
        }
        
        # Send notification
        security_monitor._notify_alert(alert)
        
        # Verify notifications were sent
        mock_email.assert_called_once()
        mock_slack.assert_called_once()


def test_compliance_verification(security_monitor):
    """Test compliance verification against standards."""
    # Create a test report
    report = security_monitor.generate_compliance_report()
    
    # Verify compliance standards
    assert "ISO_27001" in report["compliance_standards"]
    assert "SOC_2" in report["compliance_standards"]
    
    # Verify metrics
    assert "security_metrics" in report
    assert "alerts" in report["security_metrics"]
    assert "violations" in report["security_metrics"]


def test_severity_calculation(security_monitor):
    """Test severity calculation based on real-world scenarios."""
    # Test critical event
    critical_event = {
        "type": "data_exfiltration",
        "count": 20
    }
    severity = security_monitor._determine_severity(critical_event)
    assert severity >= 0.9
    
    # Test medium event
    medium_event = {
        "type": "configuration_change",
        "count": 5
    }
    severity = security_monitor._determine_severity(medium_event)
    assert 0.7 <= severity < 0.9


def test_monitoring_metrics(security_monitor):
    """Test monitoring metrics integration."""
    # Create test events
    events = [
        {"type": "authentication_failure", "count": 10},
        {"type": "data_exfiltration", "count": 5}
    ]
    
    # Process events
    security_monitor.detect_security_events(events)
    
    # Verify metrics were updated
    from prometheus_client import Counter
    
    # Verify alert counters
    assert Counter._metrics["security_alerts_total"].samples[0].value > 0
    
    # Verify violation counters
    assert Counter._metrics["security_violations_total"].samples[0].value > 0
