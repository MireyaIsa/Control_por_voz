# 🦽 Proyecto Completo - Sistema de Control por Voz con MLOps

## ✅ Estructura Creada

Se ha creado una estructura completa de MLOps para tu proyecto de control de silla de ruedas por voz. A continuación, el resumen de lo implementado:

### 📁 Estructura de Directorios

```
wheelchair-voice-control/
├── .github/workflows/              ✅ CI/CD Pipelines
│   ├── ci.yml                      # Pipeline de integración continua
│   └── mlflow-deploy.yml           # Pipeline de despliegue de modelos
│
├── config/                         ✅ Configuraciones
│   ├── mlflow_config.yaml          # Configuración de MLflow
│   └── model_config.yaml           # Configuración de modelos y sistema
│
├── data/                           ✅ Datos
│   ├── raw/.gitkeep                # Datos crudos
│   ├── processed/.gitkeep          # Datos procesados
│   └── validation/                 # Esquemas de validación
│
├── docs/                           ✅ Documentación
│   └── architecture.md             # Arquitectura del sistema
│
├── models/                         ✅ Modelos
│   └── voice/.gitkeep              # Modelos de voz
│
├── notebooks/                      ✅ Notebooks (vacío, listo para análisis)
│
├── scripts/                        ✅ Scripts de utilidad
│   └── train_model.py              # Script de entrenamiento
│
├── src/wheelchair_control/         ✅ Código fuente
│   ├── __init__.py
│   ├── main.py                     # Aplicación principal (GUI)
│   │
│   ├── core/                       # Funcionalidad principal
│   │   └── __init__.py
│   │
│   ├── ml/                         # Machine Learning
│   │   └── __init__.py
│   │
│   ├── mlops/                      # MLOps
│   │   ├── __init__.py
│   │   ├── mlflow_tracker.py       # Integración MLflow
│   │   ├── data_validator.py       # Validación de datos
│   │   └── model_monitor.py        # Monitoreo de modelos
│   │
│   └── utils/                      # Utilidades
│       ├── __init__.py
│       ├── logger.py               # Sistema de logging
│       └── config.py               # Gestión de configuración
│
├── tests/                          ✅ Tests
│   ├── __init__.py
│   ├── conftest.py                 # Configuración de pytest
│   ├── test_mlflow_integration.py  # Tests de MLflow
│   └── test_data_validator.py      # Tests de validación
│
├── .env.example                    ✅ Ejemplo de variables de entorno
├── .gitignore                      ✅ Archivos a ignorar en Git
├── CONTRIBUTING.md                 ✅ Guía de contribución
├── GITHUB_SETUP.md                 ✅ Guía para subir a GitHub
├── LICENSE                         ✅ Licencia MIT
├── README.md                       ✅ Documentación principal
├── requirements.txt                ✅ Dependencias
├── setup.py                        ✅ Configuración del paquete
└── pytest.ini                      ✅ Configuración de tests
```

## 🎯 Componentes Implementados

### 1. MLflow Integration (✅ Completo)

**Archivo**: `src/wheelchair_control/mlops/mlflow_tracker.py`

**Funcionalidades**:
- ✅ Tracking de experimentos
- ✅ Registro de parámetros y métricas
- ✅ Versionado de modelos
- ✅ Model Registry
- ✅ Métricas específicas de voz (latencia, confianza, precisión)
- ✅ Métricas de conexión

**Uso**:
```python
from wheelchair_control.mlops.mlflow_tracker import MLflowTracker

tracker = MLflowTracker(experiment_name="wheelchair_voice_control")
with tracker.start_run(run_name="test_run"):
    tracker.log_params({"model_type": "vosk"})
    tracker.log_metrics({"accuracy": 0.95})
    tracker.log_voice_command_metrics(
        command="adelante rápido",
        recognized=True,
        confidence=0.95,
        latency_ms=150,
        engine="vosk"
    )
```

### 2. Data Validation (✅ Completo)

**Archivo**: `src/wheelchair_control/mlops/data_validator.py`

