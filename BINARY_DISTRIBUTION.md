# Plato AI Orchestration System - Binary Distribution

**Plato** is an AI-powered development assistant with Claude Code-like interactive interface, featuring intelligent code analysis, multi-provider AI routing, and comprehensive tool integration.

## 🚀 Quick Start

### Option 1: Automatic Installation (Recommended)

```bash
# Build the binary (if not already built)
./build.sh

# Install system-wide
./install.sh

# Start Plato
plato
```

### Option 2: Manual Installation

```bash
# Copy binary to system location
sudo cp ./dist/plato /usr/local/bin/plato
sudo chmod +x /usr/local/bin/plato

# Verify installation
plato --version
```

### Option 3: Run Without Installation

```bash
# Run directly from dist directory
./dist/plato
```

## 📋 Requirements

- **Operating System**: Linux x86_64
- **Dependencies**: None (self-contained binary)
- **Permissions**: Standard user (sudo only required for system-wide installation)
- **Disk Space**: ~61MB for the binary

## 🎯 Features

### Core Capabilities
- 🤖 **Multi-AI Support** - Claude, GPT-4, Gemini, Qwen, and local models
- 🔍 **Smart Code Analysis** - Deep understanding with Serena LSP integration
- 💬 **Interactive Chat Interface** - Claude Code-like experience
- 🛠️ **Tool Integration** - File operations, git, project management
- 🌳 **File Explorer** - Interactive project navigation
- 🎨 **Rich UI** - Syntax highlighting, markdown rendering, progress indicators

### Supported Languages
- Python, TypeScript, JavaScript, Go, Rust, Java, PHP, C#, Ruby, Swift
- Elixir, Clojure, Bash, C/C++, Terraform, and more

### AI Providers
- **Anthropic Claude** (Claude 3.5 Sonnet, Claude 3 Opus)
- **OpenAI** (GPT-4, GPT-3.5-turbo)
- **Google Gemini** (Gemini Pro, Gemini Pro Vision)
- **Local Qwen** (Self-hosted models)
- **OpenRouter** (Access to multiple models)

## 📖 Usage

### Interactive Mode (Default)
```bash
# Start interactive interface
plato

# Or explicitly
plato interactive
```

### Command Line Usage
```bash
# Send single chat message
plato chat "Explain this Python function"

# Check server health
plato health

# List available tools
plato tools

# Analyze code with Serena
plato analyze /path/to/project --language python

# Show help
plato --help
```

### Interactive Commands
Once in interactive mode, use these commands:

```
/help          - Show available commands
/project       - Show project information  
/files         - Toggle file tree display
/tools         - List available tools
/provider      - Set AI provider (claude, gpt-4, gemini, etc.)
/read <path>   - Read and display a file
/search <term> - Search project files
/analyze <path>- Analyze file with Serena
/clear         - Clear conversation
/debug         - Toggle debug mode
/quit          - Exit Plato
```

## 🔧 Configuration

### Server URL
By default, Plato connects to `http://localhost:8080`. To use a different server:

```bash
plato --server-url http://your-server:8080
```

### Environment Variables
- `PLATO_SERVER_URL` - Default server URL
- `PLATO_DEBUG` - Enable debug mode (set to "1")

## 🏗️ Building from Source

### Prerequisites
```bash
# Install Python dependencies
pip install pyinstaller

# Install Plato in development mode
pip install -e .
```

### Build Process
```bash
# Clean build (removes previous builds)
./build.sh --clean

# Build binary
./build.sh

# Build without tests
./build.sh --skip-tests
```

### Manual Build
```bash
# Using PyInstaller directly
pyinstaller plato.spec --clean --noconfirm
```

## 📦 Installation Details

### System Installation
- **Binary Location**: `/usr/local/bin/plato`
- **Permissions**: `755` (executable by all users)
- **Owner**: `root:root`
- **Dependencies**: None (self-contained)

### What Gets Installed
- Single binary file (`plato`)
- No configuration files
- No system services
- No additional dependencies

### Installation Script Features
- ✅ Pre-installation checks
- ✅ Backup detection
- ✅ Permission verification
- ✅ Post-installation testing
- ✅ Colored output with progress indicators

