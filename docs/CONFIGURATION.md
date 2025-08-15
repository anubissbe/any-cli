# Configuration Guide

Complete guide to configuring Qwen Claude CLI for your environment and use cases.

## Configuration File Formats

The CLI supports multiple configuration formats:

- **JSON**: `qwen-claude.config.json`
- **YAML**: `qwen-claude.config.yaml` or `qwen-claude.config.yml`
- **Hidden files**: `.qwen-claude.json`, `.qwen-claude.yaml`, `.qwen-claude.yml`

## Configuration Hierarchy

Settings are loaded in the following order (later sources override earlier ones):

1. Default configuration (built-in)
2. Global configuration file
3. Local configuration file (in current directory)
4. Environment variables
5. Command-line arguments

## Complete Configuration Reference

### Basic Configuration

```yaml
# Application metadata
version: "0.1.0"
debug: false
logLevel: "info"              # error, warn, info, debug, trace
interactive: true             # Enable interactive prompts
defaultProvider: "qwen-local" # Default provider to use
```

### Provider Configuration

#### Local Qwen Provider

```yaml
providers:
  - name: "qwen-local"
    type: "local"
    priority: 1               # Lower numbers = higher priority
    enabled: true
    auth:
      type: "none"            # No authentication for local server
      baseUrl: "http://192.168.1.28:8000"
    models:
      - "qwen3-coder-30b"
      - "qwen2.5-coder-32b-instruct"
      - "qwen2.5-72b-instruct"
    endpoint: "http://192.168.1.28:8000/v1"
    timeout: 60000            # 60 seconds for local models
    retries: 2
    
    # Advanced Qwen-specific settings
    qwen:
      temperature: 0.7
      maxTokens: 4096
      topP: 0.9
      topK: 40
      repetitionPenalty: 1.1
      presencePenalty: 0.0
      frequencyPenalty: 0.0
```

#### OpenRouter Provider

```yaml
providers:
  - name: "openrouter"
    type: "remote"
    priority: 2
    enabled: true
    auth:
      type: "api_key"
      apiKey: "${QWEN_CLAUDE_OPENROUTER_API_KEY}" # Environment variable
      baseUrl: "https://openrouter.ai/api"
      headers:
        "HTTP-Referer": "https://github.com/your-org/qwen-claude-cli"
        "X-Title": "Qwen Claude CLI"
    models:
      # Free models
      - "meta-llama/llama-3.1-8b-instruct:free"
      - "mistralai/mistral-7b-instruct:free"
      - "huggingfaceh4/zephyr-7b-beta:free"
      
      # Paid models (require credits)
      - "openai/gpt-4o-mini"
      - "anthropic/claude-3-haiku"
      - "qwen/qwen-2.5-coder-32b-instruct"
      - "deepseek/deepseek-coder"
      - "google/gemini-pro"
    endpoint: "https://openrouter.ai/api/v1"
    timeout: 30000            # 30 seconds for remote models
    retries: 3
    
    # OpenRouter-specific settings
    openrouter:
      transforms: ["middle-out"] # Response transformations
      models: null              # Use all available models
      route: "fallback"         # Routing strategy
```

#### Custom Provider

```yaml
providers:
  - name: "custom-api"
    type: "remote"
    priority: 3
    enabled: false
    auth:
      type: "bearer"           # or "api_key", "basic", "custom"
      token: "${CUSTOM_API_TOKEN}"
      baseUrl: "https://api.custom.com"
      headers:
        "User-Agent": "qwen-claude-cli/0.1.0"
        "Accept": "application/json"
    models:
      - "custom-model-v1"
      - "custom-model-v2"
    endpoint: "https://api.custom.com/v1"
    timeout: 45000
    retries: 2
    
    # Custom request/response mapping
    requestMapping:
      temperature: "temp"
      maxTokens: "max_length"
      messages: "input"
    responseMapping:
      content: "choices[0].message.content"
      usage: "usage"
```

### Tool Configuration

```yaml
tools:
  safetyLevel: "cautious"     # safe, cautious, moderate, permissive
  confirmDestructive: true    # Always confirm destructive operations
  timeout: 30000             # Tool execution timeout (ms)
  maxRetries: 3              # Maximum retry attempts
  dryRun: false              # Default to actual execution
  
  # Category-specific settings
  categories:
    file:
      maxFileSize: 10485760   # 10MB max file size
      allowedExtensions:
        - ".txt"
        - ".md"
        - ".json"
        - ".yaml"
        - ".js"
        - ".ts"
        - ".py"
      restrictedPaths:
        - "/etc"
        - "/sys"
        - "/proc"
        - "C:\\Windows"
    
    shell:
      allowedCommands:
        - "ls"
        - "cat"
        - "grep"
        - "find"
        - "git"
        - "npm"
        - "node"
      restrictedCommands:
        - "rm"
        - "del"
        - "format"
        - "shutdown"
      maxExecutionTime: 60000  # 60 seconds
    
    analysis:
      maxAnalysisDepth: 5      # Directory depth for analysis
      includeTests: true       # Include test files in analysis
      includeNodeModules: false # Exclude node_modules
```

