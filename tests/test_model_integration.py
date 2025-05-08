"""
Test cases for AI model integration and versioning
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import os
from core.model_versioning import ModelVersionManager
from core.drift_detector import DriftDetector
from core.model_provider import create_model_provider

TEST_CONFIG = {
    "model": {
        "provider": "anthropic",
        "model": "claude-3.7-sonnet",
        "max_tokens": 1000000,
        "temperature": 0.2
    },
    "model_backup": {
        "provider": "openai",
        "model": "gpt-4.5",
        "max_tokens": 1000000,
        "temperature": 0.2
    }
}

class TestModelVersioning(unittest.TestCase):
    def setUp(self):
        self.version_manager = ModelVersionManager()
        self.version_manager.register_version(
            "fraud_detection",
            "1.0.0",
            TEST_CONFIG["model"]
        )
        self.version_manager.register_version(
            "kyc_verification",
            "1.0.0",
            TEST_CONFIG["model"]
        )
    
    def test_version_registration(self):
        """Test model version registration"""
        version = self.version_manager.get_version("fraud_detection", "1.0.0")
        self.assertIsNotNone(version)
        self.assertEqual(version.version, "1.0.0")
        self.assertEqual(version.config["model"], "claude-3.7-sonnet")
    
    def test_latest_version(self):
        """Test getting latest version"""
        latest = self.version_manager.get_latest_version("fraud_detection")
        self.assertIsNotNone(latest)
        self.assertEqual(latest.version, "1.0.0")
    
    def test_version_status(self):
        """Test version status updates"""
        self.version_manager.update_version_status("fraud_detection", "1.0.0", "inactive")
        version = self.version_manager.get_version("fraud_detection", "1.0.0")
        self.assertEqual(version.status, "inactive")

class TestModelDrift(unittest.TestCase):
    def setUp(self):
        self.drift_detector = DriftDetector()
        self.reference_data = {
            "feature1": [0.1, 0.2, 0.3, 0.4, 0.5],
            "feature2": [1.0, 1.1, 1.2, 1.3, 1.4]
        }
        
        for feature, data in self.reference_data.items():
            self.drift_detector.add_reference_data(feature, data)
    
    def test_drift_detection(self):
        """Test drift detection with different distributions"""
        # Test with similar distribution (should not detect drift)
        similar_data = {
            "feature1": [0.15, 0.25, 0.35, 0.45, 0.55],
            "feature2": [1.05, 1.15, 1.25, 1.35, 1.45]
        }
        
        for feature, data in similar_data.items():
            self.drift_detector.add_current_data(feature, data)
        
        results = self.drift_detector.detect_drift()
        for feature, drifted in results.items():
            self.assertFalse(drifted, f"Drift detected for {feature} when it shouldn't")
        
        # Test with different distribution (should detect drift)
        different_data = {
            "feature1": [10.0, 10.1, 10.2, 10.3, 10.4],
            "feature2": [20.0, 20.1, 20.2, 20.3, 20.4]
        }
        
        self.drift_detector.current_data.clear()
        for feature, data in different_data.items():
            self.drift_detector.add_current_data(feature, data)
        
        results = self.drift_detector.detect_drift()
        for feature, drifted in results.items():
            self.assertTrue(drifted, f"Drift not detected for {feature} when it should")

class TestModelProviderIntegration(unittest.TestCase):
    @patch('core.model_provider.create_model_provider')
    def test_model_switching(self, mock_create):
        """Test model provider switching between primary and backup"""
        mock_primary = MagicMock()
        mock_backup = MagicMock()
        
        # Simulate primary model failing
        mock_primary.generate_text.side_effect = Exception("Primary model failed")
        
        # Create mock providers
        mock_create.side_effect = [
            mock_primary,  # First call should get primary
            mock_backup    # Second call should get backup
        ]
        
        # Create model provider with config
        provider = create_model_provider(TEST_CONFIG)
        
        # First call should use primary
        with self.assertRaises(Exception):
            provider.generate_text("test prompt")
        
        # Verify primary was called
        mock_primary.generate_text.assert_called_once()
        
        # Now switch to backup
        provider = create_model_provider(TEST_CONFIG)
        
        # Verify backup was used
        provider.generate_text("test prompt")
        mock_backup.generate_text.assert_called_once()

if __name__ == '__main__':
    unittest.main()
