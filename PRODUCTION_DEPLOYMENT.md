# Plato AI Orchestration System - Production Deployment Guide

## Quick Start (5 Minutes)

### 1. Prerequisites Check
```bash
# Verify Python 3.11+
python3 --version

# Verify Serena MCP is running (optional but recommended)
curl -s http://localhost:8765/health || echo "Serena MCP not running"

# Verify API keys (set in environment)
echo $OPENAI_API_KEY | cut -c1-10    # Should show: sk-proj-...
echo $ANTHROPIC_API_KEY | cut -c1-10  # Should show: sk-ant-...
```

### 2. Install & Activate
```bash
cd /opt/projects/plato
source venv/bin/activate
pip install -e .
```

### 3. Configure
```bash
# Copy and edit configuration
cp config.example.yaml config.yaml
# Edit config.yaml with your API keys

# Or use environment variables
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
export GOOGLE_API_KEY="your-google-key"  # optional
```

### 4. Test Installation
```bash
# Test CLI
python -m plato.cli --help
python -m plato.cli health  # Will show "server not running" - this is OK

# Test with Serena MCP (if available)
python test_serena_minimal.py
```

### 5. Start Using
```bash
# Start Plato server (optional - for API access)
python -m plato.server.api &

# Use CLI interface
python -m plato.cli chat "Hello! Test the system."
python -m plato.cli tools  # List available tools
```

## Complete Production Setup

### Environment Setup

#### 1. System Requirements
- **Python**: 3.11 or higher
- **Memory**: 1GB minimum, 2GB recommended
- **Storage**: 500MB for dependencies
- **Network**: Internet access for AI providers

#### 2. Dependencies
```bash
# Core dependencies (automatically installed)
pip install fastapi uvicorn httpx pydantic rich typer

# AI provider libraries
pip install openai anthropic google-generativeai

# Optional: For MCP integration
# (Use Serena environment or install MCP libraries separately)
```

#### 3. Environment Variables
```bash
# Required
export OPENAI_API_KEY="sk-proj-your-key-here"
export ANTHROPIC_API_KEY="sk-ant-your-key-here"

# Optional
export GOOGLE_API_KEY="your-google-key"
export PLATO_LOG_LEVEL="INFO"
export PLATO_CONFIG_PATH="/path/to/config.yaml"
```

### Configuration Management

#### 1. Main Configuration (config.yaml)
```yaml
app:
  name: "plato"
  version: "1.0.0"
  debug: false
  log_level: "INFO"

ai_providers:
  openai:
    api_key: "${OPENAI_API_KEY}"
    base_url: "https://api.openai.com/v1"
    models:
      - "gpt-4"
      - "gpt-3.5-turbo"
    timeout: 30
    
  anthropic:
    api_key: "${ANTHROPIC_API_KEY}"
    base_url: "https://api.anthropic.com"
    models:
      - "claude-3-sonnet-20240229"
      - "claude-3-haiku-20240307"
    timeout: 30
    
  google:
    api_key: "${GOOGLE_API_KEY}"
    models:
      - "gemini-pro"
    timeout: 30

mcp_servers:
  serena:
    name: "serena"
    url: "http://localhost:8765/sse"
    timeout: 30
    enabled: true

context:
  storage_path: "./context"
  max_sessions: 100
  session_timeout: 3600

logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "./logs/plato.log"
```

#### 2. Production Overrides
```yaml
# config.prod.yaml
app:
  debug: false
  log_level: "WARNING"

logging:
  level: "WARNING"
  file: "/var/log/plato/plato.log"

context:
  storage_path: "/var/lib/plato/context"
```

### Service Deployment

#### 1. Systemd Service (Recommended)
```ini
# /etc/systemd/system/plato.service
[Unit]
Description=Plato AI Orchestration System
After=network.target

[Service]
Type=simple
User=plato
Group=plato
WorkingDirectory=/opt/projects/plato
Environment=PATH=/opt/projects/plato/venv/bin
Environment=PYTHONPATH=/opt/projects/plato
EnvironmentFile=/etc/plato/environment
ExecStart=/opt/projects/plato/venv/bin/python -m plato.server.api
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable plato
sudo systemctl start plato
sudo systemctl status plato
```

#### 2. Docker Deployment
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN pip install -e .

