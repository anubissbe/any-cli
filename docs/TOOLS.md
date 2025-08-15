# Tool Usage Guide

Complete guide to using the built-in tools in Qwen Claude CLI for file operations, shell commands, and code analysis.

## Tool Overview

The CLI includes a comprehensive set of tools for common development and system administration tasks:

- **File Tools**: Read, write, and manage files and directories
- **Shell Tools**: Execute commands and scripts
- **Analysis Tools**: Analyze code structure and quality

## Tool Safety Levels

All tools are categorized by safety level to prevent accidental damage:

- **SAFE**: Read-only operations with no system impact
- **MODERATE**: Non-destructive modifications (create files/directories)
- **DESTRUCTIVE**: Operations that can modify or delete existing data

## File Tools

### read_file

Read contents of a file safely.

**Safety Level**: SAFE

**Parameters**:
- `path` (string, required): Path to the file to read
- `encoding` (string, optional): File encoding (default: utf8)

**Examples**:

```bash
# Read a text file
qwen-claude tool run read_file --params '{"path": "package.json"}'

# Read with specific encoding
qwen-claude tool run read_file --params '{"path": "data.txt", "encoding": "latin1"}'

# Interactive mode (will prompt for parameters)
qwen-claude tool run read_file
```

**Security Features**:
- Prevents access outside working directory
- Supports various text encodings
- Returns file metadata (size, modification time)

### write_file

Write content to a file (destructive operation).

**Safety Level**: DESTRUCTIVE

**Parameters**:
- `path` (string, required): Path to the file to write
- `content` (string, required): Content to write to the file
- `encoding` (string, optional): File encoding (default: utf8)
- `mode` (number, optional): File permissions (Unix only)

**Examples**:

```bash
# Write a simple file
qwen-claude tool run write_file --params '{
  "path": "hello.txt",
  "content": "Hello, World!"
}'

# Write with specific permissions
qwen-claude tool run write_file --params '{
  "path": "script.sh",
  "content": "#!/bin/bash\necho \"Hello\"",
  "mode": 755
}' --confirm

# Dry run to see what would happen
qwen-claude tool run write_file --params '{
  "path": "test.txt",
  "content": "Test content"
}' --dry-run
```

**Safety Features**:
- Confirms before overwriting existing files
- Creates parent directories automatically
- Prevents access outside working directory
- Respects safety level configuration

### list_directory

List contents of a directory with detailed information.

**Safety Level**: SAFE

**Parameters**:
- `path` (string, required): Path to the directory to list
- `includeHidden` (boolean, optional): Include hidden files (default: false)
- `recursive` (boolean, optional): List recursively (default: false)

**Examples**:

```bash
# List current directory
qwen-claude tool run list_directory --params '{"path": "."}'

# List with hidden files
qwen-claude tool run list_directory --params '{
  "path": "/home/user",
  "includeHidden": true
}'

# Recursive listing
qwen-claude tool run list_directory --params '{
  "path": "src",
  "recursive": true,
  "includeHidden": false
}'
```

**Output Format**:
```json
[
  {
    "name": "package.json",
    "type": "file",
    "size": 1024,
    "modified": "2024-01-15T10:30:00.000Z"
  },
  {
    "name": "src",
    "type": "directory",
    "modified": "2024-01-15T10:30:00.000Z"
  }
]
```

### create_directory

Create a directory and parent directories if needed.

**Safety Level**: MODERATE

**Parameters**:
- `path` (string, required): Path to the directory to create
- `mode` (number, optional): Directory permissions (Unix only)

**Examples**:

```bash
# Create a simple directory
qwen-claude tool run create_directory --params '{"path": "new-project"}'

# Create nested directories
qwen-claude tool run create_directory --params '{"path": "src/components/ui"}'

# Create with specific permissions
qwen-claude tool run create_directory --params '{
  "path": "logs",
  "mode": 755
}'
```

## Shell Tools

### execute_command

Execute shell commands with safety controls.

**Safety Level**: DESTRUCTIVE

**Parameters**:
- `command` (string, required): Command to execute
- `args` (array, optional): Command arguments
- `workingDirectory` (string, optional): Working directory for command
- `timeout` (number, optional): Execution timeout in milliseconds
- `env` (object, optional): Environment variables

**Examples**:

```bash
# Simple command execution
qwen-claude tool run execute_command --params '{
  "command": "ls",
  "args": ["-la"]
}' --confirm

# Execute with custom environment
qwen-claude tool run execute_command --params '{
  "command": "node",
  "args": ["--version"],
  "env": {"NODE_ENV": "development"}
}'

# Execute in specific directory
qwen-claude tool run execute_command --params '{
  "command": "npm",
  "args": ["install"],
  "workingDirectory": "/path/to/project"
}' --confirm

# Safe dry run
qwen-claude tool run execute_command --params '{
  "command": "rm",
  "args": ["-rf", "dangerous-folder"]
}' --dry-run
```

