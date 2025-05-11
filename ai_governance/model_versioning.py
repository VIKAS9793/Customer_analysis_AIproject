"""
Model Versioning Implementation

This module implements model versioning and tracking for the FinConnectAI system.
"""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
import json
from pathlib import Path
import hashlib

class ModelVersioning:
    def __init__(self, config: Dict[str, Any]):
        """Initialize model versioning with configuration"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Version control configuration
        self.version_store = config.get("version_store", "models/versions/")
        self.metadata_store = config.get("metadata_store", "models/metadata/")
        self.max_versions = config.get("max_versions", 10)
        
        # Initialize state
        self.current_version = None
        self.version_history = {}
        self.load_version_history()
        
    def register_model_version(self, model_data: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new model version"""
        try:
            # Generate version info
            version_info = self._create_version_info(model_data)
            
            # Save model version
            self._save_model_version(version_info, model_data)
            
            # Update version history
            self.version_history[version_info["version_id"]] = version_info
            self._save_version_history()
            
            # Update current version
            self.current_version = version_info["version_id"]
            
            return version_info
        except Exception as e:
            self.logger.error(f"Model version registration failed: {str(e)}")
            raise
            
    def _create_version_info(self, model_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create version information for a model"""
        timestamp = datetime.now().isoformat()
        version_id = self._generate_version_id(model_data, timestamp)
        
        return {
            "version_id": version_id,
            "timestamp": timestamp,
            "model_type": model_data.get("type", "unknown"),
            "model_hash": self._calculate_model_hash(model_data),
            "parameters": model_data.get("parameters", {}),
            "metrics": model_data.get("metrics", {}),
            "dependencies": model_data.get("dependencies", []),
            "training_data": {
                "dataset_id": model_data.get("dataset_id"),
                "dataset_version": model_data.get("dataset_version")
            }
        }
        
    def _generate_version_id(self, model_data: Dict[str, Any], timestamp: str) -> str:
        """Generate a unique version ID"""
        components = [
            model_data.get("type", "unknown"),
            timestamp,
            model_data.get("dataset_version", "unknown")
        ]
        return hashlib.sha256("_".join(components).encode()).hexdigest()[:12]
        
    def _calculate_model_hash(self, model_data: Dict[str, Any]) -> str:
        """Calculate hash of model data"""
        return hashlib.sha256(json.dumps(model_data, sort_keys=True).encode()).hexdigest()
        
    def _save_model_version(self, version_info: Dict[str, Any], model_data: Dict[str, Any]) -> None:
        """Save model version data"""
        try:
            version_path = Path(self.version_store) / version_info["version_id"]
            version_path.mkdir(parents=True, exist_ok=True)
            
            # Save model data
            with open(version_path / "model.json", "w") as f:
                json.dump(model_data, f)
                
            # Save version info
            with open(version_path / "version_info.json", "w") as f:
                json.dump(version_info, f)
        except Exception as e:
            self.logger.error(f"Failed to save model version: {str(e)}")
            raise
            
    def load_version_history(self) -> None:
        """Load version history from storage"""
        try:
            history_path = Path(self.metadata_store) / "version_history.json"
            if history_path.exists():
                with open(history_path, "r") as f:
                    self.version_history = json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load version history: {str(e)}")
            raise
            
    def _save_version_history(self) -> None:
        """Save version history to storage"""
        try:
            history_path = Path(self.metadata_store) / "version_history.json"
            history_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(history_path, "w") as f:
                json.dump(self.version_history, f)
        except Exception as e:
            self.logger.error(f"Failed to save version history: {str(e)}")
            raise
            
    def get_model_version(self, version_id: str) -> Optional[Dict[str, Any]]:
        """Get model version information"""
        try:
            if version_id not in self.version_history:
                return None
                
            version_path = Path(self.version_store) / version_id
            if not version_path.exists():
                return None
                
            with open(version_path / "version_info.json", "r") as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to get model version: {str(e)}")
            raise
            
    def list_model_versions(self) -> List[Dict[str, Any]]:
        """List all model versions"""
        return list(self.version_history.values())
        
    def compare_versions(self, version_id1: str, version_id2: str) -> Dict[str, Any]:
        """Compare two model versions"""
        try:
            v1 = self.get_model_version(version_id1)
            v2 = self.get_model_version(version_id2)
            
            if not v1 or not v2:
                raise ValueError("One or both versions not found")
                
            return {
                "metrics_diff": self._compare_metrics(v1["metrics"], v2["metrics"]),
                "parameter_diff": self._compare_parameters(v1["parameters"], v2["parameters"]),
                "dependency_diff": self._compare_dependencies(v1["dependencies"], v2["dependencies"])
            }
        except Exception as e:
            self.logger.error(f"Version comparison failed: {str(e)}")
            raise
            
    def _compare_metrics(self, metrics1: Dict[str, Any], metrics2: Dict[str, Any]) -> Dict[str, Any]:
        """Compare metrics between versions"""
        all_metrics = set(metrics1.keys()) | set(metrics2.keys())
        return {
            metric: {
                "v1": metrics1.get(metric),
                "v2": metrics2.get(metric),
                "diff": metrics2.get(metric, 0) - metrics1.get(metric, 0)
            }
            for metric in all_metrics
        }
            
    def _compare_parameters(self, params1: Dict[str, Any], params2: Dict[str, Any]) -> Dict[str, Any]:
        """Compare parameters between versions"""
        all_params = set(params1.keys()) | set(params2.keys())
        return {
            param: {
                "v1": params1.get(param),
                "v2": params2.get(param),
                "changed": params1.get(param) != params2.get(param)
            }
            for param in all_params
        }
            
    def _compare_dependencies(self, deps1: List[str], deps2: List[str]) -> Dict[str, Any]:
        """Compare dependencies between versions"""
        return {
            "added": list(set(deps2) - set(deps1)),
            "removed": list(set(deps1) - set(deps2)),
            "common": list(set(deps1) & set(deps2))
        }
