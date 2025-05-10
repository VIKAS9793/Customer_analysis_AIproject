from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
import json
from dataclasses import dataclass
import boto3
from google.cloud import securitycenter_v1
from azure.identity import DefaultAzureCredential
from azure.mgmt.security import SecurityCenter

logger = logging.getLogger(__name__)

@dataclass
class CloudSecurityEvent:
    """Represents a security event from cloud providers."""
    provider: str
    event_id: str
    timestamp: str
    severity: str
    details: Dict[str, Any]


class CloudSecurityIntegration:
    """
    Cloud provider security integration.
    
    This class implements security event collection and processing for multiple cloud providers.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize cloud security integration.
        
        Args:
            config: Configuration containing cloud provider credentials and settings
        """
        self.config = config
        self.integrations = {}
        
        # Initialize cloud provider clients
        if config.get("aws_enabled"):
            self.integrations["aws"] = self._initialize_aws()
        
        if config.get("gcp_enabled"):
            self.integrations["gcp"] = self._initialize_gcp()
        
        if config.get("azure_enabled"):
            self.integrations["azure"] = self._initialize_azure()
    
    def _initialize_aws(self) -> Dict[str, Any]:
        """Initialize AWS security integration."""
        session = boto3.Session(
            aws_access_key_id=self.config["aws"]["access_key"],
            aws_secret_access_key=self.config["aws"]["secret_key"],
            region_name=self.config["aws"]["region"]
        )
        
        return {
            "client": session.client("securityhub"),
            "enabled": True
        }
    
    def _initialize_gcp(self) -> Dict[str, Any]:
        """Initialize GCP security integration."""
        client = securitycenter_v1.SecurityCenterClient()
        return {
            "client": client,
            "enabled": True
        }
    
    def _initialize_azure(self) -> Dict[str, Any]:
        """Initialize Azure security integration."""
        credential = DefaultAzureCredential()
        client = SecurityCenter(credential)
        return {
            "client": client,
            "enabled": True
        }
    
    def collect_security_events(self) -> List[CloudSecurityEvent]:
        """
        Collect security events from all configured cloud providers.
        
        Returns:
            List of CloudSecurityEvent objects
        """
        events = []
        
        # Collect AWS events
        if "aws" in self.integrations:
            aws_events = self._collect_aws_events()
            events.extend(aws_events)
            
        # Collect GCP events
        if "gcp" in self.integrations:
            gcp_events = self._collect_gcp_events()
            events.extend(gcp_events)
            
        # Collect Azure events
        if "azure" in self.integrations:
            azure_events = self._collect_azure_events()
            events.extend(azure_events)
            
        return events
    
    def _collect_aws_events(self) -> List[CloudSecurityEvent]:
        """Collect security events from AWS Security Hub."""
        client = self.integrations["aws"]["client"]
        
        try:
            response = client.get_findings()
            events = []
            for finding in response["Findings"]:
                event = CloudSecurityEvent(
                    provider="aws",
                    event_id=finding["Id"],
                    timestamp=finding["CreatedAt"],
                    severity=finding["Severity"]["Label"].lower(),
                    details=finding
                )
                events.append(event)
            
            return events
            
        except Exception as e:
            logger.error(f"Error collecting AWS events: {str(e)}")
            return []
    
    def _collect_gcp_events(self) -> List[CloudSecurityEvent]:
        """Collect security events from GCP Security Command Center."""
        client = self.integrations["gcp"]["client"]
        
        try:
            parent = f"organizations/{self.config['gcp']['organization_id']}"
            findings = client.list_findings(parent=parent)
            
            events = []
            for finding in findings:
                event = CloudSecurityEvent(
                    provider="gcp",
                    event_id=finding.name,
                    timestamp=finding.create_time.isoformat(),
                    severity=finding.severity.lower(),
                    details=finding
                )
                events.append(event)
            
            return events
            
        except Exception as e:
            logger.error(f"Error collecting GCP events: {str(e)}")
            return []
    
    def _collect_azure_events(self) -> List[CloudSecurityEvent]:
        """Collect security events from Azure Security Center."""
        client = self.integrations["azure"]["client"]
        
        try:
            alerts = client.alerts.list()
            
            events = []
            for alert in alerts:
                event = CloudSecurityEvent(
                    provider="azure",
                    event_id=alert.name,
                    timestamp=alert.properties.start_time_utc.isoformat(),
                    severity=alert.properties.severity.lower(),
                    details=alert.properties
                )
                events.append(event)
            
            return events
            
        except Exception as e:
            logger.error(f"Error collecting Azure events: {str(e)}")
            return []
