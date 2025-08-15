# Qwen Claude CLI - Command Reference

## Global Options

Available for all commands:

```bash
qwen-claude [global-options] <command> [command-options]

Global Options:
  -V, --version             Show version number
  -d, --debug               Enable debug mode
  -c, --config <path>       Path to configuration file
  --no-color               Disable colored output
  -v, --verbose            Verbose output
  -h, --help               Show help information
```

## Commands Overview

| Command | Description | Category |
|---------|-------------|----------|
| `chat` | Interactive chat session | Interaction |
| `ask` | Single question query | Interaction |
| `provider` | Manage model providers | Management |
| `model` | Manage models | Management |
| `tool` | Execute tools | Tools |
| `config` | Manage configuration | Configuration |
| `version` | Show version information | Utility |

## Chat Commands

### `qwen-claude chat`

Start an interactive chat session with the AI model.

```bash
qwen-claude chat [options]

Options:
  -m, --model <model>      Model to use for chat
  -p, --provider <provider> Provider to use
  -s, --system <message>   System message/prompt
  --stream                 Enable streaming responses (default: true)
  --no-stream             Disable streaming responses
  --temperature <value>    Response temperature (0.0-2.0)
  --max-tokens <number>    Maximum response tokens
  --timeout <ms>          Request timeout in milliseconds
```

**Examples:**

```bash
# Basic interactive chat
qwen-claude chat

# Chat with specific model
qwen-claude chat --model qwen3-coder-30b

# Chat with system prompt
qwen-claude chat --system "You are a helpful coding assistant"

# Chat with custom temperature
qwen-claude chat --temperature 0.7 --max-tokens 2000
```

**Interactive Commands:**

Within chat session:
- `/help` - Show chat commands
- `/clear` - Clear conversation history
- `/save <filename>` - Save conversation
- `/load <filename>` - Load conversation
- `/model <name>` - Switch model
- `/provider <name>` - Switch provider
- `/exit` - Exit chat session

### `qwen-claude ask`

Ask a single question without entering interactive mode.

```bash
qwen-claude ask <question> [options]

Arguments:
  question                 The question to ask

Options:
  -m, --model <model>      Model to use
  -p, --provider <provider> Provider to use
  --stream                 Enable streaming responses
  --no-stream             Disable streaming responses
  --temperature <value>    Response temperature (0.0-2.0)
  --max-tokens <number>    Maximum response tokens
  --format <type>         Output format (text|json|markdown)
```

**Examples:**

```bash
# Simple question
qwen-claude ask "How do I implement a binary search in TypeScript?"

# Question with specific model
qwen-claude ask "Explain async/await" --model qwen3-coder-30b

# Question with JSON output
qwen-claude ask "List TypeScript best practices" --format json

# Question without streaming
qwen-claude ask "What is the current date?" --no-stream
```

## Provider Management

### `qwen-claude provider`

Manage model providers and their configuration.

```bash
qwen-claude provider <subcommand> [options]

Subcommands:
  list                     List all configured providers
  test [provider]          Test provider connectivity
  add <name>              Add new provider (interactive)
  remove <name>           Remove provider
  enable <name>           Enable provider
  disable <name>          Disable provider
  set-default <name>      Set default provider
```

#### `qwen-claude provider list`

```bash
qwen-claude provider list [options]

Options:
  --show-disabled         Show disabled providers
  --show-config          Show provider configuration
  --format <type>        Output format (table|json|yaml)
```

#### `qwen-claude provider test`

```bash
qwen-claude provider test [provider] [options]

Arguments:
  provider                Provider name (optional, tests all if omitted)

Options:
  --timeout <ms>         Test timeout in milliseconds
  --verbose              Show detailed test results
```

**Examples:**

```bash
# List all providers
qwen-claude provider list

# Test specific provider
qwen-claude provider test "Qwen3-Coder Local"

# Test all providers with verbose output
qwen-claude provider test --verbose

# Add new provider (interactive)
qwen-claude provider add openai-gpt4
```

## Model Management

### `qwen-claude model`

Manage available models from providers.

```bash
qwen-claude model <subcommand> [options]

Subcommands:
  list                    List available models
  info <model>           Show model information
  test <model>           Test model availability
```

#### `qwen-claude model list`

```bash
qwen-claude model list [options]

Options:
  -p, --provider <provider> Filter by provider
  --capabilities          Show model capabilities
  --format <type>         Output format (table|json|yaml)
```

#### `qwen-claude model info`

```bash
qwen-claude model info <model> [options]

Arguments:
  model                   Model name

Options:
  --format <type>         Output format (table|json|yaml)
```

**Examples:**

```bash
# List all models
qwen-claude model list

# List models from specific provider
qwen-claude model list --provider "Qwen3-Coder Local"

# Show model capabilities
qwen-claude model list --capabilities

# Get info about specific model
qwen-claude model info qwen3-coder-30b
```

## Tool Execution

### `qwen-claude tool`

Execute tools for file operations, shell commands, and code analysis.

```bash
qwen-claude tool <subcommand> [options]

Subcommands:
  list                    List available tools
  run <name>             Run a specific tool
  info <name>            Show tool information
```

#### `qwen-claude tool list`

