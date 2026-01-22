"""
Tests for Data Validator
=========================

Tests para el módulo de validación de datos.
"""

import pytest
from src.wheelchair_control.mlops.data_validator import DataValidator


class TestDataValidator:
    """Tests para DataValidator."""
    
    def test_validate_voice_command_valid(self, sample_voice_command):
        """Test validación de comando de voz válido."""
        validator = DataValidator()
        result = validator.validate_voice_command(sample_voice_command)
        assert result["valid"] is True
        assert len(result["errors"]) == 0
    
    def test_validate_voice_command_missing_field(self):
        """Test validación con campo faltante."""
        validator = DataValidator()
        data = {
            "command": "adelante",
            "timestamp": "2026-01-21T22:00:00"
            # Falta 'recognized' y 'confidence'
        }
        result = validator.validate_voice_command(data)
        assert result["valid"] is False
        assert len(result["errors"]) > 0
    
    def test_validate_voice_command_invalid_confidence(self):
        """Test validación con confianza inválida."""
        validator = DataValidator()
        data = {
            "command": "adelante",
            "timestamp": "2026-01-21T22:00:00",
            "recognized": True,
            "confidence": 1.5  # Fuera de rango
        }
        result = validator.validate_voice_command(data)
        assert result["valid"] is False
    
    def test_validate_joystick_data_valid(self, sample_joystick_data):
        """Test validación de datos de joystick válidos."""
        validator = DataValidator()
        result = validator.validate_joystick_data(sample_joystick_data)
        assert result["valid"] is True
        assert len(result["errors"]) == 0
    
    def test_validate_joystick_data_invalid_angle(self):
        """Test validación con ángulo inválido."""
        validator = DataValidator()
        data = {
            "angle": 400.0,  # Fuera de rango
            "magnitude": 0.5,
            "timestamp": "2026-01-21T22:00:00"
        }
        result = validator.validate_joystick_data(data)
        assert result["valid"] is False
    
    def test_validate_connection_data_valid(self, sample_connection_data):
        """Test validación de datos de conexión válidos."""
        validator = DataValidator()
        result = validator.validate_connection_data(sample_connection_data)
        assert result["valid"] is True
        assert len(result["errors"]) == 0
    
    def test_get_validation_report(self, sample_voice_command):
        """Test obtención de reporte de validación."""
        validator = DataValidator()
        validator.validate_voice_command(sample_voice_command)
        validator.validate_voice_command(sample_voice_command)
        
        report = validator.get_validation_report()
        assert report["total_validations"] == 2
        assert report["valid"] == 2
