# Usage Examples

Practical examples and use cases for Qwen Claude CLI covering common workflows and advanced scenarios.

## Basic Usage Examples

### Interactive Chat Session

```bash
# Start basic interactive chat
qwen-claude chat

# Chat with specific model and streaming
qwen-claude chat --model qwen3-coder-30b --stream

# Chat with system message
qwen-claude chat --system "You are a helpful coding assistant specialized in TypeScript"

# Chat with specific provider
qwen-claude chat --provider openrouter --model "anthropic/claude-3-haiku"
```

**Sample Session:**
```
$ qwen-claude chat --model qwen3-coder-30b --stream
🤖 Qwen Claude CLI v0.1.0
Connected to: qwen-local (qwen3-coder-30b)
Streaming: enabled

You: How do I implement a binary search in TypeScript?