@echo off
setlocal
title Kokoro Pro AI TTS Launcher

echo ==========================================
echo    Lanzador Kokoro Pro AI TTS
echo ==========================================
echo.

:: Cambiar al directorio de la aplicacion
cd /d "%~dp0"

:: Abrir el navegador despues de un breve retraso
start http://127.0.0.1:5000

:: Iniciar el servidor de Flask con prioridad alta
echo Iniciando servidor Flask (Rendimiento Optimizado)...
start /abovenormal /wait python app.py

if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] Hubo un problema al iniciar la aplicacion.
    echo Asegurate de que Python esta instalado y las librerias cargadas.
    pause
)

endlocal
