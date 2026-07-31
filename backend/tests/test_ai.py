import pytest
import numpy as np
from app.ai.anomaly_detector import AnomalyDetector


class TestAnomalyDetector:
    """Test cases for the AnomalyDetector class."""
    
    def test_initialization(self):
        """Test that AnomalyDetector initializes correctly."""
        detector = AnomalyDetector()
        assert detector is not None
        assert hasattr(detector, 'metric_scaler')
        assert hasattr(detector, 'log_scaler')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
