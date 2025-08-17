@echo off
title David AI - Launcher

:: This command ensures the script always runs from the correct directory (C:\David)
cd /d %~dp0

echo Activating Python virtual environment...
:: CRITICAL FIX: Activate the virtual environment so the 'chainlit' command can be found.
call .venv\Scripts\activate

echo Starting Ollama service in the background...
:: Start Ollama in a separate, non-blocking background process.
start "Ollama Server" /B ollama serve

echo Waiting 5 seconds for Ollama to initialize...
timeout /t 5 /nobreak >nul

echo Starting Chainlit UI on port 8002...
:: Start Chainlit in its own window with a unique title for easy shutdown.
start "David Chainlit UI" chainlit run app.py -w --port 8002

echo.
echo David is starting up.
