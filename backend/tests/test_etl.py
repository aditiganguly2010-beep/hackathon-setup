import pytest
from app.etl.log_parser import LogParser
from app.etl.metric_parser import MetricParser
from app.etl.noise_filter import NoiseFilter


class TestLogParser:
    """Test cases for the LogParser class."""
    
    def test_parse_json_log(self):
        """Test parsing a JSON-formatted log."""
        parser = LogParser()
        log_data = '{"timestamp": "2024-01-01T00:00:00", "level": "INFO", "message": "Test log"}'
        result = parser.parse_log(log_data, "legacy-crm")
        assert result is not None
        assert result["log_level"] == "INFO"
        assert result["message"] == "Test log"
    
    def test_parse_syslog(self):
        """Test parsing a syslog-formatted log."""
        parser = LogParser()
        log_data = "Jan 1 00:00:00 server process[123]: INFO Test log message"
        result = parser.parse_log(log_data, "legacy-crm")
        assert result is not None
        assert "message" in result
    
    def test_parse_plain_text_log(self):
        """Test parsing a plain text log."""
        parser = LogParser()
        log_data = "2024-01-01 00:00:00 INFO Test log message"
        result = parser.parse_log(log_data, "legacy-crm")
        assert result is not None
        assert "message" in result
    
    def test_infer_log_level(self):
        """Test inferring log level from message content."""
        parser = LogParser()
        assert parser._infer_log_level("This is an ERROR message") == "ERROR"
        assert parser._infer_log_level("WARNING: something happened") == "WARNING"
        assert parser._infer_log_level("Just a normal message") == "INFO"


class TestMetricParser:
    """Test cases for the MetricParser class."""
    
    def test_parse_json_metric(self):
        """Test parsing a JSON-formatted metric."""
        parser = MetricParser()
        metric_data = '{"timestamp": "2024-01-01T00:00:00", "metric_type": "CPU", "value": 75.5, "unit": "%"}'
        result = parser.parse_metric(metric_data, "legacy-crm")
        assert result is not None
        assert result["metric_type"] == "CPU"
        assert result["metric_value"] == 75.5
    
    def test_parse_key_value_metric(self):
        """Test parsing a key-value formatted metric."""
        parser = MetricParser()
        metric_data = "cpu_usage=75.5% memory_usage=80.0%"
        result = parser.parse_metric(metric_data, "legacy-crm")
        assert result is not None
        assert "metric_type" in result
    
    def test_parse_numeric_metric(self):
        """Test parsing a numeric metric."""
        parser = MetricParser()
        metric_data = "75.5"
        result = parser.parse_metric(metric_data, "legacy-crm")
        assert result is not None
        assert result["metric_value"] == 75.5
    
    def test_infer_metric_type(self):
        """Test inferring metric type from data."""
        parser = MetricParser()
        assert parser._infer_metric_type("cpu_usage=75.5") == "CPU"
        assert parser._infer_metric_type("mem_usage=80.0") == "Memory"


class TestNoiseFilter:
    """Test cases for the NoiseFilter class."""
    
    def test_filter_noisy_log(self):
        """Test filtering out noisy log entries."""
        filter = NoiseFilter()
        noisy_log = {
            "log_level": "DEBUG",
            "message": "Routine health check completed successfully"
        }
        assert filter.should_filter_log(noisy_log) == True
    
    def test_keep_important_log(self):
        """Test keeping important log entries."""
        filter = NoiseFilter()
        important_log = {
            "log_level": "ERROR",
            "message": "Database connection failed"
        }
        assert filter.should_filter_log(important_log) == False
    
    def test_filter_noisy_metric(self):
        """Test filtering out noisy metric entries."""
        filter = NoiseFilter()
        noisy_metric = {
            "metric_type": "CPU",
            "metric_value": 0.0
        }
        assert filter.should_filter_metric(noisy_metric) == False  # Zero values are not filtered by default
    
    def test_keep_important_metric(self):
        """Test keeping important metric entries."""
        filter = NoiseFilter()
        important_metric = {
            "metric_type": "CPU",
            "metric_value": 95.5
        }
        assert filter.should_filter_metric(important_metric) == False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
