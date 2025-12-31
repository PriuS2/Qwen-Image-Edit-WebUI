@echo off
chcp 65001 > nul
title Qwen Image Edit WebUI - All Services

echo ========================================
echo   Qwen Image Edit WebUI - All Services
echo ========================================
echo.

:: Get the directory where this script is located
set "ROOT_DIR=%~dp0"

:: Start Backend Server
echo [*] 백엔드 서버를 시작합니다...
start "Backend - Qwen Image Edit" cmd /k "cd /d "%ROOT_DIR%backend" && call Run.bat"

:: Wait a moment for backend to initialize
timeout /t 3 /nobreak > nul

:: Start Frontend Server
echo [*] 프론트엔드 서버를 시작합니다...
start "Frontend - Qwen Image Edit" cmd /k "cd /d "%ROOT_DIR%frontend" && call Run.bat"

echo.
echo ========================================
echo   서버가 시작되었습니다!
echo ========================================
echo.
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:3000
echo   API Docs: http://localhost:8000/docs
echo.
echo   각 창을 닫으면 해당 서버가 종료됩니다.
echo ========================================
echo.

pause
