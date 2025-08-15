# Troubleshooting Guide

Comprehensive troubleshooting guide for common issues with Qwen Claude CLI.

## Quick Diagnostics

Run these commands to quickly identify common issues:

```bash
# Check CLI version and basic info
qwen-claude --version

# Verify configuration
qwen-claude config show

# Test all providers
qwen-claude provider test

# List available models
qwen-claude model list

# Test basic functionality
qwen-claude ask "Hello, world!" --dry-run
```

## Installation Issues

### Node.js Version Incompatibility

**Problem**: CLI fails to start with Node.js version errors.

**Symptoms**:
```
Error: This package requires Node.js 20.0.0 or higher
Current version: v18.17.0
```

**Solutions**:

```bash
# Check current Node.js version
node --version

# Using nvm (recommended)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 20
nvm use 20
nvm alias default 20

# Using nodenv
nodenv install 20.0.0
nodenv global 20.0.0

# Using n
npm install -g n
n 20

# Verify installation
node --version
npm --version
```

### Permission Errors During Installation

**Problem**: Permission denied when installing globally.

**Symptoms**:
```
npm ERR! Error: EACCES: permission denied, mkdir '/usr/local/lib/node_modules'
```

**Solutions**:

```bash
# Option 1: Fix npm permissions (recommended)
mkdir ~/.npm-global
npm config set prefix '~/.npm-global'
echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Option 2: Use npx (no global installation)
npx @qwen-claude/qwen-claude-cli --version

# Option 3: Use sudo (not recommended)
sudo npm install -g @qwen-claude/qwen-claude-cli
```

### Module Resolution Issues

**Problem**: Cannot find module or import errors.

**Symptoms**:
```
Error: Cannot find module '@qwen-claude/core'
Module not found: '@qwen-claude/providers'
```

**Solutions**:

```bash
# Clear npm cache
npm cache clean --force

# Remove and reinstall
npm uninstall -g @qwen-claude/qwen-claude-cli
npm install -g @qwen-claude/qwen-claude-cli

# For development installations
cd /path/to/qwen-claude-cli
rm -rf node_modules package-lock.json
npm install
npm run build
npm link
```

## Configuration Issues

### Configuration File Not Found

**Problem**: CLI cannot locate configuration file.

**Symptoms**:
```
Warning: No configuration file found, using defaults
Config file not found in any of the standard locations
```

**Diagnosis**:
```bash
# Check configuration search paths
qwen-claude config show --debug

# List configuration directories
echo "Config directories:"
echo "  - $XDG_CONFIG_HOME/qwen-claude-cli/ (if XDG_CONFIG_HOME is set)"
echo "  - ~/.config/qwen-claude-cli/"
echo "  - ~/.qwen-claude/"
echo "  - $(pwd)"
```

**Solutions**:

```bash
# Create configuration in standard location
mkdir -p ~/.config/qwen-claude-cli
qwen-claude config init --force

# Use specific configuration file
qwen-claude --config /path/to/config.yaml config show

# Create minimal configuration
cat > ~/.config/qwen-claude-cli/qwen-claude.config.yaml << 'EOF'
version: "0.1.0"
defaultProvider: "qwen-local"
providers:
  - name: "qwen-local"
    type: "local"
    priority: 1
    enabled: true
    auth:
      type: "none"
      baseUrl: "http://192.168.1.28:8000"
    endpoint: "http://192.168.1.28:8000/v1"
EOF
```

### Invalid Configuration Format

**Problem**: Configuration file has syntax errors.

**Symptoms**:
```
Error: Invalid configuration format
YAML parse error: unexpected token at line 5
JSON parse error: Unexpected token } in JSON
```

**Solutions**:

```bash
# Validate YAML syntax
python3 -c "import yaml; yaml.safe_load(open('config.yaml'))"
# or
yq eval . config.yaml

# Validate JSON syntax
python3 -c "import json; json.load(open('config.json'))"
# or
jq . config.json

# Reset to default configuration
qwen-claude config init --force

# Use configuration wizard
qwen-claude config init --interactive
```

### Environment Variable Issues

**Problem**: Environment variables not being recognized.

**Symptoms**:
```
Warning: QWEN_CLAUDE_OPENROUTER_API_KEY not set
Provider 'openrouter' authentication failed
```

