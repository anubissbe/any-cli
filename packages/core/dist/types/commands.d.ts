/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */
import { z } from "zod";
import type { JsonValue, ExecutionContext, CancellationToken, Result } from "./common.js";
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
    readonly short?: string;
    readonly long: string;
}
/**
 * Command metadata
 */
export interface CommandMetadata {
    readonly name: string;
    readonly description: string;
    readonly usage: string;
    readonly examples: ReadonlyArray<string>;
    readonly category: "chat" | "file" | "config" | "tool" | "provider" | "utility";
    readonly aliases: ReadonlyArray<string>;
    readonly hidden: boolean;
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
    execute(parsed: ParsedCommand, context: ExecutionContext, cancellationToken?: CancellationToken): Promise<CommandResult>;
    /**
     * Get command help text
     */
    getHelp(): string;
    /**
     * Get command completion suggestions
     */
    getCompletions(partial: string, context: ExecutionContext): ReadonlyArray<string>;
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
    getCommandsByCategory(category: CommandMetadata["category"]): ReadonlyArray<Command>;
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
    getCompletions(input: string, context: ExecutionContext): ReadonlyArray<string>;
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
    dispatch(parsed: ParsedCommand, context: ExecutionContext, cancellationToken?: CancellationToken): Promise<CommandResult>;
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
export declare const CommandArgumentSchema: z.ZodObject<{
    name: z.ZodString;
    description: z.ZodString;
    type: z.ZodEnum<["string", "number", "boolean", "array"]>;
    required: z.ZodBoolean;
    default: z.ZodOptional<z.ZodUnknown>;
    choices: z.ZodOptional<z.ZodArray<z.ZodString, "many">>;
    alias: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    type: "string" | "number" | "boolean" | "array";
    name: string;
    description: string;
    required: boolean;
    default?: unknown;
    choices?: string[] | undefined;
    alias?: string | undefined;
}, {
    type: "string" | "number" | "boolean" | "array";
    name: string;
    description: string;
    required: boolean;
    default?: unknown;
    choices?: string[] | undefined;
    alias?: string | undefined;
}>;
export declare const CommandOptionSchema: z.ZodObject<{
    name: z.ZodString;
    description: z.ZodString;
    type: z.ZodEnum<["string", "number", "boolean", "array"]>;
    required: z.ZodBoolean;
    default: z.ZodOptional<z.ZodUnknown>;
    choices: z.ZodOptional<z.ZodArray<z.ZodString, "many">>;
    alias: z.ZodOptional<z.ZodString>;
} & {
    short: z.ZodOptional<z.ZodString>;
    long: z.ZodString;
}, "strip", z.ZodTypeAny, {
    type: "string" | "number" | "boolean" | "array";
    name: string;
    description: string;
    required: boolean;
    long: string;
    default?: unknown;
    choices?: string[] | undefined;
    alias?: string | undefined;
    short?: string | undefined;
}, {
    type: "string" | "number" | "boolean" | "array";
    name: string;
    description: string;
    required: boolean;
    long: string;
    default?: unknown;
    choices?: string[] | undefined;
    alias?: string | undefined;
    short?: string | undefined;
}>;
export declare const CommandMetadataSchema: z.ZodObject<{
    name: z.ZodString;
    description: z.ZodString;
    usage: z.ZodString;
    examples: z.ZodArray<z.ZodString, "many">;
    category: z.ZodEnum<["chat", "file", "config", "tool", "provider", "utility"]>;
    aliases: z.ZodArray<z.ZodString, "many">;
    hidden: z.ZodBoolean;
}, "strip", z.ZodTypeAny, {
    name: string;
    description: string;
    category: "tool" | "provider" | "file" | "utility" | "chat" | "config";
    usage: string;
    examples: string[];
    aliases: string[];
    hidden: boolean;
}, {
    name: string;
    description: string;
    category: "tool" | "provider" | "file" | "utility" | "chat" | "config";
    usage: string;
    examples: string[];
    aliases: string[];
    hidden: boolean;
}>;
export declare const ParsedCommandSchema: z.ZodObject<{
    command: z.ZodString;
    subcommand: z.ZodOptional<z.ZodString>;
    arguments: z.ZodRecord<z.ZodString, z.ZodUnknown>;
    options: z.ZodRecord<z.ZodString, z.ZodUnknown>;
    flags: z.ZodArray<z.ZodString, "many">;
    raw: z.ZodArray<z.ZodString, "many">;
}, "strip", z.ZodTypeAny, {
    options: Record<string, unknown>;
    command: string;
    arguments: Record<string, unknown>;
    flags: string[];
    raw: string[];
    subcommand?: string | undefined;
}, {
    options: Record<string, unknown>;
    command: string;
    arguments: Record<string, unknown>;
    flags: string[];
    raw: string[];
    subcommand?: string | undefined;
}>;
//# sourceMappingURL=commands.d.ts.map