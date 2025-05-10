from datetime import datetime
from typing import Dict, Any, Optional

class ModelVersionManager:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.current_version = "1.0.0"
        self.model_history = {}

    def register_model(self, model_info: Dict[str, Any]) -> str:
        """Register a new model version."""
        version = model_info.get("version", self.current_version)
        self.model_history[version] = {
            **model_info,
            "registered_at": datetime.now().isoformat()
        }
        return version

    def get_model_info(self, version: Optional[str] = None) -> Dict[str, Any]:
        """Get information about a specific model version."""
        version = version or self.current_version
        return self.model_history.get(version, {})
