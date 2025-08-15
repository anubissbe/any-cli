/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */

import { z } from "zod";

/**
 * Tool execution safety levels
 */
export enum SafetyLevel {
  // eslint-disable-next-line no-unused-vars
  SAFE = "safe", // Read-only operations
  // eslint-disable-next-line no-unused-vars
  MODERATE = "moderate", // Limited modifications
  // eslint-disable-next-line no-unused-vars
  DESTRUCTIVE = "destructive", // Potentially harmful operations
}

/**
 * Tool categories
 */
export enum ToolCategory {
  // eslint-disable-next-line no-unused-vars
  FILE = "file",
  // eslint-disable-next-line no-unused-vars
  SHELL = "shell",
  // eslint-disable-next-line no-unused-vars
  ANALYSIS = "analysis",
  // eslint-disable-next-line no-unused-vars
  NETWORK = "network",
  // eslint-disable-next-line no-unused-vars
  SYSTEM = "system",
}

/**
 * Tool parameter schema
 */
export const ToolParameterSchema = z.record(z.unknown());

/**
 * Tool definition interface
 */
export interface ToolDefinition {
  name: string;
  description: string;
  category: ToolCategory;
  safetyLevel: SafetyLevel;
  parameters: Record<string, unknown>;
  execute: (
    // eslint-disable-next-line no-unused-vars
    params: Record<string, unknown>,
    // eslint-disable-next-line no-unused-vars
    context: ToolExecutionContext,
  ) => Promise<ToolExecutionResult>;
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
export const FileOperationParamsSchema = z.object({
  path: z.string(),
  content: z.string().optional(),
  encoding: z.string().optional().default("utf8"),
  mode: z.number().optional(),
});

export type FileOperationParams = z.infer<typeof FileOperationParamsSchema>;

/**
 * Shell command parameters
 */
export const ShellCommandParamsSchema = z.object({
  command: z.string(),
  args: z.array(z.string()).optional().default([]),
  cwd: z.string().optional(),
  env: z.record(z.string()).optional(),
  timeout: z.number().optional().default(30000),
  shell: z.boolean().optional().default(true),
});

export type ShellCommandParams = z.infer<typeof ShellCommandParamsSchema>;

/**
 * Code analysis parameters
 */
export const CodeAnalysisParamsSchema = z.object({
  path: z.string(),
  language: z.string().optional(),
  includeMetrics: z.boolean().optional().default(true),
  includeDependencies: z.boolean().optional().default(false),
});

export type CodeAnalysisParams = z.infer<typeof CodeAnalysisParamsSchema>;
