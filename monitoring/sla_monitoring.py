"""
SLA Monitoring System

This module handles SLA monitoring, tracking, and reporting.
"""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta
import json
from pathlib import Path
import pandas as pd
import numpy as np
from monitoring.monitoring_config import MONITORING_CONFIG
from monitoring.prometheus_exporter import PrometheusExporter

class SLAError(Exception):
    """Raised when SLA operations fail"""
    pass

class SLAMonitoring:
    """Manages SLA monitoring and reporting"""
    
    def __init__(self, config: Dict[str, Any], prometheus_exporter: PrometheusExporter):
        """Initialize SLA monitoring"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.prometheus = prometheus_exporter
        
        # Initialize SLA state
        self.sla_state = self._initialize_sla_state()
        
        # Initialize SLA targets with new thresholds
        self.sla_targets = {
            "error_rate": self.config["monitoring"]["alert_thresholds"]["error_rate"],
            "response_time": self.config["monitoring"]["alert_thresholds"]["response_time"],
            "false_positive_rate": self.config["monitoring"]["alert_thresholds"]["false_positive_rate"],
            "false_negative_rate": self.config["monitoring"]["alert_thresholds"]["false_negative_rate"],
            "availability": 0.999  # 99.9% availability target
        }
        
        # Initialize SLA metrics storage
        self.metrics_dir = Path("sla_metrics")
        self.metrics_dir.mkdir(exist_ok=True)
        
        # Initialize reporting
        self.reporting_config = MONITORING_CONFIG["sla"]["reporting"]
    
    def _initialize_sla_state(self) -> Dict[str, Any]:
        """Initialize SLA state tracking"""
        try:
            return {
                "current_period": {
                    "start_time": datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0),
                    "metrics": {},
                    "violations": [],
                    "status": "in_progress"
                },
                "historical_data": [],
                "last_updated": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"SLA state initialization failed: {str(e)}")
            raise SLAError(f"Failed to initialize SLA state: {str(e)}")
    
    def update_metrics(self, metrics: Dict[str, Any]) -> None:
        """Update SLA metrics with new data including AI-specific metrics"""
        try:
            timestamp = datetime.now()
            
            # Update AI model metrics
            if "model_metrics" in metrics:
                model_metrics = metrics["model_metrics"]
                if "false_positive_rate" in model_metrics:
                    self._check_sla_violation("false_positive_rate", model_metrics["false_positive_rate"], timestamp)
                if "false_negative_rate" in model_metrics:
                    self._check_sla_violation("false_negative_rate", model_metrics["false_negative_rate"], timestamp)
                if "model_drift" in model_metrics:
                    self._check_sla_violation("model_drift", model_metrics["model_drift"], timestamp)
            
            # Update availability metric
            if "uptime" in metrics:
                availability = metrics["uptime"] / (metrics["uptime"] + metrics["downtime"])
                self._check_sla_violation("availability", availability, timestamp)
                self.sla_state["current_period"]["metrics"]["availability"] = availability
            
            # Update response time metric
            if "response_time" in metrics:
                self._check_sla_violation("response_time", metrics["response_time"], timestamp)
                self.sla_state["current_period"]["metrics"]["response_time"] = metrics["response_time"]
            
            # Update error rate metric
            if "error_count" in metrics and "total_requests" in metrics:
                error_rate = metrics["error_count"] / metrics["total_requests"] if metrics["total_requests"] > 0 else 0
                self._check_sla_violation("error_rate", error_rate, timestamp)
                self.sla_state["current_period"]["metrics"]["error_rate"] = error_rate
            
            # Update incident response metrics
            if "incidents" in metrics:
                for incident in metrics["incidents"]:
                    response_time = incident["response_time"]
                    severity = incident["severity"]
                    self._check_incident_sla(severity, response_time, timestamp)
            
            # Store metrics
            self._store_metrics(timestamp, metrics)
            
            # Update state
            self.sla_state["last_updated"] = timestamp.isoformat()
        except Exception as e:
            self.logger.error(f"SLA metrics update failed: {str(e)}")
            raise SLAError(f"Failed to update SLA metrics: {str(e)}")
    
    def _check_sla_violation(self, metric: str, value: float, timestamp: datetime) -> None:
        """Check if metric violates SLA target"""
        try:
            target = self.sla_targets.get(metric)
            if target is None:
                return
            
            # Check for violation based on metric type
            violation = False
            if metric in ["availability"]:
                violation = value < target
            else:  # response_time, error_rate
                violation = value > target
            
            if violation:
                violation_data = {
                    "metric": metric,
                    "value": value,
                    "target": target,
                    "timestamp": timestamp.isoformat()
                }
                self.sla_state["current_period"]["violations"].append(violation_data)
                self.logger.warning(f"SLA violation detected: {violation_data}")
        except Exception as e:
            self.logger.error(f"SLA violation check failed: {str(e)}")
            raise SLAError(f"Failed to check SLA violation: {str(e)}")
    
    def _check_incident_sla(self, severity: str, response_time: int, timestamp: datetime) -> None:
        """Check if incident response time violates SLA target"""
        try:
            target = self.sla_targets["incident_response_time"].get(severity)
            if target is None:
                return
            
            if response_time > target:
                violation_data = {
                    "metric": f"incident_response_{severity}",
                    "value": response_time,
                    "target": target,
                    "timestamp": timestamp.isoformat()
                }
                self.sla_state["current_period"]["violations"].append(violation_data)
                self.logger.warning(f"Incident response SLA violation detected: {violation_data}")
        except Exception as e:
            self.logger.error(f"Incident SLA check failed: {str(e)}")
            raise SLAError(f"Failed to check incident SLA: {str(e)}")
    
    def _store_metrics(self, timestamp: datetime, metrics: Dict[str, Any]) -> None:
        """Store SLA metrics"""
        try:
            # Create year/month directory structure
            year_dir = self.metrics_dir / str(timestamp.year)
            month_dir = year_dir / f"{timestamp.month:02d}"
            month_dir.mkdir(parents=True, exist_ok=True)
            
            # Create metrics file
            metrics_file = month_dir / f"metrics_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
            with open(metrics_file, "w") as f:
                json.dump({
                    "timestamp": timestamp.isoformat(),
                    "metrics": metrics
                }, f, indent=4)
        except Exception as e:
            self.logger.error(f"Metrics storage failed: {str(e)}")
            raise SLAError(f"Failed to store metrics: {str(e)}")
    
    def generate_sla_report(self, period: str = "current") -> Dict[str, Any]:
        """Generate SLA compliance report"""
        try:
            if period == "current":
                data = self.sla_state["current_period"]
            else:
                # Load historical data for the specified period
                data = self._load_historical_data(period)
            
            # Calculate compliance metrics
            compliance_metrics = self._calculate_compliance_metrics(data)
            
            # Generate report
            report = {
                "period": period,
                "start_time": data["start_time"],
                "end_time": datetime.now().isoformat(),
                "metrics": compliance_metrics,
                "violations": data["violations"],
                "status": "compliant" if compliance_metrics["overall_compliance"] >= 99 else "non_compliant"
            }
            
            # Store report
            self._store_report(report)
            
            return report
        except Exception as e:
            self.logger.error(f"SLA report generation failed: {str(e)}")
            raise SLAError(f"Failed to generate SLA report: {str(e)}")
    
    def _calculate_compliance_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate compliance metrics from data"""
        try:
            metrics = data["metrics"]
            violations = data["violations"]
            
            # Calculate average metrics
            avg_metrics = {
                "availability": np.mean([m.get("availability", 1.0) for m in metrics.values()]),
                "response_time": np.mean([m.get("response_time", 0.0) for m in metrics.values()]),
                "error_rate": np.mean([m.get("error_rate", 0.0) for m in metrics.values()])
            }
            
            # Calculate violation percentages
            total_time = (datetime.now() - datetime.fromisoformat(data["start_time"])).total_seconds()
            violation_time = sum(
                (datetime.fromisoformat(v["timestamp"]) - datetime.fromisoformat(data["start_time"])).total_seconds()
                for v in violations
            )
            
            compliance_percentage = 100 * (1 - violation_time / total_time)
            
            return {
                "average_metrics": avg_metrics,
                "violation_count": len(violations),
                "violation_time": violation_time,
                "total_time": total_time,
                "overall_compliance": compliance_percentage
            }
        except Exception as e:
            self.logger.error(f"Compliance metrics calculation failed: {str(e)}")
            raise SLAError(f"Failed to calculate compliance metrics: {str(e)}")
    
    def _store_report(self, report: Dict[str, Any]) -> None:
        """Store SLA report"""
        try:
            # Create reports directory if it doesn't exist
            reports_dir = Path("sla_reports")
            reports_dir.mkdir(exist_ok=True)
            
            # Create report filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"sla_report_{report['period']}_{timestamp}.json"
            
            # Store report
            with open(reports_dir / filename, "w") as f:
                json.dump(report, f, indent=4)
        except Exception as e:
            self.logger.error(f"Report storage failed: {str(e)}")
            raise SLAError(f"Failed to store report: {str(e)}")
    
    def _load_historical_data(self, period: str) -> Dict[str, Any]:
        """Load historical SLA data for a specific period"""
        try:
            # Parse period (e.g., "2025-05" for May 2025)
            year, month = map(int, period.split("-"))
            
            # Get metrics directory for the period
            metrics_path = self.metrics_dir / str(year) / f"{month:02d}"
            
            if not metrics_path.exists():
                raise SLAError(f"No data available for period: {period}")
            
            # Load all metrics files for the period
            metrics = {}
            violations = []
            
            for metrics_file in metrics_path.glob("metrics_*.json"):
                with open(metrics_file, "r") as f:
                    data = json.load(f)
                    metrics[data["timestamp"]] = data["metrics"]
            
            return {
                "start_time": datetime(year, month, 1).isoformat(),
                "metrics": metrics,
                "violations": violations,
                "status": "completed"
            }
        except Exception as e:
            self.logger.error(f"Historical data loading failed: {str(e)}")
            raise SLAError(f"Failed to load historical data: {str(e)}")
    
    def check_sla_compliance(self) -> bool:
        """Check if current SLA compliance meets targets including AI-specific metrics"""
        try:
            current_metrics = self.sla_state["current_period"]["metrics"]
            
            # Check availability
            if current_metrics.get("availability", 1.0) < self.sla_targets["availability"]:
                return False
            
            # Check response time
            if current_metrics.get("response_time", 0.0) > self.sla_targets["response_time"]:
                return False
            
            # Check error rate
            if current_metrics.get("error_rate", 0.0) > self.sla_targets["error_rate"]:
                return False
                
            # Check AI-specific metrics
            if current_metrics.get("false_positive_rate", 0.0) > self.sla_targets["false_positive_rate"]:
                return False
                
            if current_metrics.get("false_negative_rate", 0.0) > self.sla_targets["false_negative_rate"]:
                return False
                
            if current_metrics.get("model_drift", 0.0) > 0.1:  # 10% drift threshold
                return False
            
            return True
        except Exception as e:
            self.logger.error(f"SLA compliance check failed: {str(e)}")
            raise SLAError(f"Failed to check SLA compliance: {str(e)}")
    
    def get_sla_status(self) -> Dict[str, Any]:
        """Get current SLA status"""
        try:
            return {
                "current_period": self.sla_state["current_period"],
                "compliance_status": "compliant" if self.check_sla_compliance() else "non_compliant",
                "last_updated": self.sla_state["last_updated"]
            }
        except Exception as e:
            self.logger.error(f"SLA status retrieval failed: {str(e)}")
            raise SLAError(f"Failed to get SLA status: {str(e)}")
