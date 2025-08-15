/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */
import type { JsonValue } from "../types/common.js";
/**
 * Error codes for different error types
 */
export declare enum ErrorCode {
    UNKNOWN = "UNKNOWN",
    INVALID_ARGUMENT = "INVALID_ARGUMENT",
    NOT_FOUND = "NOT_FOUND",
    PERMISSION_DENIED = "PERMISSION_DENIED",
    TIMEOUT = "TIMEOUT",
    CANCELLED = "CANCELLED",
    CONFIG_INVALID = "CONFIG_INVALID",
    CONFIG_NOT_FOUND = "CONFIG_NOT_FOUND",
    CONFIG_PARSE_ERROR = "CONFIG_PARSE_ERROR",
    PROVIDER_NOT_FOUND = "PROVIDER_NOT_FOUND",
    PROVIDER_UNAVAILABLE = "PROVIDER_UNAVAILABLE",
    PROVIDER_AUTH_FAILED = "PROVIDER_AUTH_FAILED",
    PROVIDER_RATE_LIMITED = "PROVIDER_RATE_LIMITED",
    PROVIDER_QUOTA_EXCEEDED = "PROVIDER_QUOTA_EXCEEDED",
    PROVIDER_INVALID_RESPONSE = "PROVIDER_INVALID_RESPONSE",
    TOOL_NOT_FOUND = "TOOL_NOT_FOUND",
    TOOL_EXECUTION_FAILED = "TOOL_EXECUTION_FAILED",
    TOOL_INVALID_PARAMS = "TOOL_INVALID_PARAMS",
    TOOL_PERMISSION_DENIED = "TOOL_PERMISSION_DENIED",
    TOOL_NOT_AVAILABLE = "TOOL_NOT_AVAILABLE",
    COMMAND_NOT_FOUND = "COMMAND_NOT_FOUND",
    COMMAND_INVALID_ARGS = "COMMAND_INVALID_ARGS",
    COMMAND_EXECUTION_FAILED = "COMMAND_EXECUTION_FAILED",
    NETWORK_ERROR = "NETWORK_ERROR",
    CONNECTION_FAILED = "CONNECTION_FAILED",
    DNS_RESOLUTION_FAILED = "DNS_RESOLUTION_FAILED",
    FILE_NOT_FOUND = "FILE_NOT_FOUND",
    FILE_ACCESS_DENIED = "FILE_ACCESS_DENIED",
    DIRECTORY_NOT_FOUND = "DIRECTORY_NOT_FOUND",
    DISK_FULL = "DISK_FULL"
}
/**
 * Base error class for all CLI errors
 */
export declare class CLIError extends Error {
    readonly code: ErrorCode;
    readonly context?: Record<string, JsonValue>;
    readonly cause?: Error;
    constructor(message: string, code?: ErrorCode, context?: Record<string, JsonValue>, cause?: Error);
    /**
     * Convert error to JSON-serializable object
     */
    toJSON(): Record<string, JsonValue>;
    /**
     * Create error from JSON object
     */
    static fromJSON(data: Record<string, JsonValue>): CLIError;
    /**
     * Check if error has specific code
     */
    hasCode(code: ErrorCode): boolean;
    /**
     * Check if error is retryable
     */
    isRetryable(): boolean;
    /**
     * Check if error is user-fixable
     */
    isUserFixable(): boolean;
}
/**
 * Error for validation failures
 */
export declare class ValidationError extends CLIError {
    constructor(message: string, context?: Record<string, JsonValue>, cause?: Error);
}
/**
 * Error for permission denied
 */
export declare class PermissionError extends CLIError {
    constructor(message: string, context?: Record<string, JsonValue>, cause?: Error);
}
/**
 * Error for timeouts
 */
export declare class TimeoutError extends CLIError {
    constructor(message: string, timeout: number, context?: Record<string, JsonValue>, cause?: Error);
}
/**
 * Error for cancelled operations
 */
export declare class CancellationError extends CLIError {
    constructor(message?: string, context?: Record<string, JsonValue>, cause?: Error);
}
/**
 * Error for not found resources
 */
export declare class NotFoundError extends CLIError {
    constructor(resource: string, context?: Record<string, JsonValue>, cause?: Error);
}
//# sourceMappingURL=base.d.ts.map