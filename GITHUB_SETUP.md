# 📋 Guía para Subir el Proyecto a GitHub

Esta guía te ayudará a subir tu proyecto de control por voz para silla de ruedas a GitHub paso a paso.

## 📝 Prerrequisitos

1. **Cuenta de GitHub**: Crea una cuenta en [github.com](https://github.com) si no tienes una
2. **Git instalado**: Descarga e instala Git desde [git-scm.com](https://git-scm.com)
3. **Configuración de Git** (primera vez):
   ```bash
   git config --global user.name "Tu Nombre"
   git config --global user.email "tu-email@ejemplo.com"
   ```

## 🚀 Pasos para Subir el Proyecto

### 1. Crear Repositorio en GitHub

1. Ve a [github.com](https://github.com) e inicia sesión
2. Haz clic en el botón **"+"** en la esquina superior derecha
3. Selecciona **"New repository"**
4. Configura el repositorio:
   - **Repository name**: `wheelchair-voice-control` (o el nombre que prefieras)
   - **Description**: "Sistema de control por voz para silla de ruedas con MLOps"
   - **Visibility**: 
     - ✅ **Public** (recomendado para proyectos académicos)
     - ⬜ **Private** (si prefieres mantenerlo privado)
   - ⬜ **NO** marques "Initialize this repository with a README" (ya tenemos uno)
   - ⬜ **NO** agregues .gitignore ni license (ya los tenemos)
5. Haz clic en **"Create repository"**

### 2. Inicializar Git en tu Proyecto Local

Abre PowerShell o CMD en la carpeta del proyecto:

```powershell
# Navegar a la carpeta del proyecto
cd "d:\Documentos\Maestria Inteligencia artificial\Sniffer\Control_por_voz"

# Inicializar repositorio Git
git init

# Verificar que .gitignore existe
Get-Content .gitignore
```

### 3. Agregar Archivos al Repositorio

```powershell
# Agregar todos los archivos (respetando .gitignore)
git add .

# Verificar qué archivos se agregarán
git status

# Hacer el primer commit
git commit -m "Initial commit: Estructura MLOps completa con MLflow"
```

### 4. Conectar con GitHub

Reemplaza `TU-USUARIO` con tu nombre de usuario de GitHub:

```powershell
# Agregar el repositorio remoto
git remote add origin https://github.com/TU-USUARIO/wheelchair-voice-control.git

# Verificar que se agregó correctamente
git remote -v
```

### 5. Subir el Código a GitHub

```powershell
# Cambiar a la rama main (GitHub usa 'main' por defecto)
git branch -M main

# Subir el código
git push -u origin main
```

**Nota**: Te pedirá tus credenciales de GitHub. Si tienes autenticación de dos factores, necesitarás un Personal Access Token en lugar de tu contraseña.

### 6. Crear Personal Access Token (si es necesario)

Si GitHub te pide un token:

1. Ve a GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click en "Generate new token (classic)"
3. Selecciona los permisos:
   - ✅ `repo` (acceso completo a repositorios)
4. Copia el token generado (¡guárdalo en un lugar seguro!)
5. Usa el token como contraseña cuando Git te lo pida

## 📂 Estructura que se Subirá

```
wheelchair-voice-control/
├── .github/workflows/          # CI/CD pipelines
├── config/                     # Configuraciones
├── data/                       # Datos (solo estructura, no archivos grandes)
├── docs/                       # Documentación
├── models/                     # Modelos (solo estructura)
├── notebooks/                  # Jupyter notebooks
├── scripts/                    # Scripts de utilidad
├── src/wheelchair_control/     # Código fuente
├── tests/                      # Tests
├── .env.example                # Ejemplo de variables de entorno
├── .gitignore                  # Archivos a ignorar
├── CONTRIBUTING.md             # Guía de contribución
├── LICENSE                     # Licencia MIT
├── README.md                   # Documentación principal
├── requirements.txt            # Dependencias
├── setup.py                    # Configuración del paquete
└── pytest.ini                  # Configuración de tests
```

## 🔒 Archivos que NO se Subirán (por .gitignore)

- `mlruns/` - Datos de MLflow (demasiado grandes)
- `mlartifacts/` - Artefactos de MLflow
- `vosk-model-*/` - Modelos de Vosk (descargar por separado)
- `*.db` - Bases de datos
- `.env` - Variables de entorno con secretos
- `__pycache__/` - Cache de Python
- `venv/` - Entorno virtual

## 📝 Comandos Git Útiles

### Ver Estado del Repositorio
```powershell
git status
```

### Ver Historial de Commits
```powershell
git log --oneline
```

### Hacer Cambios Posteriores
```powershell
# Agregar archivos modificados
git add .

# Commit con mensaje descriptivo
git commit -m "feat: agregar nueva funcionalidad"

# Subir cambios
git push
```

### Crear una Rama Nueva
```powershell
# Crear y cambiar a nueva rama
git checkout -b feature/nueva-funcionalidad

# Subir la rama a GitHub
git push -u origin feature/nueva-funcionalidad
```

## 🌟 Configurar GitHub Actions (CI/CD)

Los workflows ya están configurados en `.github/workflows/`:

1. **ci.yml**: Se ejecuta automáticamente en cada push/PR
   - Ejecuta tests
   - Verifica calidad de código
   - Genera reportes de cobertura

2. **mlflow-deploy.yml**: Deployment manual de modelos
   - Se ejecuta manualmente desde GitHub Actions
   - Valida y despliega modelos

### Configurar Secrets (Opcional)

Para que los workflows funcionen completamente:

1. Ve a tu repositorio en GitHub
2. Settings → Secrets and variables → Actions
3. Agrega estos secrets:
   - `MLFLOW_TRACKING_URI`: URL de tu servidor MLflow (si usas uno remoto)

## 📖 Actualizar README

Después de subir, actualiza el README con:

1. URL correcta del repositorio
2. Tu información de contacto
3. Badges de estado (opcional):

```markdown
[![CI](https://github.com/TU-USUARIO/wheelchair-voice-control/workflows/CI/badge.svg)](https://github.com/TU-USUARIO/wheelchair-voice-control/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
```

## 🎯 Próximos Pasos

Después de subir el proyecto:

1. **Agregar Descripción**: En GitHub, edita la descripción del repo
2. **Agregar Topics**: Agrega tags como `machine-learning`, `mlops`, `voice-control`, `wheelchair`, `accessibility`
3. **Crear Releases**: Cuando tengas versiones estables
4. **Documentar Issues**: Crea issues para features futuras
5. **Invitar Colaboradores**: Si trabajas en equipo

## 🆘 Solución de Problemas

### Error: "remote origin already exists"
```powershell
git remote remove origin
git remote add origin https://github.com/TU-USUARIO/wheelchair-voice-control.git
```

### Error: "failed to push some refs"
```powershell
# Primero hacer pull
git pull origin main --allow-unrelated-histories

# Luego push
git push -u origin main
```

### Archivos Grandes
Si tienes archivos muy grandes (>100MB):
```powershell
# Usar Git LFS (Large File Storage)
git lfs install
git lfs track "*.zip"
git add .gitattributes
```

## 📞 Recursos Adicionales

- [Documentación de Git](https://git-scm.com/doc)
- [GitHub Guides](https://guides.github.com/)
- [Git Cheat Sheet](https://education.github.com/git-cheat-sheet-education.pdf)

---

¡Listo! Tu proyecto ahora está en GitHub y listo para colaboración. 🎉
