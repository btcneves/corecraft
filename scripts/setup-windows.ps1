<#
.SYNOPSIS
    Set up the CoreCraft Docker development environment on Windows.

.DESCRIPTION
    This script validates Docker Desktop, checks common port conflicts, prepares
    the .env file, validates Docker Compose, and optionally builds images.

.PARAMETER NoBuild
    Skip Docker image builds.

.PARAMETER SingleActivity
    Build and show commands for one activity only: atividade-1, atividade-2, or atividade-3.

.EXAMPLE
    .\scripts\setup-windows.ps1

.EXAMPLE
    .\scripts\setup-windows.ps1 -NoBuild

.EXAMPLE
    .\scripts\setup-windows.ps1 -SingleActivity atividade-2
#>

[CmdletBinding()]
param(
    [switch]$NoBuild,

    [ValidateSet("atividade-1", "atividade-2", "atividade-3")]
    [string]$SingleActivity
)

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $RepoRoot

function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Cyan
}

function Write-Ok {
    param([string]$Message)
    Write-Host "[OK] $Message" -ForegroundColor Green
}

function Write-Warn {
    param([string]$Message)
    Write-Host "[WARN] $Message" -ForegroundColor Yellow
}

function Stop-WithError {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
    exit 1
}

function Test-Command {
    param([string]$Name)
    return [bool](Get-Command $Name -ErrorAction SilentlyContinue)
}

Write-Host ""
Write-Host "=========================================="
Write-Host "  CoreCraft Setup - Windows PowerShell"
Write-Host "=========================================="
Write-Host ""

Write-Info "Checking Docker installation..."
if (-not (Test-Command "docker")) {
    Stop-WithError "Docker is not installed. Install Docker Desktop from https://www.docker.com/products/docker-desktop/"
}

& docker compose version *> $null
if ($LASTEXITCODE -ne 0) {
    Stop-WithError "Docker Compose v2 is not available. Docker Desktop should include it."
}

$dockerVersion = (& docker --version)
Write-Ok $dockerVersion

Write-Info "Checking WSL 2..."
if (Test-Command "wsl") {
    & wsl --list --verbose *> $null
    if ($LASTEXITCODE -eq 0) {
        Write-Ok "WSL 2 detected"
    } else {
        Write-Warn "WSL is installed, but no distribution appears to be configured."
    }
} else {
    Write-Warn "WSL 2 was not detected. It is recommended for Docker Desktop performance."
    Write-Host "       Install with: wsl --install -d Ubuntu"
}

Write-Info "Checking Docker daemon..."
& docker info *> $null
if ($LASTEXITCODE -ne 0) {
    Stop-WithError "Docker daemon is not running. Start Docker Desktop and try again."
}
Write-Ok "Docker daemon is running"

Write-Info "Checking for port conflicts..."
$ports = @(80, 8001, 8002, 8003, 18443, 28332, 28333)
$conflicts = @()
foreach ($port in $ports) {
    $listeners = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
    if ($listeners) {
        $conflicts += $port
        Write-Warn "Port $port is already in use"
    }
}
if ($conflicts.Count -gt 0) {
    Write-Warn "Stop conflicting services or adjust docker-compose.yml ports before starting the stack."
}

Write-Info "Setting up environment file..."
if (Test-Path ".env") {
    Write-Warn ".env already exists. Skipping creation."
} elseif (Test-Path ".env.example") {
    Copy-Item ".env.example" ".env"
    Write-Ok "Created .env from .env.example"
} else {
    Stop-WithError ".env.example not found. Cannot create .env."
}

Write-Info "Validating environment file..."
$envContent = Get-Content ".env" -ErrorAction Stop
$requiredVars = @("BTC_RPC_USER", "BTC_RPC_PASSWORD", "LOG_LEVEL")
$missing = @()
foreach ($name in $requiredVars) {
    if (-not ($envContent | Where-Object { $_ -match "^$name=" })) {
        $missing += $name
    }
}
if ($missing.Count -gt 0) {
    Write-Warn "Missing environment variables: $($missing -join ', ')"
} else {
    Write-Ok "Environment file is valid"
}

if (-not ($envContent | Where-Object { $_ -match "^COMPOSE_PROFILES=" })) {
    Write-Warn "COMPOSE_PROFILES is not set in .env. Adding COMPOSE_PROFILES=all."
    Add-Content ".env" ""
    Add-Content ".env" "COMPOSE_PROFILES=all"
}

Write-Info "Validating Docker Compose configuration..."
if ($SingleActivity) {
    & docker compose --profile $SingleActivity config *> $null
} else {
    & docker compose --profile all config *> $null
}
if ($LASTEXITCODE -ne 0) {
    Stop-WithError "Docker Compose configuration is invalid."
}
Write-Ok "Docker Compose configuration is valid"

if (-not $NoBuild) {
    Write-Info "Building Docker images..."
    if ($SingleActivity) {
        & docker compose build $SingleActivity
    } else {
        & docker compose --profile all build
    }
    if ($LASTEXITCODE -ne 0) {
        Stop-WithError "Docker build failed."
    }
    Write-Ok "Docker images built successfully"
} else {
    Write-Info "Skipping Docker build (-NoBuild set)"
}

Write-Host ""
Write-Host "=========================================="
Write-Host "  Setup Complete"
Write-Host "=========================================="
Write-Host ""

if ($SingleActivity) {
    Write-Ok "To start $SingleActivity:"
    Write-Host "  docker compose --profile $SingleActivity up"
    Write-Host "  docker compose --profile $SingleActivity up -d"
} else {
    Write-Ok "To start the full stack:"
    Write-Host "  docker compose --profile all up"
    Write-Host "  docker compose --profile all up -d"
}

Write-Host ""
Write-Info "Useful commands:"
Write-Host "  docker compose logs -f"
Write-Host "  docker compose ps"
Write-Host "  docker compose down"
Write-Host ""
Write-Info "Documentation: docs/README.md"

