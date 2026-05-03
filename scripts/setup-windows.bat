@echo off
setlocal

docker compose version >nul 2>&1
if errorlevel 1 (
  echo Docker Desktop with Docker Compose v2 is required.
  exit /b 1
)

if not exist .env copy .env.example .env >nul
docker compose build
echo Setup complete. Run: docker compose up
