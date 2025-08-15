/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */

import { Command } from "commander";
import chalk from "chalk";
import { CLIApplication } from "./app.js";

const VERSION = process.env.CLI_VERSION || "0.1.0";

/**
 * Main CLI entry point
 */
async function main(): Promise<void> {
  const program = new Command();

  program
    .name("qwen-claude")
    .description(
      "Advanced TypeScript CLI tool with Qwen3-Coder 30B and OpenRouter integration",
    )
    .version(VERSION);

  // Add global options
  program
    .option("-d, --debug", "enable debug mode")
    .option("-c, --config <path>", "path to configuration file")
    .option("--no-color", "disable colored output")
    .option("-v, --verbose", "verbose output");

  // Chat command
  program
    .command("chat")
    .description("Start interactive chat session")
    .option("-m, --model <model>", "model to use for chat")
    .option("-p, --provider <provider>", "provider to use")
    .option("-s, --system <message>", "system message")
    .option("--stream", "enable streaming responses")
    .action(async (options) => {
      const app = new CLIApplication();
      await app.handleChatCommand(options);
    });

  // Ask command (one-shot)
  program
    .command("ask")
    .description("Ask a single question")
    .argument("<question>", "question to ask")
    .option("-m, --model <model>", "model to use")
    .option("-p, --provider <provider>", "provider to use")
    .option("--stream", "enable streaming responses")
    .action(async (question, options) => {
      const app = new CLIApplication();
      await app.handleAskCommand(question, options);
    });

  // Provider management
  const providerCmd = program
    .command("provider")
    .description("Manage model providers");

  providerCmd
    .command("list")
    .description("List available providers")
    .action(async () => {
      const app = new CLIApplication();
      await app.handleProviderListCommand();
    });

  providerCmd
    .command("test")
    .description("Test provider connectivity")
    .argument("[provider]", "provider to test")
    .action(async (provider) => {
      const app = new CLIApplication();
      await app.handleProviderTestCommand(provider);
    });

  // Model management
  const modelCmd = program.command("model").description("Manage models");

  modelCmd
    .command("list")
    .description("List available models")
    .option("-p, --provider <provider>", "filter by provider")
    .action(async (options) => {
      const app = new CLIApplication();
      await app.handleModelListCommand(options);
    });

  // Tool execution
  const toolCmd = program.command("tool").description("Execute tools");

  toolCmd
    .command("run")
    .description("Run a tool")
    .argument("<name>", "tool name")
    .option("-p, --params <json>", "tool parameters as JSON")
    .option("--confirm", "confirm destructive operations")
    .option("--dry-run", "show what would be done without executing")
    .action(async (name, options) => {
      const app = new CLIApplication();
      await app.handleToolRunCommand(name, options);
    });

  toolCmd
    .command("list")
    .description("List available tools")
    .option("-c, --category <category>", "filter by category")
    .action(async (options) => {
      const app = new CLIApplication();
      await app.handleToolListCommand(options);
    });

  // Configuration management
  const configCmd = program
    .command("config")
    .description("Manage configuration");

  configCmd
    .command("show")
    .description("Show current configuration")
    .action(async () => {
      const app = new CLIApplication();
      await app.handleConfigShowCommand();
    });

  configCmd
    .command("init")
    .description("Initialize configuration")
    .option("--force", "overwrite existing configuration")
    .action(async (options) => {
      const app = new CLIApplication();
      await app.handleConfigInitCommand(options);
    });

  // Version command
  program
    .command("version")
    .description("Show version information")
    .action(async () => {
      const app = new CLIApplication();
      await app.handleVersionCommand();
    });

  // Parse command line arguments
  try {
    await program.parseAsync(process.argv);
  } catch (error) {
    console.error(
      chalk.red("Error:"),
      error instanceof Error ? error.message : String(error),
    );
    process.exit(1);
  }
}

// Handle unhandled rejections and exceptions
process.on("unhandledRejection", (reason) => {
  console.error(chalk.red("Unhandled rejection:"), reason);
  process.exit(1);
});

process.on("uncaughtException", (error) => {
  console.error(chalk.red("Uncaught exception:"), error);
  process.exit(1);
});

// Run main function
main().catch((error) => {
  console.error(chalk.red("Fatal error:"), error);
  process.exit(1);
});
