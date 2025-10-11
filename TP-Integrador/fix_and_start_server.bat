@echo off
title Servidor Batalla Naval - Auto Fix
color 0E
echo.
echo ================================================
echo      SERVIDOR BATALLA NAVAL - AUTO FIX
echo ================================================
echo.
echo 🔧 Verificando puerto 8888...

:: Verificar si el puerto está ocupado
netstat -ano | findstr :8888 > nul
if %errorlevel% == 0 (
    echo ⚠️  Puerto 8888 está ocupado
    echo 🔧 Liberando puerto...
    
    :: Obtener PID del proceso que usa el puerto
    for /f "tokens=5" %%i in ('netstat -ano ^| findstr :8888') do (
        echo 🗡️  Terminando proceso PID: %%i
        taskkill /F /PID %%i > nul 2>&1
    )
    
    echo ✅ Puerto liberado
) else (
    echo ✅ Puerto 8888 disponible
)

echo.
echo 🚀 Iniciando servidor...
echo ------------------------------------------------

cd /d "C:\Users\marin\Desktop\Progra concurrente\2025-PROGC-Q2-M3\TP-Integrador"
python server.py

echo.
echo 📴 Servidor detenido.
pause