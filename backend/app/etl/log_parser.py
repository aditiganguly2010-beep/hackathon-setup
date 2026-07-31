"""
Log parser for ETL pipeline.
Handles parsing and normalization of various log formats.
"""
import json
import re
from datetime import datetime
from typing import Dict, Any, Optional
from app.core.logging import get_logger

logger = get_logger(__name__)


class LogParser:
    """Parser for various log formats."""
    
    # Common log patterns
    PATTERNS = {
        'json': r'^\s*\{.*\}\s*$',
        'syslog': r'^(\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+(\S+)\s+(\S+):\s*(.*)$',
        'apache': r'^(\S+)\s+(\S+)\s+(\S+)\s+\[([^\]]+)\]\s+"(\S+)\s+(\S+)\s+(\S+)"\s+(\d+)\s+(\d+)$',
        'generic': r'^(\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2})\s*\[?(\w+)\]?\s*(.*)$'
    }
    
    def __init__(self):
        self.compiled_patterns = {
            key: re.compile(pattern) 
            for key, pattern in self.PATTERNS.items()
        }
    
    def parse_log(self, raw_log: str, source_system: str) -> Dict[str, Any]:
        """
        Parse a raw log string into normalized format.
        
        Args:
            raw_log: Raw log string
            source_system: Source system identifier
            
        Returns:
            Normalized log data as dictionary
        """
        try:
            # Try JSON format first
            if self.compiled_patterns['json'].match(raw_log.strip()):
                return self._parse_json_log(raw_log, source_system)
            
            # Try syslog format
            match = self.compiled_patterns['syslog'].match(raw_log.strip())
            if match:
                return self._parse_syslog(match, source_system)
            
            # Try generic timestamp format
            match = self.compiled_patterns['generic'].match(raw_log.strip())
            if match:
                return self._parse_generic_log(match, source_system)
            
            # Fallback: treat as plain text
            return self._parse_plain_text(raw_log, source_system)
            
        except Exception as e:
            logger.error("Error parsing log", extra_data={
                "error": str(e),
                "raw_log": raw_log[:200]
            })
            return self._parse_plain_text(raw_log, source_system)
    
    def _parse_json_log(self, raw_log: str, source_system: str) -> Dict[str, Any]:
        """Parse JSON formatted log."""
        try:
            data = json.loads(raw_log)
            
            # Extract common fields
            timestamp = self._extract_timestamp(data)
            log_level = self._extract_log_level(data)
            message = self._extract_message(data)
            
            return {
                'source_system': source_system,
                'log_level': log_level or 'INFO',
                'message': message or raw_log,
                'timestamp': timestamp or datetime.utcnow(),
                'raw_data': raw_log,
                'normalized_data': json.dumps(data),
                'metadata': json.dumps({'format': 'json'})
            }
        except json.JSONDecodeError:
            return self._parse_plain_text(raw_log, source_system)
    
    def _parse_syslog(self, match: re.Match, source_system: str) -> Dict[str, Any]:
        """Parse syslog format."""
        timestamp_str = match.group(1)
        hostname = match.group(2)
        process = match.group(3)
        message = match.group(4)
        
        timestamp = self._parse_syslog_timestamp(timestamp_str)
        log_level = self._infer_log_level(message)
        
        return {
            'source_system': source_system,
            'log_level': log_level,
            'message': message,
            'timestamp': timestamp or datetime.utcnow(),
            'raw_data': match.group(0),
            'normalized_data': json.dumps({
                'hostname': hostname,
                'process': process,
                'message': message
            }),
            'metadata': json.dumps({'format': 'syslog', 'hostname': hostname, 'process': process})
        }
    
    def _parse_generic_log(self, match: re.Match, source_system: str) -> Dict[str, Any]:
        """Parse generic timestamp format."""
        timestamp_str = match.group(1)
        log_level = match.group(2)
        message = match.group(3)
        
        timestamp = self._parse_generic_timestamp(timestamp_str)
        
        return {
            'source_system': source_system,
            'log_level': log_level or 'INFO',
            'message': message,
            'timestamp': timestamp or datetime.utcnow(),
            'raw_data': match.group(0),
            'normalized_data': json.dumps({'message': message}),
            'metadata': json.dumps({'format': 'generic'})
        }
    
    def _parse_plain_text(self, raw_log: str, source_system: str) -> Dict[str, Any]:
        """Parse plain text log as fallback."""
        log_level = self._infer_log_level(raw_log)
        
        return {
            'source_system': source_system,
            'log_level': log_level,
            'message': raw_log.strip(),
            'timestamp': datetime.utcnow(),
            'raw_data': raw_log,
            'normalized_data': json.dumps({'message': raw_log.strip()}),
            'metadata': json.dumps({'format': 'plain'})
        }
    
    def _extract_timestamp(self, data: Dict[str, Any]) -> Optional[datetime]:
        """Extract timestamp from JSON data."""
        timestamp_fields = ['timestamp', 'time', 'date', '@timestamp', 'created_at']
        
        for field in timestamp_fields:
            if field in data:
                try:
                    timestamp_str = data[field]
                    if isinstance(timestamp_str, (int, float)):
                        return datetime.fromtimestamp(timestamp_str)
                    return self._parse_iso_timestamp(timestamp_str)
                except (ValueError, TypeError):
                    continue
        
        return None
    
    def _extract_log_level(self, data: Dict[str, Any]) -> Optional[str]:
        """Extract log level from JSON data."""
        level_fields = ['level', 'severity', 'log_level', 'priority']
        
        for field in level_fields:
            if field in data:
                level = str(data[field]).upper()
                if level in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
                    return level
        
        return None
    
    def _extract_message(self, data: Dict[str, Any]) -> Optional[str]:
        """Extract message from JSON data."""
        message_fields = ['message', 'msg', 'text', 'description']
        
        for field in message_fields:
            if field in data:
                return str(data[field])
        
        return None
    
    def _infer_log_level(self, message: str) -> str:
        """Infer log level from message content."""
        message_lower = message.lower()
        
        if any(keyword in message_lower for keyword in ['critical', 'fatal', 'emergency']):
            return 'CRITICAL'
        elif any(keyword in message_lower for keyword in ['error', 'exception', 'fail']):
            return 'ERROR'
        elif any(keyword in message_lower for keyword in ['warning', 'warn']):
            return 'WARNING'
        else:
            return 'INFO'
    
    def _parse_iso_timestamp(self, timestamp_str: str) -> Optional[datetime]:
        """Parse ISO format timestamp."""
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
    
    def _parse_syslog_timestamp(self, timestamp_str: str) -> Optional[datetime]:
        """Parse syslog timestamp format."""
        # Syslog format: MMM DD HH:MM:SS
        try:
            # This is simplified - in production, you'd handle year inference
            current_year = datetime.utcnow().year
            return datetime.strptime(f"{current_year} {timestamp_str}", '%Y %b %d %H:%M:%S')
        except ValueError:
            return None
    
    def _parse_generic_timestamp(self, timestamp_str: str) -> Optional[datetime]:
        """Parse generic timestamp."""
        return self._parse_iso_timestamp(timestamp_str)
