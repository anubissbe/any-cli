/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */
import { z } from "zod";
/**
 * Tool execution safety levels
 */
export declare enum SafetyLevel {
    SAFE = "safe",// Read-only operations
    MODERATE = "moderate",// Limited modifications
    DESTRUCTIVE = "destructive"
}
/**
 * Tool categories
 */
export declare enum ToolCategory {
    FILE = "file",
    SHELL = "shell",
    ANALYSIS = "analysis",
    NETWORK = "network",
    SYSTEM = "system"
}
/**
 * Tool parameter schema
 */
export declare const ToolParameterSchema: z.ZodRecord<z.ZodString, z.ZodUnknown>;
/**
 * Tool definition interface
 */
export interface ToolDefinition {
    name: string;
    description: string;
    category: ToolCategory;
    safetyLevel: SafetyLevel;
    parameters: Record<string, unknown>;
    execute: (params: Record<string, unknown>, context: ToolExecutionContext) => Promise<ToolExecutionResult>;
}
/**
 * Tool execution context
 */
export interface ToolExecutionContext {
    workingDirectory: string;
    safeMode: boolean;
    confirmDestructive: boolean;
    dryRun?: boolean;
    timeout?: number;
    environment?: Record<string, string>;
}
/**
 * Tool execution result
 */
export interface ToolExecutionResult {
    success: boolean;
    output?: string;
    error?: string;
    exitCode?: number;
    duration?: number;
    metadata?: Record<string, unknown>;
    warnings?: string[];
}
/**
 * Tool configuration
 */
export interface ToolConfig {
    safeMode: boolean;
    confirmDestructive: boolean;
    allowedCategories: ToolCategory[];
    timeout?: number;
    workingDirectory?: string;
}
/**
 * File operation parameters
 */
export declare const FileOperationParamsSchema: z.ZodObject<{
    path: z.ZodString;
    content: z.ZodOptional<z.ZodString>;
    encoding: z.ZodDefault<z.ZodOptional<z.ZodString>>;
    mode: z.ZodOptional<z.ZodNumber>;
}, "strip", z.ZodTypeAny, {
    path: string;
    encoding: string;
    content?: string | undefined;
    mode?: number | undefined;
}, {
    path: string;
    content?: string | undefined;
    encoding?: string | undefined;
    mode?: number | undefined;
}>;
export type FileOperationParams = z.infer<typeof FileOperationParamsSchema>;
/**
 * Shell command parameters
 */
export declare const ShellCommandParamsSchema: z.ZodObject<{
    command: z.ZodString;
    args: z.ZodDefault<z.ZodOptional<z.ZodArray<z.ZodString, "many">>>;
    cwd: z.ZodOptional<z.ZodString>;
    env: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodString>>;
    timeout: z.ZodDefault<z.ZodOptional<z.ZodNumber>>;
    shell: z.ZodDefault<z.ZodOptional<z.ZodBoolean>>;
}, "strip", z.ZodTypeAny, {
    shell: boolean;
    command: string;
    args: string[];
    timeout: number;
    cwd?: string | undefined;
    env?: Record<string, string> | undefined;
}, {
    command: string;
    shell?: boolean | undefined;
    args?: string[] | undefined;
    cwd?: string | undefined;
    env?: Record<string, string> | undefined;
    timeout?: number | undefined;
}>;
export type ShellCommandParams = z.infer<typeof ShellCommandParamsSchema>;
/**
 * Code analysis parameters
 */
export declare const CodeAnalysisParamsSchema: z.ZodObject<{
    path: z.ZodString;
    language: z.ZodOptional<z.ZodString>;
    includeMetrics: z.ZodDefault<z.ZodOptional<z.ZodBoolean>>;
    includeDependencies: z.ZodDefault<z.ZodOptional<z.ZodBoolean>>;
}, "strip", z.ZodTypeAny, {
    path: string;
    includeMetrics: boolean;
    includeDependencies: boolean;
    language?: string | undefined;
}, {
    path: string;
    language?: string | undefined;
    includeMetrics?: boolean | undefined;
    includeDependencies?: boolean | undefined;
}>;
export type CodeAnalysisParams = z.infer<typeof CodeAnalysisParamsSchema>;
//# sourceMappingURL=types.d.ts.map