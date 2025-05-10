from typing import Dict, Any, Optional
from datetime import datetime

def create_model_provider(provider_type: str, config: Dict[str, Any]):
    """Factory function to create model providers."""
    if provider_type == "local":
        return LocalModelProvider(config)
    elif provider_type == "cloud":
        return CloudModelProvider(config)
    else:
        raise ValueError(f"Unknown provider type: {provider_type}")

class BaseModelProvider:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.last_update = datetime.now()

    def get_model(self, model_id: str) -> Optional[Dict[str, Any]]:
        raise NotImplementedError

class LocalModelProvider(BaseModelProvider):
    def get_model(self, model_id: str) -> Optional[Dict[str, Any]]:
        # Placeholder for actual implementation
        return {
            "model_id": model_id,
            "type": "local",
            "last_updated": self.last_update.isoformat()
        }

class CloudModelProvider(BaseModelProvider):
    def get_model(self, model_id: str) -> Optional[Dict[str, Any]]:
        # Placeholder for actual implementation
        return {
            "model_id": model_id,
            "type": "cloud",
            "last_updated": self.last_update.isoformat()
        }
