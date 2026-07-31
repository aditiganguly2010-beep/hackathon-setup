"""
Anomaly detection system using machine learning.
Detects system degradation and anomalies in logs and metrics.
"""
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from app.models import PerformanceMetric, SystemLog, Anomaly
from app.core.logging import get_logger

logger = get_logger(__name__)


class AnomalyDetector:
    """Detect anomalies in system logs and performance metrics."""
    
    def __init__(self):
        self.metric_scaler = StandardScaler()
        self.log_scaler = StandardScaler()
    
    def detect_metric_anomalies(
        self,
        metrics: List[PerformanceMetric],
        source_system: str,
        db: Session,
        contamination: float = 0.05
    ) -> List[Anomaly]:
        """
        Detect anomalies in performance metrics using Isolation Forest.
        
        Args:
            metrics: List of performance metrics
            source_system: Source system identifier
            db: Database session
            contamination: Expected proportion of outliers
            
        Returns:
            List of detected anomalies
        """
        if len(metrics) < 10:
            logger.warning("Not enough metrics for anomaly detection")
            return []
        
        logger.info(f"Detecting metric anomalies for {source_system}", extra_data={
            "metric_count": len(metrics)
        })
        
        # Group metrics by type
        metrics_by_type = self._group_metrics_by_type(metrics)
        
        anomalies = []
        
        for metric_type, type_metrics in metrics_by_type.items():
            if len(type_metrics) < 5:
                continue
            
            # Extract features
            features = self._extract_metric_features(type_metrics)
            
            # Scale features
            scaled_features = self.metric_scaler.fit_transform(features)
            
            # Apply Isolation Forest
            iso_forest = IsolationForest(
                contamination=contamination,
                random_state=42,
                n_estimators=100
            )
            
            predictions = iso_forest.fit_predict(scaled_features)
            scores = iso_forest.score_samples(scaled_features)
            
            # Identify anomalies
            for i, (pred, score) in enumerate(zip(predictions, scores)):
                if pred == -1:  # Anomaly
                    metric = type_metrics[i]
                    anomaly = self._create_metric_anomaly(
                        metric,
                        metric_type,
                        score,
                        source_system
                    )
                    anomalies.append(anomaly)
        
        logger.info(f"Detected {len(anomalies)} metric anomalies")
        
        return anomalies
    
    def detect_log_anomalies(
        self,
        logs: List[SystemLog],
        source_system: str,
        db: Session,
        time_window_minutes: int = 60
    ) -> List[Anomaly]:
        """
        Detect anomalies in log patterns (e.g., log spikes).
        
        Args:
            logs: List of system logs
            source_system: Source system identifier
            db: Database session
            time_window_minutes: Time window for spike detection
            
        Returns:
            List of detected anomalies
        """
        if len(logs) < 10:
            logger.warning("Not enough logs for anomaly detection")
            return []
        
        logger.info(f"Detecting log anomalies for {source_system}", extra_data={
            "log_count": len(logs)
        })
        
        anomalies = []
        
        # Detect log spikes
        spike_anomalies = self._detect_log_spikes(logs, source_system, time_window_minutes)
        anomalies.extend(spike_anomalies)
        
        # Detect error rate spikes
        error_anomalies = self._detect_error_spikes(logs, source_system, time_window_minutes)
        anomalies.extend(error_anomalies)
        
        logger.info(f"Detected {len(anomalies)} log anomalies")
        
        return anomalies
    
    def _group_metrics_by_type(self, metrics: List[PerformanceMetric]) -> Dict[str, List[PerformanceMetric]]:
        """Group metrics by their type."""
        grouped = {}
        for metric in metrics:
            if metric.metric_type not in grouped:
                grouped[metric.metric_type] = []
            grouped[metric.metric_type].append(metric)
        return grouped
    
    def _extract_metric_features(self, metrics: List[PerformanceMetric]) -> np.ndarray:
        """Extract features from metrics for ML processing."""
        features = []
        
        for metric in metrics:
            # Basic features
            feature_vector = [
                metric.metric_value,
                # Time-based features
                metric.timestamp.hour,
                metric.timestamp.dayofweek,
                # Value change rate (would need previous values)
            ]
            features.append(feature_vector)
        
        return np.array(features)
    
    def _create_metric_anomaly(
        self,
        metric: PerformanceMetric,
        metric_type: str,
        anomaly_score: float,
        source_system: str
    ) -> Anomaly:
        """Create an anomaly object from a metric."""
        # Determine severity based on score and value
        confidence_score = abs(anomaly_score)
        
        if metric_type == "CPU" and metric.metric_value > 90:
            severity = "Critical"
            anomaly_type = "CPU Saturation"
        elif metric_type == "Memory" and metric.metric_value > 90:
            severity = "Critical"
            anomaly_type = "High Memory"
        elif metric_type == "Disk" and metric.metric_value > 90:
            severity = "High"
            anomaly_type = "Disk Space Low"
        elif metric_type == "Network" and metric.metric_value > 500:
            severity = "High"
            anomaly_type = "Network Latency"
        else:
            severity = "Medium"
            anomaly_type = f"{metric_type} Anomaly"
        
        description = (
            f"{anomaly_type} detected in {source_system}. "
            f"Current value: {metric.metric_value}{metric.unit or ''}. "
            f"Confidence: {confidence_score:.2f}"
        )
        
        return Anomaly(
            source_system=source_system,
            anomaly_type=anomaly_type,
            severity=severity,
            confidence_score=min(confidence_score, 0.99),
            description=description,
            detected_at=metric.timestamp,
            related_metrics=str(metric.id),
            related_logs=None
        )
    
    def _detect_log_spikes(
        self,
        logs: List[SystemLog],
        source_system: str,
        time_window_minutes: int
    ) -> List[Anomaly]:
        """Detect sudden spikes in log volume."""
        anomalies = []
        
        # Group logs by time windows
        time_windows = self._group_logs_by_time_window(logs, time_window_minutes)
        
        # Calculate statistics
        log_counts = [len(window_logs) for window_logs in time_windows.values()]
        
        if len(log_counts) < 3:
            return anomalies
        
        # Calculate threshold (mean + 2 * std)
        mean_count = np.mean(log_counts)
        std_count = np.std(log_counts)
        threshold = mean_count + 2 * std_count
        
        # Detect spikes
        for window_time, window_logs in time_windows.items():
            if len(window_logs) > threshold:
                confidence_score = min((len(window_logs) - mean_count) / (std_count + 1), 0.99)
                
                anomaly = Anomaly(
                    source_system=source_system,
                    anomaly_type="Log Spike",
                    severity="High" if confidence_score > 0.7 else "Medium",
                    confidence_score=confidence_score,
                    description=(
                        f"Log volume spike detected in {source_system}. "
                        f"{len(window_logs)} logs in {time_window_minutes} minute window "
                        f"(threshold: {threshold:.0f}). "
                        f"Confidence: {confidence_score:.2f}"
                    ),
                    detected_at=window_time,
                    related_metrics=None,
                    related_logs=",".join([str(log.id) for log in window_logs[:10]])
                )
                anomalies.append(anomaly)
        
        return anomalies
    
    def _detect_error_spikes(
        self,
        logs: List[SystemLog],
        source_system: str,
        time_window_minutes: int
    ) -> List[Anomaly]:
        """Detect spikes in error logs."""
        anomalies = []
        
        # Filter error logs
        error_logs = [log for log in logs if log.log_level in ['ERROR', 'CRITICAL']]
        
        if len(error_logs) < 5:
            return anomalies
        
        # Group by time windows
        time_windows = self._group_logs_by_time_window(error_logs, time_window_minutes)
        
        # Calculate statistics
        error_counts = [len(window_logs) for window_logs in time_windows.values()]
        
        if len(error_counts) < 3:
            return anomalies
        
        # Calculate threshold
        mean_count = np.mean(error_counts)
        std_count = np.std(error_counts)
        threshold = mean_count + 2 * std_count
        
        # Detect spikes
        for window_time, window_logs in time_windows.items():
            if len(window_logs) > threshold and len(window_logs) > 3:
                confidence_score = min((len(window_logs) - mean_count) / (std_count + 1), 0.99)
                
                anomaly = Anomaly(
                    source_system=source_system,
                    anomaly_type="Error Spike",
                    severity="High" if confidence_score > 0.7 else "Medium",
                    confidence_score=confidence_score,
                    description=(
                        f"Error log spike detected in {source_system}. "
                        f"{len(window_logs)} error logs in {time_window_minutes} minute window "
                        f"(threshold: {threshold:.0f}). "
                        f"Confidence: {confidence_score:.2f}"
                    ),
                    detected_at=window_time,
                    related_metrics=None,
                    related_logs=",".join([str(log.id) for log in window_logs[:10]])
                )
                anomalies.append(anomaly)
        
        return anomalies
    
    def _group_logs_by_time_window(
        self,
        logs: List[SystemLog],
        window_minutes: int
    ) -> Dict[datetime, List[SystemLog]]:
        """Group logs into time windows."""
        windows = {}
        
        for log in logs:
            # Round timestamp to window
            window_time = log.timestamp.replace(
                minute=log.timestamp.minute // window_minutes * window_minutes,
                second=0,
                microsecond=0
            )
            
            if window_time not in windows:
                windows[window_time] = []
            windows[window_time].append(log)
        
        return windows
    
    def calculate_health_score(
        self,
        source_system: str,
        db: Session,
        hours: int = 24
    ) -> Optional[Dict[str, Any]]:
        """
        Calculate overall health score for a system.
        
        Args:
            source_system: Source system identifier
            db: Database session
            hours: Number of hours to consider
            
        Returns:
            Dictionary with health scores
        """
        from datetime import datetime, timedelta
        
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        # Get recent metrics
        metrics = db.query(PerformanceMetric).filter(
            PerformanceMetric.source_system == source_system,
            PerformanceMetric.timestamp >= cutoff_time
        ).all()
        
        # Get recent anomalies
        anomalies = db.query(Anomaly).filter(
            Anomaly.source_system == source_system,
            Anomaly.detected_at >= cutoff_time
        ).all()
        
        if not metrics:
            logger.warning(f"No metrics found for {source_system}")
            return None
        
        # Calculate scores by metric type
        scores = {}
        
        metrics_by_type = self._group_metrics_by_type(metrics)
        for metric_type, type_metrics in metrics_by_type.items():
            avg_value = np.mean([m.metric_value for m in type_metrics])
            # Convert to score (lower is better for most metrics)
            score = max(0, min(100, 100 - avg_value))
            scores[f"{metric_type.lower()}_score"] = int(score)
        
        # Calculate anomaly score
        critical_count = sum(1 for a in anomalies if a.severity == "Critical")
        high_count = sum(1 for a in anomalies if a.severity == "High")
        anomaly_score = max(0, 100 - (critical_count * 20) - (high_count * 10))
        scores["log_anomaly_score"] = int(anomaly_score)
        
        # Calculate overall score
        metric_scores = [v for k, v in scores.items() if k.endswith("_score")]
        overall_score = int(np.mean(metric_scores)) if metric_scores else 50
        
        # Determine trend
        if overall_score >= 80:
            trend = "Stable"
        elif overall_score >= 60:
            trend = "Stable"
        else:
            trend = "Degrading"
        
        scores.update({
            "source_system": source_system,
            "overall_score": overall_score,
            "calculated_at": datetime.utcnow(),
            "trend": trend
        })
        
        return scores
