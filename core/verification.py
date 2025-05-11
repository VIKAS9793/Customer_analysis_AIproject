from typing import Dict, Any, List, TypeVar, Generic
import logging
from dataclasses import dataclass
from datetime import datetime
import requests

logger = logging.getLogger(__name__)

@dataclass
class FeatureVerification:
    """Verification data for a feature."""
    name: str
    source: str
    verification_date: str
    evidence: List[str]
    status: str = "pending"
    notes: str = ""


class FeatureVerifier:
    """Verifies that features are based on real-world implementations."""
    
    def __init__(self):
        self.verified_features = {}
        self.known_sources = {
            "security": [
                "https://docs.aws.amazon.com/",
                "https://cloud.google.com/security/",
                "https://azure.microsoft.com/en-us/security/"
            ],
            "monitoring": [
                "https://prometheus.io/docs/",
                "https://grafana.com/docs/",
                "https://docs.datadoghq.com/"
            ],
            "documentation": [
                "https://docs.google.com/",
                "https://confluence.atlassian.com/",
                "https://readthedocs.org/"
            ]
        }
    
    def verify_feature(self, feature: Dict[str, Any]) -> FeatureVerification:
        """Verify that a feature is based on real-world implementation.
        
        Args:
            feature: Feature to verify
            
        Returns:
            FeatureVerification object
        """
        verification = FeatureVerification(
            name=feature.get("name", "unknown"),
            source=feature.get("source", "unknown"),
            verification_date=datetime.now().isoformat(),
            evidence=[],
            status="pending"
        )
        
        # Check if source is valid
        if not self._is_valid_source(feature.get("source")):
            verification.status = "invalid"
            verification.notes = "Invalid source provided"
            return verification
            
        # Verify implementation
        try:
            evidence = self._gather_evidence(feature)
            if evidence:
                verification.evidence = evidence
                verification.status = "verified"
                verification.notes = "Feature verified with real-world evidence"
            else:
                verification.status = "unverified"
                verification.notes = "No real-world evidence found"
        except Exception as e:
            verification.status = "error"
            verification.notes = f"Verification failed: {str(e)}"
            
        return verification
    
    def _is_valid_source(self, source: str) -> bool:
        """Check if source is a known, verifiable source."""
        if not source:
            return False
            
        for category, sources in self.known_sources.items():
            if source in sources:
                return True
        
        # Check if source is a valid URL
        try:
            response = requests.head(source, timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def _gather_evidence(self, feature: Dict[str, Any]) -> List[str]:
        """Gather evidence that the feature exists in real-world implementations."""
        evidence = []
        
        # Check official documentation
        if feature.get("documentation_url"):
            try:
                response = requests.get(feature["documentation_url"])
                if response.status_code == 200:
                    evidence.append(f"Documentation verified: {feature['documentation_url']}")
            except:
                pass
        
        # Check existing implementations
        if feature.get("implementation_url"):
            try:
                response = requests.get(feature["implementation_url"])
                if response.status_code == 200:
                    evidence.append(f"Implementation verified: {feature['implementation_url']}")
            except:
                pass
        
        return evidence
    
    def verify_all_features(self, features: List[Dict[str, Any]]) -> Dict[str, FeatureVerification]:
        """Verify multiple features at once."""
        results = {}
        for feature in features:
            verification = self.verify_feature(feature)
            results[feature.get("name", "unknown")] = verification
        return results
