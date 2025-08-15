# API Reference

Complete API reference for Qwen Claude CLI components and interfaces.

## Core Interfaces

### AppConfig

Main application configuration interface.

```typescript
interface AppConfig {
  version: string;
  debug: boolean;
  logLevel: LogLevel;
  interactive: boolean;
  defaultProvider: string;
  providers: ProviderConfig[];
  tools: ToolConfig;
  ui: UIConfig;
  network: NetworkConfig;
  cache?: CacheConfig;
  logging?: LoggingConfig;
}
```

**Properties:**
- `version` - Application version
- `debug` - Enable debug mode
- `logLevel` - Logging level (error, warn, info, debug, trace)
- `interactive` - Enable interactive prompts
- `defaultProvider` - Default provider to use
- `providers` - Array of provider configurations
- `tools` - Tool execution configuration
- `ui` - User interface configuration
- `network` - Network configuration
- `cache` - Cache configuration (optional)
- `logging` - Logging configuration (optional)

### ProviderConfig

Configuration for model providers.

```typescript
interface ProviderConfig {
  name: string;
  type: 'local' | 'remote';
  priority: number;
  enabled: boolean;
  auth: AuthConfig;
  models: string[];
  endpoint: string;
  timeout: number;
  retries: number;
  [key: string]: any; // Provider-specific settings
}
```

**Properties:**
- `name` - Unique provider identifier
- `type` - Provider type (local or remote)
- `priority` - Provider priority (lower = higher priority)
- `enabled` - Whether provider is enabled
- `auth` - Authentication configuration
- `models` - Array of supported model IDs
- `endpoint` - API endpoint URL
- `timeout` - Request timeout in milliseconds
- `retries` - Number of retry attempts

### AuthConfig

Authentication configuration for providers.

```typescript
type AuthConfig = 
  | { type: 'none'; baseUrl?: string; }
  | { type: 'api_key'; apiKey: string; baseUrl?: string; headers?: Record<string, string>; }
  | { type: 'bearer'; token: string; baseUrl?: string; headers?: Record<string, string>; }
  | { type: 'basic'; username: string; password: string; baseUrl?: string; }
  | { type: 'custom'; headers: Record<string, string>; baseUrl?: string; };
```

**Types:**
- `none` - No authentication required
- `api_key` - API key authentication
- `bearer` - Bearer token authentication
- `basic` - Basic authentication (username/password)
- `custom` - Custom header-based authentication

### ModelInfo

Information about available models.

```typescript
interface ModelInfo {
  id: string;
  name: string;
  description: string;
  provider: string;
  version: string;
  capabilities: ModelCapabilities;
  isLocal: boolean;
  pricing?: ModelPricing;
  limits?: ModelLimits;
}
```

**Properties:**
- `id` - Unique model identifier
- `name` - Human-readable model name
- `description` - Model description
- `provider` - Provider name
- `version` - Model version
- `capabilities` - Model capabilities
- `isLocal` - Whether model runs locally
- `pricing` - Pricing information (optional)
- `limits` - Usage limits (optional)

### ModelCapabilities

Model capability flags.

```typescript
interface ModelCapabilities {
  supportsStreaming: boolean;
  supportsTools: boolean;
  supportsImages: boolean;
  supportsCodeGeneration: boolean;
  maxTokens: number;
  contextWindow: number;
}
```

## Provider API

### BaseProvider

Abstract base class for all providers.

```typescript
abstract class BaseProvider {
  readonly name: string;
  readonly config: ProviderConfig;
  
  constructor(config: ProviderConfig);
  
  abstract initialize(): Promise<void>;
  abstract getModels(): Promise<Result<ReadonlyArray<ModelInfo>>>;
  abstract chatCompletion(request: ChatCompletionRequest): Promise<Result<ChatCompletionResponse>>;
  abstract chatCompletionStream(request: ChatCompletionRequest): AsyncIterable<Result<ChatCompletionChunk>>;
  
  isAvailable(): boolean;
  healthCheck(): Promise<Result<void>>;
  dispose(): Promise<void>;
}
```

**Methods:**
- `initialize()` - Initialize the provider
- `getModels()` - Get available models
- `chatCompletion()` - Send chat completion request
- `chatCompletionStream()` - Send streaming chat completion request
- `isAvailable()` - Check if provider is available
- `healthCheck()` - Perform health check
- `dispose()` - Clean up provider resources

### ChatCompletionRequest

Request object for chat completions.