**Safety Features**:
- Command whitelist/blacklist support
- Execution timeout protection
- Working directory restrictions
- Environment variable isolation

### run_script

Execute script files with enhanced safety.

**Safety Level**: DESTRUCTIVE

**Parameters**:
- `scriptPath` (string, required): Path to the script file
- `interpreter` (string, optional): Script interpreter (auto-detected)
- `args` (array, optional): Script arguments
- `workingDirectory` (string, optional): Working directory
- `timeout` (number, optional): Execution timeout

**Examples**:

```bash
# Run a Python script
qwen-claude tool run run_script --params '{
  "scriptPath": "scripts/deploy.py",
  "args": ["--env", "staging"]
}' --confirm

# Run with specific interpreter
qwen-claude tool run run_script --params '{
  "scriptPath": "build.sh",
  "interpreter": "bash"
}'

# Run with timeout
qwen-claude tool run run_script --params '{
  "scriptPath": "long-running-task.py",
  "timeout": 300000
}' --confirm
```

## Analysis Tools

### analyze_code

Analyze code structure, quality, and complexity.

**Safety Level**: SAFE

**Parameters**:
- `path` (string, required): Path to file or directory to analyze
- `language` (string, optional): Programming language (auto-detected)
- `includeMetrics` (boolean, optional): Include complexity metrics
- `includeTests` (boolean, optional): Include test files in analysis
- `maxDepth` (number, optional): Maximum directory depth

**Examples**:

```bash
# Analyze a single file
qwen-claude tool run analyze_code --params '{
  "path": "src/main.ts",
  "includeMetrics": true
}'

# Analyze entire project
qwen-claude tool run analyze_code --params '{
  "path": ".",
  "includeTests": true,
  "maxDepth": 3
}'

# Language-specific analysis
qwen-claude tool run analyze_code --params '{
  "path": "backend/",
  "language": "python",
  "includeMetrics": true
}'
```

**Output Includes**:
- File count and size statistics
- Language distribution
- Code complexity metrics
- Dependency analysis
- Code quality indicators
- Security vulnerability hints

### generate_docs

Generate documentation from code comments and structure.

**Safety Level**: SAFE

**Parameters**:
- `path` (string, required): Path to code to document
- `format` (string, optional): Output format (markdown, html, json)
- `includePrivate` (boolean, optional): Include private members
- `outputPath` (string, optional): Where to save generated docs

**Examples**:

```bash
# Generate markdown documentation
qwen-claude tool run generate_docs --params '{
  "path": "src/",
  "format": "markdown",
  "outputPath": "docs/api.md"
}'

# Generate HTML documentation
qwen-claude tool run generate_docs --params '{
  "path": "lib/",
  "format": "html",
  "includePrivate": false
}'
```

### refactor_code

Analyze code and suggest refactoring improvements.

**Safety Level**: SAFE

**Parameters**:
- `path` (string, required): Path to code to analyze
- `rules` (array, optional): Specific refactoring rules to apply
- `severity` (string, optional): Minimum issue severity (info, warning, error)

**Examples**:

```bash
# Basic refactoring analysis
qwen-claude tool run refactor_code --params '{
  "path": "src/legacy-code.js"
}'

# Specific refactoring rules
qwen-claude tool run refactor_code --params '{
  "path": "src/",
  "rules": ["remove-unused-imports", "extract-functions"],
  "severity": "warning"
}'
```

## Tool Execution Modes

### Interactive Mode

When parameters are missing, tools enter interactive mode:

```bash
$ qwen-claude tool run read_file
? Enter file path: package.json
? Select encoding: utf8
Reading file: package.json...
✅ File read successfully (1,024 bytes)
```

### Batch Mode

Execute multiple tools in sequence:

```bash
# Using a script file
cat > tools.json << EOF
[
  {
    "tool": "list_directory",
    "params": {"path": "src", "recursive": true}
  },
  {
    "tool": "analyze_code",
    "params": {"path": "src", "includeMetrics": true}
  }
]
EOF

qwen-claude tool batch tools.json
```

### Pipeline Mode

Chain tool outputs:

```bash
# List files, then analyze each one
qwen-claude tool run list_directory --params '{"path": "src"}' | \
  jq -r '.[] | select(.type == "file") | .name' | \
  xargs -I {} qwen-claude tool run analyze_code --params '{"path": "{}"}'
```

## Tool Configuration

### Global Tool Settings

Configure tool behavior in your configuration file:

```yaml
tools:
  safetyLevel: "cautious"     # safe, cautious, moderate, permissive
  confirmDestructive: true    # Always confirm destructive operations
  timeout: 30000             # Default timeout (30 seconds)
  maxRetries: 3              # Maximum retry attempts
  dryRun: false              # Default to actual execution
  
  # Category-specific overrides
  categories:
    file:
      maxFileSize: 10485760   # 10MB limit
      allowedExtensions: [".txt", ".md", ".json", ".js", ".ts"]
      backupBeforeWrite: true  # Create backups
    
    shell:
      allowedCommands: ["ls", "cat", "grep", "git", "npm"]
      restrictedCommands: ["rm", "del", "format"]
      maxExecutionTime: 60000
      
    analysis:
      maxAnalysisDepth: 5
      includeNodeModules: false
      cacheDuration: 3600      # Cache results for 1 hour
```

