"""
FinConnectAI Dashboard - Human Review Interface
"""

import streamlit as st
from memory.db_manager import DatabaseManager
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def main():
    """Main application function."""
    # Initialize database
    db = DatabaseManager()
    
    # Set page config
    st.set_page_config(
        page_title="FinConnectAI Dashboard",
        page_icon="🔍",
        layout="wide"
    )
    
    # Sidebar
    with st.sidebar:
        st.title("FinConnectAI Dashboard")
        st.write("Review and manage AI decisions")
        
        # User ID input
        user_id = st.text_input("Your ID", value="", key="user_id")
        
    # Main content
    st.title("Pending Decisions")
    
    # Get pending decisions
    pending_decisions = db.get_pending_decisions()
    
    if not pending_decisions:
        st.info("No pending decisions to review")
        return
    
    # Display decisions in columns
    for decision in pending_decisions:
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.subheader(f"Decision #{decision['id']}")
            st.write(f"**Type:** {decision['decision_type']}")
            st.write(f"**Decision:** {decision['decision']}")
            st.write(f"**Confidence:** {decision['confidence']:.2f}")
            st.write(f"**Explanation:** {decision['explanation']}")
            st.write(f"**Action:** {decision['action_taken']}")
            st.write(f"**Timestamp:** {decision['timestamp']}")
        
        with col2:
            if st.button("Approve", key=f"approve_{decision['id']}"):
                handle_decision(decision['id'], "APPROVED", user_id, db)
        
        with col3:
            if st.button("Reject", key=f"reject_{decision['id']}"):
                handle_decision(decision['id'], "REJECTED", user_id, db)

def handle_decision(decision_id: int, status: str, user_id: str, db: DatabaseManager):
    """Handle decision approval/rejection.
    
    Args:
        decision_id: ID of the decision
        status: New status (APPROVED/REJECTED)
        user_id: ID of the reviewer
        db: Database manager instance
    """
    try:
        # Update decision status
        db.update_decision_status(decision_id, status)
        
        # Log feedback
        feedback_data = {
            'reviewer_id': user_id,
            'type': status,
            'text': f"Decision {status.lower()} by reviewer",
            'timestamp': datetime.utcnow().isoformat()
        }
        db.log_feedback(decision_id, feedback_data)
        
        st.success(f"Decision {status.lower()} successfully")
        
    except Exception as e:
        logger.error(f"Error handling decision: {str(e)}")
        st.error("Error processing decision. Please try again.")

if __name__ == "__main__":
    main()
