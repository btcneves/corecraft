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

REM Ensure commands run from the repository root even when the script is called
REM from another directory.
pushd "%~dp0\.." >nul

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
    if "%~2"=="" (
        echo [ERROR] Missing value for --single-activity
        goto :fail
    )
    echo %~2 | findstr /B "-" >nul 2>&1
    if not errorlevel 1 (
        echo [ERROR] Missing value for --single-activity
        goto :fail
    )
    set SINGLE_ACTIVITY=%~2
    shift
    shift
    goto :parse_args
)
if /i "%~1"=="-h" goto :show_help
if /i "%~1"=="--help" goto :show_help
echo [ERROR] Unknown option: %~1
goto :fail

:show_help
echo CoreCraft Setup Script for Windows
echo.
echo Usage: %~nx0 [OPTIONS]
echo.
echo Options:
echo   --no-build           Skip building images (use existing images)
echo   --single-activity    Start only one activity (atividade-1, atividade-2, or atividade-3)
echo   -h, --help           Show this help message
goto :success

:after_parse

if not "%SINGLE_ACTIVITY%"=="" (
    if /i not "%SINGLE_ACTIVITY%"=="atividade-1" if /i not "%SINGLE_ACTIVITY%"=="atividade-2" if /i not "%SINGLE_ACTIVITY%"=="atividade-3" (
        echo [ERROR] Invalid activity: %SINGLE_ACTIVITY%
        echo [ERROR] Valid values: atividade-1, atividade-2, atividade-3
        goto :fail
    )
)

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
    goto :fail
)

docker compose version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker Compose v2 is not installed. Docker Desktop should include this.
    echo.
    echo Please reinstall Docker Desktop and ensure Compose v2 is selected.
    goto :fail
)

for /f "tokens=3" %%a in ('docker --version') do set DOCKER_VERSION=%%a
echo [OK] Docker %DOCKER_VERSION% detected

REM Check WSL 2, which is recommended for developer experience on Windows.
echo [INFO] Checking WSL 2...
wsl --list -v >nul 2>&1
if errorlevel 1 (
    echo [WARN] WSL 2 was not detected.
    echo.
    echo   To install WSL 2 with Ubuntu, run in PowerShell as Administrator:
    echo     wsl --install -d Ubuntu
    echo.
    echo   Docker Desktop can work without WSL 2, but WSL 2 is recommended
    echo   for performance and Linux command compatibility.
    echo.
) else (
    echo [OK] WSL 2 detected
)

REM Step 2: Check Docker daemon is running
echo [INFO] Checking Docker daemon...

docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker daemon is not running. Please start Docker Desktop first.
    echo.
    echo Open Docker Desktop and wait for it to fully start.
    goto :fail
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
        goto :fail
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

findstr /B "^COMPOSE_PROFILES=" .env >nul 2>&1
if errorlevel 1 (
    echo [WARN] COMPOSE_PROFILES is not set in .env. Adding COMPOSE_PROFILES=all.
    echo.>> .env
    echo COMPOSE_PROFILES=all>> .env
)

REM Step 6: Validate Docker Compose configuration
echo [INFO] Validating Docker Compose configuration...
if not "%SINGLE_ACTIVITY%"=="" (
    docker compose --profile %SINGLE_ACTIVITY% config >nul
) else (
    docker compose --profile all config >nul
)
if errorlevel 1 (
    echo [ERROR] Docker Compose configuration is invalid
    goto :fail
)
echo [OK] Docker Compose configuration is valid

REM Step 7: Build Docker images
if "%DO_BUILD%"=="true" (
    echo [INFO] Building Docker images...
    echo.
    
    if not "%SINGLE_ACTIVITY%"=="" (
        echo [OK] Building images for %SINGLE_ACTIVITY%...
        docker compose build %SINGLE_ACTIVITY%
    ) else (
        echo [OK] Building all images (this may take a few minutes)...
        docker compose --profile all build
    )
    
    if errorlevel 1 (
        echo [ERROR] Docker build failed
        goto :fail
    )
    echo [OK] Docker images built successfully
) else (
    echo [INFO] Skipping Docker build (--no-build flag set)
)

REM Step 8: Show next steps
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
    echo   docker compose --profile all up
    echo.
    echo Or in detached mode:
    echo.
    echo   docker compose --profile all up -d
    echo.
    echo To start a specific activity:
    echo   docker compose --profile atividade-1 up   # Activity 1 only
    echo   docker compose --profile atividade-2 up   # Activity 2 only
    echo   docker compose --profile atividade-3 up   # Activity 3 only
)

echo.
echo [INFO] Useful commands:
echo   docker compose logs -f       # View logs
echo   docker compose ps            # Check service status
echo   docker compose down          # Stop all services
echo.
echo [INFO] Documentation: docs/README.md
echo.
echo [INFO] Manual setup notes without Docker:
echo   - To use bitcoin-cli on native Windows, add this directory to PATH:
echo       C:\Program Files\Bitcoin\daemon\
echo     (Control Panel ^> System ^> Environment Variables ^> PATH)
echo.
echo   - If PowerShell blocks .ps1 scripts, for example venv Activate.ps1:
echo       Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
echo.

goto :success

:success
popd >nul
endlocal
exit /b 0

:fail
popd >nul
endlocal
exit /b 1