**Diagnosis**:
```bash
# Check environment variables
env | grep QWEN_CLAUDE

# Verify specific variables
echo "Debug: $QWEN_CLAUDE_DEBUG"
echo "API Key: ${QWEN_CLAUDE_OPENROUTER_API_KEY:0:10}..." # Shows first 10 chars
echo "Qwen URL: $QWEN_CLAUDE_QWEN_URL"
```

**Solutions**:

```bash
# Set in current session
export QWEN_CLAUDE_OPENROUTER_API_KEY="your-api-key"
export QWEN_CLAUDE_QWEN_URL="http://192.168.1.28:8000/v1"

# Add to shell profile (Bash)
echo 'export QWEN_CLAUDE_OPENROUTER_API_KEY="your-api-key"' >> ~/.bashrc
source ~/.bashrc

# Add to shell profile (Zsh)
echo 'export QWEN_CLAUDE_OPENROUTER_API_KEY="your-api-key"' >> ~/.zshrc
source ~/.zshrc

# Use .env file
cat > .env << 'EOF'
QWEN_CLAUDE_OPENROUTER_API_KEY=your-api-key
QWEN_CLAUDE_QWEN_URL=http://192.168.1.28:8000/v1
QWEN_CLAUDE_DEBUG=false
EOF

# Load .env file
set -a; source .env; set +a
```

## Provider Issues

### Local Qwen Server Connection Issues

**Problem**: Cannot connect to local Qwen server.

**Symptoms**:
```
Error: Connection refused to http://192.168.1.28:8000
Provider 'qwen-local' health check failed
Timeout after 60000ms
```

**Diagnosis**:
```bash
# Test network connectivity
ping 192.168.1.28

# Test port accessibility
telnet 192.168.1.28 8000
# or
nc -zv 192.168.1.28 8000

# Test HTTP endpoint
curl -v http://192.168.1.28:8000/v1/models
curl -v http://192.168.1.28:8000/health
```

**Solutions**:

```bash
# Check if Qwen server is running
ssh user@192.168.1.28 "ps aux | grep qwen"

# Start Qwen server (on server machine)
ssh user@192.168.1.28 "cd /path/to/qwen && python -m vllm.entrypoints.openai.api_server --model Qwen/Qwen2.5-Coder-32B-Instruct --host 0.0.0.0 --port 8000"

# Check firewall settings
ssh user@192.168.1.28 "sudo ufw status"
ssh user@192.168.1.28 "sudo iptables -L"

# Update CLI configuration for different IP/port
qwen-claude config show > config.yaml
# Edit config.yaml to update endpoint
# Save and test
qwen-claude provider test qwen-local
```

### OpenRouter API Issues

**Problem**: OpenRouter API authentication or request failures.

**Symptoms**:
```
Error: 401 Unauthorized - Invalid API key
Error: 429 Too Many Requests - Rate limit exceeded
Error: 402 Payment Required - Insufficient credits
```

**Diagnosis**:
```bash
# Test API key manually
curl -H "Authorization: Bearer $QWEN_CLAUDE_OPENROUTER_API_KEY" \
     -H "HTTP-Referer: https://github.com/your-org/qwen-claude-cli" \
     https://openrouter.ai/api/v1/models

# Check account status
curl -H "Authorization: Bearer $QWEN_CLAUDE_OPENROUTER_API_KEY" \
     https://openrouter.ai/api/v1/auth/key
```

**Solutions**:

```bash
# Verify API key is correct
echo "API Key: ${QWEN_CLAUDE_OPENROUTER_API_KEY:0:10}..."

# Regenerate API key from OpenRouter dashboard
# https://openrouter.ai/keys

# Use free models only
qwen-claude model list --provider openrouter | grep ":free"

# Update configuration to use free models
cat > ~/.qwen-claude.yaml << 'EOF'
defaultProvider: "openrouter"
providers:
  - name: "openrouter"
    auth:
      apiKey: "your-new-api-key"
    models:
      - "meta-llama/llama-3.1-8b-instruct:free"
      - "mistralai/mistral-7b-instruct:free"
EOF
```

### Model Loading Issues

**Problem**: Specific models fail to load or respond.

**Symptoms**:
```
Error: Model 'qwen3-coder-30b' not found
Error: Model loading timeout
Error: CUDA out of memory
```

**Solutions**:

```bash
# List available models
qwen-claude model list

# Use different model
qwen-claude ask "Hello" --model "qwen2.5-coder-32b-instruct"

# Check server logs (for local Qwen)
ssh user@192.168.1.28 "tail -f /var/log/qwen-server.log"

# Restart model server with different parameters
ssh user@192.168.1.28 "pkill -f vllm"
ssh user@192.168.1.28 "python -m vllm.entrypoints.openai.api_server \
    --model Qwen/Qwen2.5-Coder-32B-Instruct \
    --tensor-parallel-size 2 \
    --max-model-len 16384"
```

