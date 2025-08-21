# OpenCode Project Index

## Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Core Components](#core-components)
4. [Tools & Features](#tools--features)
5. [API Reference](#api-reference)
6. [Development](#development)
7. [Deployment](#deployment)
8. [Extensions](#extensions)

---

## Project Overview

**OpenCode** is an AI-powered coding agent built for the terminal with 20.4k+ GitHub stars. It provides a sophisticated Terminal User Interface (TUI) with client-server architecture, supporting 75+ LLM providers.

### Key Information
- **Repository**: sst/opencode
- **Language**: TypeScript (server), Bun runtime
- **Architecture**: Client-server model with REST API
- **License**: MIT
- **Package Manager**: Bun
- **Framework**: SST v3 (deployment), Hono (HTTP server)

### Installation Methods
```bash
# Quick install
curl -fsSL https://opencode.ai/install | bash

# Package managers
npm i -g opencode-ai@latest
brew install sst/tap/opencode
paru -S opencode-bin  # Arch Linux
```

---

## Architecture

### System Architecture
```
┌─────────────────────────────────────────┐
│           Terminal UI (TUI)              │
│         packages/opencode/               │
└─────────────────┬───────────────────────┘
                  │ REST API
                  │ Port 4096
┌─────────────────▼───────────────────────┐
│          Hono Server (TypeScript)        │
│      packages/opencode/src/server/       │
├─────────────────────────────────────────┤
│  • Session Management                    │
│  • Tool Registry                         │
│  • Provider Abstraction                  │
│  • LSP Integration                       │
│  • MCP Support                           │
└─────────────────────────────────────────┘
```

### Directory Structure
```
opencode/
├── packages/
│   ├── opencode/          # Core CLI & server
│   │   ├── src/
│   │   │   ├── agent/     # AI agent logic
│   │   │   ├── app/       # Application core
│   │   │   ├── auth/      # Authentication
│   │   │   ├── cli/       # CLI commands
│   │   │   ├── config/    # Configuration
│   │   │   ├── file/      # File operations
│   │   │   ├── lsp/       # Language Server Protocol
│   │   │   ├── mcp/       # Model Context Protocol
│   │   │   ├── provider/  # AI provider abstraction
│   │   │   ├── server/    # HTTP server & API
│   │   │   ├── session/   # Session management
│   │   │   ├── tool/      # Tool implementations
│   │   │   └── util/      # Utilities
│   │   └── package.json
│   ├── sdk/               # TypeScript SDK
│   ├── plugin/            # Plugin system
│   ├── function/          # Serverless functions
│   └── web/               # Documentation site
├── cloud/                 # Cloud infrastructure
│   ├── app/              # Frontend application
│   ├── core/             # Database & business logic
│   ├── function/         # Cloudflare Workers
│   └── web/              # Landing page
├── sdks/
│   └── vscode/           # VS Code extension
├── github/               # GitHub Action
└── infra/                # SST infrastructure
```

---

## Core Components

### 1. Session Management (`packages/opencode/src/session/`)
- Persistent conversation state
- Message history tracking
- Multi-session support
- Shareable session links

### 2. Tool System (`packages/opencode/src/tool/`)
Registered tools providing AI capabilities:

| Tool | ID | Description |
|------|-----|-------------|
| **Bash** | `bash` | Execute shell commands |
| **Edit** | `edit` | Modify files with string replacement |
| **Read** | `read` | Read file contents |
| **Write** | `write` | Create/overwrite files |
| **Grep** | `grep` | Search file contents with regex |
| **Glob** | `glob` | Find files by pattern |
| **List** | `ls` | List directory contents |
| **Patch** | `patch` | Apply unified diff patches |
| **WebFetch** | `webfetch` | Fetch and process web content |
| **TodoWrite** | `todowrite` | Manage task lists |
| **TodoRead** | `todoread` | Read task lists |
| **Task** | `task` | Execute complex multi-step tasks |

### 3. Provider System (`packages/opencode/src/provider/`)
- Supports 75+ AI providers (OpenAI, Anthropic, Google, etc.)
- Provider-agnostic interface
- Model selection and routing
- Token management

### 4. LSP Integration (`packages/opencode/src/lsp/`)
- Automatic language server detection
- Multi-language support
- Code intelligence features
- Diagnostics and hover information

### 5. MCP Support (`packages/opencode/src/mcp/`)
- Model Context Protocol implementation
- External tool integration
- Extended context management

---

## Tools & Features

### CLI Commands
```bash
opencode                    # Start interactive session
opencode chat "message"     # Send single message
opencode --model <model>    # Select AI model
opencode --provider <name>  # Select provider
opencode --config <path>    # Custom config file
opencode serve              # Start server mode
opencode upgrade            # Update to latest version
```

### Configuration
- **Config File**: `~/.opencode/config.json` or `opencode.json`
- **Environment Variables**: 
  - `OPENCODE_INSTALL_DIR`: Installation directory
  - `OPENCODE_API_KEY`: Default API key
  - Various provider-specific keys

### Custom Commands
Store custom automation in `.opencode/commands/`:
```markdown
# .opencode/commands/test.md
Run all tests with coverage
```

---

## API Reference

### Server Endpoints (Port 4096)

#### Core Endpoints
- `GET /doc` - OpenAPI documentation
- `GET /event` - SSE event stream
- `GET /health` - Health check
- `GET /config` - Get configuration

#### Session Management
- `GET /session` - List sessions
- `POST /session` - Create session
- `GET /session/:id` - Get session details
- `DELETE /session/:id` - Delete session
- `PATCH /session/:id` - Update session
- `POST /session/:id/share` - Share session

#### Message Operations
- `POST /session/:id/message` - Send message
- `POST /session/:id/message/:messageId/branch` - Branch conversation
- `DELETE /session/:id/message/:messageId` - Delete message

#### Provider & Model
- `GET /provider` - List providers
- `GET /provider/:id/model` - List models
- `POST /provider/:id/validate` - Validate credentials

#### File Operations
- `GET /file` - List files
- `POST /file/read` - Read file
- `POST /file/write` - Write file
- `POST /file/search` - Search files

#### Tool Operations
- `GET /tool` - List available tools
- `POST /tool/:id/execute` - Execute tool

---

## Development

### Prerequisites
- **Bun**: Latest version (primary runtime)
- **Node.js**: For certain components
- **TypeScript**: 5.8.2+

### Setup
```bash
# Clone repository
git clone https://github.com/sst/opencode.git
cd opencode

# Install dependencies
bun install

# Run development server
bun dev
```

### Key Scripts
```bash
bun dev          # Start development server
bun typecheck    # Run TypeScript checks
bun generate     # Generate SDK from API specs
```

### Project Configuration Files
- `package.json` - Root package configuration
- `tsconfig.json` - TypeScript configuration
- `sst.config.ts` - SST deployment configuration
- `bunfig.toml` - Bun configuration
- `opencode.json` - Application configuration

---

## Deployment

### Infrastructure Stack
- **Framework**: SST v3
- **Provider**: Cloudflare
- **Components**:
  - Cloudflare Workers (API)
  - Cloudflare Pages (Web)
  - Durable Objects (Sync)
  - R2 Storage (Files)

### Deployment Commands
```bash
sst deploy --stage=production
sst dev    # Local development with cloud resources
```

### Environment Stages
- `development` - Local development
- `staging` - Testing environment
- `production` - Live environment

---

## Extensions

### VS Code Extension (`sdks/vscode/`)
- **Commands**:
  - `opencode.openTerminal` - Open in terminal
  - `opencode.openNewTerminal` - Open in new tab
  - `opencode.addFilepathToTerminal` - Add file reference
- **Keybindings**:
  - `Cmd/Ctrl + Escape` - Open OpenCode
  - `Cmd/Ctrl + Shift + Escape` - New terminal
  - `Cmd/Ctrl + Alt + K` - Insert file reference

### GitHub Action (`github/`)
- Automated CI/CD integration
- Code review automation
- PR assistance

---

## Documentation Files

### Core Documentation
- `README.md` - Main project documentation
- `CLAUDE.md` - Claude Code guidance
- `AGENTS.md` - Agent configuration
- `STATS.md` - Project statistics

### Package Documentation
- `packages/opencode/README.md` - Core package docs
- `packages/web/README.md` - Web documentation
- `sdks/vscode/README.md` - VS Code extension docs
- `github/README.md` - GitHub Action docs

---

## Key Technologies

### Languages & Runtimes
- TypeScript (primary)
- Bun (runtime & package manager)
- Node.js (compatibility)

### Frameworks & Libraries
- **Hono** - HTTP server framework
- **SST v3** - Infrastructure as code
- **Zod** - Schema validation
- **Bubble Tea** - TUI framework (Go components)
- **Drizzle ORM** - Database abstraction

### AI & Language Support
- **75+ AI Providers** via unified interface
- **LSP** - Language Server Protocol
- **MCP** - Model Context Protocol
- **Tree-sitter** - Code parsing

### Development Tools
- **Prettier** - Code formatting
- **TypeScript** - Type checking
- **Bun test** - Testing framework
- **ESBuild** - Bundling

---

## Community & Support

- **GitHub**: [sst/opencode](https://github.com/sst/opencode)
- **Discord**: [opencode.ai/discord](https://opencode.ai/discord)
- **Documentation**: [opencode.ai/docs](https://opencode.ai/docs)
- **Issues**: GitHub Issues for bug reports and features

---

*Last Updated: Based on current repository state*
*Version: 0.5.13*