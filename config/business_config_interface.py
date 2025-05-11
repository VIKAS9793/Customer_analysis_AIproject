"""
Business-specific configuration interface

Note: All business-specific implementations must be provided by the business.
This interface defines the required methods for business-specific configuration.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BusinessConfigInterface(ABC):
    """Interface for business-specific configuration implementations"""
    
    @abstractmethod
    def get_secrets(self) -> Dict[str, Any]:
        """
        Get business-specific secrets.
        
        Note: This must be implemented by the business to provide their own
        secrets management system.
        """
        pass
    
    @abstractmethod
    def get_performance_settings(self) -> Dict[str, Any]:
        """
        Get business-specific performance settings.
        
        Note: Business must implement their own performance thresholds and
        optimization settings.
        """
        pass
    
    @abstractmethod
    def get_monitoring_config(self) -> Dict[str, Any]:
        """
        Get business-specific monitoring configuration.
        
        Note: Business must implement their own monitoring thresholds and
        alerting configurations.
        """
        pass
    
    @abstractmethod
    def get_security_config(self) -> Dict[str, Any]:
        """
        Get business-specific security configuration.
        
        Note: Business must implement their own security policies and
        encryption settings.
        """
        pass
    
    @abstractmethod
    def get_customization_examples(self, section: str) -> Dict[str, Any]:
        """
        Get business-specific customization examples.
        
        Args:
            section: Configuration section to get examples for
            
        Note: Business must provide their own examples for customization.
        """
        pass
