@echo off
title David AI - Stopper

echo Stopping Chainlit UI...
:: CRITICAL FIX: Stop the Chainlit python process by targeting the unique window title
taskkill /F /FI "WINDOWTITLE eq David Chainlit UI" /IM cmd.exe /T >nul

echo Stopping Ollama service...
taskkill /F /IM ollama.exe /T >nul

echo All services stopped.
pause