```bash
qwen-claude tool list [options]

Options:
  -c, --category <category> Filter by category (file|shell|analysis)
  --safety-level <level>   Filter by safety level (safe|cautious|dangerous)
  --format <type>         Output format (table|json|yaml)
```

#### `qwen-claude tool run`

```bash
qwen-claude tool run <name> [options]

Arguments:
  name                    Tool name

Options:
  -p, --params <json>     Tool parameters as JSON
  --confirm               Confirm destructive operations
  --no-confirm           Skip confirmation prompts
  --dry-run              Show what would be done without executing
  --timeout <ms>         Execution timeout in milliseconds
  --verbose              Show detailed execution information
```

#### `qwen-claude tool info`

```bash
qwen-claude tool info <name> [options]

Arguments:
  name                    Tool name

Options:
  --format <type>         Output format (table|json|yaml)
  --show-examples        Show usage examples
```

**Examples:**

```bash
# List all tools
qwen-claude tool list

# List file operation tools
qwen-claude tool list --category file

# Run file read tool
qwen-claude tool run read_file --params '{"path":"./package.json"}'

# Run with dry run mode
qwen-claude tool run execute_command --params '{"command":"rm -rf /tmp/test"}' --dry-run

# Get tool information
qwen-claude tool info analyze_code --show-examples
```

## Configuration Management

### `qwen-claude config`

Manage CLI configuration settings.

```bash
qwen-claude config <subcommand> [options]

Subcommands:
  show                    Show current configuration
  init                    Initialize configuration (interactive)
  set <key> <value>      Set configuration value
  get <key>              Get configuration value
  reset                  Reset to default configuration
  validate               Validate configuration
  edit                   Open configuration in editor
```

#### `qwen-claude config show`

```bash
qwen-claude config show [options]

Options:
  --format <type>         Output format (json|yaml|table)
  --section <name>        Show specific section (providers|tools|ui|network)
  --mask-secrets         Hide sensitive information (default: true)
  --no-mask-secrets      Show sensitive information
```

#### `qwen-claude config init`

```bash
qwen-claude config init [options]

Options:
  --force                 Overwrite existing configuration
  --template <name>       Use configuration template
  --non-interactive       Use default values without prompts
```

#### `qwen-claude config set/get`

```bash
qwen-claude config set <key> <value> [options]
qwen-claude config get <key> [options]

Arguments:
  key                     Configuration key (dot notation supported)
  value                   Configuration value (for set command)

Options:
  --type <type>          Value type (string|number|boolean|json)
```

**Examples:**

```bash
# Show all configuration
qwen-claude config show

# Show providers section only
qwen-claude config show --section providers

# Initialize new configuration
qwen-claude config init --force

# Set default provider
qwen-claude config set defaultProvider "Qwen3-Coder Local"

# Get debug setting
qwen-claude config get debug

# Set nested configuration value
qwen-claude config set tools.safetyLevel cautious

# Validate configuration
qwen-claude config validate
```

## Utility Commands

### `qwen-claude version`

Show detailed version and system information.

```bash
qwen-claude version [options]

Options:
  --format <type>         Output format (table|json|yaml)
  --system               Show system information
  --dependencies         Show dependency versions
```

**Examples:**

```bash
# Basic version
qwen-claude version

# Version with system info
qwen-claude version --system

# Full information in JSON
qwen-claude version --format json --dependencies
```

## Exit Codes

The CLI uses standard exit codes:

- `0` - Success
- `1` - General error
- `2` - Misuse (invalid arguments)
- `3` - Configuration error
- `4` - Provider error
- `5` - Tool execution error
- `6` - Network error
- `130` - Interrupted by user (Ctrl+C)

## Environment Variables

Configuration can be overridden using environment variables:

```bash
QWEN_CLAUDE_DEBUG=true                    # Enable debug mode
QWEN_CLAUDE_CONFIG_PATH=/path/to/config   # Custom config file path
QWEN_CLAUDE_NO_COLOR=true                 # Disable colored output
QWEN_CLAUDE_VERBOSE=true                  # Enable verbose output
QWEN_CLAUDE_DEFAULT_PROVIDER=name         # Set default provider
QWEN_CLAUDE_QWEN_URL=http://host:port     # Qwen server URL
QWEN_CLAUDE_OPENROUTER_API_KEY=key        # OpenRouter API key
```

## Configuration File Precedence

1. Command line arguments (highest priority)
2. Environment variables
3. Configuration file (`~/.config/config.json`)
4. Default values (lowest priority)

## Input/Output Formats

### Supported Input Formats

- **JSON**: For tool parameters and configuration
- **YAML**: For configuration files
- **Plain text**: For questions and prompts

### Supported Output Formats

- **table**: Human-readable tabular format (default)
- **json**: Machine-readable JSON format
- **yaml**: Human-readable YAML format
- **markdown**: Formatted markdown (for responses)

## Shell Completion

Enable shell completion for better CLI experience:

```bash
# Bash
qwen-claude completion bash >> ~/.bashrc

# Zsh
qwen-claude completion zsh >> ~/.zshrc

# PowerShell (Windows)
qwen-claude completion powershell >> $PROFILE
```