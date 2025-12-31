@echo off
chcp 65001 > nul
title Qwen Image Edit WebUI - Frontend

echo ========================================
echo   Qwen Image Edit WebUI - Frontend
echo ========================================
echo.

:: Check if node_modules exists
if not exist "node_modules" (
    echo [!] node_modules 폴더가 없습니다.
    echo [*] 의존성을 설치합니다...
    echo.
    call npm install
    if errorlevel 1 (
        echo [ERROR] 의존성 설치에 실패했습니다.
        pause
        exit /b 1
    )
    echo.
) else (
    :: Check if @tailwindcss/postcss is installed
    if not exist "node_modules\@tailwindcss\postcss" (
        echo [!] 일부 패키지가 누락되었습니다.
        echo [*] 의존성을 다시 설치합니다...
        echo.
        call npm install
        if errorlevel 1 (
            echo [ERROR] 의존성 설치에 실패했습니다.
            pause
            exit /b 1
        )
        echo.
    )
)

echo [*] 개발 서버를 시작합니다...
echo [*] http://localhost:3000 에서 접속 가능합니다.
echo [*] 종료하려면 Ctrl+C를 누르세요.
echo.

:: Run the development server
call npm run dev

pause
