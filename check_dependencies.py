"""
Dependency Checker - Validates installed package versions
"""

import importlib
import sys
import logging

logger = logging.getLogger(__name__)

REQUIRED_PACKAGES = {
    "openai": "1.22.0",
    "langchain": "0.1.17",
    "streamlit": "1.33.0",
    "spacy": "3.7.2",
    "pandas": "2.2.2",
    "numpy": "1.26.4",
    "sqlite3": None  # Built-in, no version check needed
}

def check_dependencies():
    """Check if all required packages are installed with correct versions."""
    success = True
    
    for pkg, required_version in REQUIRED_PACKAGES.items():
        try:
            if pkg == "sqlite3":
                # sqlite3 is built-in, just check if it's available
                importlib.import_module(pkg)
                continue
                
            mod = importlib.import_module(pkg)
            
            # Get actual version
            actual_version = getattr(mod, "__version__", None)
            
            if actual_version is None:
                logger.warning(f"Could not get version for {pkg}")
                continue
                
            # Check version
            if required_version and actual_version != required_version:
                logger.error(f"{pkg} version mismatch: {actual_version} != {required_version}")
                success = False
                
        except ImportError:
            logger.error(f"Required package {pkg} is not installed")
            success = False
            
    return success

def main():
    """Main function to run dependency checks."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    if check_dependencies():
        print("✅ All dependencies are correctly installed and up to date.")
        sys.exit(0)
    else:
        print("❌ Some dependencies are missing or have incorrect versions.")
        print("Please run: pip install -r requirements.txt")
        sys.exit(1)

if __name__ == "__main__":
    main()
