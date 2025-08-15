/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */
import { CLIError, ErrorCode } from "./base.js";
import type { JsonValue } from "../types/common.js";
/**
 * Base error for tool-related issues
 */
export declare class ToolError extends CLIError {
    readonly tool: string;
    constructor(message: string, tool: string, code?: ErrorCode, context?: Record<string, JsonValue>, cause?: Error);
}
/**
 * Error when tool is not found
 */
export declare class ToolNotFoundError extends ToolError {
    constructor(tool: string, context?: Record<string, JsonValue>, cause?: Error);
}
/**
 * Error when tool execution fails
 */
export declare class ToolExecutionError extends ToolError {
    readonly exitCode?: number;
    readonly stderr?: string;
    constructor(tool: string, message: string, exitCode?: number, stderr?: string, context?: Record<string, JsonValue>, cause?: Error);
}
/**
 * Error when tool parameters are invalid
 */
export declare class ToolInvalidParamsError extends ToolError {
    readonly invalidParams: ReadonlyArray<string>;
    constructor(tool: string, invalidParams: ReadonlyArray<string>, context?: Record<string, JsonValue>, cause?: Error);
}
/**
 * Error when tool access is denied
 */
export declare class ToolPermissionError extends ToolError {
    constructor(tool: string, resource?: string, context?: Record<string, JsonValue>, cause?: Error);
}
/**
 * Error when tool is not available on current platform
 */
export declare class ToolNotAvailableError extends ToolError {
    readonly platform: string;
    constructor(tool: string, platform: string, reason?: string, context?: Record<string, JsonValue>, cause?: Error);
}
/**
 * Error when tool times out
 */
export declare class ToolTimeoutError extends ToolError {
    readonly timeout: number;
    constructor(tool: string, timeout: number, context?: Record<string, JsonValue>, cause?: Error);
}
/**
 * Error when tool requires confirmation but none provided
 */
export declare class ToolConfirmationError extends ToolError {
    constructor(tool: string, action: string, context?: Record<string, JsonValue>, cause?: Error);
}
/**
 * Error when tool dependency is missing
 */
export declare class ToolDependencyError extends ToolError {
    readonly dependency: string;
    constructor(tool: string, dependency: string, context?: Record<string, JsonValue>, cause?: Error);
}
//# sourceMappingURL=tool.d.ts.map