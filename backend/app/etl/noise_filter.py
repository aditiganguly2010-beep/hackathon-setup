"""
Noise filter for ETL pipeline.
Filters out noise and irrelevant data from logs and metrics.
"""
import re
from typing import List, Dict, Any
from app.core.logging import get_logger

logger = get_logger(__name__)


class NoiseFilter:
    """Filter for removing noise from logs and metrics."""
    
    # Common noise patterns to filter out
    NOISE_PATTERNS = [
        # Debug/verbose logs
        r'^debug:',
        r'^trace:',
        r'^verbose:',
        
        # Health check/heartbeat logs
        r'health.*check',
        r'heartbeat',
        r'ping.*pong',
        r'status.*ok',
        
        # Repetitive connection logs
        r'connection.*accepted',
        r'connection.*established',
        
        # Background task logs
        r'background.*task',
        r'scheduler.*running',
        
        # Empty or whitespace-only messages
        r'^\s*$',
        
        # Common noise keywords
        r'^\[info\]\s*$',
        r'^\s*-\s*$',
    ]
    
    # Keywords that indicate important logs (should NOT be filtered)
    IMPORTANT_KEYWORDS = [
        'error',
        'exception',
        'fail',
        'critical',
        'fatal',
        'timeout',
        'crash',
        'panic',
        'alert',
        'warning',
        'deprecated',
        'security',
        'breach',
        'unauthorized',
        'forbidden',
        'denied'
    ]
    
    def __init__(self):
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.NOISE_PATTERNS]
    
    def should_filter_log(self, log_data: Dict[str, Any]) -> bool:
        """
        Determine if a log should be filtered out as noise.
        
        Args:
            log_data: Normalized log data
            
        Returns:
            True if log should be filtered, False otherwise
        """
        message = log_data.get('message', '').lower()
        log_level = log_data.get('log_level', '').upper()
        
        # Never filter error or critical logs
        if log_level in ['ERROR', 'CRITICAL']:
            return False
        
        # Never filter logs with important keywords
        for keyword in self.IMPORTANT_KEYWORDS:
            if keyword in message:
                return False
        
        # Check against noise patterns
        for pattern in self.compiled_patterns:
            if pattern.search(message):
                logger.debug("Filtering noise log", extra_data={"message": message[:100]})
                return True
        
        # Filter very short messages (likely noise)
        if len(message.strip()) < 5:
            return True
        
        return False
    
    def should_filter_metric(self, metric_data: Dict[str, Any]) -> bool:
        """
        Determine if a metric should be filtered out as noise.
        
        Args:
            metric_data: Normalized metric data
            
        Returns:
            True if metric should be filtered, False otherwise
        """
        metric_value = metric_data.get('metric_value', 0)
        metric_type = metric_data.get('metric_type', '')
        
        # Filter out invalid values
        if metric_value < 0 or metric_value > 1000:
            # Allow some outliers but filter extreme values
            if metric_type in ['CPU', 'Memory', 'Disk'] and metric_value > 100:
                return True
        
        # Filter zero values for certain metric types (might indicate missing data)
        if metric_value == 0 and metric_type in ['CPU', 'Memory']:
            # Allow some zeros but filter if consecutive (would need state tracking)
            pass
        
        return False
    
    def filter_logs(self, logs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter a list of logs, removing noise.
        
        Args:
            logs: List of normalized log data
            
        Returns:
            Filtered list of logs
        """
        filtered = [log for log in logs if not self.should_filter_log(log)]
        
        logger.info(f"Filtered logs: {len(logs)} -> {len(filtered)} ({len(logs) - len(filtered)} removed)")
        
        return filtered
    
    def filter_metrics(self, metrics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter a list of metrics, removing noise.
        
        Args:
            metrics: List of normalized metric data
            
        Returns:
            Filtered list of metrics
        """
        filtered = [metric for metric in metrics if not self.should_filter_metric(metric)]
        
        logger.info(f"Filtered metrics: {len(metrics)} -> {len(filtered)} ({len(metrics) - len(filtered)} removed)")
        
        return filtered
