"""
Metric parser for ETL pipeline.
Handles parsing and normalization of performance metrics.
"""
import json
import re
from datetime import datetime
from typing import Dict, Any, Optional
from app.core.logging import get_logger

logger = get_logger(__name__)


class MetricParser:
    """Parser for various metric formats."""
    
    METRIC_TYPES = ['CPU', 'Memory', 'Disk', 'Network']
    UNITS = {
        'CPU': '%',
        'Memory': '%',
        'Disk': '%',
        'Network': 'Mbps'
    }
    
    def __init__(self):
        pass
    
    def parse_metric(self, raw_metric: str, source_system: str) -> Dict[str, Any]:
        """
        Parse a raw metric string into normalized format.
        
        Args:
            raw_metric: Raw metric string or JSON
            source_system: Source system identifier
            
        Returns:
            Normalized metric data as dictionary
        """
        try:
            # Try JSON format first
            if raw_metric.strip().startswith('{'):
                return self._parse_json_metric(raw_metric, source_system)
            
            # Try key=value format
            if '=' in raw_metric:
                return self._parse_kv_metric(raw_metric, source_system)
            
            # Fallback: try to extract numeric value
            return self._parse_numeric_metric(raw_metric, source_system)
            
        except Exception as e:
            logger.error("Error parsing metric", extra_data={
                "error": str(e),
                "raw_metric": raw_metric[:200]
            })
            return self._parse_numeric_metric(raw_metric, source_system)
    
    def _parse_json_metric(self, raw_metric: str, source_system: str) -> Dict[str, Any]:
        """Parse JSON formatted metric."""
        try:
            data = json.loads(raw_metric)
            
            metric_type = self._extract_metric_type(data)
            metric_value = self._extract_metric_value(data)
            unit = self._extract_unit(data, metric_type)
            timestamp = self._extract_timestamp(data)
            
            return {
                'source_system': source_system,
                'metric_type': metric_type,
                'metric_value': metric_value,
                'unit': unit,
                'timestamp': timestamp or datetime.utcnow(),
                'raw_data': raw_metric,
                'normalized_data': json.dumps(data),
                'metadata': json.dumps({'format': 'json'})
            }
        except json.JSONDecodeError:
            return self._parse_numeric_metric(raw_metric, source_system)
    
    def _parse_kv_metric(self, raw_metric: str, source_system: str) -> Dict[str, Any]:
        """Parse key=value format metric."""
        parts = raw_metric.split(',')
        data = {}
        
        for part in parts:
            if '=' in part:
                key, value = part.split('=', 1)
                data[key.strip()] = value.strip()
        
        metric_type = data.get('type', data.get('metric_type', 'CPU'))
        metric_value = self._parse_number(data.get('value', data.get('metric_value', '0')))
        unit = data.get('unit', self.UNITS.get(metric_type, '%'))
        timestamp = self._parse_timestamp(data.get('timestamp', data.get('time')))
        
        return {
            'source_system': source_system,
            'metric_type': metric_type,
            'metric_value': metric_value,
            'unit': unit,
            'timestamp': timestamp or datetime.utcnow(),
            'raw_data': raw_metric,
            'normalized_data': json.dumps(data),
            'metadata': json.dumps({'format': 'kv'})
        }
    
    def _parse_numeric_metric(self, raw_metric: str, source_system: str) -> Dict[str, Any]:
        """Parse numeric value from raw metric."""
        # Extract first number found
        numbers = re.findall(r'[-+]?\d*\.?\d+', raw_metric)
        
        if numbers:
            metric_value = float(numbers[0])
        else:
            metric_value = 0.0
        
        # Infer metric type from context
        metric_type = self._infer_metric_type(raw_metric)
        unit = self.UNITS.get(metric_type, '%')
        
        return {
            'source_system': source_system,
            'metric_type': metric_type,
            'metric_value': metric_value,
            'unit': unit,
            'timestamp': datetime.utcnow(),
            'raw_data': raw_metric,
            'normalized_data': json.dumps({'value': metric_value}),
            'metadata': json.dumps({'format': 'numeric'})
        }
    
    def _extract_metric_type(self, data: Dict[str, Any]) -> str:
        """Extract metric type from data."""
        type_fields = ['type', 'metric_type', 'name', 'metric']
        
        for field in type_fields:
            if field in data:
                metric_type = str(data[field]).upper()
                if metric_type in self.METRIC_TYPES:
                    return metric_type
        
        return 'CPU'  # Default
    
    def _extract_metric_value(self, data: Dict[str, Any]) -> float:
        """Extract metric value from data."""
        value_fields = ['value', 'metric_value', 'val', 'reading']
        
        for field in value_fields:
            if field in data:
                return self._parse_number(data[field])
        
        return 0.0
    
    def _extract_unit(self, data: Dict[str, Any], metric_type: str) -> str:
        """Extract unit from data or use default."""
        if 'unit' in data:
            return str(data['unit'])
        return self.UNITS.get(metric_type, '%')
    
    def _extract_timestamp(self, data: Dict[str, Any]) -> Optional[datetime]:
        """Extract timestamp from data."""
        timestamp_fields = ['timestamp', 'time', 'date', '@timestamp']
        
        for field in timestamp_fields:
            if field in data:
                return self._parse_timestamp(data[field])
        
        return None
    
    def _parse_number(self, value: Any) -> float:
        """Parse value as float."""
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0.0
    
    def _parse_timestamp(self, timestamp_str: Any) -> Optional[datetime]:
        """Parse timestamp string."""
        if isinstance(timestamp_str, datetime):
            return timestamp_str
        
        if isinstance(timestamp_str, (int, float)):
            try:
                return datetime.fromtimestamp(timestamp_str)
            except (ValueError, TypeError):
                return None
        
        if isinstance(timestamp_str, str):
            formats = [
                '%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%dT%H:%M:%S.%f',
                '%Y-%m-%dT%H:%M:%SZ',
                '%Y-%m-%dT%H:%M:%S.%fZ',
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%d %H:%M:%S.%f'
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(timestamp_str, fmt)
                except ValueError:
                    continue
        
        return None
    
    def _infer_metric_type(self, text: str) -> str:
        """Infer metric type from text content."""
        text_lower = text.lower()
        
        if any(keyword in text_lower for keyword in ['cpu', 'processor']):
            return 'CPU'
        elif any(keyword in text_lower for keyword in ['memory', 'ram', 'mem']):
            return 'Memory'
        elif any(keyword in text_lower for keyword in ['disk', 'storage', 'space']):
            return 'Disk'
        elif any(keyword in text_lower for keyword in ['network', 'bandwidth', 'latency']):
            return 'Network'
        
        return 'CPU'  # Default
