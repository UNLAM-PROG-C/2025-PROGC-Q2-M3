@echo off
setlocal

set "PYTHON_VERSION=3.11.9"
set "PYTHON_INSTALLER_URL=https://www.python.org/ftp/python/%PYTHON_VERSION%/python-%PYTHON_VERSION%-amd64.exe"
set "PYTHON_INSTALLER=%TEMP%\python-installer.exe"

echo ==========================================================
echo  Verificando Python...
echo ==========================================================

python --version >nul 2>nul
if %errorlevel%==0 goto :python_ok

python3 --version >nul 2>nul
if %errorlevel%==0 goto :python_ok

echo Python no encontrado. Descargando Python %PYTHON_VERSION%...
powershell -Command "Invoke-WebRequest -Uri '%PYTHON_INSTALLER_URL%' -OutFile '%PYTHON_INSTALLER%' -UseBasicParsing"

if not exist "%PYTHON_INSTALLER%" (
    echo Error: no se pudo descargar el instalador.
    exit /b 1
)

echo Instalando Python...
"%PYTHON_INSTALLER%" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
if %errorlevel% neq 0 (
    echo Falló la instalación de Python.
    del "%PYTHON_INSTALLER%"
    exit /b 1
)
del "%PYTHON_INSTALLER%"

:python_ok
echo Python disponible:
python --version 2>nul || python3 --version 2>nul

echo ==========================================================
echo Actualizando pip...
python -m ensurepip --upgrade >nul 2>nul
python -m pip install --upgrade pip

echo Instalando Pygame...
python -m pip install pygame

set /p SERVER_HOST="Ingrese la direccion IP del servidor (default: 127.0.0.1): "
if "%SERVER_HOST%"=="" set SERVER_HOST=127.0.0.1

set /p SERVER_PORT="Ingrese el puerto del servidor (default: 8888): "
if "%SERVER_PORT%"=="" set SERVER_PORT=8888

echo ==========================================================
echo Ejecutando juego...
echo ==========================================================

py main.py --host %SERVER_HOST% --port %SERVER_PORT% %AUTO_CONNECT_ARG%

endlocal
