# Qwen Claude CLI

Advanced TypeScript CLI tool with Qwen3-Coder 30B and OpenRouter integration for AI-powered code assistance.

## Features

- **Local Qwen3-Coder 30B Integration** - Connect to local Qwen model server (192.168.1.28:8000)
- **OpenRouter.ai Support** - Access free models from multiple providers
- **Tool Execution Framework** - File operations, shell commands, and code analysis
- **Cross-platform Compatibility** - Works on Linux, macOS, and Windows
- **TypeScript Implementation** - Modern ESM modules with ESBuild bundling
- **Configuration Management** - Flexible YAML/JSON configuration with validation
- **Interactive & One-shot Modes** - Chat sessions or single questions
- **Streaming Responses** - Real-time response streaming support
- **Safety Features** - Configurable safety levels for destructive operations

## Quick Start

### Installation

```bash
# Install globally
npm install -g @qwen-claude/qwen-claude-cli

# Or install locally in your project
npm install @qwen-claude/qwen-claude-cli

# Link for development
npm run install:global
```

### Basic Usage

```bash
# Start interactive chat
qwen-claude chat

# Ask a single question
qwen-claude ask "How do I implement a binary tree in TypeScript?"

# Use specific model and provider
qwen-claude ask "Explain async/await" --model qwen3-coder-30b --provider qwen-local

# List available models
qwen-claude model list

# Initialize configuration
qwen-claude config init
```

## Commands

### Chat Commands

```bash
# Interactive chat session
qwen-claude chat [options]
  -m, --model <model>      Model to use for chat
  -p, --provider <provider> Provider to use
  -s, --system <message>   System message
  --stream                 Enable streaming responses

# Single question
qwen-claude ask <question> [options]
  -m, --model <model>      Model to use
  -p, --provider <provider> Provider to use
  --stream                 Enable streaming responses
```

### Provider Management

```bash
# List available providers
qwen-claude provider list

# Test provider connectivity
qwen-claude provider test [provider]
```

### Tool Execution

```bash
# Run a tool
qwen-claude tool run <name> [options]
  -p, --params <json>      Tool parameters as JSON
  --confirm                Confirm destructive operations
  --dry-run               Show what would be done

# List available tools
qwen-claude tool list [options]
  -c, --category <category> Filter by category
```

### Configuration

```bash
# Show current configuration
qwen-claude config show

# Initialize configuration
qwen-claude config init [options]
  --force                  Overwrite existing configuration
```

## Configuration

Create a configuration file to customize providers and settings:

```yaml
# qwen-claude.config.yaml
version: "0.1.0"
defaultProvider: "qwen-local"

providers:
  - name: "qwen-local"
    type: "local"
    priority: 1
    enabled: true
    endpoint: "http://192.168.1.28:8000/v1"
    models: ["qwen3-coder-30b"]
    
  - name: "openrouter"
    type: "remote"
    priority: 2
    enabled: true
    auth:
      type: "api_key"
      apiKey: "${QWEN_CLAUDE_OPENROUTER_API_KEY}"
    endpoint: "https://openrouter.ai/api/v1"
    models:
      - "meta-llama/llama-3.1-8b-instruct:free"
      - "anthropic/claude-3-haiku"

tools:
  safetyLevel: "cautious"
  confirmDestructive: true

ui:
  colorOutput: true
  spinner: true
```

### Environment Variables

```bash
export QWEN_CLAUDE_DEBUG=true
export QWEN_CLAUDE_DEFAULT_PROVIDER=qwen-local
export QWEN_CLAUDE_QWEN_URL=http://192.168.1.28:8000/v1
export QWEN_CLAUDE_OPENROUTER_API_KEY=your_api_key_here
```

## Available Tools

- **File Operations**: `read_file`, `write_file`, `list_directory`, `create_directory`
- **Shell Operations**: `execute_command`, `run_script`
- **Code Analysis**: `analyze_code`, `generate_docs`, `refactor_code`

Example tool usage:

```bash
# Read a file
qwen-claude tool run read_file --params '{"path": "package.json"}'

# List directory contents
qwen-claude tool run list_directory --params '{"path": "src", "recursive": true}'

# Analyze code structure
qwen-claude tool run analyze_code --params '{"path": ".", "includeMetrics": true}'
```

## Documentation

- [Setup Guide](docs/SETUP.md) - Installation and setup for all platforms
- [Configuration Guide](docs/CONFIGURATION.md) - Complete configuration reference
- [Tool Usage](docs/TOOLS.md) - Detailed tool documentation and examples
- [Troubleshooting](docs/TROUBLESHOOTING.md) - Common issues and solutions
- [Development Guide](docs/DEVELOPMENT.md) - Contributing and extending the CLI
- [API Reference](docs/API.md) - Complete API documentation
- [Examples](docs/EXAMPLES.md) - Practical usage examples

## Development

### Requirements

- Node.js 20.0.0+
- npm 10.0.0+
- TypeScript 5.6+

### Development Setup

```bash
# Clone repository
git clone https://github.com/your-org/qwen-claude-cli.git
cd qwen-claude-cli

# Install dependencies
npm install

# Build packages
npm run build

# Link for local development
npm link

# Run tests
npm test

# Format and lint
npm run format
npm run lint
```

### Project Structure

```
qwen-claude-cli/
├── packages/
│   ├── cli/              # CLI entry point and commands
│   ├── core/             # Core types and configuration
│   ├── providers/        # Model provider implementations
│   ├── tools/            # Tool execution framework
│   └── utils/            # Shared utilities
├── docs/                 # Documentation
├── scripts/              # Build and development scripts
└── bundle/               # Compiled output
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make changes following the coding standards
4. Add tests for new functionality
5. Ensure all tests pass: `npm test`
6. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

- [GitHub Issues](https://github.com/your-org/qwen-claude-cli/issues) - Bug reports and feature requests
- [GitHub Discussions](https://github.com/your-org/qwen-claude-cli/discussions) - Questions and community
- [Documentation](docs/) - Comprehensive guides and references

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for release history and changes.