EXPOSE 8080
CMD ["python", "-m", "plato.server.api"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  plato:
    build: .
    ports:
      - "8080:8080"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    volumes:
      - ./config.yaml:/app/config.yaml
      - ./logs:/app/logs
      - ./context:/app/context
    restart: unless-stopped
```

#### 3. Process Manager (PM2)
```bash
# Install PM2
npm install -g pm2

# Create ecosystem file
cat > ecosystem.config.js << EOF
module.exports = {
  apps: [{
    name: 'plato',
    script: 'python',
    args: '-m plato.server.api',
    cwd: '/opt/projects/plato',
    interpreter: './venv/bin/python',
    env: {
      'PYTHONPATH': '/opt/projects/plato',
      'OPENAI_API_KEY': process.env.OPENAI_API_KEY,
      'ANTHROPIC_API_KEY': process.env.ANTHROPIC_API_KEY
    }
  }]
};
EOF

# Start with PM2
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

### Monitoring & Maintenance

#### 1. Health Checks
```bash
# API health check
curl -f http://localhost:8080/health || exit 1

# CLI health check
python -m plato.cli health

# Serena MCP check
curl -f http://localhost:8765/health || echo "Serena not available"
```

#### 2. Logging
```bash
# Application logs
tail -f /var/log/plato/plato.log

# Service logs
journalctl -u plato -f

# Docker logs
docker-compose logs -f plato
```

#### 3. Performance Monitoring
```bash
# Resource usage
ps aux | grep plato
top -p $(pgrep -f plato)

# API response times
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8080/health
```

### Security Hardening

#### 1. API Key Management
```bash
# Use environment variables, not config files
export OPENAI_API_KEY="$(cat /secure/openai.key)"

# Restrict file permissions
chmod 600 /etc/plato/environment
chown plato:plato /etc/plato/environment
```

#### 2. Network Security
```bash
# Firewall rules (if using UFW)
ufw allow 8080/tcp  # Plato API
ufw allow from 127.0.0.1 to any port 8765  # Serena MCP (local only)
```

#### 3. User Isolation
```bash
# Create dedicated user
useradd -r -s /bin/false plato
chown -R plato:plato /opt/projects/plato
```

### Backup & Recovery

#### 1. Configuration Backup
```bash
# Backup script
#!/bin/bash
tar -czf /backup/plato-config-$(date +%Y%m%d).tar.gz \
  /opt/projects/plato/config.yaml \
  /opt/projects/plato/context/ \
  /var/log/plato/
```

#### 2. Context Data
```bash
# Backup context storage
rsync -av /var/lib/plato/context/ /backup/context/
```

### Troubleshooting

#### 1. Common Issues

**Import Errors (MCP libraries)**
```bash
# Solution: Use optional imports (already implemented)
python -c "from plato.cli import app; print('CLI working')"
```

**Connection Timeout**
```bash
# Check Serena MCP
curl http://localhost:8765/health

# Check API providers
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
  https://api.openai.com/v1/models
```

**Performance Issues**
```bash
# Check memory usage
free -h

# Check disk space
df -h

# Check network latency
ping api.openai.com
```

#### 2. Debug Mode
```bash
# Enable debug logging
export PLATO_LOG_LEVEL=DEBUG
python -m plato.cli chat "test" --verbose
```

### Scaling Considerations

#### 1. Horizontal Scaling
- Run multiple Plato instances behind load balancer
- Use shared storage for context data
- Configure session affinity if needed

#### 2. Resource Optimization
- Adjust AI provider timeouts
- Implement request caching
- Use connection pooling

#### 3. High Availability
- Deploy across multiple servers
- Use database for context storage
- Implement health checks and auto-restart

### API Usage Examples

#### 1. Health Check
```bash
curl http://localhost:8080/health
```

#### 2. Chat Completion
```bash
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, how are you?",
    "preferred_provider": "openai"
  }'
```

#### 3. Tool Operations
```bash
# List tools
curl http://localhost:8080/tools

# Call tool
curl -X POST http://localhost:8080/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "name": "read_file",
    "arguments": {"path": "README.md"}
  }'
```

---

## Support & Maintenance

### Regular Tasks
- **Daily**: Check service status and logs
- **Weekly**: Review performance metrics
- **Monthly**: Update dependencies and backup configuration
- **Quarterly**: Security audit and penetration testing

### Getting Help
- Check logs: `/var/log/plato/plato.log`
- CLI help: `python -m plato.cli --help`
- Health check: `python -m plato.cli health`
- Test suite: `python test_serena_minimal.py`

### Version Upgrades
```bash
# Backup first
tar -czf plato-backup-$(date +%Y%m%d).tar.gz /opt/projects/plato

# Pull updates
cd /opt/projects/plato
git pull origin main

# Update dependencies
source venv/bin/activate
pip install -e . --upgrade

# Test
python -m plato.cli health

# Restart service
sudo systemctl restart plato
```

**The Plato system is now ready for production deployment! 🚀**