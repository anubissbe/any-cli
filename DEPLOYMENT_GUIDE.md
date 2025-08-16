# Plato Deployment Guide

## Quick Start

1. **Install dependencies**:
   ```bash
   cd /opt/projects/plato
   python -m venv venv
   source venv/bin/activate
   pip install -e .
   ```

2. **Configure API keys** (optional):
   ```bash
   export ANTHROPIC_API_KEY="your-key"
   export OPENAI_API_KEY="your-key" 
   export GEMINI_API_KEY="your-key"
   export OPENROUTER_API_KEY="your-key"
   export QWEN_BASE_URL="http://localhost:8000"
   ```

3. **Start MCP servers**:
   ```bash
   # Start Serena MCP for LSP operations
   /opt/start_serena_mcp.sh start
   
   # Optional: Start other MCP servers
   /opt/start_office_word_mcp.sh start
   /opt/start_archy_mcp.sh start
   ```

4. **Start Plato server**:
   ```bash
   ./start_plato.sh
   # Or manually:
   python -m plato.server.api
   ```

5. **Test the system**:
   ```bash
   # CLI interface
   plato health
   plato chat "Hello Plato"
   plato interactive
   
   # REST API
   curl http://localhost:8080/health
   ```

## Architecture Overview

### Core Components

- **AI Router** (`plato/core/ai_router.py`): Intelligent routing between 6 AI providers
- **Context Manager** (`plato/core/context_manager.py`): Session and context management with compression
- **MCP Manager** (`plato/core/mcp_manager.py`): MCP server connection management
- **Serena Integration** (`plato/integrations/serena_mcp.py`): LSP operations for 16+ languages
- **FastAPI Server** (`plato/server/api.py`): Production API with streaming and WebSocket support

### Key Features

1. **Multi-AI Provider Support**: Claude, GPT-4, GPT-3.5, Local Qwen, OpenRouter, Gemini
2. **Intelligent Routing**: Task-based provider selection with fallback
3. **MCP Integration**: Serena LSP, Office Word, Archy diagram generation
4. **Context Management**: Automatic compression, session persistence
5. **Production API**: OpenAI-compatible endpoints, real-time WebSocket
6. **CLI Interface**: Rich terminal interface for all operations

## API Examples

### Chat with AI
```bash
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Analyze this Python code for improvements",
    "task_type": "code_analysis",
    "preferred_provider": "claude"
  }'
```

### Call MCP Tool
```bash
curl -X POST http://localhost:8080/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "find_symbols",
    "arguments": {
      "workspace_path": "/opt/projects",
      "query": "function"
    }
  }'
```

### Serena Code Analysis
```bash
curl -X POST http://localhost:8080/serena/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "project_path": "/opt/projects/plato",
    "operation": "build_context"
  }'
```

## Production Deployment

1. **Environment Variables**:
   ```bash
   export ANTHROPIC_API_KEY="..."
   export OPENAI_API_KEY="..."
   export PLATO_HOST="0.0.0.0"
   export PLATO_PORT="8080"
   ```

2. **Docker Deployment**:
   ```bash
   docker build -t plato .
   docker run -p 8080:8080 \
     -e ANTHROPIC_API_KEY="..." \
     -e OPENAI_API_KEY="..." \
     plato
   ```

3. **Systemd Service**:
   ```ini
   [Unit]
   Description=Plato AI Orchestration Service
   After=network.target
   
   [Service]
   Type=simple
   User=plato
   WorkingDirectory=/opt/projects/plato
   ExecStart=/opt/projects/plato/venv/bin/python -m plato.server.api
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   ```

## Monitoring

- **Health endpoint**: `GET /health`
- **Metrics**: Token usage, provider health, session stats
- **Logs**: Structured logging with request tracing
- **WebSocket**: Real-time status updates

## Troubleshooting

1. **MCP Connection Issues**:
   ```bash
   # Check Serena status
   /opt/start_serena_mcp.sh status
   
   # View logs
   tail -f /tmp/serena_mcp.log
   ```

2. **AI Provider Errors**:
   - Verify API keys in environment
   - Check provider health: `GET /health`
   - Review request logs

3. **Performance Issues**:
   - Monitor context compression
   - Check token usage patterns
   - Scale with multiple instances