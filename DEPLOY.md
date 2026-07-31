# Guía de Despliegue - INSCRIB SYSTEM

## Opción 1: Render.com (Recomendada - Gratis)

### Paso 1: Preparar el repositorio
1. Crear una cuenta en [GitHub](https://github.com)
2. Instalar [Git](https://git-scm.com/) en tu PC
3. Abrir una terminal en la carpeta del proyecto y ejecutar:
```bash
git init
git add .
git commit -m "Initial commit"
```

### Paso 2: Subir a GitHub
1. Crear un nuevo repositorio en GitHub (público o privado)
2. Conectar el repositorio local:
```bash
git remote add origin https://github.com/TU_USUARIO/inscrib_system.git
git push -u origin master
```

### Paso 3: Desplegar en Render
1. Crear cuenta en [Render.com](https://render.com)
2. Click en "New +" → "Web Service"
3. Conectar tu repositorio de GitHub
4. Configurar:
   - **Name**: inscrib-system
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app_combined:application --bind 0.0.0.0:$PORT`
5. Agregar **Environment Variables**:
   - `SECRET_KEY`: `tu_clave_secreta_muy_larga_aqui_2026`
   - `JWT_SECRET_KEY`: `otra_clave_secreta_jwt_aqui_2026`
6. Click "Create Web Service"

---

## Opción 2: PythonAnywhere (Gratis con limitaciones)

### Paso 1: Crear cuenta
1. Ir a [PythonAnywhere.com](https://pythonanywhere.com)
2. Crear cuenta gratuita

### Paso 2: Subir archivos
1. Abrir "Dashboard" → "Files"
2. Click "Upload" y subir todos los archivos del proyecto
3. O usar Git si lo tienes configurado

### Paso 3: Configurar la app
1. Ir a "Web" → "Add a new web app"
2. Seleccionar "Python 3.11" → "Manual configuration"
3. En "WSGI configuration file", agregar:
```python
import sys
path = '/home/TU_USUARIO/inscrib_system'
if path not in sys.path:
    sys.path.insert(0, path)

from app_combined import app as application
```

### Paso 4: Instalar dependencias
1. Abrir "Console" (Bash)
2. Ejecutar:
```bash
cd inscrib_system
pip install -r requirements.txt
```

### Paso 5: Variables de entorno
1. Ir a "Web" → "Configuration" → "Environment variables"
2. Agregar:
   - `SECRET_KEY`: `tu_clave_secreta_muy_larga`
   - `JWT_SECRET_KEY`: `otra_clave_secreta`

### Paso 6: Iniciar
1. Click "Reload" en la página de Web

---

## Opción 3: Railway.app

1. Crear cuenta en [Railway.app](https://railway.app)
2. Conectar repositorio de GitHub
3. Configurar como "Python" project
4. Agregar variables de entorno
5. Deploy automático

---

## Credenciales por defecto

| Campo | Valor |
|-------|-------|
| Usuario Admin | `admin` |
| Contraseña | `admin123` |
| Usuario Secretario | `secretario` |
| Contraseña | `secretario123` |

**IMPORTANTE**: Cambiar estas credenciales después del primer inicio de sesión.

---

## Variables de entorno necesarias

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `SECRET_KEY` | Clave secreta para Flask | `mi_clave_secreta_muy_larga_2026` |
| `JWT_SECRET_KEY` | Clave para tokens JWT | `otra_clave_jwt_secreta` |
| `DATABASE_URL` | URL de base de datos (opcional) | `sqlite:///test.db` |

---

## Solución de problemas

### Error: "SECRET_KEY no definido"
- Verificar que las variables de entorno estén configuradas en el hosting

### Error: "ModuleNotFoundError"
- Verificar que `requirements.txt` esté en la raíz del proyecto
- Revisar los logs del hosting para ver qué módulo falta

### La base de datos no persiste
- En Render/Railway, la base de datos SQLite se reinicia al cada deploy
- Para producción real, usar PostgreSQL ( cambia `DATABASE_URL` a `postgresql://...` )

### Los archivos subidos se pierden
- Los uploads se guardan en `/static/uploads/`
- En producción, usar un servicio de almacenamiento como AWS S3 o Cloudinary
