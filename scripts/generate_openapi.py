"""
Generate OpenAPI documentation for FinConnectAI API
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from fastapi.openapi.utils import get_openapi
from app.api_routes import app
import json

def generate_openapi():
    try:
        # Ensure docs directory exists
        docs_dir = Path("docs")
        docs_dir.mkdir(exist_ok=True)
        
        # Generate OpenAPI schema
        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            openapi_version=app.openapi_version,
            description=app.description,
            routes=app.routes,
            tags=[{
                "name": "fraud",
                "description": "Fraud detection and analysis endpoints"
            }]
        )
        
        # Add additional metadata
        openapi_schema["info"]["x-logo"] = {
            "url": "https://example.com/logo.png"
        }
        
        # Write schema to file
        output_file = docs_dir / "openapi.json"
        with open(output_file, "w") as f:
            json.dump(openapi_schema, f, indent=2)
            
        print(f"OpenAPI schema generated successfully at {output_file}")
        return True
        
    except Exception as e:
        print(f"Error generating OpenAPI schema: {str(e)}")
        return False

if __name__ == "__main__":
    generate_openapi()