## 🗑️ Uninstallation

### Automatic Uninstallation
```bash
./uninstall.sh
```

### Manual Uninstallation
```bash
sudo rm -f /usr/local/bin/plato
```

### Uninstall Script Features
- ✅ Safety confirmations
- ✅ Complete removal verification
- ✅ Shell cache cleanup
- ✅ Forced uninstall option (`--force`)

## 🔒 Security Considerations

### Binary Safety
- Built from verified source code
- No embedded credentials
- Self-contained (no external dependencies)
- Standard Linux executable format

### Network Connections
- Only connects to specified Plato server
- No external API calls without explicit configuration
- All AI provider connections go through the server

### File System Access
- Reads files only in current working directory by default
- No automatic file modifications
- Respects standard Unix permissions

## 🐛 Troubleshooting

### Common Issues

**Binary won't start:**
```bash
# Check if binary is executable
ls -la /usr/local/bin/plato

# Check dependencies
ldd /usr/local/bin/plato

# Run with debug output
PLATO_DEBUG=1 plato
```

**Command not found:**
```bash
# Check if installed
which plato

# Check PATH
echo $PATH

# Restart shell or reload profile
source ~/.bashrc
```

**Server connection issues:**
```bash
# Check server status
plato health

# Use different server URL
plato --server-url http://localhost:8080

# Check network connectivity
curl http://localhost:8080/health
```

**Interactive mode issues:**
```bash
# Check terminal compatibility
echo $TERM

# Try basic mode
plato chat "test message"

# Enable debug mode
plato
# Then type: /debug
```

### Debug Information
```bash
# Version information
plato --version

# Show all available commands
plato --help

# Server health check
plato health

# Test with simple command
plato chat "Hello"
```

### Log Files
- Interactive mode errors: Check terminal output
- No system logs created by default
- Enable debug mode for detailed error information

## 📈 Performance

### Binary Characteristics
- **Size**: ~61MB (self-contained)
- **Startup Time**: ~2-3 seconds (cold start)
- **Memory Usage**: ~50-100MB (typical)
- **CPU Usage**: Minimal when idle

### Optimization Tips
- Use local Plato server for best performance
- Enable file tree caching for large projects
- Use specific AI providers instead of auto-selection
- Clear conversation history periodically

## 🤝 Support

### Getting Help
1. **Interactive Help**: Type `/help` in interactive mode
2. **Command Help**: Run `plato --help`
3. **Server Status**: Run `plato health`
4. **Debug Mode**: Enable with `/debug` or `PLATO_DEBUG=1`

### Reporting Issues
Include this information when reporting issues:
- Plato version (`plato --version`)
- Operating system and architecture
- Error messages (with debug mode enabled)
- Steps to reproduce the issue

### Community
- **Documentation**: See project README and documentation
- **Source Code**: Available in the project repository
- **Issues**: Report bugs and feature requests in the issue tracker

## 🔄 Updates

### Updating Plato
1. Download new binary or rebuild from source
2. Run `./install.sh` (will prompt to overwrite)
3. Verify installation with `plato --version`

### Rollback
Keep the old binary as backup:
```bash
# Before updating
cp /usr/local/bin/plato /usr/local/bin/plato.backup

# To rollback
sudo cp /usr/local/bin/plato.backup /usr/local/bin/plato
```

## 📋 Appendix

### File Structure
```
plato/
├── dist/
│   └── plato                    # Main binary
├── build.sh                    # Build script
├── install.sh                  # Installation script
├── uninstall.sh               # Uninstallation script
├── plato.spec                 # PyInstaller specification
├── plato_launcher.py          # Binary entry point
└── BINARY_DISTRIBUTION.md     # This file
```

### Environment Variables Reference
| Variable | Default | Description |
|----------|---------|-------------|
| `PLATO_SERVER_URL` | `http://localhost:8080` | Default server URL |
| `PLATO_DEBUG` | `0` | Enable debug output |
| `TERM` | (auto) | Terminal type for rich formatting |

### Exit Codes
| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Invalid arguments |
| 130 | Interrupted by user (Ctrl+C) |

---

**Plato AI Orchestration System v0.1.0**  
*Intelligent development assistance with Claude Code-like interface*