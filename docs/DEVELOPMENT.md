# Development Guide

Comprehensive guide for contributing to and extending Qwen Claude CLI.

## Project Overview

Qwen Claude CLI is built with modern TypeScript and follows a modular architecture:

- **Monorepo Structure**: Multiple packages with clear separation of concerns
- **ESM Modules**: Native ES modules with Node.js 20+ support
- **Type Safety**: Full TypeScript coverage with strict type checking
- **Bundling**: ESBuild for fast, optimized bundling
- **Testing**: Vitest for unit and integration testing

## Architecture

### Package Structure

```
qwen-claude-cli/
├── packages/
│   ├── cli/              # CLI entry point and command handlers
│   ├── core/             # Core types, interfaces, and configuration
│   ├── providers/        # Model provider implementations
│   ├── tools/            # Tool execution framework
│   └── utils/            # Shared utilities
├── scripts/              # Build and development scripts
├── docs/                 # Documentation
└── bundle/               # Compiled bundle output
```

### Core Components

#### CLI Package (`packages/cli/`)
- Command-line interface implementation
- Command parsing and routing
- User interaction handling

#### Core Package (`packages/core/`)
- Type definitions and interfaces
- Configuration schema and defaults
- Error handling classes
- Common utilities

#### Providers Package (`packages/providers/`)
- Abstract provider base classes
- Qwen local provider implementation
- OpenRouter provider implementation
- Provider registry and management

#### Tools Package (`packages/tools/`)
- Tool execution framework
- Built-in tools (file, shell, analysis)
- Safety and permission system
- Tool registry

#### Utils Package (`packages/utils/`)
- Platform detection utilities
- Configuration management
- Path utilities
- Validation helpers

## Development Setup

### Prerequisites

- Node.js 20.0.0 or higher
- npm 10.0.0 or higher
- Git
- VS Code (recommended) or similar editor

### Initial Setup

```bash
# Clone the repository
git clone https://github.com/your-org/qwen-claude-cli.git
cd qwen-claude-cli

# Install dependencies
npm install

# Build all packages
npm run build

# Link for local development
npm link

# Verify setup
qwen-claude --version
```

### Development Workflow

```bash
# Start development mode (watches for changes)
npm run dev

# Run tests
npm test

# Run tests with coverage
npm run test:coverage

# Run tests in watch mode
npm run test:watch

# Lint code
npm run lint

# Fix linting issues
npm run lint:fix

# Format code
npm run format

# Type checking
npm run typecheck

# Build for production
npm run build

# Create bundle
npm run bundle

# Clean build artifacts
npm run clean
```

### Package Scripts

Each package has its own scripts for isolated development:

```bash
# Work on specific package
cd packages/providers
npm run build
npm run test
npm run dev

# Run package-specific commands from root
npm run build --workspace=packages/core
npm run test --workspace=packages/tools
```

## Code Organization

### TypeScript Configuration

The project uses a strict TypeScript configuration with:

- **Strict Mode**: All strict type checking options enabled
- **ES2022 Target**: Modern JavaScript features
- **ESM Modules**: Native ES module support
- **Path Mapping**: Workspace package aliases
- **Declaration Generation**: Full type declaration output

### Import/Export Conventions

```typescript
// Use explicit imports/exports
import { ProviderFactory } from '@qwen-claude/providers';
import type { ModelInfo } from '@qwen-claude/core';

// Prefer named exports over default exports
export { QwenProvider } from './qwen-provider.js';
export type { QwenConfig } from './types.js';

// Use index files for package exports
export * from './provider.js';
export * from './factory.js';
export type * from './types.js';
```

### File Extensions

- Use `.ts` for TypeScript source files
- Use `.js` extensions in import statements (ESM requirement)
- Use `.d.ts` for type declaration files
- Use `.test.ts` for test files

## Adding New Features

### Creating a New Provider

1. **Define Provider Interface**

```typescript
// packages/providers/src/custom/types.ts
export interface CustomProviderConfig extends ProviderConfig {
  custom: {
    apiVersion: string;
    region?: string;
  };
}
```

2. **Implement Provider Class**

