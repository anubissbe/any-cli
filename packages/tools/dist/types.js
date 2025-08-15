/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */
import { z } from "zod";
/**
 * Tool execution safety levels
 */
export var SafetyLevel;
(function (SafetyLevel) {
    // eslint-disable-next-line no-unused-vars
    SafetyLevel["SAFE"] = "safe";
    // eslint-disable-next-line no-unused-vars
    SafetyLevel["MODERATE"] = "moderate";
    // eslint-disable-next-line no-unused-vars
    SafetyLevel["DESTRUCTIVE"] = "destructive";
})(SafetyLevel || (SafetyLevel = {}));
/**
 * Tool categories
 */
export var ToolCategory;
(function (ToolCategory) {
    // eslint-disable-next-line no-unused-vars
    ToolCategory["FILE"] = "file";
    // eslint-disable-next-line no-unused-vars
    ToolCategory["SHELL"] = "shell";
    // eslint-disable-next-line no-unused-vars
    ToolCategory["ANALYSIS"] = "analysis";
    // eslint-disable-next-line no-unused-vars
    ToolCategory["NETWORK"] = "network";
    // eslint-disable-next-line no-unused-vars
    ToolCategory["SYSTEM"] = "system";
})(ToolCategory || (ToolCategory = {}));
/**
 * Tool parameter schema
 */
export const ToolParameterSchema = z.record(z.unknown());
/**
 * File operation parameters
 */
export const FileOperationParamsSchema = z.object({
    path: z.string(),
    content: z.string().optional(),
    encoding: z.string().optional().default("utf8"),
    mode: z.number().optional(),
});
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
/**
 * Code analysis parameters
 */
export const CodeAnalysisParamsSchema = z.object({
    path: z.string(),
    language: z.string().optional(),
    includeMetrics: z.boolean().optional().default(true),
    includeDependencies: z.boolean().optional().default(false),
});
//# sourceMappingURL=types.js.map