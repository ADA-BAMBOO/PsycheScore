@echo off
REM Midnight Network Development Environment Startup Script for Windows
REM This script builds and starts the complete Docker-based development environment

echo 🚀 Starting Midnight Network Development Environment...
echo ========================================================

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

echo ✅ Docker is running

REM Build and start the environment
echo 📦 Building and starting Docker containers...
docker-compose -f ..\docker-compose.midnight.yml up --build -d

REM Wait for services to start
echo ⏳ Waiting for services to initialize...
timeout /t 10 /nobreak >nul

REM Check service status
echo 🔍 Checking service status...
docker-compose -f ..\docker-compose.midnight.yml ps

echo.
echo 🎉 Midnight Network Development Environment is ready!
echo.
echo 📱 Access Points:
echo    Frontend:      http://localhost:3000
echo    Backend API:   http://localhost:8000
echo    Proof Server:  http://localhost:6300
echo.
echo 🔧 Development Commands:
echo    View logs:     docker-compose -f ..\docker-compose.midnight.yml logs -f
echo    Stop services: docker-compose -f ..\docker-compose.midnight.yml down
echo    Restart:       docker-compose -f ..\docker-compose.midnight.yml restart
echo.
echo 💡 Next Steps:
echo    1. Configure Lace wallet to use local proof server (http://localhost:6300)
echo    2. Get test tokens from Midnight Testnet Faucet
echo    3. Test the PsycheScore DApp functionality

pause