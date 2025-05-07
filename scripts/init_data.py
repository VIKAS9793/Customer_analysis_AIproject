"""
Initialize Data - Script to initialize the project with sample data.

This script initializes the CustomerAI project with sample data for testing
and demonstration purposes.
"""

import logging
import os
import sys
from typing import Any, Dict, List

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.config_manager import ConfigManager
from core.logging import setup_logging
from core.model_provider import create_model_provider
from knowledge.factory import create_knowledge_base
from memory.factory import create_memory

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_sample_documents() -> List[Dict[str, Any]]:
    """
    Create sample documents for the knowledge base.

    Returns:
        List of sample documents
    """
    return [
        {
            "title": "Customer Support FAQ",
            "content": """
            Frequently Asked Questions about our Customer Support

            Q: How do I contact customer support?
            A: You can contact customer support through our website, mobile app, or by calling our toll-free number at 1-800-123-4567.

            Q: What are your customer support hours?
            A: Our customer support team is available 24/7 to assist you with any questions or issues.

            Q: How long does it typically take to get a response?
            A: We aim to respond to all inquiries within 1 hour. Complex issues may take longer to resolve.

            Q: Can I track the status of my support ticket?
            A: Yes, you can track the status of your support ticket through our website or mobile app by logging into your account.
            """,
            "source": "internal",
            "metadata": {"category": "support", "tags": ["faq", "customer support", "contact"]},
        },
        {
            "title": "Product Features Overview",
            "content": """
            Our Product Features

            Our product offers a comprehensive set of features designed to meet your needs:

            1. Real-time Analytics: Monitor your data in real-time with our advanced analytics dashboard.
            2. Customizable Reports: Create custom reports tailored to your specific requirements.
            3. Integration Capabilities: Seamlessly integrate with your existing systems and tools.
            4. Mobile Access: Access your data on-the-go with our mobile app.
            5. Automated Alerts: Set up automated alerts to stay informed about important events.

            All features are available on our Standard, Professional, and Enterprise plans, with varying levels of functionality.
            """,
            "source": "internal",
            "metadata": {"category": "product", "tags": ["features", "overview", "capabilities"]},
        },
        {
            "title": "Pricing Information",
            "content": """
            Pricing Plans

            We offer several pricing plans to meet your needs:

            1. Standard Plan: $29/month
               - Basic features
               - Up to 5 users
               - 10GB storage

            2. Professional Plan: $99/month
               - All Standard features
               - Up to 20 users
               - 50GB storage
               - Priority support

            3. Enterprise Plan: Contact sales for pricing
               - All Professional features
               - Unlimited users
               - 500GB storage
               - Dedicated support
               - Custom integrations

            All plans include a 14-day free trial. No credit card required to start.
            """,
            "source": "internal",
            "metadata": {"category": "pricing", "tags": ["plans", "pricing", "subscription"]},
        },
        {
            "title": "Getting Started Guide",
            "content": """
            Getting Started with Our Product

            Welcome to our product! This guide will help you get started quickly.

            Step 1: Create an account
            Visit our website and click on the "Sign Up" button. Fill out the registration form and verify your email address.

            Step 2: Set up your profile
            Complete your profile by adding your company information and preferences.

            Step 3: Connect your data sources
            Go to the "Integrations" section and connect your data sources.

            Step 4: Create your first dashboard
            Navigate to the "Dashboards" section and click on "Create New Dashboard". Follow the wizard to set up your first dashboard.

            Step 5: Invite team members
            Go to the "Team" section and invite your team members to collaborate.

            If you need any assistance, our support team is available 24/7 to help you.
            """,
            "source": "internal",
            "metadata": {
                "category": "onboarding",
                "tags": ["getting started", "guide", "tutorial"],
            },
        },
        {
            "title": "Security Practices",
            "content": """
            Our Security Practices

            At our company, security is our top priority. We implement the following security measures to protect your data:

            1. Data Encryption: All data is encrypted in transit and at rest using industry-standard encryption protocols.

            2. Multi-factor Authentication: We support multi-factor authentication to add an extra layer of security to your account.

            3. Regular Security Audits: We conduct regular security audits and penetration testing to identify and address potential vulnerabilities.

            4. Compliance: We are compliant with industry standards such as SOC 2, GDPR, and HIPAA.

            5. Access Controls: We implement strict access controls to ensure that only authorized personnel can access your data.

            If you have any questions about our security practices, please contact our security team at security@example.com.
            """,
            "source": "internal",
            "metadata": {"category": "security", "tags": ["security", "encryption", "compliance"]},
        },
    ]


