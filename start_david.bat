@echo off
title David AI - Launcher

:: Make sure the script runs from its own directory
cd /d %~dp0

echo Starting Ollama service in the background...
:: Use start /B to run Ollama truly in the background without a new window
start "Ollama Background Process" /B cmd /c "ollama serve"

echo Waiting 5 seconds for Ollama to initialize...
timeout /t 5 /nobreak >nul

echo Starting Chainlit UI on port 8002...
:: Set a unique title for the Chainlit window so we can target it for shutdown
:: CRITICAL FIX: Add --port 8002 to specify the correct port
start "David Chainlit UI" cmd /c "chainlit run src/app.py -w --port 8002"

echo.
echo David is starting up. You can access the UI at http://localhost:8002
echo.
pause
