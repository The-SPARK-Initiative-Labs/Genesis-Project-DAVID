@echo off
title David AI - Stopper

echo Stopping Chainlit UI...
:: This command finds the window named "David Chainlit UI" and closes it.
taskkill /F /FI "WINDOWTITLE eq David Chainlit UI" /T >nul

echo Stopping Ollama service...
taskkill /F /IM ollama.exe /T >nul

echo.
echo All services stopped.
pause