```typescript
interface ChatCompletionRequest {
  model: string;
  messages: ChatMessage[];
  temperature?: number;
  maxTokens?: number;
  topP?: number;
  topK?: number;
  stop?: string[];
  stream?: boolean;
  tools?: ToolDefinition[];
  toolChoice?: string | ToolChoice;
  user?: string;
}
```

### ChatCompletionResponse

Response object for chat completions.

```typescript
interface ChatCompletionResponse {
  id: string;
  model: string;
  message: ChatMessage;
  finishReason: 'stop' | 'length' | 'tool_calls' | 'content_filter';
  usage: TokenUsage;
  toolCalls?: ToolCall[];
  created?: Date;
}
```

### ChatMessage

Individual chat message.

```typescript
interface ChatMessage {
  role: 'system' | 'user' | 'assistant' | 'tool';
  content: string;
  name?: string;
  toolCallId?: string;
  timestamp?: Date;
}
```

### HttpProvider

Base class for HTTP-based providers.

```typescript
abstract class HttpProvider extends BaseProvider {
  protected makeRequest<T>(options: RequestOptions): Promise<Result<T>>;
  protected makeStreamingRequest<T>(options: RequestOptions): AsyncIterable<Result<T>>;
  
  protected validateResponse(response: any): boolean;
  protected transformRequest(request: ChatCompletionRequest): any;
  protected transformResponse(response: any): ChatCompletionResponse;
}
```

## Tool API

### BaseTool

Abstract base class for all tools.

```typescript
abstract class BaseTool {
  abstract readonly name: string;
  abstract readonly description: string;
  abstract readonly category: ToolCategory;
  abstract readonly safetyLevel: SafetyLevel;
  abstract readonly parameters: Record<string, ParameterDefinition>;
  
  abstract execute(params: Record<string, any>, context: ToolExecutionContext): Promise<ToolExecutionResult>;
  
  protected validateParameters<T>(params: Record<string, any>, schema: ZodSchema<T>): T;
  protected checkSafety(context: ToolExecutionContext): void;
  protected confirmOperation(context: ToolExecutionContext, message: string): Promise<boolean>;
  protected createSuccessResult(message: string, data?: any): ToolExecutionResult;
  protected createErrorResult(message: string, error?: any): ToolExecutionResult;
  protected createDryRunResult(message: string, data?: any): ToolExecutionResult;
}
```

### ToolExecutionContext

Context provided to tools during execution.

```typescript
interface ToolExecutionContext {
  workingDirectory: string;
  dryRun: boolean;
  safetyLevel: SafetyLevel;
  confirm: (message: string) => Promise<boolean>;
  userId?: string;
  sessionId?: string;
  environment?: Record<string, string>;
}
```

### ToolExecutionResult

Result returned by tool execution.

```typescript
interface ToolExecutionResult {
  success: boolean;
  message: string;
  data?: any;
  error?: any;
  metadata?: {
    toolName: string;
    executionTime: number;
    timestamp: Date;
    dryRun: boolean;
  };
}
```

### SafetyLevel

Tool safety levels.

```typescript
enum SafetyLevel {
  SAFE = 'safe',
  MODERATE = 'moderate', 
  DESTRUCTIVE = 'destructive'
}
```

### ToolCategory

Tool categories.

```typescript
enum ToolCategory {
  FILE = 'file',
  SHELL = 'shell',
  ANALYSIS = 'analysis',
  NETWORK = 'network',
  CUSTOM = 'custom'
}
```

## Built-in Tools

### File Tools

#### ReadFileTool

```typescript
class ReadFileTool extends BaseTool {
  readonly name = 'read_file';
  readonly description = 'Read contents of a file';
  readonly category = ToolCategory.FILE;
  readonly safetyLevel = SafetyLevel.SAFE;
  
  readonly parameters = {
    path: { type: 'string', description: 'Path to the file to read' },
    encoding: { type: 'string', description: 'File encoding', default: 'utf8' }
  };
}
```

#### WriteFileTool

```typescript
class WriteFileTool extends BaseTool {
  readonly name = 'write_file';
  readonly description = 'Write content to a file';
  readonly category = ToolCategory.FILE;
  readonly safetyLevel = SafetyLevel.DESTRUCTIVE;
  
  readonly parameters = {
    path: { type: 'string', description: 'Path to the file to write' },
    content: { type: 'string', description: 'Content to write' },
    encoding: { type: 'string', description: 'File encoding', default: 'utf8' },
    mode: { type: 'number', description: 'File permissions', optional: true }
  };
}
```

