@echo off
:: Script para iniciar el servidor directo (sin ngrok)
title Batalla Naval - Servidor Directo

echo.
echo ========================================================================
echo                BATALLA NAVAL - SERVIDOR DIRECTO
echo ========================================================================
echo.
echo Este script iniciara el servidor sin dependencias externas
echo Los jugadores podran conectarse usando la IP local o publica
echo.
echo IMPORTANTE:
echo - No requiere ngrok ni otros servicios externos
echo - Configura el firewall para permitir conexiones al puerto
echo - Los jugadores deben usar tu IP publica y el puerto configurado
echo.
echo ========================================================================
echo.

pause

:: Ejecutar el script de Python para servidor directo
python start_server.py

pause
