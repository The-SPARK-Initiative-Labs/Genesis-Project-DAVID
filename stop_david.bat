@echo off
TITLE David AI - Shutdown

ECHO Unloading David's model from memory...
ollama stop qwen3:14b

ECHO Shutting down the Ollama service...
taskkill /IM ollama.exe /F

ECHO David shutdown complete. Press any key to exit.
pause
