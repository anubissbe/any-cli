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
 * Tool parameter definition
 */
export interface ToolParameter {
  readonly name: string;
  readonly type: "string" | "number" | "boolean" | "array" | "object";
  readonly description: string;
  readonly required: boolean;
  readonly default?: JsonValue;
  readonly enum?: ReadonlyArray<JsonValue>;
  readonly pattern?: string; // regex for string validation
  readonly minimum?: number; // for numbers
  readonly maximum?: number; // for numbers
  readonly items?: ToolParameter; // for arrays
  readonly properties?: Record<string, ToolParameter>; // for objects
}

/**
 * Tool metadata
 */
export interface ToolMetadata {
  readonly name: string;
  readonly description: string;
  readonly version: string;
  readonly author?: string;
  readonly category:
    | "file"
    | "shell"
    | "network"
    | "analysis"
    | "utility"
    | "system";
  readonly tags: ReadonlyArray<string>;
  readonly platforms: ReadonlyArray<"linux" | "windows" | "darwin" | "all">;
  readonly requiresAuth: boolean;
  readonly isDestructive: boolean; // requires confirmation
  readonly estimatedDuration?: "instant" | "fast" | "slow" | "very-slow";
}

/**
 * Tool execution result
 */
export interface ToolExecutionResult {
  readonly success: boolean;
  readonly output: string;
  readonly error?: string;
  readonly exitCode?: number;
  readonly duration: number; // milliseconds
  readonly metadata?: Record<string, JsonValue>;
}

/**
 * Tool execution options
 */
export interface ToolExecutionOptions {
  readonly timeout?: number; // milliseconds
  readonly workingDirectory?: string;
  readonly environment?: Record<string, string>;
  readonly confirmDestructive?: boolean;
  readonly dryRun?: boolean;
}

/**
 * Tool interface that all tools must implement
 */
export interface Tool {
  readonly metadata: ToolMetadata;
  readonly parameters: ReadonlyArray<ToolParameter>;

  /**
   * Validate tool parameters
   */
  validateParameters(
    params: Record<string, JsonValue>,
  ): Result<Record<string, JsonValue>>;

  /**
   * Execute the tool
   */
  execute(
    params: Record<string, JsonValue>,
    context: ExecutionContext,
    options?: ToolExecutionOptions,
    cancellationToken?: CancellationToken,
  ): Promise<ToolExecutionResult>;

  /**
   * Get tool help/documentation
   */
  getHelp(): string;

  /**
   * Check if tool is available on current platform
   */
  isAvailable(context: ExecutionContext): boolean;
}

/**
 * Tool factory for creating tool instances
 */
export interface ToolFactory {
  readonly name: string;
  readonly supportedCategories: ReadonlyArray<ToolMetadata["category"]>;

  create(config?: Record<string, JsonValue>): Result<Tool>;
  listAvailableTools(): ReadonlyArray<string>;
}

/**
 * Tool registry for managing available tools
 */
export interface ToolRegistry {
  /**
   * Register a tool factory
   */
  register(factory: ToolFactory): void;

  /**
   * Get tool by name
   */
  getTool(name: string): Result<Tool>;

  /**
   * Get all tools in a category
   */
  getToolsByCategory(category: ToolMetadata["category"]): ReadonlyArray<Tool>;

  /**
   * Get all available tools
   */
  getAllTools(): ReadonlyArray<Tool>;

  /**
   * Search tools by name/description
   */
  searchTools(query: string): ReadonlyArray<Tool>;

  /**
   * Validate tool exists and is available
   */
  validateTool(name: string, context: ExecutionContext): Result<Tool>;
}

/**
 * Tool execution safety levels
 */
export type SafetyLevel = "safe" | "cautious" | "dangerous";

/**
 * Tool executor for running tools with safety checks
 */
export interface ToolExecutor {
  /**
   * Execute a tool with safety checks
   */
  execute(
    toolName: string,
    params: Record<string, JsonValue>,
    context: ExecutionContext,
    options?: ToolExecutionOptions & {
      safetyLevel?: SafetyLevel;
      allowDestructive?: boolean;
    },
    cancellationToken?: CancellationToken,
  ): Promise<ToolExecutionResult>;

  /**
   * Dry run a tool to see what it would do
   */
  dryRun(
    toolName: string,
    params: Record<string, JsonValue>,
    context: ExecutionContext,
  ): Promise<string>;

  /**
   * Get confirmation for destructive operations
   */
  confirmDestructive(
    toolName: string,
    params: Record<string, JsonValue>,
  ): Promise<boolean>;
}

/**
 * Validation schemas
 */
export const ToolParameterSchema: z.ZodType<ToolParameter> = z.lazy(() =>
  z.object({
    name: z.string(),
    type: z.enum(["string", "number", "boolean", "array", "object"]),
    description: z.string(),
    required: z.boolean(),
    default: z
      .union([z.string(), z.number(), z.boolean(), z.null()])
      .optional(),
    enum: z
      .array(z.union([z.string(), z.number(), z.boolean(), z.null()]))
      .optional(),
    pattern: z.string().optional(),
    minimum: z.number().optional(),
    maximum: z.number().optional(),
    items: ToolParameterSchema.optional(),
    properties: z.record(ToolParameterSchema).optional(),
  }),
);

export const ToolMetadataSchema = z.object({
  name: z.string(),
  description: z.string(),
  version: z.string(),
  author: z.string().optional(),
  category: z.enum([
    "file",
    "shell",
    "network",
    "analysis",
    "utility",
    "system",
  ]),
  tags: z.array(z.string()),
  platforms: z.array(z.enum(["linux", "windows", "darwin", "all"])),
  requiresAuth: z.boolean(),
  isDestructive: z.boolean(),
  estimatedDuration: z
    .enum(["instant", "fast", "slow", "very-slow"])
    .optional(),
});

export const SafetyLevelSchema = z.enum(["safe", "cautious", "dangerous"]);
