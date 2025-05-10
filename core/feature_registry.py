from typing import Dict, Any, List, TypeVar, Generic
import logging
from dataclasses import dataclass
from datetime import datetime
import json

logger = logging.getLogger(__name__)

@dataclass
class Feature:
    """Represents a verified feature."""
    name: str
    description: str
    source: str
    verification_status: str
    verification_date: str
    evidence: List[str]
    implementation_status: str = "pending"
    tags: List[str] = None


class FeatureRegistry:
    """Registry for verified features."""
    
    def __init__(self):
        self.features = {}
        self.verified_sources = {
            "security": [
                "AWS Security Best Practices",
                "Google Cloud Security Documentation",
                "Microsoft Azure Security Documentation"
            ],
            "monitoring": [
                "Prometheus Documentation",
                "Grafana Documentation",
                "Datadog Documentation"
            ],
            "documentation": [
                "Google Docs API",
                "Confluence API",
                "ReadTheDocs API"
            ]
        }
    
    def register_feature(self, feature_data: Dict[str, Any]) -> Feature:
        """Register a new feature after verification.
        
        Args:
            feature_data: Feature data to register
            
        Returns:
            Registered Feature object
        
        Raises:
            ValueError: If feature is not verified
        """
        if not feature_data.get("verification_status") == "verified":
            raise ValueError("Feature must be verified before registration")
            
        feature = Feature(
            name=feature_data["name"],
            description=feature_data["description"],
            source=feature_data["source"],
            verification_status=feature_data["verification_status"],
            verification_date=feature_data["verification_date"],
            evidence=feature_data["evidence"],
            tags=feature_data.get("tags", [])
        )
        
        self.features[feature.name] = feature
        return feature
    
    def get_verified_features(self) -> List[Feature]:
        """Get all verified features."""
        return [f for f in self.features.values() if f.verification_status == "verified"]
    
    def verify_source(self, source: str) -> bool:
        """Verify if a source is valid and documented.
        
        Args:
            source: Source to verify
            
        Returns:
            True if source is verified, False otherwise
        """
        for category, sources in self.verified_sources.items():
            if source in sources:
                return True
        
        # Check if source exists in documentation
        try:
            with open("docs/sources.json", "r") as f:
                sources = json.load(f)
                return source in sources
        except:
            return False
    
    def export_registry(self, filename: str = "features_registry.json") -> None:
        """Export the feature registry to a JSON file.
        
        Args:
            filename: Output filename
        """
        features = []
        for feature in self.features.values():
            features.append({
                "name": feature.name,
                "description": feature.description,
                "source": feature.source,
                "verification_status": feature.verification_status,
                "verification_date": feature.verification_date,
                "evidence": feature.evidence,
                "tags": feature.tags
            })
            
        with open(filename, "w") as f:
            json.dump(features, f, indent=2)
