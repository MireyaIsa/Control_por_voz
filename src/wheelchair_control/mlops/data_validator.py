"""
Data Validator
==============

Validación de datos usando Great Expectations.
"""

import pandas as pd
from typing import Dict, Any, Optional, List
from pathlib import Path
import json
from datetime import datetime


class DataValidator:
    """
    Validador de datos para comandos de voz y telemetría.
    """
    
    def __init__(self, validation_rules_path: Optional[Path] = None):
        """
        Inicializar validador.
        
        Args:
            validation_rules_path: Ruta a archivo con reglas de validación
        """
        self.validation_rules = self._load_validation_rules(validation_rules_path)
        self.validation_results = []
    
    def _load_validation_rules(self, rules_path: Optional[Path]) -> Dict[str, Any]:
        """Cargar reglas de validación desde archivo."""
        if rules_path and rules_path.exists():
            with open(rules_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # Reglas por defecto
        return {
            "voice_commands": {
                "required_fields": ["command", "timestamp", "recognized", "confidence"],
                "confidence_range": [0.0, 1.0],
                "valid_commands": [
                    "adelante", "atrás", "izquierda", "derecha",
                    "adelante derecha", "adelante izquierda",
                    "atrás derecha", "atrás izquierda",
                    "detener", "alto", "parar", "stop"
                ]
            },
            "joystick_data": {
                "required_fields": ["angle", "magnitude", "timestamp"],
                "angle_range": [0.0, 360.0],
                "magnitude_range": [0.0, 1.0]
            },
            "connection_data": {
                "required_fields": ["connection_type", "status", "timestamp"],
                "valid_connection_types": ["serial", "bluetooth"],
                "valid_statuses": ["connected", "disconnected", "error"]
            }
        }
    
    def validate_voice_command(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validar datos de comando de voz.
        
        Args:
            data: Diccionario con datos del comando
            
        Returns:
            Resultado de validación
        """
        rules = self.validation_rules["voice_commands"]
        errors = []
        warnings = []
        
        # Validar campos requeridos
        for field in rules["required_fields"]:
            if field not in data:
                errors.append(f"Campo requerido faltante: {field}")
        
        # Validar confianza
        if "confidence" in data:
            conf = data["confidence"]
            min_conf, max_conf = rules["confidence_range"]
            if not (min_conf <= conf <= max_conf):
                errors.append(f"Confianza fuera de rango: {conf} (esperado: {min_conf}-{max_conf})")
        
        # Validar comando
        if "command" in data:
            cmd = data["command"].lower()
            valid_cmds = rules["valid_commands"]
            # Verificar si contiene algún comando válido
            if not any(valid_cmd in cmd for valid_cmd in valid_cmds):
                warnings.append(f"Comando no reconocido: {cmd}")
        
        result = {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "timestamp": datetime.now().isoformat(),
            "data_type": "voice_command"
        }
        
        self.validation_results.append(result)
        return result
    
    def validate_joystick_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validar datos de joystick.
        
        Args:
            data: Diccionario con datos del joystick
            
        Returns:
            Resultado de validación
        """
        rules = self.validation_rules["joystick_data"]
        errors = []
        warnings = []
        
        # Validar campos requeridos
        for field in rules["required_fields"]:
            if field not in data:
                errors.append(f"Campo requerido faltante: {field}")
        
        # Validar ángulo
        if "angle" in data:
            angle = data["angle"]
            min_angle, max_angle = rules["angle_range"]
            if not (min_angle <= angle <= max_angle):
                errors.append(f"Ángulo fuera de rango: {angle} (esperado: {min_angle}-{max_angle})")
        
        # Validar magnitud
        if "magnitude" in data:
            mag = data["magnitude"]
            min_mag, max_mag = rules["magnitude_range"]
            if not (min_mag <= mag <= max_mag):
                errors.append(f"Magnitud fuera de rango: {mag} (esperado: {min_mag}-{max_mag})")
        
        result = {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "timestamp": datetime.now().isoformat(),
            "data_type": "joystick_data"
        }
        
        self.validation_results.append(result)
        return result
    
    def validate_connection_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validar datos de conexión.
        
        Args:
            data: Diccionario con datos de conexión
            
        Returns:
            Resultado de validación
        """
        rules = self.validation_rules["connection_data"]
        errors = []
        warnings = []
        
        # Validar campos requeridos
        for field in rules["required_fields"]:
            if field not in data:
                errors.append(f"Campo requerido faltante: {field}")
        
        # Validar tipo de conexión
        if "connection_type" in data:
            conn_type = data["connection_type"]
            if conn_type not in rules["valid_connection_types"]:
                errors.append(f"Tipo de conexión inválido: {conn_type}")
        
        # Validar estado
        if "status" in data:
            status = data["status"]
            if status not in rules["valid_statuses"]:
                errors.append(f"Estado inválido: {status}")
        
        result = {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "timestamp": datetime.now().isoformat(),
            "data_type": "connection_data"
        }
        
        self.validation_results.append(result)
        return result
    
    def validate_dataframe(self, df: pd.DataFrame, data_type: str) -> Dict[str, Any]:
        """
        Validar un DataFrame completo.
        
        Args:
            df: DataFrame a validar
            data_type: Tipo de datos (voice_commands, joystick_data, connection_data)
            
        Returns:
            Resumen de validación
        """
        results = []
        
        for idx, row in df.iterrows():
            data = row.to_dict()
            
            if data_type == "voice_commands":
                result = self.validate_voice_command(data)
            elif data_type == "joystick_data":
                result = self.validate_joystick_data(data)
            elif data_type == "connection_data":
                result = self.validate_connection_data(data)
            else:
                result = {"valid": False, "errors": [f"Tipo de datos desconocido: {data_type}"]}
            
            results.append(result)
        
        # Resumen
        total = len(results)
        valid = sum(1 for r in results if r["valid"])
        invalid = total - valid
        
        summary = {
            "total_records": total,
            "valid_records": valid,
            "invalid_records": invalid,
            "validation_rate": valid / total if total > 0 else 0.0,
            "timestamp": datetime.now().isoformat(),
            "data_type": data_type
        }
        
        return summary
    
    def get_validation_report(self) -> Dict[str, Any]:
        """
        Obtener reporte de todas las validaciones.
        
        Returns:
            Reporte completo
        """
        if not self.validation_results:
            return {"message": "No hay validaciones registradas"}
        
        total = len(self.validation_results)
        valid = sum(1 for r in self.validation_results if r["valid"])
        
        return {
            "total_validations": total,
            "valid": valid,
            "invalid": total - valid,
            "success_rate": valid / total if total > 0 else 0.0,
            "results": self.validation_results
        }
    
    def save_validation_report(self, output_path: Path):
        """
        Guardar reporte de validación.
        
        Args:
            output_path: Ruta del archivo de salida
        """
        report = self.get_validation_report()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Reporte guardado: {output_path}")


# Ejemplo de uso
if __name__ == "__main__":
    validator = DataValidator()
    
    # Validar comando de voz
    voice_data = {
        "command": "adelante rápido",
        "timestamp": datetime.now().isoformat(),
        "recognized": True,
        "confidence": 0.95
    }
    
    result = validator.validate_voice_command(voice_data)
    print(f"Validación: {'✓ Válido' if result['valid'] else '✗ Inválido'}")
    
    if result['errors']:
        print(f"Errores: {result['errors']}")
    if result['warnings']:
        print(f"Advertencias: {result['warnings']}")
