# Qwen Claude CLI - Quick Reference

## Installation & Setup

```bash
# Install dependencies
npm install

# Build all packages
npm run build

# Create executable bundle
npm run bundle

# Test the CLI
node ./bundle/qwen-claude.js --version
```

## Essential Commands

### Basic Usage
```bash
# Show help
qwen-claude --help

# Show version
qwen-claude --version

# Interactive chat
qwen-claude chat

# Ask single question
qwen-claude ask "How do I use async/await?"
```

### Configuration
```bash
# Initialize config (interactive)
qwen-claude config init

# Show current config
qwen-claude config show

# Config file location: ~/.config/config.json
```

### Providers
```bash
# List available providers
qwen-claude provider list

# Test provider connectivity
qwen-claude provider test qwen-local
```

### Tools
```bash
# List all tools
qwen-claude tool list

# Run file operations
qwen-claude tool run read_file --params '{"path":"./README.md"}'
qwen-claude tool run list_directory --params '{"path":"./src"}'

# Run shell commands (with confirmation)
qwen-claude tool run execute_command --params '{"command":"ls -la"}'
```

## Configuration Quick Setup

### Basic Config (~/.config/config.json)
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
    }
  ],
  "defaultProvider": "Qwen3-Coder Local"
}
```

### Environment Variables
```bash
export QWEN_CLAUDE_DEBUG=true
export QWEN_CLAUDE_QWEN_URL=http://192.168.1.28:8000
export QWEN_CLAUDE_OPENROUTER_API_KEY=your_key_here
```

## Tool Categories

### File Tools
- `read_file` - Read file contents
- `write_file` - Write to file
- `list_directory` - List directory contents  
- `create_directory` - Create directories

### Shell Tools
- `execute_command` - Run shell commands
- `which_command` - Find executable path

### Analysis Tools
- `analyze_code` - Code analysis and metrics
- `count_lines` - Count lines of code
- `find_files` - Find files by pattern

## Safety Levels

- **safe** - No confirmation needed
- **cautious** - Confirmation for potentially risky operations (default)
- **dangerous** - Always requires confirmation

## Common Issues

### CLI Not Found
```bash
# Make bundle executable
chmod +x ./bundle/qwen-claude.js

# Or run with node
node ./bundle/qwen-claude.js
```

### Provider Connection Failed
```bash
# Check if Qwen server is running
curl http://192.168.1.28:8000/health

# Test provider
qwen-claude provider test qwen-local
```

### Configuration Issues
```bash
# Reset config
rm ~/.config/config.json
qwen-claude config init

# Check config validity
qwen-claude config show
```

## Development

### Building
```bash
npm run build        # Build all packages
npm run bundle       # Create executable
npm run clean        # Clean build artifacts
```

### Testing
```bash
# No tests configured yet - manual testing only
node ./bundle/qwen-claude.js --help
```

### Package Structure
```
packages/
├── cli/           # Command interface
├── core/          # Types and schemas
├── providers/     # Model integrations
├── tools/         # Tool implementations
└── utils/         # Cross-platform utilities
```