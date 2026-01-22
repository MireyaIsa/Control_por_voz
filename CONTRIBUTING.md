# Guía de Contribución

¡Gracias por tu interés en contribuir al proyecto de Control por Voz para Silla de Ruedas! 🦽

## Código de Conducta

Este proyecto se adhiere a un código de conducta. Al participar, se espera que mantengas un ambiente respetuoso y profesional.

## ¿Cómo Contribuir?

### Reportar Bugs

Si encuentras un bug:

1. Verifica que no haya sido reportado anteriormente en [Issues](https://github.com/tu-usuario/wheelchair-voice-control/issues)
2. Abre un nuevo issue con:
   - Título descriptivo
   - Pasos para reproducir el bug
   - Comportamiento esperado vs. actual
   - Versión de Python y sistema operativo
   - Logs relevantes

### Sugerir Mejoras

Para sugerir nuevas características:

1. Abre un issue con la etiqueta `enhancement`
2. Describe claramente la funcionalidad propuesta
3. Explica por qué sería útil
4. Si es posible, proporciona ejemplos de uso

### Pull Requests

1. **Fork el repositorio**
   ```bash
   git clone https://github.com/tu-usuario/wheelchair-voice-control.git
   cd wheelchair-voice-control
   ```

2. **Crea una rama para tu feature**
   ```bash
   git checkout -b feature/mi-nueva-funcionalidad
   ```

3. **Configura el entorno de desarrollo**
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -e .
   ```

4. **Realiza tus cambios**
   - Sigue las guías de estilo (ver abajo)
   - Agrega tests para nuevas funcionalidades
   - Actualiza la documentación si es necesario

5. **Ejecuta los tests**
   ```bash
   pytest
   black src tests
   flake8 src tests
   ```

6. **Commit tus cambios**
   ```bash
   git add .
   git commit -m "feat: descripción clara del cambio"
   ```

   Usa prefijos de commit convencionales:
   - `feat:` nueva funcionalidad
   - `fix:` corrección de bug
   - `docs:` cambios en documentación
   - `test:` agregar o modificar tests
   - `refactor:` refactorización de código
   - `style:` cambios de formato
   - `chore:` tareas de mantenimiento

7. **Push a tu fork**
   ```bash
   git push origin feature/mi-nueva-funcionalidad
   ```

8. **Abre un Pull Request**
   - Describe claramente los cambios
   - Referencias issues relacionados
   - Asegúrate de que los tests pasen

## Guías de Estilo

### Python

- Seguir [PEP 8](https://pep8.org/)
- Usar [Black](https://black.readthedocs.io/) para formateo automático
- Máximo 100 caracteres por línea
- Usar type hints cuando sea posible
- Documentar funciones con docstrings (estilo Google)

Ejemplo:
```python
def process_voice_command(command: str, confidence: float) -> Dict[str, Any]:
    """
    Procesar comando de voz.
    
    Args:
        command: Comando de voz reconocido
        confidence: Nivel de confianza (0-1)
        
    Returns:
        Diccionario con resultado del procesamiento
        
    Raises:
        ValueError: Si el comando no es válido
    """
    pass
```

### Tests

- Usar pytest
- Nombrar tests descriptivamente: `test_<funcionalidad>_<escenario>`
- Organizar tests con clases cuando sea apropiado
- Usar fixtures para datos de prueba
- Apuntar a >80% de cobertura de código

Ejemplo:
```python
class TestVoiceEngine:
    def test_recognize_command_with_high_confidence(self):
        """Test reconocimiento con alta confianza."""
        pass
    
    def test_recognize_command_with_low_confidence(self):
        """Test reconocimiento con baja confianza."""
        pass
```

### Commits

- Mensajes en español o inglés (consistente)
- Primera línea: resumen conciso (<50 caracteres)
- Cuerpo: explicación detallada si es necesario
- Referenciar issues: `Fixes #123` o `Closes #456`

## Estructura del Proyecto

```
wheelchair-voice-control/
├── src/wheelchair_control/    # Código fuente
│   ├── core/                  # Funcionalidad principal
│   ├── ml/                    # Machine Learning
│   ├── mlops/                 # MLOps (MLflow, validación)
│   └── utils/                 # Utilidades
├── tests/                     # Tests
├── config/                    # Configuración
├── scripts/                   # Scripts de utilidad
└── docs/                      # Documentación
```

## MLflow y Experimentos

Al trabajar con modelos:

1. Registrar todos los experimentos en MLflow
2. Documentar parámetros y métricas
3. Versionar modelos apropiadamente
4. Incluir ejemplos de uso

```python
from wheelchair_control.mlops.mlflow_tracker import MLflowTracker

tracker = MLflowTracker()
with tracker.start_run(run_name="mi_experimento"):
    tracker.log_params({"param1": value1})
    tracker.log_metrics({"accuracy": 0.95})
```

## Documentación

- Actualizar README.md si cambias funcionalidad principal
- Documentar nuevas APIs en `docs/api.md`
- Incluir ejemplos de uso
- Mantener changelog actualizado

## Proceso de Revisión

1. Los maintainers revisarán tu PR
2. Pueden solicitar cambios
3. Una vez aprobado, se hará merge
4. Tu contribución será reconocida en el proyecto

## Preguntas

Si tienes preguntas:
- Abre un issue con la etiqueta `question`
- Contacta a los maintainers

## Licencia

Al contribuir, aceptas que tus contribuciones se licencien bajo la misma licencia del proyecto (MIT).

---

¡Gracias por contribuir! 🎉
