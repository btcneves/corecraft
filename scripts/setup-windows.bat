@echo off
REM
REM CoreCraft Setup Script for Windows
REM ===================================
REM This script sets up the CoreCraft Docker environment on Windows.
REM
REM Usage: scripts\setup-windows.bat [--no-build] [--single-activity <name>]
REM
REM Options:
REM   --no-build           Skip building images (use existing images)
REM   --single-activity    Start only one activity (atividade-1, atividade-2, or atividade-3)
REM

setlocal EnableDelayedExpansion

REM Default options
set DO_BUILD=true
set SINGLE_ACTIVITY=

REM Parse command line arguments
:parse_args
if "%~1"=="" goto :after_parse
if /i "%~1"=="--no-build" (
    set DO_BUILD=false
    shift
    goto :parse_args
)
if /i "%~1"=="--single-activity" (
    set SINGLE_ACTIVITY=%~2
    shift
    shift
    goto :parse_args
)
if /i "%~1"=="-h" goto :show_help
if /i "%~1"=="--help" goto :show_help
echo [ERROR] Unknown option: %~1
exit /b 1

:show_help
echo CoreCraft Setup Script for Windows
echo.
echo Usage: %~nx0 [OPTIONS]
echo.
echo Options:
echo   --no-build           Skip building images (use existing images)
echo   --single-activity    Start only one activity (atividade-1, atividade-2, or atividade-3)
echo   -h, --help           Show this help message
exit /b 0

:after_parse

echo.
echo ==========================================
echo   CoreCraft Setup - Windows
echo ==========================================
echo.

REM Step 1: Check Docker installation
echo [INFO] Checking Docker installation...

docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not installed. Please install Docker Desktop for Windows first.
    echo.
    echo Download from: https://www.docker.com/products/docker-desktop/
    echo.
    echo Make sure to enable WSL 2 backend during installation.
    exit /b 1
)

docker compose version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker Compose v2 is not installed. Docker Desktop should include this.
    echo.
    echo Please reinstall Docker Desktop and ensure Compose v2 is selected.
    exit /b 1
)

for /f "tokens=3" %%a in ('docker --version') do set DOCKER_VERSION=%%a
echo [OK] Docker %DOCKER_VERSION% detected

REM Verificar WSL 2 (recomendado para melhor desempenho)
echo [INFO] Checking WSL 2...
wsl --list -v >nul 2>&1
if errorlevel 1 (
    echo [WARN] WSL 2 nao detetado ou nao esta instalado.
    echo.
    echo   Para instalar WSL 2 com Ubuntu (PowerShell como Administrador):
    echo     wsl --install -d Ubuntu
    echo.
    echo   O Docker Desktop funciona sem WSL 2, mas e recomendado para melhor
    echo   desempenho e compatibilidade com comandos Linux.
    echo.
) else (
    echo [OK] WSL 2 disponivel
)

REM Step 2: Check Docker daemon is running
echo [INFO] Checking Docker daemon...

docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker daemon is not running. Please start Docker Desktop first.
    echo.
    echo Open Docker Desktop and wait for it to fully start.
    exit /b 1
)
echo [OK] Docker daemon is running

REM Step 3: Check for port conflicts
echo [INFO] Checking for port conflicts...

set PORT_CONFLICTS=false
for %%P in (80 8001 8002 8003 18443 28332 28333) do (
    netstat -ano ^| findstr ":%%P " ^| findstr "LISTENING" >nul 2>&1
    if not errorlevel 1 (
        echo [WARN] Port %%P is already in use
        set PORT_CONFLICTS=true
    )
)

if "%PORT_CONFLICTS%"=="true" (
    echo [WARN] Some ports are already in use. You may need to stop other services or change ports.
)

REM Step 4: Setup .env file
echo [INFO] Setting up environment file...

if exist .env (
    echo [WARN] .env file already exists. Skipping creation.
    echo   To reset, delete .env and run again.
) else (
    if exist .env.example (
        copy .env.example .env >nul
        echo [OK] Created .env from .env.example
    ) else (
        echo [ERROR] .env.example not found. Cannot create .env file.
        exit /b 1
    )
)

REM Step 5: Validate .env file
echo [INFO] Validating environment file...

set MISSING_VARS=
findstr /B "^BTC_RPC_USER=" .env >nul 2>&1
if errorlevel 1 set MISSING_VARS=!MISSING_VARS! BTC_RPC_USER

findstr /B "^BTC_RPC_PASSWORD=" .env >nul 2>&1
if errorlevel 1 set MISSING_VARS=!MISSING_VARS! BTC_RPC_PASSWORD

findstr /B "^LOG_LEVEL=" .env >nul 2>&1
if errorlevel 1 set MISSING_VARS=!MISSING_VARS! LOG_LEVEL

if not "!MISSING_VARS!"=="" (
    echo [WARN] Missing environment variables:!MISSING_VARS!
    echo [WARN] Please add them to .env file
) else (
    echo [OK] Environment file is valid
)

REM Step 6: Build Docker images
if "%DO_BUILD%"=="true" (
    echo [INFO] Building Docker images...
    echo.
    
    if not "%SINGLE_ACTIVITY%"=="" (
        echo [OK] Building images for %SINGLE_ACTIVITY%...
        docker compose build %SINGLE_ACTIVITY%
    ) else (
        echo [OK] Building all images (this may take a few minutes)...
        docker compose build
    )
    
    if errorlevel 1 (
        echo [ERROR] Docker build failed
        exit /b 1
    )
    echo [OK] Docker images built successfully
) else (
    echo [INFO] Skipping Docker build (--no-build flag set)
)

REM Step 7: Show next steps
echo.
echo ==========================================
echo   Setup Complete!
echo ==========================================
echo.

if not "%SINGLE_ACTIVITY%"=="" (
    echo [OK] To start %SINGLE_ACTIVITY%, run:
    echo.
    echo   docker compose --profile %SINGLE_ACTIVITY% up
    echo.
    echo Or in detached mode:
    echo.
    echo   docker compose --profile %SINGLE_ACTIVITY% up -d
) else (
    echo [OK] To start all services, run:
    echo.
    echo   docker compose up
    echo.
    echo Or in detached mode:
    echo.
    echo   docker compose up -d
    echo.
    echo To start a specific activity:
    echo   docker compose --profile atividade-1 up   # Only Atividade 1
    echo   docker compose --profile atividade-2 up   # Only Atividade 2
    echo   docker compose --profile atividade-3 up   # Only Atividade 3
)

echo.
echo [INFO] Useful commands:
echo   docker compose logs -f       # View logs
echo   docker compose ps            # Check service status
echo   docker compose down          # Stop all services
echo.
echo [INFO] Documentation: docs/README.md
echo.
echo [INFO] Notas para uso manual (sem Docker):
echo   - Para usar bitcoin-cli no Windows nativo, adicione ao PATH:
echo       C:\Program Files\Bitcoin\daemon\
echo     (Painel de Controlo ^> Sistema ^> Variaveis de Ambiente ^> PATH)
echo.
echo   - Se o PowerShell bloquear scripts .ps1 (ex: Activate.ps1 do venv):
echo       Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
echo.

endlocal