#### ListDirectoryTool

```typescript
class ListDirectoryTool extends BaseTool {
  readonly name = 'list_directory';
  readonly description = 'List contents of a directory';
  readonly category = ToolCategory.FILE;
  readonly safetyLevel = SafetyLevel.SAFE;
  
  readonly parameters = {
    path: { type: 'string', description: 'Directory path' },
    includeHidden: { type: 'boolean', description: 'Include hidden files', default: false },
    recursive: { type: 'boolean', description: 'List recursively', default: false }
  };
}
```

### Shell Tools

#### ExecuteCommandTool

```typescript
class ExecuteCommandTool extends BaseTool {
  readonly name = 'execute_command';
  readonly description = 'Execute shell commands';
  readonly category = ToolCategory.SHELL;
  readonly safetyLevel = SafetyLevel.DESTRUCTIVE;
  
  readonly parameters = {
    command: { type: 'string', description: 'Command to execute' },
    args: { type: 'array', description: 'Command arguments', optional: true },
    workingDirectory: { type: 'string', description: 'Working directory', optional: true },
    timeout: { type: 'number', description: 'Execution timeout', optional: true },
    env: { type: 'object', description: 'Environment variables', optional: true }
  };
}
```

### Analysis Tools

#### AnalyzeCodeTool

```typescript
class AnalyzeCodeTool extends BaseTool {
  readonly name = 'analyze_code';
  readonly description = 'Analyze code structure and quality';
  readonly category = ToolCategory.ANALYSIS;
  readonly safetyLevel = SafetyLevel.SAFE;
  
  readonly parameters = {
    path: { type: 'string', description: 'Path to analyze' },
    language: { type: 'string', description: 'Programming language', optional: true },
    includeMetrics: { type: 'boolean', description: 'Include complexity metrics', default: false },
    includeTests: { type: 'boolean', description: 'Include test files', default: true },
    maxDepth: { type: 'number', description: 'Maximum directory depth', default: 10 }
  };
}
```

## Configuration Management

### ConfigManager

Configuration management utility.

```typescript
class ConfigManager {
  static async load(configPath?: string): Promise<AppConfig>;
  static async save(config: AppConfig, configPath?: string): Promise<void>;
  static validate(config: any): ValidationResult<AppConfig>;
  static merge(base: AppConfig, override: Partial<AppConfig>): AppConfig;
  static getDefaultConfig(): AppConfig;
  static getConfigPaths(): string[];
}
```

**Methods:**
- `load()` - Load configuration from file or defaults
- `save()` - Save configuration to file
- `validate()` - Validate configuration object
- `merge()` - Merge configuration objects
- `getDefaultConfig()` - Get default configuration
- `getConfigPaths()` - Get configuration search paths

### Environment Variables

Configuration can be overridden using environment variables:

```typescript
interface EnvironmentMappings {
  QWEN_CLAUDE_DEBUG: 'debug';
  QWEN_CLAUDE_LOG_LEVEL: 'logLevel';
  QWEN_CLAUDE_INTERACTIVE: 'interactive';
  QWEN_CLAUDE_DEFAULT_PROVIDER: 'defaultProvider';
  QWEN_CLAUDE_QWEN_URL: 'providers.0.endpoint';
  QWEN_CLAUDE_OPENROUTER_API_KEY: 'providers.1.auth.apiKey';
  QWEN_CLAUDE_PROXY: 'network.proxy';
  QWEN_CLAUDE_TIMEOUT: 'network.timeout';
  NO_COLOR: 'ui.colorOutput';
  FORCE_COLOR: 'ui.colorOutput';
}
```

## Utility Functions

### Result Type

Generic result type for error handling.

```typescript
type Result<T, E = Error> = 
  | { success: true; data: T }
  | { success: false; error: E };
```

**Usage:**
```typescript
function riskyOperation(): Result<string> {
  try {
    const result = performOperation();
    return { success: true, data: result };
  } catch (error) {
    return { success: false, error: error as Error };
  }
}
```

### Platform Detection

```typescript
interface PlatformInfo {
  os: 'linux' | 'darwin' | 'win32';
  arch: string;
  homeDir: string;
  configDir: string;
  dataDir: string;
  cacheDir: string;
}

function getPlatformInfo(): PlatformInfo;
```

### Path Utilities

