# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

opencode is an AI coding agent built for the terminal, similar to Claude Code but 100% open source and provider-agnostic. It uses a client/server architecture with a focus on TUI (Terminal User Interface).

## Development Setup

### Prerequisites
- Bun (primary package manager)
- Golang 1.24.x (for some components)
- Node.js (for VS Code extension and web components)

### Running Locally
```bash
bun install
bun dev  # Runs packages/opencode/src/index.ts in development mode
```

## Common Commands

### Type Checking
```bash
bun run typecheck  # Run TypeScript type checking across all packages
```

### SDK Generation
```bash
bun run generate  # Generate SDK after modifying TypeScript API endpoints
```

### VS Code Extension Development
```bash
cd sdks/vscode
bun run compile     # Compile TypeScript and lint
bun run package     # Create production build
bun run check-types # Type checking only
bun run lint        # ESLint checking
```

## Architecture

### Monorepo Structure
The project uses Bun workspaces with the following key packages:

- **packages/opencode**: Core CLI application and server
  - MCP (Model Context Protocol) integration
  - LSP (Language Server Protocol) client/server
  - Tool implementations (bash, edit, grep, etc.)
  - Provider abstraction for multiple AI models
  - Session management and prompt handling

- **packages/sdk**: TypeScript SDK for API client
  - Auto-generated from OpenAPI specifications

- **packages/plugin**: Plugin system infrastructure

- **cloud/**: Cloud deployment components
  - **app**: Frontend Astro application  
  - **core**: Database models and business logic (Drizzle ORM)
  - **function**: Cloudflare Workers for API endpoints
  - **web**: Landing page and documentation site

- **sdks/vscode**: VS Code extension
  - Commands for opening opencode in terminal
  - Keybindings for quick access

- **github/**: GitHub Action integration

### Infrastructure
- Uses SST v3 for deployment to Cloudflare
- Database: SQL with Drizzle ORM migrations
- Authentication: OpenAuth integration
- Workers: Cloudflare Workers for serverless functions
- Durable Objects: For sync server functionality

### Key Technical Components

1. **Tool System**: Extensible tool registry in `packages/opencode/src/tool/`
   - Each tool has TypeScript implementation and text description
   - Tools include: bash, edit, glob, grep, ls, read, write, etc.

2. **Provider Abstraction**: Support for multiple AI providers
   - Located in `packages/opencode/src/provider/`
   - Handles model selection and transformation

3. **LSP Integration**: Language Server Protocol support
   - Client/server implementation in `packages/opencode/src/lsp/`
   - Provides code intelligence features

4. **MCP Support**: Model Context Protocol integration
   - Implementation in `packages/opencode/src/mcp/`

5. **Session Management**: Handles conversation state
   - Message handling and prompt templates in `packages/opencode/src/session/`

## Deployment

### SST Configuration
The project uses SST v3 with Cloudflare as the deployment target:
```bash
sst deploy --stage=<stage>  # Deploy to specific stage
```

### Environment Variables
- `STRIPE_SECRET_KEY`: For billing integration
- `GITHUB_APP_ID`: GitHub App integration
- `GITHUB_APP_PRIVATE_KEY`: GitHub App authentication

## Testing Notes
Currently, no automated test suites are configured. When implementing tests:
- Consider using Vitest or Jest for unit tests
- VS Code extension uses standard VS Code testing framework

## Code Style
- Prettier configuration: no semicolons, 120 character line width
- TypeScript for all new code
- Zod for runtime validation
- Hono for HTTP framework