"""
Pytest Configuration
====================

Configuración y fixtures para tests.
"""

import pytest
from pathlib import Path
import tempfile
import shutil


@pytest.fixture
def temp_dir():
    """Crear directorio temporal para tests."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def sample_voice_command():
    """Comando de voz de ejemplo."""
    return {
        "command": "adelante rápido",
        "timestamp": "2026-01-21T22:00:00",
        "recognized": True,
        "confidence": 0.95,
        "engine": "vosk"
    }


@pytest.fixture
def sample_joystick_data():
    """Datos de joystick de ejemplo."""
    return {
        "angle": 45.0,
        "magnitude": 0.8,
        "timestamp": "2026-01-21T22:00:00"
    }


@pytest.fixture
def sample_connection_data():
    """Datos de conexión de ejemplo."""
    return {
        "connection_type": "serial",
        "status": "connected",
        "timestamp": "2026-01-21T22:00:00"
    }


@pytest.fixture
def mock_mlflow_tracker(mocker):
    """Mock de MLflow tracker."""
    mock = mocker.patch('src.wheelchair_control.mlops.mlflow_tracker.mlflow')
    return mock


@pytest.fixture
def mock_serial_connection(mocker):
    """Mock de conexión serial."""
    mock = mocker.patch('serial.Serial')
    return mock