### UI Configuration

```yaml
ui:
  theme: "default"            # default, dark, light, minimal
  colorOutput: true           # Enable colored output
  spinner: true               # Show spinner during operations
  progressBar: true           # Show progress bars
  
  # Color customization
  colors:
    primary: "#007acc"
    success: "#28a745"
    warning: "#ffc107"
    error: "#dc3545"
    info: "#17a2b8"
    muted: "#6c757d"
  
  # Spinner customization
  spinners:
    type: "dots"              # dots, line, pipe, etc.
    color: "cyan"
    
  # Progress bar customization
  progressBars:
    style: "modern"           # classic, modern, minimal
    showPercentage: true
    showETA: true
```

### Network Configuration

```yaml
network:
  timeout: 30000             # Default request timeout (ms)
  retries: 3                 # Default retry attempts
  userAgent: "qwen-claude-cli/0.1.0"
  
  # Proxy settings
  proxy:
    http: "http://proxy:8080"
    https: "https://proxy:8080"
    noProxy: "localhost,127.0.0.1,.local"
  
  # Rate limiting
  rateLimit:
    enabled: true
    requestsPerMinute: 60
    burstSize: 10
  
  # SSL/TLS settings
  ssl:
    rejectUnauthorized: true
    ca: "/path/to/ca-cert.pem"
    cert: "/path/to/client-cert.pem"
    key: "/path/to/client-key.pem"
```

### Logging Configuration

```yaml
logging:
  level: "info"              # error, warn, info, debug, trace
  format: "pretty"           # pretty, json, structured
  file: "/var/log/qwen-claude-cli.log" # Log file path (optional)
  maxFileSize: "10MB"        # Rotate when file exceeds size
  maxFiles: 5                # Keep maximum number of log files
  
  # Logger-specific levels
  loggers:
    "provider": "debug"
    "tool": "info"
    "config": "warn"
    "network": "error"
```

### Cache Configuration

```yaml
cache:
  enabled: true
  directory: "~/.cache/qwen-claude-cli"
  maxSize: "100MB"           # Maximum cache size
  ttl: 3600                  # Time to live in seconds
  
  # Cache-specific settings
  models:
    enabled: true
    ttl: 86400               # 24 hours
  
  responses:
    enabled: false           # Don't cache responses by default
    ttl: 300                 # 5 minutes if enabled
  
  tools:
    enabled: true
    ttl: 1800                # 30 minutes
```

## Environment Variable Reference

All configuration options can be overridden using environment variables:

### Basic Settings

```bash
export QWEN_CLAUDE_DEBUG=true
export QWEN_CLAUDE_LOG_LEVEL=debug
export QWEN_CLAUDE_INTERACTIVE=false
export QWEN_CLAUDE_DEFAULT_PROVIDER=openrouter
```

### Provider Settings

```bash
# Qwen Local
export QWEN_CLAUDE_QWEN_URL=http://192.168.1.28:8000/v1
export QWEN_CLAUDE_QWEN_TIMEOUT=60000

# OpenRouter
export QWEN_CLAUDE_OPENROUTER_API_KEY=your_api_key_here
export QWEN_CLAUDE_OPENROUTER_URL=https://openrouter.ai/api/v1

# Custom Provider
export QWEN_CLAUDE_CUSTOM_API_TOKEN=your_token_here
export QWEN_CLAUDE_CUSTOM_API_URL=https://api.custom.com/v1
```

### Network Settings

```bash
export QWEN_CLAUDE_PROXY=http://proxy:8080
export QWEN_CLAUDE_TIMEOUT=30000
export QWEN_CLAUDE_RETRIES=3
export QWEN_CLAUDE_USER_AGENT="custom-agent/1.0"
```

### Tool Settings

```bash
export QWEN_CLAUDE_TOOLS_SAFETY_LEVEL=cautious
export QWEN_CLAUDE_TOOLS_CONFIRM_DESTRUCTIVE=true
export QWEN_CLAUDE_TOOLS_TIMEOUT=30000
export QWEN_CLAUDE_TOOLS_DRY_RUN=false
```

### UI Settings

```bash
export QWEN_CLAUDE_THEME=dark
export NO_COLOR=1              # Disable colors (standard)
export FORCE_COLOR=1           # Force colors (standard)
export QWEN_CLAUDE_SPINNER=false
export QWEN_CLAUDE_PROGRESS_BAR=true
```

## Configuration Examples

### Development Configuration

