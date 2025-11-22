#!/bin/bash
# Quick script to run all MCP tests

cd /Users/sammargolis/clinicaltrialqualifier
source venv/bin/activate

echo "=========================================="
echo "MCP Server Test Suite"
echo "=========================================="
echo ""

echo "1. Quick Server Status Check..."
python check_mcp_server.py
echo ""

read -p "Press Enter to continue to endpoint testing..."

echo ""
echo "2. Testing Server Endpoints..."
python test_mcp_server.py
echo ""

read -p "Press Enter to continue to detailed format testing..."

echo ""
echo "3. Testing Request Formats..."
python test_mcp_detailed.py
echo ""

read -p "Press Enter to continue to full integration test..."

echo ""
echo "4. Full Integration Test..."
python test_mcp_integration.py
echo ""

echo "=========================================="
echo "All tests complete!"
echo "=========================================="

