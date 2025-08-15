# Setup Guide

Comprehensive setup instructions for Qwen Claude CLI on different platforms.

## Prerequisites

- Node.js 20.0.0 or higher
- npm or yarn package manager
- Git (for development)

## Installation Methods

### Method 1: Global Installation (Recommended)

```bash
# Install from npm registry
npm install -g @qwen-claude/qwen-claude-cli

# Verify installation
qwen-claude --version
```

### Method 2: Local Development Installation

```bash
# Clone repository
git clone https://github.com/your-org/qwen-claude-cli.git
cd qwen-claude-cli

# Install dependencies
npm install

# Build and link globally
npm run install:global

# Verify installation
qwen-claude --version
```

### Method 3: Direct Bundle Usage

```bash
# Download and run bundled version
wget https://github.com/your-org/qwen-claude-cli/releases/latest/download/qwen-claude.js
chmod +x qwen-claude.js
node qwen-claude.js --version
```

## Platform-Specific Setup

### Linux Setup

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install nodejs npm git

# Red Hat/CentOS/Fedora
sudo dnf install nodejs npm git

# Arch Linux
sudo pacman -S nodejs npm git

# Install CLI
npm install -g @qwen-claude/qwen-claude-cli

# Add to PATH if needed
echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### macOS Setup

```bash
# Using Homebrew
brew install node npm git

# Using MacPorts
sudo port install nodejs18 +universal npm10

# Install CLI
npm install -g @qwen-claude/qwen-claude-cli

# Add to PATH if needed
echo 'export PATH="/usr/local/lib/node_modules/.bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### Windows Setup

#### Using Chocolatey

```powershell
# Install Node.js and npm
choco install nodejs npm git

# Install CLI
npm install -g @qwen-claude/qwen-claude-cli

# Verify installation
qwen-claude --version
```

#### Using Winget

```powershell
# Install Node.js
winget install OpenJS.NodeJS

# Install Git
winget install Git.Git

# Restart terminal and install CLI
npm install -g @qwen-claude/qwen-claude-cli
```

#### Manual Installation

1. Download Node.js from [nodejs.org](https://nodejs.org/)
2. Download Git from [git-scm.com](https://git-scm.com/)
3. Install both with default settings
4. Open PowerShell or Command Prompt
5. Run: `npm install -g @qwen-claude/qwen-claude-cli`

## Configuration Setup

### Initial Configuration

```bash
# Initialize default configuration
qwen-claude config init

# Show current configuration
qwen-claude config show
```

### Configuration Locations

The CLI searches for configuration files in the following order:

#### Linux/macOS
1. `$XDG_CONFIG_HOME/qwen-claude-cli/` (if XDG_CONFIG_HOME is set)
2. `~/.config/qwen-claude-cli/`
3. `~/.qwen-claude/`
4. Current working directory

#### Windows
1. `%APPDATA%\qwen-claude-cli\`
2. `%USERPROFILE%\.qwen-claude\`
3. Current working directory

### Environment Variables Setup

Create a `.env` file or add to your shell profile:

```bash
# For Bash (~/.bashrc)
export QWEN_CLAUDE_DEBUG=false
export QWEN_CLAUDE_LOG_LEVEL=info
export QWEN_CLAUDE_DEFAULT_PROVIDER=qwen-local
export QWEN_CLAUDE_QWEN_URL=http://192.168.1.28:8000/v1
export QWEN_CLAUDE_OPENROUTER_API_KEY=your_api_key_here

# For Zsh (~/.zshrc)
export QWEN_CLAUDE_DEBUG=false
export QWEN_CLAUDE_LOG_LEVEL=info
export QWEN_CLAUDE_DEFAULT_PROVIDER=qwen-local
export QWEN_CLAUDE_QWEN_URL=http://192.168.1.28:8000/v1
export QWEN_CLAUDE_OPENROUTER_API_KEY=your_api_key_here

# For Fish (~/.config/fish/config.fish)
set -x QWEN_CLAUDE_DEBUG false
set -x QWEN_CLAUDE_LOG_LEVEL info
set -x QWEN_CLAUDE_DEFAULT_PROVIDER qwen-local
set -x QWEN_CLAUDE_QWEN_URL http://192.168.1.28:8000/v1
set -x QWEN_CLAUDE_OPENROUTER_API_KEY your_api_key_here
```

For Windows PowerShell, add to your profile:

```powershell
$env:QWEN_CLAUDE_DEBUG = "false"
$env:QWEN_CLAUDE_LOG_LEVEL = "info"
$env:QWEN_CLAUDE_DEFAULT_PROVIDER = "qwen-local"
$env:QWEN_CLAUDE_QWEN_URL = "http://192.168.1.28:8000/v1"
$env:QWEN_CLAUDE_OPENROUTER_API_KEY = "your_api_key_here"
```

## Local Qwen Model Setup

### Prerequisites for Local Qwen

1. **Hardware Requirements**
   - GPU: NVIDIA RTX 4090, RTX 3090, or similar (24GB+ VRAM recommended)
   - RAM: 64GB+ system memory
   - Storage: 100GB+ free space for model files

2. **Software Requirements**
   - Python 3.9+ with PyTorch
   - CUDA 11.8+ or ROCm (for AMD GPUs)
   - vLLM or TGI for model serving

### Setting up Qwen3-Coder 30B Server

#### Option 1: Using vLLM

```bash
# Install vLLM
pip install vllm

