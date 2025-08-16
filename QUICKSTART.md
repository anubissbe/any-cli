# Plato AI - Quick Start Guide

## 🚀 Start Using Plato in 30 Seconds

### 1. Start the Interactive CLI
```bash
cd /opt/projects/plato
./plato-cli
```

### 2. Try These Commands

#### Ask AI to write a file:
```
You: Create a Python script called hello.py that prints "Hello from Plato!"
```

#### Read a file:
```
You: Show me the README.md file
```

#### Search for code:
```
You: Find all TODO comments in the project
```

#### Get help:
```
/help     # Show all commands
/tools    # List available tools (13 embedded)
/model    # Check current AI model
```

## 💡 What Plato Can Do

### File Operations (Like Claude Code!)
- ✅ **Read files** - "Show me config.py"
- ✅ **Write files** - "Create a test.py file"
- ✅ **Edit files** - "Change DEBUG to True in settings.py"
- ✅ **Search files** - "Find all imports of numpy"
- ✅ **List directories** - "What files are in src/"
- ✅ **Create directories** - "Make a tests folder"

### Code Analysis
- ✅ **Find symbols** - "What classes are in models.py?"
- ✅ **Find references** - "Where is UserModel used?"
- ✅ **Get diagnostics** - "Check main.py for errors"
- ✅ **Code completion** - "What methods does this class have?"

## 🎯 Examples

### Create a Complete Script
```
You: Create a fibonacci.py script with a recursive fibonacci function and a main function that tests it
AI: I'll create that script for you.
[Creates file with complete implementation]
```

### Analyze Existing Code
```
You: What's the structure of the database module?
AI: Let me analyze the database module for you.
[Shows classes, functions, and relationships]
```

### Fix Code Issues
```
You: Find and fix any syntax errors in my script.py
AI: I'll check for errors and fix them.
[Identifies issues and corrects them]
```

## 🔧 Advanced Usage

### Direct Tool Execution
```bash
# Use a specific tool directly
/tool ReadFileTool main.py

# With JSON parameters
/tool {"tool": "WriteFileTool", "parameters": {"file_path": "test.txt", "content": "Hello"}}
```

### Natural Language Works Best
Just describe what you want naturally:
- "Create a REST API endpoint for user management"
- "Add error handling to the database connection"
- "Generate unit tests for the auth module"
- "Refactor this function to be more efficient"

## 📊 System Status

| Component | Status | Details |
|-----------|--------|---------|
| **Server** | ✅ Running | Port 8080 |
| **AI Model** | ✅ Connected | Qwen at 192.168.1.28:8000 |
| **Embedded Tools** | ✅ 13 Available | File ops + Code analysis |
| **Interactive CLI** | ✅ Ready | Natural language interface |

## 🛠️ Troubleshooting

### If CLI won't start:
```bash
# Make sure server is running
ps aux | grep plato

# Restart if needed
pkill -f plato.server.api
python -m plato.server.api &

# Then start CLI
python -m plato.interactive_cli
```

### If AI doesn't respond:
- Check server is running: `curl http://localhost:8080/health`
- Check Qwen is accessible: `curl http://192.168.1.28:8000/v1/models`
- View logs: `tail -f /tmp/plato_server.log`

### If tools don't work:
- List available tools: `/tools`
- Check tool schemas: `/tool <ToolName> --help`
- Try direct execution: `/tool ReadFileTool test.py`

## 🎉 You're Ready!

Plato is your AI coding assistant with:
- **13 embedded tools** - No external dependencies
- **Natural language** - Just describe what you want
- **File operations** - Read, write, edit like Claude Code
- **Code intelligence** - Analyze and understand code
- **Multi-provider** - Works with local and cloud AI models

Start with `./plato-cli` and let Plato help you code!

---
*Version 0.1.0 | Status: OPERATIONAL*