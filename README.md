# 🦽 Sistema de Control por Voz para Silla de Ruedas

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![MLflow](https://img.shields.io/badge/MLflow-Tracking-orange.svg)](https://mlflow.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Sistema avanzado de control por voz para silla de ruedas eléctrica con arquitectura MLOps completa, incluyendo reconocimiento de voz offline (Vosk) y online (Google), interfaz gráfica intuitiva, y seguimiento de experimentos con MLflow.

## 🎯 Características Principales

### Control Multimodal
- **🎤 Control por Voz**: Reconocimiento offline (Vosk) y online (Google Speech Recognition)
- **🕹️ Joystick Virtual**: Control con mouse, 16 direcciones, magnitud proporcional
- **🔘 Botones de Función**: 3 botones programables personalizables
- **📊 Visualización en Tiempo Real**: Estado del joystick físico, conexión BLE, notificaciones

### Conectividad
- **USB Serial**: Conexión directa por cable USB
- **Bluetooth Classic**: Conexión inalámbrica con ESP32
- **Comunicación Bidireccional**: Envío de comandos y recepción de telemetría

### MLOps
- **MLflow Tracking**: Seguimiento de experimentos, métricas y modelos
- **Data Validation**: Validación de datos con Great Expectations
- **Model Monitoring**: Monitoreo de rendimiento con Evidently
- **CI/CD**: Pipeline automatizado con GitHub Actions
- **Versionado de Modelos**: Control de versiones de modelos de voz

## 📁 Estructura del Proyecto

```
wheelchair-voice-control/
├── .github/
│   └── workflows/
│       ├── ci.yml                    # CI/CD pipeline
│       └── mlflow-deploy.yml         # MLflow deployment
├── config/
│   ├── mlflow_config.yaml           # Configuración MLflow
│   ├── model_config.yaml            # Configuración de modelos
│   └── logging_config.yaml          # Configuración de logs
├── data/
│   ├── raw/                         # Datos crudos
│   ├── processed/                   # Datos procesados
│   └── validation/                  # Esquemas de validación
├── docs/
│   ├── architecture.md              # Arquitectura del sistema
│   ├── api.md                       # Documentación API
│   └── user_guide.md                # Guía de usuario
├── models/
│   ├── voice/                       # Modelos de voz
│   └── .gitkeep
├── notebooks/
│   ├── 01_data_exploration.ipynb    # Exploración de datos
│   ├── 02_model_training.ipynb      # Entrenamiento de modelos
│   └── 03_evaluation.ipynb          # Evaluación de modelos
├── src/
│   └── wheelchair_control/
│       ├── __init__.py
│       ├── main.py                  # Aplicación principal (GUI)
│       ├── core/
│       │   ├── __init__.py
│       │   ├── connection.py        # Gestión de conexiones
│       │   ├── joystick.py          # Control de joystick
│       │   └── voice_engine.py      # Motor de reconocimiento de voz
│       ├── ml/
│       │   ├── __init__.py
│       │   ├── model_trainer.py     # Entrenamiento de modelos
│       │   ├── model_evaluator.py   # Evaluación de modelos
│       │   └── data_processor.py    # Procesamiento de datos
│       ├── mlops/
│       │   ├── __init__.py
│       │   ├── mlflow_tracker.py    # Integración MLflow
│       │   ├── data_validator.py    # Validación de datos
│       │   └── model_monitor.py     # Monitoreo de modelos
│       └── utils/
│           ├── __init__.py
│           ├── logger.py            # Sistema de logging
│           └── config.py            # Gestión de configuración
├── tests/
│   ├── __init__.py
│   ├── test_connection.py
│   ├── test_voice_engine.py
│   ├── test_mlflow_integration.py
│   └── conftest.py
├── scripts/
│   ├── setup_environment.py         # Configuración del entorno
│   ├── train_model.py               # Script de entrenamiento
│   └── deploy_model.py              # Script de despliegue
├── .gitignore
├── requirements.txt
├── setup.py
├── pytest.ini
├── .env.example
└── README.md
```

## 🚀 Instalación

### Prerrequisitos
- Python 3.8 o superior
- ESP32 con firmware compatible
- Micrófono funcional
- (Opcional) Modelo Vosk para reconocimiento offline

### Instalación Rápida

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/wheelchair-voice-control.git
cd wheelchair-voice-control

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Instalar el paquete en modo desarrollo
pip install -e .

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones
```

### Descargar Modelo Vosk (Opcional para modo offline)

```bash
# Descargar modelo español (39 MB)
# Desde: https://alphacephei.com/vosk/models
# Extraer en la raíz del proyecto:
# vosk-model-small-es-0.42/
```

## 📊 MLflow - Seguimiento de Experimentos

### Iniciar MLflow UI

```bash
# Iniciar servidor MLflow
mlflow ui --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./mlartifacts

# Acceder a: http://localhost:5000
```

### Registrar Experimento

```python
from src.wheelchair_control.mlops.mlflow_tracker import MLflowTracker

tracker = MLflowTracker(experiment_name="wheelchair_voice_control")

with tracker.start_run(run_name="voice_recognition_test"):
    # Tu código aquí
    tracker.log_param("model_type", "vosk")
    tracker.log_metric("accuracy", 0.95)
    tracker.log_artifact("model.pkl")
```

## 🎮 Uso

### Modo GUI (Interfaz Gráfica)

```bash
# Ejecutar aplicación
python src/wheelchair_control/main.py

# O usando el comando instalado:
wheelchair-control
```

### Comandos de Voz Disponibles

**Direcciones:**
- `adelante [lento/medio/rápido]`
- `atrás [lento/medio/rápido]`
- `izquierda [lento/medio/rápido]`
- `derecha [lento/medio/rápido]`
- `adelante derecha [lento/medio/rápido]`
- `adelante izquierda [lento/medio/rápido]`
- `atrás derecha [lento/medio/rápido]`
- `atrás izquierda [lento/medio/rápido]`

**Control:**
- `detener / alto / parar / stop`

**Velocidades:**
- `lento`: 50%
- `medio`: 75%
- `rápido`: 100%
- Sin especificar: 50% (por defecto)

## 🧪 Testing

```bash
# Ejecutar todos los tests
pytest

# Con cobertura
pytest --cov=src --cov-report=html

# Tests específicos
pytest tests/test_voice_engine.py -v
```

## 📈 Monitoreo y Validación

### Validar Datos

```bash
python scripts/validate_data.py --data-path data/raw/voice_commands.csv
```

### Monitorear Modelo

```bash
python scripts/monitor_model.py --model-uri models/voice/model.pkl
```

## 🔧 Configuración

### Archivo `.env`

```env
# MLflow
MLFLOW_TRACKING_URI=sqlite:///mlflow.db
MLFLOW_ARTIFACT_ROOT=./mlartifacts
MLFLOW_EXPERIMENT_NAME=wheelchair_voice_control

# Serial/Bluetooth
DEFAULT_BAUDRATE=115200
CONNECTION_TIMEOUT=10

# Voice Recognition
VOSK_MODEL_PATH=vosk-model-small-es-0.42
SAMPLE_RATE=16000
```

## 📚 Documentación

- [Arquitectura del Sistema](docs/architecture.md)
- [Guía de Usuario](docs/user_guide.md)
- [API Reference](docs/api.md)
- [Guía de Contribución](CONTRIBUTING.md)

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

Ver [CONTRIBUTING.md](CONTRIBUTING.md) para más detalles.

## 📝 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 👥 Autores

- **Proyecto de Maestría en Inteligencia Artificial**

## 🙏 Agradecimientos

- [Vosk](https://alphacephei.com/vosk/) - Reconocimiento de voz offline
- [MLflow](https://mlflow.org/) - Plataforma MLOps
- Comunidad de código abierto

## 📞 Soporte

Para preguntas y soporte:
- Abrir un issue en GitHub
- Email: tu-email@ejemplo.com

---

**Nota**: Este proyecto es parte de un trabajo de investigación académica en el área de tecnologías asistivas y control por voz.
