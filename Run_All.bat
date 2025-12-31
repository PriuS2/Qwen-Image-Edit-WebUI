@echo off
chcp 65001 > nul
title Qwen Image Edit WebUI - All Services

echo ========================================
echo   Qwen Image Edit WebUI - All Services
echo ========================================
echo.

:: Get the directory where this script is located
set "ROOT_DIR=%~dp0"
cd /d "%ROOT_DIR%"

:: Git fetch and pull
echo [*] Git 저장소를 업데이트합니다...
echo.

git fetch
if errorlevel 1 (
    echo [!] Git fetch 실패. Git이 설치되어 있는지 확인하세요.
    echo [*] 업데이트 없이 계속 진행합니다...
    echo.
) else (
    echo [*] 변경사항을 가져옵니다...
    git pull
    if errorlevel 1 (
        echo [!] Git pull 실패. 충돌이 있을 수 있습니다.
        echo [*] 수동으로 해결한 후 다시 실행하세요.
        pause
        exit /b 1
    )
    echo [OK] Git 업데이트 완료!
    echo.
)

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
