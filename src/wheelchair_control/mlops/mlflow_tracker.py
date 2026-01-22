"""
MLflow Tracker
==============

Integración con MLflow para seguimiento de experimentos, métricas y modelos.
"""

import mlflow
import mlflow.sklearn
import mlflow.pytorch
from pathlib import Path
from typing import Dict, Any, Optional, Union
import yaml
import os
from datetime import datetime


class MLflowTracker:
    """
    Clase para gestionar el seguimiento de experimentos con MLflow.
    
    Permite registrar parámetros, métricas, artefactos y modelos de forma
    estructurada y consistente.
    """
    
    def __init__(
        self,
        experiment_name: str = "wheelchair_voice_control",
        tracking_uri: Optional[str] = None,
        artifact_location: Optional[str] = None
    ):
        """
        Inicializar MLflow Tracker.
        
        Args:
            experiment_name: Nombre del experimento
            tracking_uri: URI del servidor de tracking (default: sqlite local)
            artifact_location: Ubicación para almacenar artefactos
        """
        self.experiment_name = experiment_name
        
        # Configurar tracking URI
        if tracking_uri is None:
            tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "sqlite:///mlflow.db")
        mlflow.set_tracking_uri(tracking_uri)
        
        # Crear o obtener experimento
        try:
            experiment = mlflow.get_experiment_by_name(experiment_name)
            if experiment is None:
                experiment_id = mlflow.create_experiment(
                    experiment_name,
                    artifact_location=artifact_location
                )
            else:
                experiment_id = experiment.experiment_id
            
            mlflow.set_experiment(experiment_name)
            self.experiment_id = experiment_id
            print(f"✓ MLflow experiment: {experiment_name} (ID: {experiment_id})")
            
        except Exception as e:
            print(f"⚠ Error configurando MLflow: {e}")
            self.experiment_id = None
    
    def start_run(
        self,
        run_name: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ):
        """
        Iniciar un nuevo run de MLflow.
        
        Args:
            run_name: Nombre del run
            tags: Tags adicionales para el run
            
        Returns:
            Contexto del run de MLflow
        """
        if run_name is None:
            run_name = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        default_tags = {
            "project": "wheelchair_voice_control",
            "version": "3.0.0"
        }
        
        if tags:
            default_tags.update(tags)
        
        return mlflow.start_run(run_name=run_name, tags=default_tags)
    
    def log_param(self, key: str, value: Any):
        """Registrar un parámetro."""
        try:
            mlflow.log_param(key, value)
        except Exception as e:
            print(f"⚠ Error logging param {key}: {e}")
    
    def log_params(self, params: Dict[str, Any]):
        """Registrar múltiples parámetros."""
        try:
            mlflow.log_params(params)
        except Exception as e:
            print(f"⚠ Error logging params: {e}")
    
    def log_metric(self, key: str, value: float, step: Optional[int] = None):
        """Registrar una métrica."""
        try:
            mlflow.log_metric(key, value, step=step)
        except Exception as e:
            print(f"⚠ Error logging metric {key}: {e}")
    
    def log_metrics(self, metrics: Dict[str, float], step: Optional[int] = None):
        """Registrar múltiples métricas."""
        try:
            mlflow.log_metrics(metrics, step=step)
        except Exception as e:
            print(f"⚠ Error logging metrics: {e}")
    
    def log_artifact(self, local_path: Union[str, Path], artifact_path: Optional[str] = None):
        """
        Registrar un artefacto (archivo).
        
        Args:
            local_path: Ruta local del archivo
            artifact_path: Ruta dentro del almacén de artefactos
        """
        try:
            mlflow.log_artifact(str(local_path), artifact_path)
        except Exception as e:
            print(f"⚠ Error logging artifact {local_path}: {e}")
    
    def log_artifacts(self, local_dir: Union[str, Path], artifact_path: Optional[str] = None):
        """
        Registrar múltiples artefactos (directorio).
        
        Args:
            local_dir: Directorio local
            artifact_path: Ruta dentro del almacén de artefactos
        """
        try:
            mlflow.log_artifacts(str(local_dir), artifact_path)
        except Exception as e:
            print(f"⚠ Error logging artifacts from {local_dir}: {e}")
    
    def log_model(
        self,
        model: Any,
        artifact_path: str,
        registered_model_name: Optional[str] = None,
        **kwargs
    ):
        """
        Registrar un modelo.
        
        Args:
            model: Modelo a registrar
            artifact_path: Ruta del artefacto
            registered_model_name: Nombre para registro en Model Registry
            **kwargs: Argumentos adicionales para mlflow.log_model
        """
        try:
            # Detectar tipo de modelo y usar el método apropiado
            model_type = type(model).__module__
            
            if "sklearn" in model_type:
                mlflow.sklearn.log_model(
                    model,
                    artifact_path,
                    registered_model_name=registered_model_name,
                    **kwargs
                )
            elif "torch" in model_type or "pytorch" in model_type:
                mlflow.pytorch.log_model(
                    model,
                    artifact_path,
                    registered_model_name=registered_model_name,
                    **kwargs
                )
            else:
                # Usar pyfunc para modelos genéricos
                mlflow.pyfunc.log_model(
                    artifact_path,
                    python_model=model,
                    registered_model_name=registered_model_name,
                    **kwargs
                )
            
            print(f"✓ Modelo registrado: {artifact_path}")
            
        except Exception as e:
            print(f"⚠ Error logging model: {e}")
    
    def log_voice_command_metrics(
        self,
        command: str,
        recognized: bool,
        confidence: float,
        latency_ms: float,
        engine: str
    ):
        """
        Registrar métricas específicas de comandos de voz.
        
        Args:
            command: Comando de voz
            recognized: Si fue reconocido correctamente
            confidence: Nivel de confianza (0-1)
            latency_ms: Latencia en milisegundos
            engine: Motor usado (vosk/google)
        """
        metrics = {
            "voice_recognition_success": 1.0 if recognized else 0.0,
            "voice_confidence": confidence,
            "voice_latency_ms": latency_ms
        }
        
        params = {
            "voice_command": command,
            "voice_engine": engine
        }
        
        self.log_params(params)
        self.log_metrics(metrics)
    
    def log_connection_metrics(
        self,
        connection_type: str,
        connection_time_ms: float,
        success: bool
    ):
        """
        Registrar métricas de conexión.
        
        Args:
            connection_type: Tipo de conexión (serial/bluetooth)
            connection_time_ms: Tiempo de conexión en ms
            success: Si la conexión fue exitosa
        """
        metrics = {
            "connection_success": 1.0 if success else 0.0,
            "connection_time_ms": connection_time_ms
        }
        
        params = {
            "connection_type": connection_type
        }
        
        self.log_params(params)
        self.log_metrics(metrics)
    
    def log_system_config(self, config: Dict[str, Any]):
        """
        Registrar configuración del sistema.
        
        Args:
            config: Diccionario con configuración
        """
        # Aplanar configuración anidada
        flat_config = self._flatten_dict(config)
        self.log_params(flat_config)
    
    def _flatten_dict(self, d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
        """Aplanar diccionario anidado."""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)
    
    def end_run(self):
        """Finalizar el run actual."""
        try:
            mlflow.end_run()
        except Exception as e:
            print(f"⚠ Error ending run: {e}")
    
    @staticmethod
    def load_model(model_uri: str):
        """
        Cargar un modelo desde MLflow.
        
        Args:
            model_uri: URI del modelo (e.g., "runs:/<run_id>/model")
            
        Returns:
            Modelo cargado
        """
        try:
            return mlflow.pyfunc.load_model(model_uri)
        except Exception as e:
            print(f"⚠ Error loading model: {e}")
            return None
    
    @staticmethod
    def get_run_info(run_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtener información de un run.
        
        Args:
            run_id: ID del run
            
        Returns:
            Diccionario con información del run
        """
        try:
            run = mlflow.get_run(run_id)
            return {
                "run_id": run.info.run_id,
                "experiment_id": run.info.experiment_id,
                "status": run.info.status,
                "start_time": run.info.start_time,
                "end_time": run.info.end_time,
                "params": run.data.params,
                "metrics": run.data.metrics,
                "tags": run.data.tags
            }
        except Exception as e:
            print(f"⚠ Error getting run info: {e}")
            return None


# Ejemplo de uso
if __name__ == "__main__":
    # Inicializar tracker
    tracker = MLflowTracker(experiment_name="wheelchair_test")
    
    # Iniciar run
    with tracker.start_run(run_name="test_run"):
        # Registrar parámetros
        tracker.log_params({
            "model_type": "vosk",
            "sample_rate": 16000,
            "language": "es"
        })
        
        # Registrar métricas
        tracker.log_metrics({
            "accuracy": 0.95,
            "latency_ms": 150
        })
        
        # Registrar comando de voz
        tracker.log_voice_command_metrics(
            command="adelante rápido",
            recognized=True,
            confidence=0.95,
            latency_ms=150,
            engine="vosk"
        )
        
        print("✓ Test completado")
