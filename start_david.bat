@echo off
TITLE David AI - Launcher

ECHO Starting Ollama service in the background...
start "" "ollama" serve

ECHO Waiting 5 seconds for Ollama to initialize...
timeout /t 5 > nul

ECHO Starting Chainlit UI (David will load automatically)...
cd src
python -m chainlit run app.py --port 8002 -w

ECHO Chainlit has been closed. Press any key to exit.
pause