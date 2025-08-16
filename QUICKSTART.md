# Plato Quick Start Guide

## Installation

```bash
# Clone the repository
git clone https://github.com/anubissbe/plato.git
cd plato

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy config example
cp config.example.yaml config.yaml
# Edit config.yaml with your API keys (optional)
```

## Starting Plato

```bash
# Start the server
./start_plato.sh

# Or manually
uvicorn plato.server.api:app --host 0.0.0.0 --port 8080
```

## Using the Interactive CLI

```bash
# Start the CLI
./plato-cli

# Or
python plato_interactive.py
```

## Key Features

- **13 Embedded Tools**: No external dependencies required
- **Multi-Language Support**: Python, JavaScript, TypeScript, Go, Rust, Java
- **AI Providers**: Claude, GPT-4, Qwen (local), Gemini
- **Interactive CLI**: Rich terminal interface with project awareness

## Example Usage

In the CLI:
```
You: Write a hello world Python script and save it as hello.py
AI: [Creates the file with tool execution feedback]

You: Analyze the current project structure
AI: [Shows project analysis with file tree]

You: Find all functions in the codebase
AI: [Uses LSP tools to find and list functions]
```

## Configuration

Edit `config.yaml` to add your API keys:
```yaml
ai_providers:
  anthropic:
    api_key: "${ANTHROPIC_API_KEY}"
  openai:
    api_key: "${OPENAI_API_KEY}"
```

For local Qwen model, ensure it's running on port 8000.

## Documentation

- [README.md](README.md) - Full documentation
- [config.example.yaml](config.example.yaml) - Configuration template

## Support

Open an issue on [GitHub](https://github.com/anubissbe/plato/issues)