**Funcionalidades**:
- ✅ Validación de comandos de voz
- ✅ Validación de datos de joystick
- ✅ Validación de eventos de conexión
- ✅ Reportes de validación
- ✅ Reglas configurables

**Uso**:
```python
from wheelchair_control.mlops.data_validator import DataValidator

validator = DataValidator()
result = validator.validate_voice_command({
    "command": "adelante rápido",
    "timestamp": "2026-01-21T22:00:00",
    "recognized": True,
    "confidence": 0.95
})
```

### 3. Model Monitoring (✅ Completo)

**Archivo**: `src/wheelchair_control/mlops/model_monitor.py`

**Funcionalidades**:
- ✅ Monitoreo de rendimiento en tiempo real
- ✅ Métricas móviles (ventana configurable)
- ✅ Sistema de alertas automáticas
- ✅ Reportes de monitoreo
- ✅ Exportación de métricas

**Uso**:
```python
from wheelchair_control.mlops.model_monitor import ModelMonitor

monitor = ModelMonitor(window_size=100)
monitor.log_prediction(
    command="adelante",
    predicted="adelante",
    actual="adelante",
    confidence=0.95,
    latency_ms=150,
    engine="vosk"
)
print(monitor.generate_report())
```

### 4. Utilities (✅ Completo)

**Logger**: Sistema de logging centralizado
**Config**: Gestión de configuración YAML y variables de entorno

### 5. CI/CD Pipelines (✅ Completo)

**GitHub Actions**:
- ✅ CI Pipeline: Tests, linting, cobertura
- ✅ MLflow Deploy: Despliegue de modelos
- ✅ Security scanning
- ✅ Code quality checks

### 6. Configuración (✅ Completo)

**MLflow Config**: Configuración completa de MLflow
**Model Config**: Configuración de modelos, comandos, conexiones

### 7. Tests (✅ Completo)

- ✅ Tests de MLflow integration
- ✅ Tests de data validator
- ✅ Fixtures y configuración de pytest

## 📊 Características de MLflow

### Tracking de Experimentos
```yaml
Experimentos:
  - Nombre: wheelchair_voice_control
  - Tracking URI: sqlite:///mlflow.db (local)
  - Artifacts: ./mlartifacts

Métricas Registradas:
  - Comandos de voz: accuracy, confidence, latency
  - Conexiones: success_rate, connection_time
  - Sistema: cpu_usage, memory_usage, uptime

Parámetros Registrados:
  - Modelo: type, version, sample_rate, language
  - Sistema: connection_type, baudrate, timeout
  - Voz: model_path, confidence_threshold
```

### Iniciar MLflow UI
```bash
# Desde la raíz del proyecto
mlflow ui --backend-store-uri sqlite:///mlflow.db

# Acceder a: http://localhost:5000
```

## 🚀 Cómo Usar el Proyecto

### 1. Instalación

```bash
# Clonar o navegar al proyecto
cd "d:\Documentos\Maestria Inteligencia artificial\Sniffer\Control_por_voz"

# Crear entorno virtual
python -m venv venv
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Instalar en modo desarrollo
pip install -e .

# Copiar configuración de entorno
copy .env.example .env
```

### 2. Ejecutar la Aplicación

```bash
# Opción 1: Ejecutar directamente
python src/wheelchair_control/main.py

# Opción 2: Usar comando instalado
wheelchair-control
```

### 3. Iniciar MLflow

```bash
# Terminal separada
mlflow ui
```

### 4. Ejecutar Tests

```bash
# Todos los tests
pytest

# Con cobertura
pytest --cov=src --cov-report=html

# Ver reporte de cobertura
start htmlcov/index.html
```

## 📤 Subir a GitHub

### Guía Rápida

```powershell
# 1. Inicializar Git
git init

# 2. Agregar archivos
git add .

# 3. Primer commit
git commit -m "Initial commit: Estructura MLOps completa con MLflow"

# 4. Crear repositorio en GitHub (web)
# Ve a github.com y crea un nuevo repositorio

# 5. Conectar con GitHub (reemplaza TU-USUARIO)
git remote add origin https://github.com/TU-USUARIO/wheelchair-voice-control.git

# 6. Subir código
git branch -M main
git push -u origin main
```