```yaml
# qwen-claude.config.yaml
version: "0.1.0"
debug: true
logLevel: "debug"
interactive: true
defaultProvider: "qwen-local"

providers:
  - name: "qwen-local"
    type: "local"
    priority: 1
    enabled: true
    auth:
      type: "none"
      baseUrl: "http://localhost:8000"
    models: ["qwen3-coder-30b"]
    endpoint: "http://localhost:8000/v1"
    timeout: 120000  # Longer timeout for development

tools:
  safetyLevel: "permissive"
  confirmDestructive: false
  dryRun: true  # Safe default for development

ui:
  theme: "dark"
  colorOutput: true
  spinner: true

logging:
  level: "debug"
  format: "pretty"
```

### Production Configuration

```yaml
# qwen-claude.config.yaml
version: "0.1.0"
debug: false
logLevel: "info"
interactive: false
defaultProvider: "openrouter"

providers:
  - name: "openrouter"
    type: "remote"
    priority: 1
    enabled: true
    auth:
      type: "api_key"
      apiKey: "${QWEN_CLAUDE_OPENROUTER_API_KEY}"
      baseUrl: "https://openrouter.ai/api"
    models: ["anthropic/claude-3-haiku"]
    endpoint: "https://openrouter.ai/api/v1"
    timeout: 30000
    retries: 3

tools:
  safetyLevel: "cautious"
  confirmDestructive: true
  dryRun: false

ui:
  theme: "minimal"
  colorOutput: false
  spinner: false

logging:
  level: "warn"
  format: "json"
  file: "/var/log/qwen-claude-cli.log"
```

### CI/CD Configuration

```yaml
# .qwen-claude.yaml
version: "0.1.0"
debug: false
logLevel: "error"
interactive: false
defaultProvider: "openrouter"

providers:
  - name: "openrouter"
    type: "remote"
    priority: 1
    enabled: true
    auth:
      type: "api_key"
      apiKey: "${CI_OPENROUTER_API_KEY}"
    models: ["meta-llama/llama-3.1-8b-instruct:free"]
    timeout: 60000
    retries: 5

tools:
  safetyLevel: "safe"
  confirmDestructive: false
  dryRun: true
  timeout: 120000

ui:
  colorOutput: false
  spinner: false
  progressBar: false

network:
  timeout: 60000
  retries: 5

cache:
  enabled: false  # Disable cache in CI
```

## Configuration Validation

The CLI validates configuration on startup. Common validation errors:

### Invalid Provider Configuration

```yaml
# ❌ Invalid - missing required fields
providers:
  - name: "incomplete"
    enabled: true

# ✅ Valid - all required fields present
providers:
  - name: "complete"
    type: "remote"
    priority: 1
    enabled: true
    auth:
      type: "api_key"
      apiKey: "your-key"
    endpoint: "https://api.example.com/v1"
```

### Invalid Tool Configuration

```yaml
# ❌ Invalid - unknown safety level
tools:
  safetyLevel: "unknown"

# ✅ Valid - known safety level
tools:
  safetyLevel: "cautious"
```

### Invalid Network Configuration

```yaml
# ❌ Invalid - negative timeout
network:
  timeout: -1000

# ✅ Valid - positive timeout
network:
  timeout: 30000
```

## Configuration Best Practices

### Security

1. **Never commit API keys** to version control
2. **Use environment variables** for sensitive data
3. **Restrict file permissions** on configuration files
4. **Use separate configs** for different environments

### Performance

1. **Set appropriate timeouts** based on model speed
2. **Configure retry limits** to avoid infinite loops
3. **Enable caching** for frequently used data
4. **Tune rate limits** to avoid API throttling

### Maintenance

1. **Use version control** for configuration files
2. **Document custom settings** with comments
3. **Test configurations** before deployment
4. **Monitor logs** for configuration issues

## Advanced Configuration

### Dynamic Configuration

Configuration can be modified at runtime using environment variables:

```bash
# Override provider for single command
QWEN_CLAUDE_DEFAULT_PROVIDER=openrouter qwen-claude ask "Hello"

# Override safety level for specific operation
QWEN_CLAUDE_TOOLS_SAFETY_LEVEL=permissive qwen-claude tool run write_file
```

### Profile-based Configuration

Create multiple configuration profiles:

```bash
# Development profile
cp qwen-claude.config.yaml qwen-claude.dev.yaml

# Production profile
cp qwen-claude.config.yaml qwen-claude.prod.yaml

# Use specific profile
qwen-claude --config qwen-claude.prod.yaml ask "Hello"
```

### Configuration Inheritance

Use configuration inheritance for complex setups:

```yaml
# base.yaml
version: "0.1.0"
ui:
  colorOutput: true
  spinner: true

# development.yaml
extends: "./base.yaml"
debug: true
logLevel: "debug"

# production.yaml
extends: "./base.yaml"
debug: false
logLevel: "warn"
```

For more advanced configuration scenarios, see the [API Documentation](./API.md).