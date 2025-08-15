/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */

import { z } from "zod";
import type {
  JsonValue,
  ExecutionContext,
  CancellationToken,
  Result,
} from "./common.js";

/**
 * Command argument definition
 */
export interface CommandArgument {
  readonly name: string;
  readonly description: string;
  readonly type: "string" | "number" | "boolean" | "array";
  readonly required: boolean;
  readonly default?: JsonValue;
  readonly choices?: ReadonlyArray<string>;
  readonly alias?: string;
}

/**
 * Command option definition
 */
export interface CommandOption extends CommandArgument {
  readonly short?: string; // single character alias
  readonly long: string; // full name
}

/**
 * Command metadata
 */
export interface CommandMetadata {
  readonly name: string;
  readonly description: string;
  readonly usage: string;
  readonly examples: ReadonlyArray<string>;
  readonly category:
    | "chat"
    | "file"
    | "config"
    | "tool"
    | "provider"
    | "utility";
  readonly aliases: ReadonlyArray<string>;
  readonly hidden: boolean; // hide from help
}

/**
 * Parsed command arguments and options
 */
export interface ParsedCommand {
  readonly command: string;
  readonly subcommand?: string;
  readonly arguments: Record<string, JsonValue>;
  readonly options: Record<string, JsonValue>;
  readonly flags: ReadonlyArray<string>;
  readonly raw: ReadonlyArray<string>;
}

/**
 * Command execution result
 */
export interface CommandResult {
  readonly success: boolean;
  readonly output?: string;
  readonly error?: string;
  readonly exitCode: number;
  readonly metadata?: Record<string, JsonValue>;
}

/**
 * Command interface that all commands must implement
 */
export interface Command {
  readonly metadata: CommandMetadata;
  readonly arguments: ReadonlyArray<CommandArgument>;
  readonly options: ReadonlyArray<CommandOption>;

  /**
   * Validate command arguments and options
   */
  validate(parsed: ParsedCommand): Result<ParsedCommand>;

  /**
   * Execute the command
   */
  execute(
    parsed: ParsedCommand,
    context: ExecutionContext,
    cancellationToken?: CancellationToken,
  ): Promise<CommandResult>;

  /**
   * Get command help text
   */
  getHelp(): string;

  /**
   * Get command completion suggestions
   */
  getCompletions(
    partial: string,
    context: ExecutionContext,
  ): ReadonlyArray<string>;
}

/**
 * Command group for organizing related commands
 */
export interface CommandGroup {
  readonly name: string;
  readonly description: string;
  readonly commands: ReadonlyArray<Command>;
  readonly subgroups: ReadonlyArray<CommandGroup>;
}

/**
 * Command registry for managing available commands
 */
export interface CommandRegistry {
  /**
   * Register a command
   */
  register(command: Command): void;

  /**
   * Register a command group
   */
  registerGroup(group: CommandGroup): void;

  /**
   * Get command by name or alias
   */
  getCommand(name: string): Result<Command>;

  /**
   * Get all commands in a category
   */
  getCommandsByCategory(
    category: CommandMetadata["category"],
  ): ReadonlyArray<Command>;

  /**
   * Get all available commands
   */
  getAllCommands(): ReadonlyArray<Command>;

  /**
   * Search commands by name/description
   */
  searchCommands(query: string): ReadonlyArray<Command>;

  /**
   * Get command groups
   */
  getGroups(): ReadonlyArray<CommandGroup>;
}

/**
 * Command parser for parsing CLI input
 */
export interface CommandParser {
  /**
   * Parse command line arguments
   */
  parse(args: ReadonlyArray<string>): Result<ParsedCommand>;

  /**
   * Get completions for partial input
   */
  getCompletions(
    input: string,
    context: ExecutionContext,
  ): ReadonlyArray<string>;

  /**
   * Validate parsed command
   */
  validate(parsed: ParsedCommand): Result<ParsedCommand>;
}

/**
 * Command dispatcher for executing commands
 */
export interface CommandDispatcher {
  /**
   * Dispatch a parsed command to its handler
   */
  dispatch(
    parsed: ParsedCommand,
    context: ExecutionContext,
    cancellationToken?: CancellationToken,
  ): Promise<CommandResult>;

  /**
   * Check if command exists
   */
  hasCommand(name: string): boolean;

  /**
   * Get help for a command
   */
  getHelp(commandName?: string): string;
}

/**
 * Validation schemas
 */
export const CommandArgumentSchema = z.object({
  name: z.string(),
  description: z.string(),
  type: z.enum(["string", "number", "boolean", "array"]),
  required: z.boolean(),
  default: z.unknown().optional(),
  choices: z.array(z.string()).optional(),
  alias: z.string().optional(),
});

export const CommandOptionSchema = CommandArgumentSchema.extend({
  short: z.string().length(1).optional(),
  long: z.string(),
});

export const CommandMetadataSchema = z.object({
  name: z.string(),
  description: z.string(),
  usage: z.string(),
  examples: z.array(z.string()),
  category: z.enum(["chat", "file", "config", "tool", "provider", "utility"]),
  aliases: z.array(z.string()),
  hidden: z.boolean(),
});

export const ParsedCommandSchema = z.object({
  command: z.string(),
  subcommand: z.string().optional(),
  arguments: z.record(z.unknown()),
  options: z.record(z.unknown()),
  flags: z.array(z.string()),
  raw: z.array(z.string()),
});
