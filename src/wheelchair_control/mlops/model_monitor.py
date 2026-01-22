"""
Model Monitor
=============

Monitoreo de rendimiento de modelos en producción.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
import json


class ModelMonitor:
    """
    Monitor de rendimiento para modelos de reconocimiento de voz.
    """
    
    def __init__(self, window_size: int = 100):
        """
        Inicializar monitor.
        
        Args:
            window_size: Tamaño de ventana para métricas móviles
        """
        self.window_size = window_size
        self.predictions = []
        self.metrics_history = []
        self.alerts = []
        
        # Umbrales de alerta
        self.thresholds = {
            "accuracy": 0.80,  # Mínimo 80% de precisión
            "latency_ms": 500,  # Máximo 500ms de latencia
            "confidence": 0.60  # Mínimo 60% de confianza promedio
        }
    
    def log_prediction(
        self,
        command: str,
        predicted: str,
        actual: Optional[str],
        confidence: float,
        latency_ms: float,
        engine: str,
        timestamp: Optional[datetime] = None
    ):
        """
        Registrar una predicción.
        
        Args:
            command: Comando original
            predicted: Comando predicho
            actual: Comando real (si está disponible)
            confidence: Nivel de confianza
            latency_ms: Latencia en ms
            engine: Motor usado (vosk/google)
            timestamp: Timestamp de la predicción
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        prediction = {
            "command": command,
            "predicted": predicted,
            "actual": actual,
            "confidence": confidence,
            "latency_ms": latency_ms,
            "engine": engine,
            "timestamp": timestamp.isoformat(),
            "correct": predicted == actual if actual else None
        }
        
        self.predictions.append(prediction)
        
        # Mantener solo las últimas N predicciones
        if len(self.predictions) > self.window_size * 2:
            self.predictions = self.predictions[-self.window_size * 2:]
        
        # Calcular métricas
        self._calculate_metrics()
        
        # Verificar alertas
        self._check_alerts()
    
    def _calculate_metrics(self):
        """Calcular métricas actuales."""
        if not self.predictions:
            return
        
        # Obtener últimas N predicciones
        recent = self.predictions[-self.window_size:]
        
        # Calcular métricas
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "window_size": len(recent),
            "total_predictions": len(self.predictions)
        }
        
        # Precisión (solo si tenemos ground truth)
        with_actual = [p for p in recent if p["actual"] is not None]
        if with_actual:
            correct = sum(1 for p in with_actual if p["correct"])
            metrics["accuracy"] = correct / len(with_actual)
            metrics["total_with_ground_truth"] = len(with_actual)
        else:
            metrics["accuracy"] = None
        
        # Confianza promedio
        confidences = [p["confidence"] for p in recent]
        metrics["avg_confidence"] = np.mean(confidences)
        metrics["min_confidence"] = np.min(confidences)
        metrics["max_confidence"] = np.max(confidences)
        metrics["std_confidence"] = np.std(confidences)
        
        # Latencia
        latencies = [p["latency_ms"] for p in recent]
        metrics["avg_latency_ms"] = np.mean(latencies)
        metrics["min_latency_ms"] = np.min(latencies)
        metrics["max_latency_ms"] = np.max(latencies)
        metrics["p95_latency_ms"] = np.percentile(latencies, 95)
        metrics["p99_latency_ms"] = np.percentile(latencies, 99)
        
        # Distribución por motor
        engines = [p["engine"] for p in recent]
        engine_counts = pd.Series(engines).value_counts().to_dict()
        metrics["engine_distribution"] = engine_counts
        
        self.metrics_history.append(metrics)
    
    def _check_alerts(self):
        """Verificar si hay alertas."""
        if not self.metrics_history:
            return
        
        current_metrics = self.metrics_history[-1]
        
        # Verificar precisión
        if current_metrics["accuracy"] is not None:
            if current_metrics["accuracy"] < self.thresholds["accuracy"]:
                self.alerts.append({
                    "type": "accuracy",
                    "severity": "high",
                    "message": f"Precisión baja: {current_metrics['accuracy']:.2%} (umbral: {self.thresholds['accuracy']:.2%})",
                    "timestamp": datetime.now().isoformat(),
                    "value": current_metrics["accuracy"]
                })
        
        # Verificar latencia
        if current_metrics["avg_latency_ms"] > self.thresholds["latency_ms"]:
            self.alerts.append({
                "type": "latency",
                "severity": "medium",
                "message": f"Latencia alta: {current_metrics['avg_latency_ms']:.0f}ms (umbral: {self.thresholds['latency_ms']}ms)",
                "timestamp": datetime.now().isoformat(),
                "value": current_metrics["avg_latency_ms"]
            })
        
        # Verificar confianza
        if current_metrics["avg_confidence"] < self.thresholds["confidence"]:
            self.alerts.append({
                "type": "confidence",
                "severity": "medium",
                "message": f"Confianza baja: {current_metrics['avg_confidence']:.2%} (umbral: {self.thresholds['confidence']:.2%})",
                "timestamp": datetime.now().isoformat(),
                "value": current_metrics["avg_confidence"]
            })
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Obtener métricas actuales."""
        if not self.metrics_history:
            return {"message": "No hay métricas disponibles"}
        
        return self.metrics_history[-1]
    
    def get_metrics_summary(self, last_n_hours: Optional[int] = None) -> Dict[str, Any]:
        """
        Obtener resumen de métricas.
        
        Args:
            last_n_hours: Filtrar por últimas N horas
            
        Returns:
            Resumen de métricas
        """
        if not self.metrics_history:
            return {"message": "No hay métricas disponibles"}
        
        metrics = self.metrics_history
        
        # Filtrar por tiempo si se especifica
        if last_n_hours:
            cutoff = datetime.now() - timedelta(hours=last_n_hours)
            metrics = [
                m for m in metrics
                if datetime.fromisoformat(m["timestamp"]) > cutoff
            ]
        
        if not metrics:
            return {"message": f"No hay métricas en las últimas {last_n_hours} horas"}
        
        # Calcular resumen
        accuracies = [m["accuracy"] for m in metrics if m["accuracy"] is not None]
        confidences = [m["avg_confidence"] for m in metrics]
        latencies = [m["avg_latency_ms"] for m in metrics]
        
        summary = {
            "period": f"last_{last_n_hours}_hours" if last_n_hours else "all_time",
            "total_metrics_points": len(metrics),
            "total_predictions": metrics[-1]["total_predictions"] if metrics else 0
        }
        
        if accuracies:
            summary["accuracy"] = {
                "mean": np.mean(accuracies),
                "min": np.min(accuracies),
                "max": np.max(accuracies),
                "std": np.std(accuracies)
            }
        
        summary["confidence"] = {
            "mean": np.mean(confidences),
            "min": np.min(confidences),
            "max": np.max(confidences),
            "std": np.std(confidences)
        }
        
        summary["latency_ms"] = {
            "mean": np.mean(latencies),
            "min": np.min(latencies),
            "max": np.max(latencies),
            "p95": np.percentile(latencies, 95),
            "p99": np.percentile(latencies, 99)
        }
        
        return summary
    
    def get_alerts(self, severity: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Obtener alertas.
        
        Args:
            severity: Filtrar por severidad (high/medium/low)
            
        Returns:
            Lista de alertas
        """
        if severity:
            return [a for a in self.alerts if a["severity"] == severity]
        return self.alerts
    
    def clear_alerts(self):
        """Limpiar alertas."""
        self.alerts = []
    
    def export_metrics(self, output_path: Path):
        """
        Exportar métricas a archivo JSON.
        
        Args:
            output_path: Ruta del archivo de salida
        """
        data = {
            "metrics_history": self.metrics_history,
            "alerts": self.alerts,
            "thresholds": self.thresholds,
            "export_timestamp": datetime.now().isoformat()
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Métricas exportadas: {output_path}")
    
    def export_predictions(self, output_path: Path):
        """
        Exportar predicciones a CSV.
        
        Args:
            output_path: Ruta del archivo de salida
        """
        if not self.predictions:
            print("⚠ No hay predicciones para exportar")
            return
        
        df = pd.DataFrame(self.predictions)
        df.to_csv(output_path, index=False, encoding='utf-8')
        print(f"✓ Predicciones exportadas: {output_path}")
    
    def generate_report(self) -> str:
        """
        Generar reporte de monitoreo.
        
        Returns:
            Reporte en formato texto
        """
        report = []
        report.append("=" * 60)
        report.append("REPORTE DE MONITOREO - SISTEMA DE VOZ")
        report.append("=" * 60)
        report.append("")
        
        # Métricas actuales
        current = self.get_current_metrics()
        if "message" not in current:
            report.append("MÉTRICAS ACTUALES:")
            report.append(f"  Total predicciones: {current['total_predictions']}")
            report.append(f"  Ventana: {current['window_size']} predicciones")
            
            if current["accuracy"] is not None:
                report.append(f"  Precisión: {current['accuracy']:.2%}")
            
            report.append(f"  Confianza promedio: {current['avg_confidence']:.2%}")
            report.append(f"  Latencia promedio: {current['avg_latency_ms']:.0f}ms")
            report.append(f"  Latencia P95: {current['p95_latency_ms']:.0f}ms")
            report.append("")
        
        # Alertas
        if self.alerts:
            report.append("ALERTAS ACTIVAS:")
            for alert in self.alerts[-5:]:  # Últimas 5 alertas
                report.append(f"  [{alert['severity'].upper()}] {alert['message']}")
            report.append("")
        else:
            report.append("✓ No hay alertas activas")
            report.append("")
        
        # Resumen
        summary = self.get_metrics_summary()
        if "message" not in summary:
            report.append("RESUMEN GENERAL:")
            report.append(f"  Puntos de métrica: {summary['total_metrics_points']}")
            
            if "accuracy" in summary:
                report.append(f"  Precisión media: {summary['accuracy']['mean']:.2%}")
            
            report.append(f"  Confianza media: {summary['confidence']['mean']:.2%}")
            report.append(f"  Latencia media: {summary['latency_ms']['mean']:.0f}ms")
        
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)


# Ejemplo de uso
if __name__ == "__main__":
    monitor = ModelMonitor(window_size=50)
    
    # Simular predicciones
    commands = ["adelante", "atrás", "izquierda", "derecha", "detener"]
    
    for i in range(100):
        import random
        cmd = random.choice(commands)
        
        monitor.log_prediction(
            command=cmd,
            predicted=cmd,
            actual=cmd if random.random() > 0.1 else random.choice(commands),
            confidence=random.uniform(0.7, 0.99),
            latency_ms=random.uniform(100, 300),
            engine="vosk"
        )
    
    # Generar reporte
    print(monitor.generate_report())
    
    # Obtener alertas
    alerts = monitor.get_alerts()
    if alerts:
        print(f"\n⚠ {len(alerts)} alertas encontradas")
