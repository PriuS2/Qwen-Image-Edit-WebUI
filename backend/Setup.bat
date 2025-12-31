@echo off
title Qwen Image Edit API - Setup

echo ===========================================================
echo   Qwen Image Edit API - Setup
echo ===========================================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed.
    echo Please install Python 3.10+: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [INFO] Checking Python version...
python --version
echo.

:: Create virtual environment
if not exist "venv" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
) else (
    echo [INFO] Using existing virtual environment
)
echo.

:: Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat
echo.

:: Upgrade pip
echo [INFO] Upgrading pip...
python -m pip install --upgrade pip
echo.

:: Install PyTorch
echo [INFO] Installing PyTorch (CUDA 12.6)...
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu126
echo.

:: Install dependencies
echo [INFO] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo [OK] Dependencies installed
echo.

:: Create directories
echo [INFO] Creating storage directories...
if not exist "storage\images" mkdir storage\images
if not exist "storage\thumbnails" mkdir storage\thumbnails
if not exist "storage\temp" mkdir storage\temp
if not exist "storage\uploads" mkdir storage\uploads
echo [OK] Directories created
echo.

:: Done
echo ===========================================================
echo   Setup Complete!
echo ===========================================================
echo.
echo   Run 'Run.bat' to start the server.
echo.
echo   API Docs: http://localhost:8000/docs
echo   Default API Key: qwen-image-edit-default-key
echo.
pause
