"""
Tests for MLflow Integration
=============================

Tests para el módulo de integración con MLflow.
"""

import pytest
from src.wheelchair_control.mlops.mlflow_tracker import MLflowTracker


class TestMLflowTracker:
    """Tests para MLflowTracker."""
    
    def test_initialization(self, mock_mlflow_tracker):
        """Test inicialización del tracker."""
        tracker = MLflowTracker(experiment_name="test_experiment")
        assert tracker.experiment_name == "test_experiment"
    
    def test_log_param(self, mock_mlflow_tracker):
        """Test registro de parámetro."""
        tracker = MLflowTracker()
        tracker.log_param("test_param", "test_value")
        mock_mlflow_tracker.log_param.assert_called_once()
    
    def test_log_metric(self, mock_mlflow_tracker):
        """Test registro de métrica."""
        tracker = MLflowTracker()
        tracker.log_metric("accuracy", 0.95)
        mock_mlflow_tracker.log_metric.assert_called_once()
    
    def test_log_voice_command_metrics(self, mock_mlflow_tracker):
        """Test registro de métricas de comando de voz."""
        tracker = MLflowTracker()
        tracker.log_voice_command_metrics(
            command="adelante",
            recognized=True,
            confidence=0.95,
            latency_ms=150,
            engine="vosk"
        )
        assert mock_mlflow_tracker.log_params.called
        assert mock_mlflow_tracker.log_metrics.called
    
    def test_log_connection_metrics(self, mock_mlflow_tracker):
        """Test registro de métricas de conexión."""
        tracker = MLflowTracker()
        tracker.log_connection_metrics(
            connection_type="serial",
            connection_time_ms=100,
            success=True
        )
        assert mock_mlflow_tracker.log_params.called
        assert mock_mlflow_tracker.log_metrics.called
    
    def test_flatten_dict(self):
        """Test aplanado de diccionario."""
        tracker = MLflowTracker()
        nested = {
            "a": {
                "b": {
                    "c": 1
                },
                "d": 2
            },
            "e": 3
        }
        flat = tracker._flatten_dict(nested)
        assert flat == {
            "a.b.c": 1,
            "a.d": 2,
            "e": 3
        }
