"""
Sistema de Control por Voz para Silla de Ruedas
================================================

Sistema avanzado de control por voz con arquitectura MLOps completa.

Módulos:
    - core: Funcionalidad principal (conexión, joystick, voz)
    - ml: Machine Learning (entrenamiento, evaluación)
    - mlops: MLOps (tracking, validación, monitoreo)
    - utils: Utilidades (logging, configuración)
"""

__version__ = "3.0.0"
__author__ = "Maestría en Inteligencia Artificial"

from .main import AdvancedWheelchairController, main

__all__ = ["AdvancedWheelchairController", "main"]
