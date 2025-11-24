#!/bin/bash

# Script to verify Compact installation in Docker container
echo "Verifying Compact installation in Docker environment..."

# Check if Compact is installed
echo "1. Checking Compact installation..."
compact --version

# Check Compact installation path
echo "2. Checking Compact installation path..."
which compact

# Verify Compact can compile the contract
echo "3. Verifying Compact can compile the contract..."
cd /app/psychescore-mn/contracts
compact compile psychescore.compact

echo "Compact installation verification complete!"