#!/bin/bash

# Midnight Network Proof Server Startup Script
# This script starts the Midnight proof server for ZK proof generation

set -e

echo "Starting Midnight Network Proof Server..."

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed or not in PATH"
    exit 1
fi

# Check if proof server image exists
if ! docker images | grep -q "midnightnetwork/proof-server"; then
    echo "Pulling Midnight proof server image..."
    docker pull midnightnetwork/proof-server:latest
fi

# Stop any existing proof server containers
echo "Stopping any existing proof server containers..."
docker stop midnight-proof-server 2>/dev/null || true
docker rm midnight-proof-server 2>/dev/null || true

# Start the proof server
echo "Starting Midnight proof server on port 6300..."
docker run -d \
    --name midnight-proof-server \
    -p 6300:6300 \
    midnightnetwork/proof-server:latest \
    midnight-proof-server --network testnet

# Wait for server to start
echo "Waiting for proof server to start..."
sleep 5

# Check if server is running
if curl -s http://localhost:6300/health > /dev/null 2>&1; then
    echo "✅ Midnight proof server is running on http://localhost:6300"
else
    echo "⚠️  Proof server started but health check failed. It may take a moment to initialize."
    echo "You can check the logs with: docker logs midnight-proof-server"
fi

echo ""
echo "Proof server configuration:"
echo "  - Network: testnet"
echo "  - Port: 6300"
echo "  - Health endpoint: http://localhost:6300/health"
echo ""
echo "To stop the server: docker stop midnight-proof-server"
echo "To view logs: docker logs -f midnight-proof-server"