```typescript
class PathUtils {
  static resolve(path: string, basePath?: string): string;
  static isAbsolute(path: string): boolean;
  static isWithinDirectory(path: string, directory: string): boolean;
  static ensureDirectory(path: string): Promise<void>;
  static getFileExtension(path: string): string;
  static getBasename(path: string): string;
  static getDirname(path: string): string;
}
```

### Validation Utilities

```typescript
class ValidationUtils {
  static isValidUrl(url: string): boolean;
  static isValidPath(path: string): boolean;
  static isValidApiKey(apiKey: string): boolean;
  static sanitizePath(path: string): string;
  static validateTimeout(timeout: number): boolean;
}
```

## Event System

### EventEmitter

Base event emitter for component communication.

```typescript
class EventEmitter<T extends Record<string, any[]>> {
  on<K extends keyof T>(event: K, listener: (...args: T[K]) => void): this;
  off<K extends keyof T>(event: K, listener: (...args: T[K]) => void): this;
  emit<K extends keyof T>(event: K, ...args: T[K]): boolean;
  once<K extends keyof T>(event: K, listener: (...args: T[K]) => void): this;
  removeAllListeners<K extends keyof T>(event?: K): this;
}
```

### Provider Events

```typescript
interface ProviderEvents {
  'initialized': [provider: BaseProvider];
  'model-list-updated': [models: ModelInfo[]];
  'request-start': [request: ChatCompletionRequest];
  'request-complete': [response: ChatCompletionResponse];
  'request-error': [error: Error];
  'stream-chunk': [chunk: ChatCompletionChunk];
}
```

### Tool Events

```typescript
interface ToolEvents {
  'execution-start': [tool: string, params: any];
  'execution-complete': [tool: string, result: ToolExecutionResult];
  'execution-error': [tool: string, error: Error];
  'safety-check': [tool: string, level: SafetyLevel];
  'confirmation-required': [tool: string, message: string];
}
```

## Error Handling

### Error Classes

```typescript
abstract class CLIError extends Error {
  abstract readonly code: string;
  abstract readonly category: string;
  
  constructor(message: string, public readonly cause?: Error) {
    super(message);
    this.name = this.constructor.name;
  }
}

class ConfigError extends CLIError {
  readonly code = 'CONFIG_ERROR';
  readonly category = 'configuration';
}

class ProviderError extends CLIError {
  readonly code = 'PROVIDER_ERROR';
  readonly category = 'provider';
}

class ToolError extends CLIError {
  readonly code = 'TOOL_ERROR';
  readonly category = 'tool';
}

class NetworkError extends CLIError {
  readonly code = 'NETWORK_ERROR';
  readonly category = 'network';
}
```

### Error Handling Utilities

```typescript
class ErrorHandler {
  static handle(error: unknown): void;
  static isRetryable(error: Error): boolean;
  static getErrorCategory(error: Error): string;
  static formatError(error: Error): string;
  static logError(error: Error, context?: any): void;
}
```

## CLI Framework

### Command System

```typescript
interface CommandDefinition {
  name: string;
  description: string;
  arguments?: ArgumentDefinition[];
  options?: OptionDefinition[];
  handler: CommandHandler;
}

interface ArgumentDefinition {
  name: string;
  description: string;
  required?: boolean;
  variadic?: boolean;
}

interface OptionDefinition {
  flags: string;
  description: string;
  default?: any;
  choices?: string[];
  required?: boolean;
}

type CommandHandler = (args: any[], options: any) => Promise<void>;
```

### CLIApplication

Main CLI application class.

```typescript
class CLIApplication {
  constructor(config?: AppConfig);
  
  async handleChatCommand(options: any): Promise<void>;
  async handleAskCommand(question: string, options: any): Promise<void>;
  async handleProviderListCommand(): Promise<void>;
  async handleProviderTestCommand(provider?: string): Promise<void>;
  async handleModelListCommand(options: any): Promise<void>;
  async handleToolRunCommand(name: string, options: any): Promise<void>;
  async handleToolListCommand(options: any): Promise<void>;
  async handleConfigShowCommand(): Promise<void>;
  async handleConfigInitCommand(options: any): Promise<void>;
  async handleVersionCommand(): Promise<void>;
  
  private formatOutput(data: any, format: string): string;
  private showSpinner(text: string): () => void;
  private handleError(error: Error): void;
}
```

This API reference provides comprehensive documentation for all public interfaces and classes in the Qwen Claude CLI. For implementation examples and usage patterns, see the other documentation files.