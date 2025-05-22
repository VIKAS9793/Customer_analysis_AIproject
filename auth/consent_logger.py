"""
Simple consent logger that stores user consent actions as flat JSON.
No external logging libraries used.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Literal

ConsentAction = Literal["opt-in", "deny", "revoke"]


class ConsentLogger:
    """Simple consent logger that stores events in JSON format."""

    def __init__(self, log_file: str = "logs/consent_events.json"):
        """Initialize consent logger with log file path."""
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

        # Create empty log file if it doesn't exist
        if not self.log_file.exists():
            self._write_logs([])

    def log_consent(
        self, user_id: str, action: ConsentAction, feature: str, metadata: Dict[str, Any] = None
    ) -> None:
        """Log a consent action."""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "action": action,
            "feature": feature,
            "metadata": metadata or {},
            "version": "2.1",  # Track consent version
        }

        # Read existing logs
        logs = self._read_logs()

        # Append new event
        logs.append(event)

        # Write updated logs
        self._write_logs(logs)

    def get_user_consent_status(self, user_id: str, feature: str) -> bool:
        """Get current consent status for a user and feature."""
        logs = self._read_logs()

        # Filter logs for this user and feature, get latest
        relevant_logs = [
            log for log in logs if log["user_id"] == user_id and log["feature"] == feature
        ]

        if not relevant_logs:
            return False

        # Get latest action
        latest_log = max(relevant_logs, key=lambda x: x["timestamp"])
        return latest_log["action"] == "opt-in"

    def _read_logs(self) -> list:
        """Read existing logs from file."""
        if not self.log_file.exists():
            return []

        try:
            with open(self.log_file) as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []

    def _write_logs(self, logs: list) -> None:
        """Write logs to file."""
        with open(self.log_file, "w") as f:
            json.dump(logs, f, indent=2)
