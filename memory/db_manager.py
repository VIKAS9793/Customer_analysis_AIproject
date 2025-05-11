"""
Database Manager - Handles storage and retrieval of decisions and feedback
"""

import sqlite3
import logging
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages the SQLite database for storing decisions and feedback."""
    
    def __init__(self, db_path: str = "finconnectai.db"):
        """Initialize the database manager.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self._initialize_database()
    
    def _initialize_database(self) -> None:
        """Create database tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create decisions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS decisions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    decision_type TEXT NOT NULL,
                    decision TEXT NOT NULL CHECK (decision IN ('APPROVE', 'REJECT', 'FLAG', 'ERROR')),
                    confidence REAL CHECK (confidence BETWEEN 0 AND 1),
                    explanation TEXT,
                    action_taken TEXT,
                    timestamp TEXT,
                    reviewer_id TEXT,
                    status TEXT DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'APPROVED', 'REJECTED', 'FLAGGED'))
                )
            ''')
            
            # Create feedback table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    decision_id INTEGER,
                    reviewer_id TEXT NOT NULL,
                    feedback_type TEXT NOT NULL,
                    feedback_text TEXT,
                    timestamp TEXT,
                    FOREIGN KEY (decision_id) REFERENCES decisions (id)
                )
            ''')
            
            conn.commit()
    
    def log_decision(self, decision_data: Dict[str, Any]) -> int:
        """Log a decision in the database.
        
        Args:
            decision_data: Dictionary containing decision information
            
        Returns:
            ID of the newly created decision record
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO decisions (
                    decision_type, decision, confidence, explanation,
                    action_taken, timestamp, reviewer_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                decision_data.get('type', 'UNKNOWN'),
                decision_data.get('decision', 'UNKNOWN'),
                decision_data.get('confidence', 0.0),
                decision_data.get('explanation', ''),
                decision_data.get('action', ''),
                decision_data.get('timestamp', datetime.utcnow().isoformat()),
                decision_data.get('reviewer_id', '')
            ))
            
            decision_id = cursor.lastrowid
            conn.commit()
            return decision_id
    
    def log_feedback(self, decision_id: int, feedback_data: Dict[str, Any]) -> None:
        """Log feedback for a decision.
        
        Args:
            decision_id: ID of the decision being reviewed
            feedback_data: Dictionary containing feedback information
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO feedback (
                    decision_id, reviewer_id, feedback_type, feedback_text, timestamp
                ) VALUES (?, ?, ?, ?, ?)
            ''', (
                decision_id,
                feedback_data.get('reviewer_id', ''),
                feedback_data.get('type', 'UNKNOWN'),
                feedback_data.get('text', ''),
                feedback_data.get('timestamp', datetime.utcnow().isoformat())
            ))
            
            conn.commit()
    
    def get_pending_decisions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get pending decisions for human review.
        
        Args:
            limit: Maximum number of decisions to return
            
        Returns:
            List of pending decisions
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM decisions 
                WHERE status = 'PENDING' 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
            
            return [dict(zip([col[0] for col in cursor.description], row)) 
                    for row in cursor.fetchall()]
    
    def update_decision_status(self, decision_id: int, status: str) -> None:
        """Update the status of a decision.
        
        Args:
            decision_id: ID of the decision to update
            status: New status (e.g., 'APPROVED', 'REJECTED')
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE decisions 
                SET status = ? 
                WHERE id = ?
            ''', (status, decision_id))
            
            conn.commit()
