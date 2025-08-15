# Qwen Claude CLI - Installation Guide

## Prerequisites

- **Node.js**: Version 20.0.0 or higher
- **npm**: Version 10.0.0 or higher
- **Operating System**: Linux, macOS, or Windows
- **Local Qwen Model**: Qwen3-Coder 30B running on accessible server

## Installation Methods

### Method 1: Local Development Installation

```bash
# Clone or navigate to the project
cd /opt/projects/qwen-claude-cli

# Install dependencies
npm install

# Build all packages
npm run build

# Create executable bundle
npm run bundle

# Test installation
node ./bundle/qwen-claude.js --version
```

### Method 2: Global npm Installation (Future)

```bash
# When published to npm registry
npm install -g @qwen-claude/qwen-claude-cli

# Then use globally
qwen-claude --version
```

### Method 3: Direct Bundle Usage

```bash
# Make bundle executable
chmod +x ./bundle/qwen-claude.js

# Add to PATH (optional)
export PATH="$PATH:/opt/projects/qwen-claude-cli/bundle"

# Create symbolic link (optional)
sudo ln -s /opt/projects/qwen-claude-cli/bundle/qwen-claude.js /usr/local/bin/qwen-claude
```

## Platform-Specific Setup

### Linux

```bash
# Ubuntu/Debian - Install Node.js
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# CentOS/RHEL - Install Node.js
curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -
sudo yum install -y nodejs

# Install qwen-claude-cli
cd /opt/projects/qwen-claude-cli
npm install && npm run build && npm run bundle

# Create config directories
mkdir -p ~/.config ~/.local/share/qwen-claude ~/.cache/qwen-claude
```

### macOS

```bash
# Install Node.js using Homebrew
brew install node@20

# Or download from nodejs.org
# https://nodejs.org/en/download/

# Install qwen-claude-cli
cd /opt/projects/qwen-claude-cli
npm install && npm run build && npm run bundle

# Create config directories
mkdir -p ~/.config ~/Library/Application\ Support/qwen-claude ~/Library/Caches/qwen-claude
```

### Windows

```powershell
# Install Node.js from nodejs.org or using Chocolatey
choco install nodejs --version=20.0.0

# Or using winget
winget install OpenJS.NodeJS

# Install qwen-claude-cli
cd C:\opt\projects\qwen-claude-cli
npm install
npm run build
npm run bundle

# Create config directories
mkdir $env:APPDATA\qwen-claude
mkdir $env:LOCALAPPDATA\qwen-claude
```

## Configuration Setup

### Quick Configuration

```bash
# Navigate to project directory
cd /opt/projects/qwen-claude-cli

# Create basic configuration
node ./bundle/qwen-claude.js config init
```

### Manual Configuration

Create configuration file at `~/.config/config.json`:

```json
{
  "version": "0.1.0",
  "configDir": "/home/user/.config",
  "dataDir": "/home/user/.local/share/qwen-claude",
  "cacheDir": "/home/user/.cache/qwen-claude",
  "providers": [
    {
      "name": "Qwen3-Coder Local",
      "type": "local",
      "priority": 1,
      "enabled": true,
      "auth": {
        "type": "none",
        "baseUrl": "http://192.168.1.28:8000"
      },
      "models": ["qwen3-coder-30b"],
      "endpoint": "http://192.168.1.28:8000"
    },
    {
      "name": "OpenRouter",
      "type": "remote",
      "priority": 2,
      "enabled": true,
      "auth": {
        "type": "api_key",
        "baseUrl": "https://openrouter.ai/api/v1",
        "apiKey": ""
      },
      "models": ["meta-llama/llama-3.1-8b-instruct:free"],
      "endpoint": "https://openrouter.ai/api/v1"
    }
  ],
  "defaultProvider": "Qwen3-Coder Local"
}
```

### Environment Variables

Add to your shell profile (`~/.bashrc`, `~/.zshrc`, etc.):

```bash
# Qwen Claude CLI Configuration
export QWEN_CLAUDE_DEBUG=false
export QWEN_CLAUDE_QWEN_URL=http://192.168.1.28:8000
export QWEN_CLAUDE_OPENROUTER_API_KEY=your_api_key_here
export QWEN_CLAUDE_DEFAULT_PROVIDER="Qwen3-Coder Local"
```

## Verification

### Test Basic Functionality

```bash
# Check version
node ./bundle/qwen-claude.js --version

# Show help
node ./bundle/qwen-claude.js --help

# List providers
node ./bundle/qwen-claude.js provider list

# List tools
node ./bundle/qwen-claude.js tool list

# Test configuration
node ./bundle/qwen-claude.js config show
```

### Test Provider Connectivity

```bash
# Test local Qwen provider
node ./bundle/qwen-claude.js provider test "Qwen3-Coder Local"

# Test basic tool execution
node ./bundle/qwen-claude.js tool run read_file --params '{"path":"./README.md"}'

# Test directory listing
node ./bundle/qwen-claude.js tool run list_directory --params '{"path":"."}'
```

## Troubleshooting

### Common Issues

#### 1. Command Not Found

```bash
# Make sure bundle is executable
chmod +x ./bundle/qwen-claude.js

# Or run with node explicitly
node ./bundle/qwen-claude.js --help
```

#### 2. Configuration Errors

```bash
# Remove invalid config and reinitialize
rm ~/.config/config.json
node ./bundle/qwen-claude.js config init

# Check configuration validity
node ./bundle/qwen-claude.js config show
```

#### 3. Provider Connection Failed

```bash
# Check if Qwen server is accessible
curl http://192.168.1.28:8000/health

# Verify network connectivity
ping 192.168.1.28

# Check firewall settings
sudo ufw status  # Linux
```

#### 4. Permission Errors

```bash
# Fix directory permissions
mkdir -p ~/.config ~/.local/share/qwen-claude ~/.cache/qwen-claude
chmod 755 ~/.config ~/.local/share/qwen-claude ~/.cache/qwen-claude

# Fix bundle permissions
chmod +x ./bundle/qwen-claude.js
```

#### 5. Node.js Version Issues

```bash
# Check Node.js version
node --version  # Should be 20.0.0+

# Update Node.js if needed
# Linux
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# macOS
brew upgrade node
```

### Debug Mode

Enable debug mode for detailed logging:

```bash
# Set debug environment variable
export QWEN_CLAUDE_DEBUG=true

# Or use debug flag
node ./bundle/qwen-claude.js --debug provider list
```

### Log Files

Check log files for detailed error information:

```bash
# Linux/macOS
tail -f ~/.local/share/qwen-claude/logs/qwen-claude.log

# Windows
type %LOCALAPPDATA%\qwen-claude\logs\qwen-claude.log
```

## Next Steps

After successful installation:

1. **Read the Documentation**: See [docs/](docs/) for comprehensive guides
2. **Configure Providers**: Set up your preferred AI model providers
3. **Explore Tools**: Try different tools for file operations and code analysis
4. **Start Chatting**: Begin interactive sessions with your local Qwen model

## Getting Help

- **Documentation**: [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
- **Configuration Guide**: [docs/CONFIGURATION.md](docs/CONFIGURATION.md)
- **Tool Usage**: [docs/TOOLS.md](docs/TOOLS.md)
- **Architecture**: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)