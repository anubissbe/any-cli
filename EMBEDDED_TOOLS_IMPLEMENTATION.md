# Embedded File Operations Tools for Plato

## Overview

Successfully implemented embedded file operation tools for Plato that enable Claude Code-like file operations without requiring external MCP servers. These tools are directly integrated into the Plato system and can be used by both the AI and users through the interactive CLI.

## Implementation Structure

### Core Components

1. **Base Classes** (`/opt/projects/plato/plato/core/embedded_tools/base.py`)
   - `EmbeddedTool`: Abstract base class for all tools
   - `ToolParameter`: Parameter definition with type validation
   - `ToolResult`: Standardized result format
   - `ToolError`: Custom exception for tool errors

2. **File Tools** (`/opt/projects/plato/plato/core/embedded_tools/file_tools.py`)
   - `ReadFileTool`: Read files with line number support
   - `WriteFileTool`: Write content to files
   - `EditFileTool`: Edit specific sections of files
   - `ListDirectoryTool`: List directory contents (flat or recursive)
   - `SearchFilesTool`: Search for patterns in files
   - `CreateDirectoryTool`: Create directories

3. **Tool Manager** (`/opt/projects/plato/plato/core/embedded_tools/tool_manager.py`)
   - Manages tool registration and execution
   - Parses natural language and JSON tool requests
   - Formats tool results for display
   - Provides schemas for AI integration

## Integration Points

### 1. Interactive CLI Integration

The tools are integrated into `/opt/projects/plato/plato/interactive_cli.py`:

- **New Commands Added:**
  - `/read <path>` - Read and display a file
  - `/write <path>` - Write content to a file
  - `/edit <path>` - Edit a file interactively
  - `/mkdir <path>` - Create a directory
  - `/tool <request>` - Execute a tool directly
  - `/tools` - List all available tools (embedded + MCP)

- **AI Integration:**
  - Tools are automatically included in chat context
  - AI can request tool execution through structured responses
  - Tool results are displayed in the chat interface

### 2. Server API Integration

The tools are exposed via the Plato server API (`/opt/projects/plato/plato/server/api.py`):

- **Endpoints:**
  - `GET /tools` - Lists both embedded and MCP tools
  - `POST /tools/embedded/{tool_name}` - Execute embedded tools via API

## Key Features

### 1. Claude Code-like Functionality
- **Line Numbers**: All file reads include line numbers (format: `6→content`)
- **Line Ranges**: Support for reading specific line ranges
- **Exact Editing**: Edit files by replacing exact content matches
- **Safe Operations**: Security checks prevent access outside project directories

### 2. Natural Language Support
The tool manager can parse natural language requests:
- "read file main.py"
- "list directory /tmp"
- "search for 'TODO' in src/"

### 3. JSON Tool Requests
Structured tool requests for precise control:
```json
{
  "tool": "WriteFileTool",
  "parameters": {
    "file_path": "/path/to/file.txt",
    "content": "File content here"
  }
}
```

### 4. Error Handling
- Comprehensive parameter validation
- Safe path checking (prevents access outside allowed directories)
- Graceful encoding fallbacks for different file types
- Detailed error messages for troubleshooting

## Security Features

### Path Safety
All tools implement `_is_safe_path()` which restricts access to:
- Current working directory
- User home directory
- `/opt/projects` directory
- `/tmp` directory

### Input Validation
- Type checking for all parameters
- Range validation for numeric inputs
- Pattern validation for string inputs
- Required parameter enforcement

## Usage Examples

### 1. Reading a File
```python
result = await tool_manager.execute_tool(
    "ReadFileTool",
    file_path="main.py",
    start_line=1,
    end_line=20
)
```

### 2. Writing a File
```python
result = await tool_manager.execute_tool(
    "WriteFileTool",
    file_path="config.json",
    content='{"key": "value"}'
)
```

### 3. Editing a File
```python
result = await tool_manager.execute_tool(
    "EditFileTool",
    file_path="README.md",
    old_content="old text",
    new_content="new text"
)
```

### 4. Searching Files
```python
result = await tool_manager.execute_tool(
    "SearchFilesTool",
    pattern="TODO",
    directory="./src",
    file_pattern="*.py"
)
```

## Testing

Two test scripts are provided:

1. **`test_embedded_tools.py`** - Unit tests for all tools
2. **`demo_embedded_tools.py`** - Interactive demo showing AI-like usage

Run tests:
```bash
python test_embedded_tools.py
python demo_embedded_tools.py
```

## Benefits

1. **No External Dependencies**: Works without MCP servers
2. **Fast Execution**: Direct Python implementation, no IPC overhead
3. **Full Integration**: Seamlessly integrated with Plato's AI and CLI
4. **Claude Code Compatibility**: Follows Claude Code's file operation patterns
5. **Extensible**: Easy to add new tools following the base class pattern

## Future Enhancements

Potential improvements:
1. Add git operations (status, diff, commit)
2. Add file move/rename operations
3. Add archive operations (zip, tar)
4. Add syntax highlighting for more file types
5. Add file watching/monitoring capabilities
6. Add batch operations for multiple files

## Conclusion

The embedded tools implementation successfully provides Claude Code-like file operations directly within Plato, enabling the AI to read, write, and manipulate files without requiring external MCP servers. This makes Plato more self-contained and efficient while maintaining full compatibility with the expected file operation patterns.