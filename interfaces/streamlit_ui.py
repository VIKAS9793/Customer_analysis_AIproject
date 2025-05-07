"""
Streamlit UI - Streamlit-based demo UI for internal testing.

This module implements a Streamlit-based UI for interacting with the CustomerAI framework.
"""

import json
import logging
from typing import Optional

import streamlit as st

from core.agent_manager import AgentManager
from core.config_manager import ConfigManager

logger = logging.getLogger(__name__)


def run_streamlit(agent_manager: Optional[AgentManager] = None) -> None:
    """
    Run the Streamlit UI.

    Args:
        agent_manager: Optional agent manager instance
    """
    # Load configuration
    config_manager = ConfigManager()
    config = config_manager.load_config()

    # Create agent manager if not provided
    if agent_manager is None:
        from core.agent_manager import AgentManager

        agent_manager = AgentManager()

        # Initialize safety measures
        from core.safety import AntiHallucinationGuard

        safety_guard = AntiHallucinationGuard()
        agent_manager.register_safety_guard(safety_guard)

        # Initialize memory
        from memory.base import LongTermMemory, ShortTermMemory

        memory_config = config.get("memory", {})
        memory_type = memory_config.get("type", "short_term")

        if memory_type == "short_term":
            memory = ShortTermMemory()
        elif memory_type == "long_term":
            memory = LongTermMemory(
                vector_store_type=memory_config.get("vector_db", {}).get("type", "mock")
            )
        else:
            memory = ShortTermMemory()

        agent_manager.set_memory(memory)

    # Set up Streamlit page
    st.set_page_config(
        page_title="CustomerAI Demo",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Sidebar
    with st.sidebar:
        st.title("CustomerAI Demo")
        st.markdown("---")

        # Mode selection
        st.subheader("Mode")
        mode = st.radio("Select mode", ["Chat", "Insights", "Actions"], index=0)

        st.markdown("---")

        # Settings
        st.subheader("Settings")

        # Model provider selection
        model_providers = config.get("model_providers", {})
        default_provider = model_providers.get("default", "openai")
        provider_options = list(model_providers.keys())
        if "default" in provider_options:
            provider_options.remove("default")

        if not provider_options:
            provider_options = ["openai", "mock"]

        selected_provider = st.selectbox(
            "Model Provider",
            provider_options,
            index=provider_options.index(config.get("provider", "openai")),
        )

        # Safety settings
        st.subheader("Safety Settings")

        st.checkbox(
            "Anti-Hallucination Guard",
            value=config.get("safety", {}).get("anti_hallucination", True),
        )

        st.checkbox(
            "Source Verification", value=config.get("safety", {}).get("source_verification", True)
        )

        st.checkbox(
            "Bias Filter", value=config.get("safety", {}).get("bias_filter", True)
        )

        st.markdown("---")

        # About section
        st.subheader("About")
        st.markdown(
            """
            **CustomerAI** is an enterprise-ready modular AI agent framework designed to automate customer engagement and operations with anti-hallucination and anti-bias architecture.

            Version: 1.0.0
            """
        )

    # Main content
    if mode == "Chat":
        chat_interface(agent_manager)
    elif mode == "Insights":
        insights_interface(agent_manager)
    elif mode == "Actions":
        actions_interface(agent_manager)


def chat_interface(agent_manager: AgentManager) -> None:
    """
    Render the chat interface.

    Args:
        agent_manager: Agent manager instance
    """
    st.title("Chat with CustomerAI")

    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = None

    # Display chat history
    for message in st.session_state.chat_history:
        role = message["role"]
        content = message["content"]

        if role == "user":
            st.chat_message("user").write(content)
        else:
            with st.chat_message("assistant"):
                st.write(content)

                # Display sources if available
                if "sources" in message and message["sources"]:
                    with st.expander("Sources"):
                        for source in message["sources"]:
                            st.markdown(f"**{source['title']}**")
                            st.markdown(f"*{source['url']}*")
                            st.markdown(source["content_snippet"])
                            st.markdown("---")

    # Chat input
    user_input = st.chat_input("Type your message here...")

    if user_input:
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        # Display user message
        st.chat_message("user").write(user_input)

        # Prepare task for agent
        task = {
            "type": "chat",
            "content": user_input,
            "conversation_id": st.session_state.conversation_id,
            "metadata": {},
        }

        # Run task
        with st.spinner("Thinking..."):
            result = agent_manager.run_task(task)

        # Extract response fields
        response = result.get("content", "I'm sorry, I couldn't generate a response.")
        conversation_id = result.get("conversation_id", "new_conversation")
        sources = result.get("sources", [])
        confidence = result.get("confidence", 0.0)

        # Update conversation ID
        st.session_state.conversation_id = conversation_id

        # Add assistant message to chat history
        st.session_state.chat_history.append(
            {"role": "assistant", "content": response, "sources": sources, "confidence": confidence}
        )

        # Display assistant message
        with st.chat_message("assistant"):
            st.write(response)

            # Display sources if available
            if sources:
                with st.expander("Sources"):
                    for source in sources:
                        st.markdown(f"**{source['title']}**")
                        st.markdown(f"*{source['url']}*")
                        st.markdown(source["content_snippet"])
                        st.markdown("---")

    # Clear chat button
    if st.button("Clear Chat"):
        st.session_state.chat_history = []
        st.session_state.conversation_id = None
        st.rerun()


def insights_interface(agent_manager: AgentManager) -> None:
    """
    Render the insights interface.

    Args:
        agent_manager: Agent manager instance
    """
    st.title("Generate Insights")

    # Data source selection
    st.subheader("Data Sources")

    data_sources = [
        "customer_data",
        "sales_data",
        "support_tickets",
        "product_usage",
        "feedback_surveys",
    ]

    selected_sources = st.multiselect(
        "Select data sources", data_sources, default=["customer_data", "support_tickets"]
    )

    # Filters
    st.subheader("Filters")

    col1, col2 = st.columns(2)

    with col1:
        date_range = st.date_input("Date range", value=[], help="Filter data by date range")

    with col2:
        customer_segment = st.selectbox(
            "Customer segment",
            ["All", "Enterprise", "SMB", "Startup"],
            index=0,
            help="Filter by customer segment",
        )

    # Query input
    st.subheader("Insight Query")

    query = st.text_area(
        "What insights are you looking for?",
        height=100,
        help="Describe the insights you want to generate",
    )

    # Generate insights button
    if st.button("Generate Insights"):
        if not query:
            st.error("Please enter a query")
            return

        if not selected_sources:
            st.error("Please select at least one data source")
            return

        # Prepare filters
        filters = {}

        if len(date_range) == 2:
            filters["date_range"] = {
                "start": date_range[0].isoformat(),
                "end": date_range[1].isoformat(),
            }

        if customer_segment != "All":
            filters["customer_segment"] = customer_segment

        # Prepare task for agent
        task = {
            "type": "insight",
            "content": query,
            "data_sources": selected_sources,
            "filters": filters,
        }

        # Run task
        with st.spinner("Generating insights..."):
            result = agent_manager.run_task(task)

        # Extract response fields
        insights = result.get("insights", [])
        sources = result.get("sources", [])

        # Display insights
        if insights:
            st.subheader("Generated Insights")

            for i, insight in enumerate(insights):
                with st.container():
                    st.markdown(f"### Insight {i+1}")
                    st.markdown(insight.get("title", ""))
                    st.markdown(insight.get("description", ""))

                    # Display metrics if available
                    metrics = insight.get("metrics", [])
                    if metrics:
                        cols = st.columns(min(len(metrics), 3))
                        for j, metric in enumerate(metrics):
                            with cols[j % 3]:
                                st.metric(
                                    label=metric.get("label", ""),
                                    value=metric.get("value", ""),
                                    delta=metric.get("delta", None),
                                )

                    st.markdown("---")

            # Display sources
            if sources:
                with st.expander("Data Sources"):
                    for source in sources:
                        st.markdown(f"**{source['title']}**")
                        st.markdown(f"*{source['source']}*")
                        st.markdown(source["description"])
                        st.markdown("---")
        else:
            st.warning(
                "No insights generated. Try refining your query or selecting different data sources."
            )


def actions_interface(agent_manager: AgentManager) -> None:
    """
    Render the actions interface.

    Args:
        agent_manager: Agent manager instance
    """
    st.title("Execute Actions")

    # Get available actions
    task = {"type": "list_actions"}

    result = agent_manager.run_task(task)
    available_actions = result.get("actions", [])

    if not available_actions:
        available_actions = [
            {
                "type": "send_email",
                "description": "Send an email to a recipient",
                "params": {
                    "to": "Email address of the recipient",
                    "subject": "Subject of the email",
                    "body": "Body of the email",
                },
            },
            {
                "type": "create_ticket",
                "description": "Create a support ticket",
                "params": {
                    "title": "Title of the ticket",
                    "description": "Description of the ticket",
                    "priority": "Priority of the ticket (low, medium, high)",
                },
            },
            {
                "type": "update_customer",
                "description": "Update customer information",
                "params": {
                    "customer_id": "ID of the customer",
                    "fields": "Fields to update (JSON object)",
                },
            },
        ]

    # Action selection
    st.subheader("Select Action")

    action_types = [action["type"] for action in available_actions]
    action_descriptions = {action["type"]: action["description"] for action in available_actions}

    selected_action = st.selectbox(
        "Action", action_types, format_func=lambda x: f"{x} - {action_descriptions[x]}"
    )

    # Get selected action details
    selected_action_details = next(
        (action for action in available_actions if action["type"] == selected_action), None
    )

    if selected_action_details:
        st.markdown(f"**{selected_action_details['description']}**")

        # Parameter inputs
        st.subheader("Parameters")

        params = {}
        param_details = selected_action_details.get("params", {})

        for param_name, param_description in param_details.items():
            if "email" in param_name.lower() and "to" in param_name.lower():
                params[param_name] = st.text_input(
                    f"{param_name}", help=param_description, placeholder="user@example.com"
                )
            elif "subject" in param_name.lower():
                params[param_name] = st.text_input(f"{param_name}", help=param_description)
            elif "body" in param_name.lower() or "description" in param_name.lower():
                params[param_name] = st.text_area(
                    f"{param_name}", help=param_description, height=150
                )
            elif "priority" in param_name.lower():
                params[param_name] = st.selectbox(
                    f"{param_name}", ["low", "medium", "high"], help=param_description
                )
            elif "id" in param_name.lower():
                params[param_name] = st.text_input(f"{param_name}", help=param_description)
            elif "fields" in param_name.lower():
                fields_str = st.text_area(
                    f"{param_name}",
                    help=param_description + " (Enter as JSON)",
                    height=150,
                    placeholder='{"name": "John Doe", "email": "john@example.com"}',
                )

                if fields_str:
                    try:
                        params[param_name] = json.loads(fields_str)
                    except json.JSONDecodeError:
                        st.error("Invalid JSON format")
            else:
                params[param_name] = st.text_input(f"{param_name}", help=param_description)

        # Execute action button
        if st.button("Execute Action"):
            # Validate required parameters
            missing_params = [param for param, value in params.items() if not value]

            if missing_params:
                st.error(f"Missing required parameters: {', '.join(missing_params)}")
                return

            # Prepare task for agent
            task = {"type": "action", "action_type": selected_action, "params": params}

            # Run task
            with st.spinner("Executing action..."):
                result = agent_manager.run_task(task)

            # Display result
            status = result.get("status", "error")
            message = result.get("message", "Action execution failed")
            details = result.get("details", {})

            if status == "success":
                st.success(message)
            else:
                st.error(message)

            # Display details
            if details:
                with st.expander("Action Details"):
                    st.json(details)


if __name__ == "__main__":
    run_streamlit()