```typescript
// packages/providers/src/custom/custom-provider.ts
import { HttpProvider } from '../base/http-provider.js';
import type { CustomProviderConfig } from './types.js';

export class CustomProvider extends HttpProvider {
  constructor(config: CustomProviderConfig) {
    super(config);
  }

  protected async doInitialize(): Promise<void> {
    // Initialize provider
  }

  public async getModels(): Promise<Result<ReadonlyArray<ModelInfo>>> {
    // Implement model listing
  }

  public async chatCompletion(
    request: ChatCompletionRequest
  ): Promise<Result<ChatCompletionResponse>> {
    // Implement chat completion
  }
}
```

3. **Create Provider Factory**

```typescript
// packages/providers/src/custom/custom-factory.ts
import { ProviderFactory } from '../base/provider-factory.js';
import { CustomProvider } from './custom-provider.js';

export class CustomProviderFactory extends ProviderFactory {
  create(config: ProviderConfig): CustomProvider {
    return new CustomProvider(config as CustomProviderConfig);
  }
}
```

4. **Register Provider**

```typescript
// packages/providers/src/registry.ts
import { CustomProviderFactory } from './custom/custom-factory.js';

export const PROVIDER_FACTORIES = {
  // ... existing providers
  custom: new CustomProviderFactory(),
} as const;
```

5. **Add Tests**

```typescript
// packages/providers/src/custom/custom-provider.test.ts
import { describe, it, expect } from 'vitest';
import { CustomProvider } from './custom-provider.js';

describe('CustomProvider', () => {
  it('should create provider instance', () => {
    const config = {
      name: 'custom',
      type: 'remote' as const,
      endpoint: 'https://api.custom.com/v1',
      // ... other config
    };
    
    const provider = new CustomProvider(config);
    expect(provider.name).toBe('custom');
  });
});
```

### Creating a New Tool

1. **Define Tool Interface**

```typescript
// packages/tools/src/custom-tool.ts
import { BaseTool } from './base-tool.js';
import { ToolCategory, SafetyLevel } from './types.js';
import type { ToolExecutionContext, ToolExecutionResult } from './types.js';

export class CustomTool extends BaseTool {
  readonly name = 'custom_operation';
  readonly description = 'Performs custom operation';
  readonly category = ToolCategory.CUSTOM;
  readonly safetyLevel = SafetyLevel.MODERATE;
  
  readonly parameters = {
    input: { type: 'string', description: 'Input parameter' },
    options: { type: 'object', description: 'Optional settings' }
  };

  async execute(
    params: Record<string, any>,
    context: ToolExecutionContext
  ): Promise<ToolExecutionResult> {
    const { input, options } = this.validateParameters(params, {
      input: z.string(),
      options: z.object({}).optional()
    });

    if (context.dryRun) {
      return this.createDryRunResult(`Would perform custom operation on: ${input}`);
    }

    try {
      // Implement tool logic
      const result = await this.performCustomOperation(input, options);
      
      return this.createSuccessResult('Custom operation completed', {
        result,
        input,
        timestamp: new Date()
      });
    } catch (error) {
      return this.createErrorResult(
        `Custom operation failed: ${error instanceof Error ? error.message : String(error)}`
      );
    }
  }

  private async performCustomOperation(input: string, options?: any): Promise<any> {
    // Implement custom logic
    return { processed: input, ...options };
  }
}
```

2. **Register Tool**

```typescript
// packages/tools/src/registry.ts
import { CustomTool } from './custom-tool.js';

export const DEFAULT_TOOLS = [
  // ... existing tools
  new CustomTool(),
] as const;
```

3. **Add Tests**

```typescript
// packages/tools/src/custom-tool.test.ts
import { describe, it, expect } from 'vitest';
import { CustomTool } from './custom-tool.js';

describe('CustomTool', () => {
  const tool = new CustomTool();
  const mockContext = {
    workingDirectory: '/test',
    dryRun: false,
    confirm: async () => true,
    safetyLevel: 'moderate' as const
  };

  it('should execute successfully', async () => {
    const result = await tool.execute(
      { input: 'test' },
      mockContext
    );

    expect(result.success).toBe(true);
    expect(result.data).toContain('test');
  });
});
```

### Adding CLI Commands

1. **Add Command Definition**

```typescript
// packages/cli/src/commands/custom-command.ts
import { Command } from 'commander';
import { CLIApplication } from '../app.js';

export function addCustomCommand(program: Command, app: CLIApplication): void {
  const customCmd = program
    .command('custom')
    .description('Custom command operations');

  customCmd
    .command('operation')
    .description('Perform custom operation')
    .argument('<input>', 'Input for operation')
    .option('-o, --output <path>', 'Output path')
    .option('--format <format>', 'Output format', 'json')
    .action(async (input, options) => {
      await app.handleCustomCommand(input, options);
    });
}
```

