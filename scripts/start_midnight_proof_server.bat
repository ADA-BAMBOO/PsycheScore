@echo off
REM Midnight Network Proof Server Startup Script for Windows
REM This script starts the Midnight proof server for ZK proof generation

echo Starting Midnight Network Proof Server...

REM Check if Docker is available
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Docker is not installed or not in PATH
    exit /b 1
)

REM Check if proof server image exists
docker images | findstr "midnightnetwork/proof-server" >nul
if %errorlevel% neq 0 (
    echo Pulling Midnight proof server image...
    docker pull midnightnetwork/proof-server:latest
)

REM Stop any existing proof server containers
echo Stopping any existing proof server containers...
docker stop midnight-proof-server >nul 2>&1
docker rm midnight-proof-server >nul 2>&1

REM Start the proof server
echo Starting Midnight proof server on port 6300...
docker run -d ^
    --name midnight-proof-server ^
    -p 6300:6300 ^
    midnightnetwork/proof-server:latest ^
    midnight-proof-server --network testnet

REM Wait for server to start
echo Waiting for proof server to start...
timeout /t 5 /nobreak >nul

REM Check if server is running
curl -s http://localhost:6300/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Midnight proof server is running on http://localhost:6300
) else (
    echo ⚠️  Proof server started but health check failed. It may take a moment to initialize.
    echo You can check the logs with: docker logs midnight-proof-server
)

echo.
echo Proof server configuration:
echo   - Network: testnet
echo   - Port: 6300
echo   - Health endpoint: http://localhost:6300/health
echo.
echo To stop the server: docker stop midnight-proof-server
echo To view logs: docker logs -f midnight-proof-server