@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

cd /d "%~dp0"

echo ===================================================
echo   INSCRIB SYSTEM - Iniciador automatico
echo ===================================================
echo(

REM --- Verificar que Python este instalado ---
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no esta instalado o no esta en el PATH.
    echo Descarga e instala Python desde https://www.python.org/downloads/
    echo Asegurate de marcar "Add Python to PATH" al instalar.
    pause
    exit /b 1
)

REM --- Crear entorno virtual si no existe ---
if not exist "env\Scripts\python.exe" (
    echo Creando entorno virtual...
    python -m venv env
    if errorlevel 1 (
        echo [ERROR] No se pudo crear el entorno virtual.
        pause
        exit /b 1
    )
    echo Entorno virtual creado correctamente.
)

REM --- Activar entorno virtual ---
call env\Scripts\activate.bat

REM --- Instalar dependencias ---
echo [1/3] Verificando dependencias...
pip install -r requirements.txt --quiet 2>nul
if errorlevel 1 (
    echo [AVISO] Algunas dependencias no se pudieron instalar.
    echo Verificando dependencias criticas...
    pip install flask flask_sqlalchemy flask_cors flask_talisman flask_limiter bcrypt python-docx reportlab PyJWT gunicorn --quiet 2>nul
)
echo Dependencias verificadas.
echo(

REM --- Iniciar servidor de administracion (puerto 5001) ---
echo [2/3] Iniciando servidor de administracion (http://127.0.0.1:5001)...
start "INSCRIB Admin" python app.py

REM --- Iniciar sitio publico (puerto 5002) ---
echo [3/3] Iniciando sitio publico (http://127.0.0.1:5002)...
start "INSCRIB Publico" python run_public.py

echo(
echo Esperando a que los servidores arranquen...
timeout /t 5 /nobreak >nul

REM --- Abrir navegador ---
start "" http://127.0.0.1:5001/login
start "" http://127.0.0.1:5002/

echo(
echo ===================================================
echo  Servidores iniciados correctamente.
echo  Admin:    http://127.0.0.1:5001/login
echo  Publico:  http://127.0.0.1:5002/
echo(
echo  CREDENCIALES:
echo    Usuario:  admin
echo    Sena:     admin123
echo(
echo  Cierra las ventanas de los servidores para detenerlos.
echo ===================================================
echo(
pause
