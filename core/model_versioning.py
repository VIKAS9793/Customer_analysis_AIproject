"""
Model Versioning System

This module manages versioning of AI models, including tracking, validation,
and version-specific configurations.
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ModelVersion:
    def __init__(self, model_id: str, version: str, config: Dict[str, Any]):
        self.model_id = model_id
        self.version = version
        self.config = config
        self.created_at = datetime.now()
        self.last_updated = datetime.now()
        self.status = "active"
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "model_id": self.model_id,
            "version": self.version,
            "config": self.config,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "status": self.status
        }

class ModelVersionManager:
    def __init__(self, version_file: str = "model_versions.json"):
        self.version_file = version_file
        self.versions: Dict[str, Dict[str, ModelVersion]] = {}
        self._load_versions()
        
    def _load_versions(self):
        """Load model versions from file"""
        if os.path.exists(self.version_file):
            with open(self.version_file, 'r') as f:
                data = json.load(f)
                for model_id, versions in data.items():
                    self.versions[model_id] = {}
                    for version, version_data in versions.items():
                        self.versions[model_id][version] = ModelVersion(
                            model_id=model_id,
                            version=version,
                            config=version_data["config"]
                        )
                        self.versions[model_id][version].created_at = datetime.fromisoformat(version_data["created_at"])
                        self.versions[model_id][version].last_updated = datetime.fromisoformat(version_data["last_updated"])
                        self.versions[model_id][version].status = version_data["status"]
    
    def _save_versions(self):
        """Save model versions to file"""
        data = {}
        for model_id, versions in self.versions.items():
            data[model_id] = {}
            for version, model_version in versions.items():
                data[model_id][version] = model_version.to_dict()
        
        with open(self.version_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def register_version(self, model_id: str, version: str, config: Dict[str, Any]) -> None:
        """Register a new model version"""
        if model_id not in self.versions:
            self.versions[model_id] = {}
        
        if version in self.versions[model_id]:
            raise ValueError(f"Version {version} already exists for model {model_id}")
        
        self.versions[model_id][version] = ModelVersion(model_id, version, config)
        self._save_versions()
        logger.info(f"Registered new model version: {model_id} v{version}")
    
    def get_version(self, model_id: str, version: str) -> Optional[ModelVersion]:
        """Get a specific model version"""
        if model_id in self.versions and version in self.versions[model_id]:
            return self.versions[model_id][version]
        return None
    
    def get_latest_version(self, model_id: str) -> Optional[ModelVersion]:
        """Get the latest active version of a model"""
        if model_id not in self.versions:
            return None
            
        active_versions = [v for v in self.versions[model_id].values() 
                         if v.status == "active"]
        if not active_versions:
            return None
            
        return max(active_versions, key=lambda v: v.last_updated)
    
    def update_version_status(self, model_id: str, version: str, status: str) -> None:
        """Update the status of a model version"""
        if model_id in self.versions and version in self.versions[model_id]:
            self.versions[model_id][version].status = status
            self.versions[model_id][version].last_updated = datetime.now()
            self._save_versions()
            logger.info(f"Updated status of {model_id} v{version} to {status}")
    
    def get_all_versions(self, model_id: str) -> Dict[str, ModelVersion]:
        """Get all versions of a model"""
        return self.versions.get(model_id, {})
    
    def validate_version(self, model_id: str, version: str) -> bool:
        """Validate if a version is valid and active"""
        version_obj = self.get_version(model_id, version)
        return version_obj is not None and version_obj.status == "active"