**📖 Guía Detallada**: Ver `GITHUB_SETUP.md` para instrucciones paso a paso.

## 🔧 Configuración Recomendada

### Variables de Entorno (.env)

```env
# MLflow
MLFLOW_TRACKING_URI=sqlite:///mlflow.db
MLFLOW_EXPERIMENT_NAME=wheelchair_voice_control

# Voice Recognition
VOSK_MODEL_PATH=vosk-model-small-es-0.42
SAMPLE_RATE=16000

# Logging
LOG_LEVEL=INFO
```

### Descargar Modelo Vosk

```bash
# Descargar desde: https://alphacephei.com/vosk/models
# Modelo recomendado: vosk-model-small-es-0.42 (39 MB)
# Extraer en la raíz del proyecto
```

## 📈 Integración con el Código Existente

Tu archivo `wheelchair_control_advanced.py` ha sido:
- ✅ Copiado a `src/wheelchair_control/main.py`
- ✅ Mantenido en su ubicación original como backup
- ✅ Listo para refactorizar en módulos (opcional)

### Próximos Pasos de Refactorización (Opcional)

1. **Separar en módulos**:
   - `core/connection.py` → Gestión de conexiones
   - `core/joystick.py` → Control de joystick
   - `core/voice_engine.py` → Motor de voz

2. **Integrar MLflow en la GUI**:
   ```python
   from wheelchair_control.mlops.mlflow_tracker import MLflowTracker
   
   # En __init__ de la clase
   self.tracker = MLflowTracker()
   
   # Al procesar comando de voz
   self.tracker.log_voice_command_metrics(...)
   ```

3. **Agregar validación**:
   ```python
   from wheelchair_control.mlops.data_validator import DataValidator
   
   validator = DataValidator()
   result = validator.validate_voice_command(data)
   ```

## 📚 Documentación

- **README.md**: Documentación principal y guía de uso
- **GITHUB_SETUP.md**: Guía paso a paso para subir a GitHub
- **CONTRIBUTING.md**: Guía para contribuidores
- **docs/architecture.md**: Arquitectura detallada del sistema
- **LICENSE**: Licencia MIT

## 🎓 Características para Proyecto Académico

✅ **Estructura Profesional**: Organización estándar de la industria
✅ **MLOps Completo**: Tracking, validación, monitoreo
✅ **CI/CD**: Pipelines automatizados
✅ **Tests**: Cobertura de código
✅ **Documentación**: Completa y detallada
✅ **Versionado**: Git y GitHub
✅ **Reproducibilidad**: MLflow para experimentos
✅ **Calidad de Código**: Linting y formateo

## 🔍 Verificación de la Estructura

```powershell
# Ver estructura de archivos
tree /F /A

# Verificar que Git está inicializado
git status

# Ver archivos que se subirán
git add --dry-run .
```

## 💡 Tips Importantes

1. **No subir archivos grandes**: Los modelos Vosk no se suben (están en .gitignore)
2. **Variables de entorno**: Nunca subir `.env` con secretos
3. **MLflow local**: Por defecto usa SQLite local
4. **Tests**: Ejecutar antes de cada commit
5. **Documentación**: Actualizar README con tu información

## 🆘 Soporte

Si tienes problemas:
1. Revisa `GITHUB_SETUP.md` para problemas con Git
2. Revisa logs en `logs/wheelchair.log`
3. Ejecuta tests: `pytest -v`
4. Verifica configuración: `.env` y `config/*.yaml`

## ✨ Resumen

Has obtenido:
- ✅ Estructura MLOps completa y profesional
- ✅ Integración con MLflow para tracking
- ✅ Sistema de validación de datos
- ✅ Monitoreo de modelos en producción
- ✅ CI/CD con GitHub Actions
- ✅ Tests automatizados
- ✅ Documentación completa
- ✅ Listo para subir a GitHub

**Tu proyecto ahora tiene una arquitectura de nivel profesional lista para producción y presentación académica.** 🎉