## Network Issues

### Proxy Configuration Problems

**Problem**: Requests fail when behind corporate proxy.

**Symptoms**:
```
Error: connect ECONNREFUSED proxy:8080
Error: tunnel connection failed
SSL certificate verification failed
```

**Solutions**:

```bash
# Configure proxy in CLI
export QWEN_CLAUDE_PROXY=http://proxy:8080
export HTTPS_PROXY=http://proxy:8080
export HTTP_PROXY=http://proxy:8080

# Configure proxy with authentication
export QWEN_CLAUDE_PROXY=http://username:password@proxy:8080

# Configure no proxy for local services
export NO_PROXY="localhost,127.0.0.1,192.168.1.28"

# Test proxy configuration
curl --proxy $QWEN_CLAUDE_PROXY https://api.openrouter.ai/api/v1/models
```

### SSL Certificate Issues

**Problem**: SSL certificate verification failures.

**Symptoms**:
```
Error: unable to verify the first certificate
Error: self signed certificate in certificate chain
CERT_UNTRUSTED
```

**Solutions**:

```bash
# Add custom CA certificate
export NODE_EXTRA_CA_CERTS=/path/to/ca-certificate.pem

# Disable SSL verification (development only)
export NODE_TLS_REJECT_UNAUTHORIZED=0

# Configure custom certificates in CLI
cat > ~/.qwen-claude.yaml << 'EOF'
network:
  ssl:
    ca: "/path/to/ca-cert.pem"
    rejectUnauthorized: true
EOF
```

### Timeout Issues

**Problem**: Requests timing out frequently.

**Symptoms**:
```
Error: Request timeout after 30000ms
Connection reset by peer
Socket hang up
```

**Solutions**:

```bash
# Increase timeout globally
export QWEN_CLAUDE_TIMEOUT=120000

# Increase timeout for specific provider
cat > ~/.qwen-claude.yaml << 'EOF'
providers:
  - name: "qwen-local"
    timeout: 120000  # 2 minutes
  - name: "openrouter"
    timeout: 60000   # 1 minute
EOF

# Use faster models
qwen-claude ask "Hello" --model "meta-llama/llama-3.1-8b-instruct:free"
```

## Tool Execution Issues

### Permission Denied for Tools

**Problem**: Tools fail due to insufficient permissions.

**Symptoms**:
```
Error: EACCES: permission denied, open '/etc/hosts'
Error: Operation blocked by safety level 'cautious'
Tool execution failed: access denied
```

**Solutions**:

```bash
# Check current safety level
qwen-claude config show | grep safetyLevel

# Use less restrictive safety level
export QWEN_CLAUDE_TOOLS_SAFETY_LEVEL=moderate
qwen-claude tool run write_file --params '{"path": "test.txt", "content": "test"}'

# Use confirmation flag
qwen-claude tool run execute_command --params '{"command": "ls"}' --confirm

# Run in dry-run mode first
qwen-claude tool run write_file --params '{"path": "test.txt", "content": "test"}' --dry-run
```

### Tool Timeout Issues

**Problem**: Tools timeout during execution.

**Symptoms**:
```
Error: Tool execution timed out after 30000ms
Error: Command killed due to timeout
Process terminated by timeout
```

**Solutions**:

```bash
# Increase tool timeout
export QWEN_CLAUDE_TOOLS_TIMEOUT=120000

# Use specific timeout for command
qwen-claude tool run execute_command --params '{
  "command": "long-running-script.sh",
  "timeout": 300000
}'

# Run in background for very long operations
qwen-claude tool run execute_command --params '{
  "command": "long-task.sh"
}' --background
```

### File Access Issues

**Problem**: Cannot read or write files.

**Symptoms**:
```
Error: Access denied: file outside working directory
Error: ENOENT: no such file or directory
Error: EISDIR: illegal operation on a directory
```

**Solutions**:

```bash
# Check current working directory
pwd

# Use absolute paths within working directory
qwen-claude tool run read_file --params '{"path": "/full/path/to/file.txt"}'

# Change working directory
cd /path/to/project
qwen-claude tool run read_file --params '{"path": "relative/file.txt"}'

# Check file permissions
ls -la file.txt
chmod 644 file.txt  # Make readable
```

## Performance Issues

