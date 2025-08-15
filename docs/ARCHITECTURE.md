# Qwen Claude CLI - Architecture Documentation

## Overview

The qwen-claude-cli is built as a modular TypeScript application using modern ESM modules, organized as a monorepo with multiple packages. The architecture follows clean separation of concerns with dependency injection and abstract interfaces.

## High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│      CLI        │    │    Providers    │    │     Tools       │
│   Interface     │───▶│   (Models)      │    │  (Execution)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 ▼
         ┌─────────────────────────────────────────────────┐
         │                  Core                           │
         │        (Types, Config, Interfaces)              │
         └─────────────────────────────────────────────────┘
                                 │
                                 ▼
         ┌─────────────────────────────────────────────────┐
         │                 Utils                           │
         │      (Platform, Config Manager)                 │
         └─────────────────────────────────────────────────┘
```

## Package Structure

### 1. Core Package (`@qwen-claude/core`)

**Purpose**: Central types, interfaces, configuration schemas, and error definitions.

**Key Components**:
- `types/` - TypeScript interfaces and types
- `config/` - Configuration schemas using Zod
- `interfaces/` - Abstract interfaces for providers and tools
- `errors/` - Structured error classes

**Key Files**:
- `config/schema.ts` - Zod schemas for validation
- `types/providers.ts` - Provider and model interfaces
- `types/tools.ts` - Tool execution interfaces
- `interfaces/config.ts` - Configuration management interfaces

### 2. Providers Package (`@qwen-claude/providers`)

**Purpose**: Model provider implementations for local and remote AI models.

**Key Components**:
- `base/` - Abstract base provider class
- `http/` - HTTP-based provider for local Qwen models
- `remote/` - Remote provider for OpenRouter and other APIs
- `registry/` - Provider factory and registration system

**Provider Types**:
- **Local Providers**: Direct HTTP communication with local models
- **Remote Providers**: API key authenticated external services

### 3. Tools Package (`@qwen-claude/tools`)

**Purpose**: Tool execution framework with safety controls and categories.

**Tool Categories**:
- **File Tools**: File system operations (read, write, list, create)
- **Shell Tools**: Command execution with safety controls
- **Analysis Tools**: Code analysis and metrics generation

**Safety Framework**:
- Safety levels: `safe`, `cautious`, `dangerous`
- User confirmation for destructive operations
- Execution timeouts and resource limits

### 4. Utils Package (`@qwen-claude/utils`)

**Purpose**: Cross-platform utilities and configuration management.

**Key Components**:
- `platform.ts` - Platform detection and utilities
- `config-manager.ts` - Configuration loading and validation
- `file-system.ts` - Cross-platform file operations

### 5. CLI Package (`@qwen-claude/cli`)

**Purpose**: Command-line interface and user interaction.

**Key Components**:
- `commands/` - CLI command implementations
- `ui/` - User interface components (prompts, formatting)
- `main.ts` - Application entry point and initialization

## Data Flow

### 1. Application Initialization

```typescript
Application Startup
├── Load Configuration (utils/config-manager)
├── Validate Configuration (core/config/schema)
├── Initialize Providers (providers/registry)
├── Register Tools (tools/registry)
└── Start CLI Interface (cli/main)
```

### 2. Command Execution Flow

```typescript
User Command
├── Parse Arguments (cli/commands)
├── Validate Parameters (core validation)
├── Select Provider (providers/registry)
├── Execute Request/Tool (providers + tools)
├── Format Response (cli/ui)
└── Display Result (cli/ui)
```

### 3. Provider Communication

```typescript
Chat Request
├── Provider Selection (based on config/availability)
├── Request Validation (schema validation)
├── Model Communication (HTTP/API calls)
├── Response Streaming (AsyncIterable)
└── Error Handling (structured errors)
```

## Configuration Architecture

### Configuration Hierarchy

1. **Default Values** (hardcoded in schemas)
2. **Configuration Files** (JSON/YAML)
3. **Environment Variables** (QWEN_CLAUDE_*)
4. **Command Line Arguments** (highest priority)

### Configuration Sources

```typescript
interface ConfigSource {
  file: string;           // ~/.config/qwen-claude/config.json
  environment: object;    // process.env.QWEN_CLAUDE_*
  args: object;          // CLI arguments
  defaults: object;      // Schema defaults
}
```

## Error Handling Strategy

### Error Types

```typescript
abstract class QwenClaudeError extends Error {
  abstract code: string;
  abstract category: 'config' | 'provider' | 'tool' | 'network';
}
```

### Error Categories

- **ConfigError**: Configuration validation and loading errors
- **ProviderError**: Model provider communication errors
- **ToolError**: Tool execution and validation errors
- **NetworkError**: Network connectivity and timeout errors

## Security Architecture

### Tool Safety Framework

```typescript
interface SafetyLevel {
  safe: string[];        // No confirmation needed
  cautious: string[];    // Requires confirmation
  dangerous: string[];   // Always requires explicit confirmation
}
```

### Input Validation

- **Zod Schemas**: Runtime validation for all inputs
- **Parameter Sanitization**: Safe parameter handling
- **Path Validation**: Prevent directory traversal attacks

## Performance Considerations

### Lazy Loading

- Providers are loaded on-demand
- Tools are registered but not initialized until used
- Configuration is cached after first load

### Streaming Support

- Real-time response streaming from models
- AsyncIterable interfaces for chunked responses
- Cancellation token support for long-running operations

### Resource Management

- Proper cleanup of HTTP connections
- Timeout controls for all operations
- Memory-efficient streaming for large responses

## Extension Points

### Adding New Providers

```typescript
class CustomProvider extends BaseProvider {
  async initialize(): Promise<Result<void>> { ... }
  async chatCompletion(request: ChatCompletionRequest): Promise<Result<ChatCompletionResponse>> { ... }
}