### Safety Level Behavior

#### Safe Mode
- Only read operations allowed
- No file modifications
- No command execution

#### Cautious Mode (Default)
- Read operations allowed
- File creation allowed with confirmation
- Limited command execution with whitelist

#### Moderate Mode
- Most operations allowed
- Automatic confirmations for non-destructive operations
- Broader command execution permissions

#### Permissive Mode
- All operations allowed
- Minimal confirmations
- Full command execution capabilities

### Command Whitelisting

Configure allowed/restricted commands:

```yaml
tools:
  categories:
    shell:
      # Commands that are always allowed
      allowedCommands:
        - "ls"
        - "cat"
        - "grep"
        - "find"
        - "git"
        - "npm"
        - "node"
        - "python"
        - "pip"
        
      # Commands that are never allowed
      restrictedCommands:
        - "rm"
        - "del"
        - "format"
        - "shutdown"
        - "reboot"
        - "dd"
        
      # Pattern-based restrictions
      restrictedPatterns:
        - "rm -rf.*"
        - "sudo.*"
        - ".*>/dev/.*"
```

## Error Handling and Recovery

### Common Tool Errors

#### Permission Denied
```bash
❌ Error: Access denied: file outside working directory
💡 Solution: Use relative paths or configure allowed directories
```

#### Timeout Errors
```bash
❌ Error: Tool execution timed out after 30000ms
💡 Solution: Increase timeout or optimize operation
```

#### Safety Violations
```bash
❌ Error: Operation blocked by safety level 'cautious'
💡 Solution: Use --confirm flag or adjust safety level
```

### Recovery Strategies

#### Automatic Retry
```bash
# Tools automatically retry on transient failures
qwen-claude tool run execute_command --params '{
  "command": "flaky-script.sh"
}' --retries 5
```

#### Backup and Restore
```bash
# Create backup before destructive operations
qwen-claude tool run write_file --params '{
  "path": "important.txt",
  "content": "new content"
}' --backup

# Restore from backup if needed
qwen-claude tool restore important.txt.backup
```

## Advanced Tool Usage

### Custom Tool Parameters

Pass complex parameters using JSON:

```bash
qwen-claude tool run analyze_code --params '{
  "path": "src/",
  "options": {
    "includeMetrics": true,
    "rules": {
      "complexity": {"max": 10},
      "lineLength": {"max": 120},
      "naming": {"style": "camelCase"}
    },
    "exclude": ["*.test.js", "node_modules/"]
  }
}'
```

### Environment-specific Tool Execution

```bash
# Development environment
export QWEN_CLAUDE_TOOLS_SAFETY_LEVEL=permissive
qwen-claude tool run execute_command --params '{"command": "npm", "args": ["test"]}'

# Production environment
export QWEN_CLAUDE_TOOLS_SAFETY_LEVEL=safe
qwen-claude tool run execute_command --params '{"command": "npm", "args": ["test"]}' # Will fail safely
```

### Tool Composition

Combine multiple tools for complex workflows:

```bash
# Analyze project, generate report, and email results
qwen-claude tool run analyze_code --params '{"path": "."}' > analysis.json
qwen-claude tool run generate_docs --params '{"path": ".", "format": "html"}' > docs.html
qwen-claude tool run execute_command --params '{
  "command": "mail",
  "args": ["-s", "Code Analysis Results", "team@company.com"],
  "stdin": "analysis.json"
}'
```

## Tool Development

### Creating Custom Tools

Tools can be extended by implementing the `BaseTool` interface:

```typescript
// custom-tool.ts
import { BaseTool, ToolCategory, SafetyLevel } from '@qwen-claude/tools';

export class CustomTool extends BaseTool {
  readonly name = 'custom_operation';
  readonly description = 'Performs custom operation';
  readonly category = ToolCategory.CUSTOM;
  readonly safetyLevel = SafetyLevel.MODERATE;
  
  readonly parameters = {
    input: { type: 'string', description: 'Input parameter' },
    options: { type: 'object', description: 'Optional settings' }
  };
  
  async execute(params: any, context: ToolExecutionContext) {
    // Implementation here
    return this.createSuccessResult('Operation completed', { result: 'data' });
  }
}
```

### Tool Testing

Test tools in isolation:

```bash
# Test tool with dry run
qwen-claude tool run custom_operation --params '{"input": "test"}' --dry-run

# Test with verbose output
qwen-claude tool run custom_operation --params '{"input": "test"}' --verbose

# Test error handling
qwen-claude tool run custom_operation --params '{"invalid": "params"}'
```

For more information on extending the tool system, see the [Development Guide](./DEVELOPMENT.md).