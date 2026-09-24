# AI Small Business Operations Agent - Startup Script (Windows)
# Starts n8n with proper configuration

@echo off
echo ==========================================
echo   AI Business Operations Agent - Startup
echo ==========================================
echo.

REM Check if n8n is installed
where n8n >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: n8n not found. Install with: npm install -g n8n
    exit /b 1
)

echo n8n found
echo Node version:
node --version
echo.

REM Set environment variables
set N8N_PORT=5678
set N8N_PROTOCOL=http
set N8N_HOST=localhost

REM Load .env if exists
if exist .env (
    echo Loading environment variables from .env...
    for /f "usebackq tokens=*" %%a in (".env") do (
        set %%a
    )
)

echo Starting n8n on http://localhost:%N8N_PORT%
echo Workflow endpoint: http://localhost:%N8N_PORT%/webhook/order-request
echo.
echo Press Ctrl+C to stop
echo.

REM Start n8n
n8n start
