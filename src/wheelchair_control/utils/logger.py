"""
Logger Utility
==============

Sistema de logging centralizado para el proyecto.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


def setup_logger(
    name: str = "wheelchair_control",
    level: str = "INFO",
    log_file: Optional[Path] = None,
    console: bool = True,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    Configurar logger para el proyecto.
    
    Args:
        name: Nombre del logger
        level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Ruta del archivo de log (opcional)
        console: Si mostrar logs en consola
        format_string: Formato personalizado de logs
        
    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Evitar duplicar handlers
    if logger.handlers:
        return logger
    
    # Formato por defecto
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    formatter = logging.Formatter(format_string)
    
    # Handler de consola
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, level.upper()))
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # Handler de archivo
    if log_file:
        # Crear directorio si no existe
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(getattr(logging, level.upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = "wheelchair_control") -> logging.Logger:
    """
    Obtener logger existente.
    
    Args:
        name: Nombre del logger
        
    Returns:
        Logger
    """
    return logging.getLogger(name)


class LoggerMixin:
    """
    Mixin para agregar logging a clases.
    """
    
    @property
    def logger(self) -> logging.Logger:
        """Obtener logger para la clase."""
        name = f"wheelchair_control.{self.__class__.__name__}"
        return get_logger(name)
    
    def log_debug(self, message: str):
        """Log debug."""
        self.logger.debug(message)
    
    def log_info(self, message: str):
        """Log info."""
        self.logger.info(message)
    
    def log_warning(self, message: str):
        """Log warning."""
        self.logger.warning(message)
    
    def log_error(self, message: str, exc_info: bool = False):
        """Log error."""
        self.logger.error(message, exc_info=exc_info)
    
    def log_critical(self, message: str, exc_info: bool = False):
        """Log critical."""
        self.logger.critical(message, exc_info=exc_info)


# Configurar logger por defecto
default_logger = setup_logger(
    name="wheelchair_control",
    level="INFO",
    log_file=Path("logs") / f"wheelchair_{datetime.now().strftime('%Y%m%d')}.log",
    console=True
)
