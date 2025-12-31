@echo off
title Qwen Image Edit API - Server

echo ===========================================================
echo   Qwen Image Edit API - Server
echo ===========================================================
echo.

:: Check virtual environment
if not exist "venv" (
    echo [ERROR] Virtual environment not found.
    echo Please run Setup.bat first.
    pause
    exit /b 1
)

:: Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat
echo.

:: Show GPU info
echo [INFO] Checking GPU info...
python -c "import torch; print(f'CUDA Available: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0)}') if torch.cuda.is_available() else print('GPU: None')"
echo.

:: Check .env file
if exist ".env" (
    echo [INFO] .env file loaded
) else (
    echo [INFO] No .env file - using default settings
)
echo.

:: Start server
echo ===========================================================
echo   Starting Server
echo ===========================================================
echo.
echo   API Docs: http://localhost:8000/docs
echo   Health Check: http://localhost:8000/health
echo.
echo   Press Ctrl+C to stop the server.
echo.
echo ===========================================================
echo.

python main.py

:: Server stopped
echo.
echo [INFO] Server stopped.
pause
