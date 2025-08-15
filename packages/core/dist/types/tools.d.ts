/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */
import { z } from "zod";
import type { JsonValue, ExecutionContext, CancellationToken, Result } from "./common.js";
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
    readonly pattern?: string;
    readonly minimum?: number;
    readonly maximum?: number;
    readonly items?: ToolParameter;
    readonly properties?: Record<string, ToolParameter>;
}
/**
 * Tool metadata
 */
export interface ToolMetadata {
    readonly name: string;
    readonly description: string;
    readonly version: string;
    readonly author?: string;
    readonly category: "file" | "shell" | "network" | "analysis" | "utility" | "system";
    readonly tags: ReadonlyArray<string>;
    readonly platforms: ReadonlyArray<"linux" | "windows" | "darwin" | "all">;
    readonly requiresAuth: boolean;
    readonly isDestructive: boolean;
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
    readonly duration: number;
    readonly metadata?: Record<string, JsonValue>;
}
/**
 * Tool execution options
 */
export interface ToolExecutionOptions {
    readonly timeout?: number;
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
    validateParameters(params: Record<string, JsonValue>): Result<Record<string, JsonValue>>;
    /**
     * Execute the tool
     */
    execute(params: Record<string, JsonValue>, context: ExecutionContext, options?: ToolExecutionOptions, cancellationToken?: CancellationToken): Promise<ToolExecutionResult>;
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
    execute(toolName: string, params: Record<string, JsonValue>, context: ExecutionContext, options?: ToolExecutionOptions & {
        safetyLevel?: SafetyLevel;
        allowDestructive?: boolean;
    }, cancellationToken?: CancellationToken): Promise<ToolExecutionResult>;
    /**
     * Dry run a tool to see what it would do
     */
    dryRun(toolName: string, params: Record<string, JsonValue>, context: ExecutionContext): Promise<string>;
    /**
     * Get confirmation for destructive operations
     */
    confirmDestructive(toolName: string, params: Record<string, JsonValue>): Promise<boolean>;
}
/**
 * Validation schemas
 */
export declare const ToolParameterSchema: z.ZodType<ToolParameter>;
export declare const ToolMetadataSchema: z.ZodObject<{
    name: z.ZodString;
    description: z.ZodString;
    version: z.ZodString;
    author: z.ZodOptional<z.ZodString>;
    category: z.ZodEnum<["file", "shell", "network", "analysis", "utility", "system"]>;
    tags: z.ZodArray<z.ZodString, "many">;
    platforms: z.ZodArray<z.ZodEnum<["linux", "windows", "darwin", "all"]>, "many">;
    requiresAuth: z.ZodBoolean;
    isDestructive: z.ZodBoolean;
    estimatedDuration: z.ZodOptional<z.ZodEnum<["instant", "fast", "slow", "very-slow"]>>;
}, "strip", z.ZodTypeAny, {
    name: string;
    description: string;
    version: string;
    category: "system" | "file" | "shell" | "network" | "analysis" | "utility";
    tags: string[];
    platforms: ("linux" | "windows" | "darwin" | "all")[];
    requiresAuth: boolean;
    isDestructive: boolean;
    author?: string | undefined;
    estimatedDuration?: "instant" | "fast" | "slow" | "very-slow" | undefined;
}, {
    name: string;
    description: string;
    version: string;
    category: "system" | "file" | "shell" | "network" | "analysis" | "utility";
    tags: string[];
    platforms: ("linux" | "windows" | "darwin" | "all")[];
    requiresAuth: boolean;
    isDestructive: boolean;
    author?: string | undefined;
    estimatedDuration?: "instant" | "fast" | "slow" | "very-slow" | undefined;
}>;
export declare const SafetyLevelSchema: z.ZodEnum<["safe", "cautious", "dangerous"]>;
//# sourceMappingURL=tools.d.ts.map