2. **Add Command Handler**

```typescript
// packages/cli/src/app.ts
export class CLIApplication {
  // ... existing methods

  async handleCustomCommand(input: string, options: any): Promise<void> {
    try {
      console.log(chalk.blue('🔧 Performing custom operation...'));
      
      // Implement command logic
      const result = await this.performCustomOperation(input, options);
      
      console.log(chalk.green('✅ Custom operation completed'));
      console.log(JSON.stringify(result, null, 2));
    } catch (error) {
      console.error(chalk.red('❌ Custom operation failed:'), error);
      process.exit(1);
    }
  }
}
```

3. **Register Command**

```typescript
// packages/cli/src/main.ts
import { addCustomCommand } from './commands/custom-command.js';

async function main(): Promise<void> {
  const program = new Command();
  const app = new CLIApplication();

  // ... existing commands
  addCustomCommand(program, app);

  await program.parseAsync(process.argv);
}
```

## Testing

### Testing Strategy

- **Unit Tests**: Individual functions and classes
- **Integration Tests**: Component interactions
- **End-to-End Tests**: Full CLI workflows
- **Snapshot Tests**: Command output verification

### Testing Setup

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: ['node_modules/', 'dist/', '**/*.test.ts']
    }
  }
});
```

### Test Examples

#### Unit Test

```typescript
// packages/core/src/config/schema.test.ts
import { describe, it, expect } from 'vitest';
import { validateConfig } from './schema.js';

describe('Config Schema', () => {
  it('should validate valid config', () => {
    const config = {
      version: '0.1.0',
      defaultProvider: 'qwen-local',
      providers: [{
        name: 'qwen-local',
        type: 'local',
        priority: 1,
        enabled: true,
        endpoint: 'http://localhost:8000/v1'
      }]
    };

    const result = validateConfig(config);
    expect(result.success).toBe(true);
  });

  it('should reject invalid config', () => {
    const config = { invalid: true };
    const result = validateConfig(config);
    expect(result.success).toBe(false);
  });
});
```

#### Integration Test

```typescript
// packages/providers/src/qwen/qwen-provider.integration.test.ts
import { describe, it, expect, beforeAll } from 'vitest';
import { QwenProvider } from './qwen-provider.js';

describe('QwenProvider Integration', () => {
  let provider: QwenProvider;

  beforeAll(async () => {
    provider = new QwenProvider({
      name: 'qwen-test',
      type: 'local',
      endpoint: process.env.QWEN_TEST_URL || 'http://localhost:8000/v1'
    });
    await provider.initialize();
  });

  it('should get models', async () => {
    const result = await provider.getModels();
    expect(result.success).toBe(true);
    expect(result.data).toBeInstanceOf(Array);
  });
});
```

#### CLI Test

```typescript
// packages/cli/src/app.test.ts
import { describe, it, expect } from 'vitest';
import { spawn } from 'child_process';

describe('CLI Integration', () => {
  it('should show version', async () => {
    const child = spawn('node', ['dist/qwen-claude.js', '--version']);
    
    let output = '';
    child.stdout.on('data', (data) => {
      output += data.toString();
    });

    await new Promise((resolve) => {
      child.on('close', resolve);
    });

    expect(output).toMatch(/^\d+\.\d+\.\d+/);
  });
});
```

### Mock Setup

```typescript
// packages/providers/src/__mocks__/http-provider.ts
export class MockHttpProvider {
  async makeRequest(options: any) {
    return {
      success: true,
      data: { mocked: true }
    };
  }
}
```

## Code Quality

### ESLint Configuration

```javascript
// eslint.config.js
import eslint from '@eslint/js';
import tseslint from 'typescript-eslint';
import prettier from 'eslint-config-prettier';

export default tseslint.config(
  eslint.configs.recommended,
  ...tseslint.configs.recommendedTypeChecked,
  prettier,
  {
    languageOptions: {
      parserOptions: {
        project: true,
        tsconfigRootDir: import.meta.dirname,
      },
    },
    rules: {
      '@typescript-eslint/no-unused-vars': 'error',
      '@typescript-eslint/no-explicit-any': 'warn',
      '@typescript-eslint/prefer-readonly': 'error',
      'prefer-const': 'error',
      'no-var': 'error'
    }
  }
);
```

### Prettier Configuration

```javascript
// prettier.config.js
export default {
  semi: true,
  trailingComma: 'es5',
  singleQuote: true,
  printWidth: 80,
  tabWidth: 2,
  useTabs: false
};
```

### Pre-commit Hooks

```bash
# .husky/pre-commit
#!/usr/bin/env sh
. "$(dirname -- "$0")/_/husky.sh"