// Register in providers/registry
providerRegistry.register(new CustomProviderFactory());
```

### Adding New Tools

```typescript
class CustomTool extends BaseTool<Params, Result> {
  name = 'custom_tool';
  safetyLevel = 'cautious';
  
  async execute(params: Params, context: ExecutionContext): Promise<Result> { ... }
}

// Register in tools/registry
toolRegistry.register(new CustomTool());
```

### Adding New Commands

```typescript
// cli/commands/custom.ts
export const customCommand = {
  name: 'custom',
  description: 'Custom command',
  action: async (options: CustomOptions) => { ... }
};
```

## Build Architecture

### ESBuild Configuration

- **Entry Point**: `packages/cli/index.ts`
- **Bundle Target**: Single executable JavaScript file
- **Platform**: Node.js ESM modules
- **External Dependencies**: Node.js built-ins and npm packages

### Package Management

- **npm Workspaces**: Monorepo with interdependent packages
- **TypeScript Project References**: Efficient incremental builds
- **Shared Dependencies**: Common dependencies hoisted to root

## Testing Strategy

### Unit Testing

- **Tool Testing**: Mock execution contexts and parameters
- **Provider Testing**: Mock HTTP responses and API calls
- **Configuration Testing**: Validate schema parsing and validation

### Integration Testing

- **End-to-End CLI Testing**: Full command execution
- **Provider Integration**: Real API communication tests
- **Cross-Platform Testing**: Windows/macOS/Linux compatibility

## Deployment Architecture

### Distribution

- **npm Package**: Global installation via npm
- **Bundled Executable**: Single-file distribution
- **Cross-Platform**: Windows (.exe), macOS, Linux binaries

### Configuration Management

- **User Configuration**: `~/.config/qwen-claude/`
- **Data Storage**: `~/.local/share/qwen-claude/`
- **Cache**: `~/.cache/qwen-claude/`
- **Cross-Platform Paths**: Automatic platform detection