### Slow Response Times

**Problem**: CLI responses are unusually slow.

**Diagnosis**:
```bash
# Enable debug mode to see timing information
export QWEN_CLAUDE_DEBUG=true
qwen-claude ask "Hello" --verbose

# Test different providers
time qwen-claude ask "Hello" --provider qwen-local
time qwen-claude ask "Hello" --provider openrouter

# Check network latency
ping 192.168.1.28
ping openrouter.ai
```

**Solutions**:

```bash
# Use faster models
qwen-claude ask "Hello" --model "meta-llama/llama-3.1-8b-instruct:free"

# Enable response caching
cat > ~/.qwen-claude.yaml << 'EOF'
cache:
  enabled: true
  responses:
    enabled: true
    ttl: 300  # 5 minutes
EOF

# Use streaming for real-time feedback
qwen-claude chat --stream
```

### High Memory Usage

**Problem**: CLI consumes excessive memory.

**Diagnosis**:
```bash
# Monitor memory usage
top -p $(pgrep -f qwen-claude)
ps aux | grep qwen-claude

# Check for memory leaks
qwen-claude --version  # Should exit quickly
```

**Solutions**:

```bash
# Disable caching
export QWEN_CLAUDE_CACHE_ENABLED=false

# Reduce concurrent requests
cat > ~/.qwen-claude.yaml << 'EOF'
network:
  maxConcurrentRequests: 1
EOF

# Use smaller models
qwen-claude ask "Hello" --model "meta-llama/llama-3.1-8b-instruct:free"
```

## Debugging and Logging

### Enable Debug Logging

```bash
# Enable debug mode
export QWEN_CLAUDE_DEBUG=true
export QWEN_CLAUDE_LOG_LEVEL=debug

# Run command with verbose output
qwen-claude ask "Hello" --verbose --debug

# Save debug output to file
qwen-claude ask "Hello" --debug 2>&1 | tee debug.log
```

### Analyze Log Files

```bash
# Find log files
find ~ -name "*qwen-claude*log" 2>/dev/null

# Monitor logs in real-time
tail -f ~/.cache/qwen-claude-cli/logs/app.log

# Search for specific errors
grep -i error ~/.cache/qwen-claude-cli/logs/app.log
grep -i "connection" ~/.cache/qwen-claude-cli/logs/app.log
```

### Network Debugging

```bash
# Capture network traffic
sudo tcpdump -i any -A host 192.168.1.28
sudo tcpdump -i any -A host openrouter.ai

# Use curl for manual testing
curl -v -X POST http://192.168.1.28:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "qwen3-coder-30b", "messages": [{"role": "user", "content": "Hello"}]}'
```

## Getting Help

### Built-in Help

```bash
# General help
qwen-claude --help

# Command-specific help
qwen-claude ask --help
qwen-claude tool --help
qwen-claude config --help

# Tool-specific help
qwen-claude tool list
qwen-claude tool run read_file --help
```

### System Information

```bash
# Collect system information for bug reports
cat > system-info.txt << 'EOF'
=== System Information ===
OS: $(uname -a)
Node.js: $(node --version)
npm: $(npm --version)
CLI Version: $(qwen-claude --version)
Working Directory: $(pwd)
Home Directory: $HOME

=== Configuration ===
$(qwen-claude config show)

=== Environment Variables ===
$(env | grep QWEN_CLAUDE || echo "None set")

=== Provider Status ===
$(qwen-claude provider test 2>&1)

=== Recent Logs ===
$(tail -50 ~/.cache/qwen-claude-cli/logs/app.log 2>/dev/null || echo "No logs found")
EOF

cat system-info.txt
```

### Common Recovery Steps

When all else fails, try these recovery steps:

```bash
# 1. Reset configuration
rm -rf ~/.config/qwen-claude-cli
rm -rf ~/.qwen-claude
qwen-claude config init

# 2. Clear cache
rm -rf ~/.cache/qwen-claude-cli

# 3. Reinstall CLI
npm uninstall -g @qwen-claude/qwen-claude-cli
npm cache clean --force
npm install -g @qwen-claude/qwen-claude-cli

# 4. Reset environment
unset $(env | grep QWEN_CLAUDE | cut -d= -f1)

# 5. Test basic functionality
qwen-claude --version
qwen-claude config show
qwen-claude provider test
```

If issues persist after following this guide, please file a bug report with:
- System information output
- Complete error messages
- Steps to reproduce the issue
- Configuration files (with sensitive data removed)