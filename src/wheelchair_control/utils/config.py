"""
Configuration Utility
=====================

Gestión de configuración del proyecto.
"""

import yaml
from pathlib import Path
from typing import Any, Dict, Optional
import os
from dotenv import load_dotenv


class Config:
    """
    Clase para gestionar configuración del proyecto.
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Inicializar configuración.
        
        Args:
            config_path: Ruta al archivo de configuración YAML
        """
        self._config = {}
        
        # Cargar variables de entorno
        load_dotenv()
        
        # Cargar configuración desde archivo
        if config_path and config_path.exists():
            self.load_from_file(config_path)
    
    def load_from_file(self, config_path: Path):
        """
        Cargar configuración desde archivo YAML.
        
        Args:
            config_path: Ruta al archivo de configuración
        """
        with open(config_path, 'r', encoding='utf-8') as f:
            self._config = yaml.safe_load(f)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Obtener valor de configuración.
        
        Args:
            key: Clave de configuración (soporta notación punto: 'mlflow.tracking_uri')
            default: Valor por defecto si no existe
            
        Returns:
            Valor de configuración
        """
        # Intentar obtener de variables de entorno primero
        env_key = key.upper().replace('.', '_')
        env_value = os.getenv(env_key)
        if env_value is not None:
            return env_value
        
        # Obtener de configuración
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """
        Establecer valor de configuración.
        
        Args:
            key: Clave de configuración
            value: Valor a establecer
        """
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convertir configuración a diccionario.
        
        Returns:
            Diccionario con configuración
        """
        return self._config.copy()
    
    def save(self, output_path: Path):
        """
        Guardar configuración a archivo.
        
        Args:
            output_path: Ruta del archivo de salida
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(self._config, f, default_flow_style=False, allow_unicode=True)


def load_config(config_name: str = "model_config") -> Config:
    """
    Cargar configuración desde archivo.
    
    Args:
        config_name: Nombre del archivo de configuración (sin extensión)
        
    Returns:
        Objeto Config
    """
    # Buscar en directorio config
    config_path = Path("config") / f"{config_name}.yaml"
    
    if not config_path.exists():
        # Buscar en directorio raíz
        config_path = Path(f"{config_name}.yaml")
    
    if not config_path.exists():
        print(f"⚠ Archivo de configuración no encontrado: {config_name}.yaml")
        return Config()
    
    return Config(config_path)


# Cargar configuraciones por defecto
mlflow_config = load_config("mlflow_config")
model_config = load_config("model_config")
