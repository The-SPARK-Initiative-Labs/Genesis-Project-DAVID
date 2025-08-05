@echo off
TITLE David AI - Shutdown

ECHO Forcing Ollama to unload the model and free VRAM...
curl http://localhost:11434/api/generate -d "{\"model\": \"david\", \"keep_alive\": 0}"

ECHO Shutting down the Ollama service...
taskkill /IM ollama.exe /F

ECHO System shutdown complete. Press any key to exit.
pause