# Start Qwen3-Coder 30B server
python -m vllm.entrypoints.openai.api_server \
  --model Qwen/Qwen2.5-Coder-32B-Instruct \
  --host 192.168.1.28 \
  --port 8000 \
  --tensor-parallel-size 2 \
  --max-model-len 32768
```

#### Option 2: Using Text Generation Inference

```bash
# Install TGI
pip install text-generation-inference

# Start server
text-generation-launcher \
  --model-id Qwen/Qwen2.5-Coder-32B-Instruct \
  --hostname 192.168.1.28 \
  --port 8000 \
  --max-input-length 32768 \
  --max-total-tokens 33792
```

#### Option 3: Using Docker

```bash
# Using vLLM Docker image
docker run --gpus all \
  -p 8000:8000 \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  vllm/vllm-openai:latest \
  --model Qwen/Qwen2.5-Coder-32B-Instruct \
  --host 0.0.0.0 \
  --port 8000
```

### Verifying Local Setup

```bash
# Test Qwen server connectivity
curl http://192.168.1.28:8000/v1/models

# Test with CLI
qwen-claude provider test qwen-local

# Test chat completion
qwen-claude ask "Hello, world!" --provider qwen-local
```

## OpenRouter Setup

### Getting API Key

1. Visit [OpenRouter.ai](https://openrouter.ai/)
2. Sign up for a free account
3. Navigate to API Keys section
4. Generate a new API key
5. Copy the key for configuration

### Setting up OpenRouter

```bash
# Set API key as environment variable
export QWEN_CLAUDE_OPENROUTER_API_KEY=your_api_key_here

# Or add to configuration file
qwen-claude config show > config.yaml
# Edit config.yaml to add your API key under providers.openrouter.auth.apiKey
```

### Testing OpenRouter

```bash
# Test OpenRouter connectivity
qwen-claude provider test openrouter

# List available models
qwen-claude model list --provider openrouter

# Test with free model
qwen-claude ask "What is TypeScript?" --provider openrouter --model "meta-llama/llama-3.1-8b-instruct:free"
```

## Troubleshooting Setup Issues

### Common Issues

#### 1. Permission Errors

```bash
# Linux/macOS: Fix npm permissions
mkdir ~/.npm-global
npm config set prefix '~/.npm-global'
echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Windows: Run as Administrator
# Right-click PowerShell -> "Run as Administrator"
```

#### 2. Node.js Version Issues

```bash
# Check Node.js version
node --version

# Using nvm to install correct version
nvm install 20
nvm use 20
```

#### 3. Network/Proxy Issues

```bash
# Configure npm proxy
npm config set proxy http://proxy:8080
npm config set https-proxy http://proxy:8080

# Or use CLI proxy setting
export QWEN_CLAUDE_PROXY=http://proxy:8080
```

#### 4. SSL Certificate Issues

```bash
# Disable SSL verification (not recommended for production)
npm config set strict-ssl false

# Or configure proper certificates
npm config set ca /path/to/certificate.pem
```

### Verification Commands

```bash
# Verify complete setup
qwen-claude --version
qwen-claude config show
qwen-claude provider list
qwen-claude model list
qwen-claude tool list

# Test basic functionality
qwen-claude ask "Hello, world!" --dry-run
```

## Development Setup

### Setting up Development Environment

```bash
# Clone repository
git clone https://github.com/your-org/qwen-claude-cli.git
cd qwen-claude-cli

# Install dependencies
npm install

# Build TypeScript
npm run build

# Run in development mode
npm run dev

# Run tests
npm test

# Format and lint
npm run format
npm run lint

# Bundle for distribution
npm run bundle
```

### IDE Configuration

#### VS Code

Create `.vscode/settings.json`:

```json
{
  "typescript.preferences.preferTypeOnlyAutoImports": true,
  "eslint.workingDirectories": ["packages/*"],
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode"
}
```

#### IntelliJ/WebStorm

1. Enable TypeScript service
2. Configure ESLint integration
3. Set Prettier as default formatter
4. Enable automatic imports optimization

### Git Hooks Setup

```bash
# Install husky for git hooks
npm install --save-dev husky
npx husky install

# Add pre-commit hook
npx husky add .husky/pre-commit "npm run lint && npm run test"
```

## Next Steps

After successful setup:

1. Read the [Configuration Guide](./CONFIGURATION.md)
2. Explore [Tool Usage Documentation](./TOOLS.md)
3. Check [Troubleshooting Guide](./TROUBLESHOOTING.md)
4. Review [Development Documentation](./DEVELOPMENT.md)