#!/bin/bash

# Plato AI System - Clean Startup Script (Embedded Tools Only)
# No external MCP dependencies required

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "${BLUE}🚀 Starting Plato AI System (Embedded Tools Edition)${NC}"
echo "============================================"

# Handle commands
case "$1" in
    stop)
        echo -e "${YELLOW}Stopping Plato server...${NC}"
        pkill -f "uvicorn plato.server.api:app" || echo "Server not running"
        exit 0
        ;;
    restart)
        echo -e "${YELLOW}Restarting Plato server...${NC}"
        pkill -f "uvicorn plato.server.api:app" || true
        sleep 2
        ;;
    status)
        if pgrep -f "uvicorn plato.server.api:app" > /dev/null; then
            echo -e "${GREEN}✅ Plato server is running${NC}"
            curl -s http://localhost:8080/health | python3 -m json.tool
        else
            echo -e "${RED}❌ Plato server is not running${NC}"
        fi
        exit 0
        ;;
esac

# Check if server is already running
if pgrep -f "uvicorn plato.server.api:app" > /dev/null; then
    echo -e "${YELLOW}⚠️  Plato server is already running${NC}"
    echo -e "   Use: $0 restart   to restart"
    echo -e "   Use: $0 stop     to stop"
    exit 1
fi

# Check if Python virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 Creating Python virtual environment...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    pip install -e .
else
    source venv/bin/activate
fi

# Check if configuration exists
if [ ! -f "config.yaml" ]; then
    echo -e "${YELLOW}⚙️  No config.yaml found, copying from example...${NC}"
    cp config.example.yaml config.yaml
    echo -e "${YELLOW}📝 Please edit config.yaml with your API keys${NC}"
fi

echo -e "${GREEN}✅ Environment ready${NC}"
echo -e "${BLUE}📦 13 Embedded Tools Available:${NC}"
echo "   - File Operations: Read, Write, Edit, List, Search, Create Dir"
echo "   - Code Analysis: Get Symbols, References, Definitions, etc."
echo ""
echo -e "${YELLOW}⚠️  No external MCP servers required!${NC}"

# Set environment variables
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

# Check if port 8080 is already in use
if lsof -i :8080 > /dev/null 2>&1; then
    echo -e "${RED}❌ Port 8080 is already in use!${NC}"
    echo -e "${YELLOW}💡 Stop it with: kill -9 \$(lsof -t -i:8080)${NC}"
    exit 1
fi

# Start the server
echo ""
echo -e "${GREEN}🎯 Starting Plato server...${NC}"
echo -e "${BLUE}   API: http://localhost:8080${NC}"
echo -e "${BLUE}   Health: http://localhost:8080/health${NC}"
echo -e "${BLUE}   Docs: http://localhost:8080/docs${NC}"
echo ""

# Start in background with proper logging
echo -e "${YELLOW}Starting server in background...${NC}"
nohup uvicorn plato.server.api:app \
    --host 0.0.0.0 \
    --port 8080 \
    --log-level info \
    > /tmp/plato_server.log 2>&1 &

SERVER_PID=$!
echo -e "${GREEN}✅ Server started with PID: $SERVER_PID${NC}"

# Wait for server to be ready
echo -n "Waiting for server to be ready"
for i in {1..10}; do
    if curl -s http://localhost:8080/health > /dev/null 2>&1; then
        echo -e " ${GREEN}✅${NC}"
        break
    fi
    echo -n "."
    sleep 1
done

# Final status check
if curl -s http://localhost:8080/health > /dev/null 2>&1; then
    echo ""
    echo "============================================"
    echo -e "${GREEN}✅ Plato server is running successfully!${NC}"
    echo "============================================"
    echo ""
    echo "Quick start:"
    echo "  1. Open new terminal"
    echo "  2. Run: ./plato-cli"
    echo "  3. Start chatting!"
    echo ""
    echo "Server management:"
    echo "  - View logs: tail -f /tmp/plato_server.log"
    echo "  - Stop: ./start_plato.sh stop"
    echo "  - Restart: ./start_plato.sh restart"
    echo "  - Status: ./start_plato.sh status"
else
    echo -e " ${RED}❌${NC}"
    echo "Server failed to start. Check logs:"
    tail -20 /tmp/plato_server.log
    exit 1
fi