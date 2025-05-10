"""
Centralized Configuration Management System

This module provides a unified way to manage all business-specific configurations.
Businesses must customize these configurations according to their requirements.
"""

import yaml
import os
from typing import Dict, Any, Optional
import logging
from .business_config_interface import BusinessConfigInterface

logger = logging.getLogger(__name__)

class ConfigError(Exception):
    """Raised when configuration validation fails"""
    pass

class ConfigManager:
    """Centralized configuration management system
    
    Note: This is a foundation configuration system. Businesses MUST:
    1. Implement their own secrets management system
    2. Configure environment-specific settings
    3. Implement their own key management system
    4. Set up their own monitoring and alerting
    5. Customize security settings according to their policies
    """
    
    def __init__(self, environment: str = 'development', 
                 business_config: Optional[BusinessConfigInterface] = None):
        """
        Initialize the configuration manager.
        
        Args:
            environment: Environment name (development, staging, production)
            business_config: Optional business-specific configuration interface
            
        Note: All configuration values must be customized by businesses according to their requirements.
        Default values shown here are for demonstration purposes only.
        """
        self.environment = environment
        self.business_config = business_config or self._create_default_business_config()
        self.config = self._load_config()
        self._validate_config()
        
        # Business-specific initialization
        self._initialize_business_configurations()
        
    def _create_default_business_config(self) -> BusinessConfigInterface:
        """Create default business configuration interface"""
        class DefaultBusinessConfig(BusinessConfigInterface):
            def get_secrets(self) -> Dict[str, Any]:
                raise NotImplementedError("Business must implement get_secrets")
            
            def get_performance_settings(self) -> Dict[str, Any]:
                raise NotImplementedError("Business must implement get_performance_settings")
            
            def get_monitoring_config(self) -> Dict[str, Any]:
                raise NotImplementedError("Business must implement get_monitoring_config")
            
            def get_security_config(self) -> Dict[str, Any]:
                raise NotImplementedError("Business must implement get_security_config")
            
            def get_customization_examples(self, section: str) -> Dict[str, Any]:
                raise NotImplementedError("Business must implement get_customization_examples")
        
        return DefaultBusinessConfig()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file or business-specific source
        
        Note: Businesses MUST implement their own configuration loading strategy.
        This could include:
        - Environment-based configuration
        - Secrets management integration
        - Configuration encryption
        - Version control integration
        """
        # First try to load from business-specific configuration
        if self.business_config:
            try:
                return self.business_config.get_customization_examples('all')
            except NotImplementedError:
                pass
        
        # Fall back to YAML file
        config_path = os.path.join(os.path.dirname(__file__), 'business_config.yaml')
        
        if not os.path.exists(config_path):
            raise ConfigError("""
            Business configuration file not found. Please:
            1. Create business_config.yaml
            2. Implement your own configuration loading strategy
            3. Set up environment-specific configurations
            4. Configure secrets management
            """)
            
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config
        
    def _validate_config(self):
        """Validate configuration values
        
        Note: Businesses MUST implement their own validation rules based on:
        - Security policies
        - Compliance requirements
        - Performance requirements
        - Business-specific constraints
        """
        required_sections = [
            'security',
            'compliance',
            'authentication',
            'monitoring',
            'data_processing',
            'performance',
            'secrets_management'
        ]
        
        # Validate required sections
        for section in required_sections:
            if section not in self.config:
                raise ConfigError(f"Missing required configuration section: {section}")
        
        # Validate security configuration
        security_config = self.config.get('security', {})
        if not security_config.get('encryption', {}).get('key_management_system'):
            raise ConfigError("Security configuration must specify key management system")
        
        # Validate compliance configuration
        compliance_config = self.config.get('compliance', {})
        if not compliance_config.get('standards'):
            raise ConfigError("Compliance configuration must specify regulatory standards")
        
        # Validate secrets management
        if not self.config.get('secrets_management', {}).get('provider'):
            raise ConfigError("Configuration must specify secrets management provider")
        
        # Validate performance settings
        performance_config = self.config.get('performance', {})
        if not performance_config.get('cache_settings'):
            raise ConfigError("Performance configuration must include cache settings")
        if not performance_config.get('rate_limits'):
            raise ConfigError("Performance configuration must include rate limits")
                
    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration"""
        return self.config.get('security', {})
        
    def get_compliance_config(self) -> Dict[str, Any]:
        """Get compliance configuration"""
        return self.config.get('compliance', {})
        
    def get_auth_config(self) -> Dict[str, Any]:
        """Get authentication configuration"""
        return self.config.get('authentication', {})
        
    def get_monitoring_config(self) -> Dict[str, Any]:
        """Get monitoring configuration"""
        return self.config.get('monitoring', {})
        
    def get_data_processing_config(self) -> Dict[str, Any]:
        """Get data processing configuration"""
        return self.config.get('data_processing', {})
        
    def validate_business_requirements(self) -> None:
        """Validate that business requirements are met"""
        # This method should be customized by businesses
        # to validate their specific requirements
        pass
        
    def get_config(self, section: str, key: str, default: Optional[Any] = None) -> Any:
        """Get a specific configuration value"""
        try:
            return self.config.get(section, {}).get(key, default)
        except KeyError:
            if default is not None:
                return default
            raise ConfigError(f"Configuration key not found: {section}.{key}")

# Create a singleton instance
config_manager = ConfigManager()

# Example usage:
# security_config = config_manager.get_security_config()
# compliance_config = config_manager.get_compliance_config()
# auth_config = config_manager.get_auth_config()