def create_sample_interactions() -> List[Dict[str, Any]]:
    """
    Create sample interactions for the memory store.

    Returns:
        List of sample interactions
    """
    return [
        {
            "query": {
                "content": "How do I contact customer support?",
                "user_id": "user-123",
                "conversation_id": "conv-1",
                "timestamp": "2023-01-01T12:00:00Z",
            },
            "response": {
                "content": "You can contact customer support through our website, mobile app, or by calling our toll-free number at 1-800-123-4567. Our customer support team is available 24/7 to assist you with any questions or issues.",
                "timestamp": "2023-01-01T12:00:05Z",
                "source": "knowledge_base",
            },
        },
        {
            "query": {
                "content": "What's included in the Professional plan?",
                "user_id": "user-123",
                "conversation_id": "conv-1",
                "timestamp": "2023-01-01T12:05:00Z",
            },
            "response": {
                "content": "The Professional Plan costs $99/month and includes all Standard features, up to 20 users, 50GB storage, and priority support. It's a great option for growing teams that need more advanced features and support.",
                "timestamp": "2023-01-01T12:05:05Z",
                "source": "knowledge_base",
            },
        },
        {
            "query": {
                "content": "How do I create a dashboard?",
                "user_id": "user-456",
                "conversation_id": "conv-2",
                "timestamp": "2023-01-02T10:00:00Z",
            },
            "response": {
                "content": "To create a dashboard, navigate to the 'Dashboards' section and click on 'Create New Dashboard'. Follow the wizard to set up your dashboard. You can add various widgets and customize the layout according to your preferences.",
                "timestamp": "2023-01-02T10:00:05Z",
                "source": "knowledge_base",
            },
        },
        {
            "query": {
                "content": "Is my data secure?",
                "user_id": "user-789",
                "conversation_id": "conv-3",
                "timestamp": "2023-01-03T15:00:00Z",
            },
            "response": {
                "content": "Yes, your data is secure with us. We implement multiple security measures including data encryption in transit and at rest, multi-factor authentication, regular security audits, compliance with industry standards (SOC 2, GDPR, HIPAA), and strict access controls. If you have specific security concerns, you can contact our security team at security@example.com.",
                "timestamp": "2023-01-03T15:00:05Z",
                "source": "knowledge_base",
            },
        },
        {
            "query": {
                "content": "Can I try before I buy?",
                "user_id": "user-789",
                "conversation_id": "conv-3",
                "timestamp": "2023-01-03T15:05:00Z",
            },
            "response": {
                "content": "Yes, all our plans include a 14-day free trial. No credit card is required to start the trial. You can sign up on our website and explore all the features before making a decision.",
                "timestamp": "2023-01-03T15:05:05Z",
                "source": "knowledge_base",
            },
        },
    ]


def main():
    """Main function to initialize the project with sample data."""
    logger.info("Initializing project with sample data")

    # Load configuration
    config_manager = ConfigManager()
    config = config_manager.load_config()

    # Set up logging
    setup_logging(config)

    # Create model provider
    model_provider = create_model_provider(config.get("model_providers", {}))

    # Create knowledge base
    knowledge_base = create_knowledge_base(config.get("knowledge", {}), model_provider)

    # Create memory store
    memory = create_memory(config.get("memory", {}), model_provider)

    # Add sample documents to knowledge base
    logger.info("Adding sample documents to knowledge base")
    sample_documents = create_sample_documents()
    for doc in sample_documents:
        try:
            doc_id = knowledge_base.add_document(doc)
            logger.info(f"Added document: {doc['title']} (ID: {doc_id})")
        except Exception as e:
            logger.error(f"Error adding document '{doc['title']}': {e}")

    # Add sample interactions to memory
    logger.info("Adding sample interactions to memory")
    sample_interactions = create_sample_interactions()
    for interaction in sample_interactions:
        try:
            memory_id = memory.store_interaction(interaction["query"], interaction["response"])
            logger.info(f"Added interaction: {interaction['query']['content']} (ID: {memory_id})")
        except Exception as e:
            logger.error(f"Error adding interaction '{interaction['query']['content']}': {e}")

    logger.info("Sample data initialization complete")


if __name__ == "__main__":
    main()
