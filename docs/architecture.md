# Arquitectura del Sistema

## Visión General

El sistema de control por voz para silla de ruedas está diseñado con una arquitectura modular que separa las responsabilidades en capas bien definidas, siguiendo principios de MLOps para garantizar trazabilidad, reproducibilidad y mantenibilidad.

## Diagrama de Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│                        INTERFAZ DE USUARIO                       │
│                     (Tkinter GUI - main.py)                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────┴────────────────────────────────────┐
│                         CAPA DE CONTROL                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │   Joystick   │  │  Voice Engine│  │  Connection Manager  │  │
│  │   Control    │  │  (Vosk/Google)│  │  (Serial/Bluetooth) │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────┴────────────────────────────────────┐
│                        CAPA DE MLOps                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │   MLflow     │  │     Data     │  │      Model           │  │
│  │   Tracker    │  │  Validator   │  │     Monitor          │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────┴────────────────────────────────────┐
│                      CAPA DE PERSISTENCIA                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │   MLflow DB  │  │  Data Store  │  │   Model Registry     │  │
│  │  (SQLite)    │  │  (CSV/JSON)  │  │   (Artifacts)        │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                             │
┌────────────────────────────┴────────────────────────────────────┐
│                         HARDWARE LAYER                           │
│                    ESP32 ↔ Silla de Ruedas                       │
└─────────────────────────────────────────────────────────────────┘
```

## Componentes Principales

### 1. Interfaz de Usuario (GUI)
- **Tecnología**: Tkinter
- **Responsabilidades**:
  - Visualización del joystick virtual
  - Control por voz (push-to-talk)
  - Monitoreo de estado en tiempo real
  - Notificaciones y alertas

### 2. Core Modules

#### 2.1 Connection Manager
- Gestión de conexiones Serial/USB y Bluetooth
- Protocolo de comunicación con ESP32
- Manejo de reconexiones automáticas
- Timeout y safety features

#### 2.2 Voice Engine
- **Vosk (Offline)**: Reconocimiento local sin internet
- **Google (Online)**: Reconocimiento cloud con alta precisión
- Procesamiento de comandos de voz
- Mapeo de comandos a acciones

#### 2.3 Joystick Control
- Joystick virtual (16 direcciones)
- Zona muerta configurable
- Magnitud proporcional
- Integración con joystick físico

### 3. MLOps Layer

#### 3.1 MLflow Tracker
- **Propósito**: Seguimiento de experimentos y modelos
- **Funcionalidades**:
  - Registro de parámetros y métricas
  - Versionado de modelos
  - Comparación de experimentos
  - Model Registry

#### 3.2 Data Validator
- **Propósito**: Validación de datos de entrada
- **Validaciones**:
  - Comandos de voz (formato, confianza)
  - Datos de joystick (ángulo, magnitud)
  - Eventos de conexión
  - Esquemas de datos

#### 3.3 Model Monitor
- **Propósito**: Monitoreo de rendimiento en producción
- **Métricas**:
  - Precisión de reconocimiento
  - Latencia de respuesta
  - Confianza promedio
  - Alertas automáticas

### 4. Utilities

#### 4.1 Logger
- Sistema de logging centralizado
- Niveles configurables
- Rotación de logs
- Formato estructurado

#### 4.2 Config Manager
- Gestión de configuración YAML
- Variables de entorno
- Configuración por ambiente

## Flujo de Datos

### Flujo de Comando de Voz

```
Usuario presiona botón → Captura de audio → Motor de voz (Vosk/Google)
    ↓
Reconocimiento de texto → Validación de datos → Procesamiento de comando
    ↓
Mapeo a ángulo/magnitud → Registro en MLflow → Envío a ESP32
    ↓
Actualización de GUI ← Telemetría de ESP32 ← Ejecución en silla
```

### Flujo de Joystick Virtual

```
Usuario arrastra mouse → Cálculo de ángulo/magnitud → Validación
    ↓
Registro en MLflow → Envío continuo (100ms) → ESP32
    ↓
Visualización en GUI ← Telemetría ← Ejecución
```

## Patrones de Diseño

### 1. Observer Pattern
- GUI observa cambios en el estado de conexión
- Notificaciones de eventos asíncronos

### 2. Strategy Pattern
- Múltiples motores de voz intercambiables
- Diferentes tipos de conexión (Serial/Bluetooth)

### 3. Singleton Pattern
- Logger global
- Configuración compartida

### 4. Factory Pattern
- Creación de conexiones según tipo
- Instanciación de motores de voz

## Threading Model

```
Main Thread (GUI)
    ├── Read Thread (Recepción de datos del ESP32)
    ├── Send Thread (Envío continuo de comandos)
    └── Voice Thread (Reconocimiento de voz)
```

### Sincronización
- Queue para comunicación entre threads
- Locks para recursos compartidos
- Thread-safe updates a GUI con `root.after()`

## Seguridad

### Safety Features
1. **Timeout de Comando**: 500ms sin comando = parada automática
2. **Zona Muerta**: Evita movimientos no intencionados
3. **Validación de Datos**: Todos los comandos son validados
4. **Emergency Stop**: Comando de detención prioritario
5. **Connection Monitoring**: Detección de desconexiones

### Data Privacy
- Reconocimiento de voz offline (Vosk) para privacidad
- Datos almacenados localmente
- Sin envío de información a servidores externos

## Escalabilidad

### Horizontal
- Múltiples instancias de monitoreo
- Distribución de carga en MLflow server

### Vertical
- Optimización de modelos de voz
- Caching de configuraciones
- Buffer de comandos

## Deployment

### Ambientes

1. **Development**
   - SQLite local para MLflow
   - Logs detallados
   - Hot reload

2. **Staging**
   - MLflow server compartido
   - Validación de modelos
   - Tests de integración

3. **Production**
   - Alta disponibilidad
   - Monitoreo continuo
   - Alertas automáticas

## Tecnologías

| Componente | Tecnología | Versión |
|------------|------------|---------|
| GUI | Tkinter | Built-in |
| Voice (Offline) | Vosk | 0.3.45+ |
| Voice (Online) | Google Speech | 3.10+ |
| MLOps | MLflow | 2.9+ |
| Validation | Great Expectations | 0.18+ |
| Monitoring | Evidently | 0.4+ |
| Serial | PySerial | 3.5+ |
| Bluetooth | PyBluez | 0.23+ |
| Testing | Pytest | 7.4+ |

## Métricas de Rendimiento

### Objetivos
- **Latencia de Voz**: < 300ms (P95)
- **Precisión de Reconocimiento**: > 90%
- **Uptime**: > 99%
- **Tiempo de Conexión**: < 2s

### KPIs
- Comandos procesados por minuto
- Tasa de error de reconocimiento
- Tiempo de respuesta del sistema
- Disponibilidad del servicio

## Mantenimiento

### Logs
- Rotación diaria
- Retención: 7 días
- Nivel: INFO en producción

### Backups
- Modelos: Versionados en MLflow
- Datos: Backup semanal
- Configuración: Git

### Updates
- Modelos: Validación antes de deploy
- Dependencias: Revisión mensual
- Security patches: Inmediato