npm run lint
npm run typecheck
npm run test
```

## Build System

### ESBuild Configuration

```javascript
// esbuild.config.js
import esbuild from 'esbuild';

await esbuild.build({
  entryPoints: ['packages/cli/index.ts'],
  bundle: true,
  outfile: 'bundle/qwen-claude.js',
  platform: 'node',
  format: 'esm',
  target: 'node20',
  external: ['fs', 'path', 'os'],
  alias: {
    '@qwen-claude/core': './packages/core/src',
    '@qwen-claude/providers': './packages/providers/src',
    '@qwen-claude/tools': './packages/tools/src',
    '@qwen-claude/utils': './packages/utils/src',
  },
  minify: process.env.NODE_ENV === 'production',
  sourcemap: process.env.NODE_ENV !== 'production'
});
```

### Build Scripts

```javascript
// scripts/build.js
import { build } from 'esbuild';
import { readdir } from 'fs/promises';

async function buildPackages() {
  const packages = await readdir('packages');
  
  for (const pkg of packages) {
    console.log(`Building ${pkg}...`);
    await build({
      entryPoints: [`packages/${pkg}/src/index.ts`],
      outdir: `packages/${pkg}/dist`,
      format: 'esm',
      platform: 'node',
      target: 'node20'
    });
  }
}

buildPackages().catch(console.error);
```

## Documentation

### API Documentation

Use TSDoc comments for API documentation:

```typescript
/**
 * Represents a model provider for AI services.
 * 
 * @example
 * ```typescript
 * const provider = new QwenProvider(config);
 * await provider.initialize();
 * const models = await provider.getModels();
 * ```
 */
export abstract class BaseProvider {
  /**
   * Initialize the provider with the given configuration.
   * 
   * @param config - Provider configuration
   * @throws {ProviderError} When initialization fails
   */
  abstract initialize(config: ProviderConfig): Promise<void>;

  /**
   * Get available models from this provider.
   * 
   * @returns Promise resolving to list of available models
   */
  abstract getModels(): Promise<Result<ReadonlyArray<ModelInfo>>>;
}
```

### README Templates

Use consistent README structure for packages:

```markdown
# @qwen-claude/package-name

Brief description of the package.

## Installation

\`\`\`bash
npm install @qwen-claude/package-name
\`\`\`

## Usage

\`\`\`typescript
import { ExampleClass } from '@qwen-claude/package-name';

const instance = new ExampleClass();
\`\`\`

## API Reference

### Classes

#### ExampleClass

Description of the class.

## License

MIT
```

## Release Process

### Version Management

```bash
# Update version
npm version patch|minor|major

# Update all package versions
npm run version:update

# Generate changelog
npm run changelog

# Build and test
npm run build
npm test

# Create bundle
npm run bundle

# Commit changes
git add .
git commit -m "chore: release v$(npm version --json | jq -r '.version')"

# Tag release
git tag "v$(npm version --json | jq -r '.version')"

# Push changes
git push origin main --tags
```

### Publishing

```bash
# Publish to npm
npm publish --access public

# Publish packages
npm run publish:packages

# Create GitHub release
gh release create "v$(npm version --json | jq -r '.version')" \
  --title "Release v$(npm version --json | jq -r '.version')" \
  --notes-file CHANGELOG.md \
  bundle/qwen-claude.js
```

## Contributing Guidelines

### Pull Request Process

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make changes following coding standards
4. Add tests for new functionality
5. Ensure all tests pass: `npm test`
6. Update documentation as needed
7. Commit using conventional commits: `feat: add new feature`
8. Push to your fork: `git push origin feature/my-feature`
9. Create a pull request

### Commit Message Format

Follow [Conventional Commits](https://conventionalcommits.org/):

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Build process or auxiliary tool changes

### Code Review Checklist

- [ ] Code follows project style guidelines
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] No breaking changes (or properly documented)
- [ ] Performance impact considered
- [ ] Security implications reviewed
- [ ] Accessibility considerations addressed

For more detailed contribution guidelines, see [CONTRIBUTING.md](../CONTRIBUTING.md).