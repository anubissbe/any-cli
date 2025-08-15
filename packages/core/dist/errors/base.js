/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */
/**
 * Error codes for different error types
 */
export var ErrorCode;
(function (ErrorCode) {
    // Generic errors
    ErrorCode["UNKNOWN"] = "UNKNOWN";
    ErrorCode["INVALID_ARGUMENT"] = "INVALID_ARGUMENT";
    ErrorCode["NOT_FOUND"] = "NOT_FOUND";
    ErrorCode["PERMISSION_DENIED"] = "PERMISSION_DENIED";
    ErrorCode["TIMEOUT"] = "TIMEOUT";
    ErrorCode["CANCELLED"] = "CANCELLED";
    // Configuration errors
    ErrorCode["CONFIG_INVALID"] = "CONFIG_INVALID";
    ErrorCode["CONFIG_NOT_FOUND"] = "CONFIG_NOT_FOUND";
    ErrorCode["CONFIG_PARSE_ERROR"] = "CONFIG_PARSE_ERROR";
    // Provider errors
    ErrorCode["PROVIDER_NOT_FOUND"] = "PROVIDER_NOT_FOUND";
    ErrorCode["PROVIDER_UNAVAILABLE"] = "PROVIDER_UNAVAILABLE";
    ErrorCode["PROVIDER_AUTH_FAILED"] = "PROVIDER_AUTH_FAILED";
    ErrorCode["PROVIDER_RATE_LIMITED"] = "PROVIDER_RATE_LIMITED";
    ErrorCode["PROVIDER_QUOTA_EXCEEDED"] = "PROVIDER_QUOTA_EXCEEDED";
    ErrorCode["PROVIDER_INVALID_RESPONSE"] = "PROVIDER_INVALID_RESPONSE";
    // Tool errors
    ErrorCode["TOOL_NOT_FOUND"] = "TOOL_NOT_FOUND";
    ErrorCode["TOOL_EXECUTION_FAILED"] = "TOOL_EXECUTION_FAILED";
    ErrorCode["TOOL_INVALID_PARAMS"] = "TOOL_INVALID_PARAMS";
    ErrorCode["TOOL_PERMISSION_DENIED"] = "TOOL_PERMISSION_DENIED";
    ErrorCode["TOOL_NOT_AVAILABLE"] = "TOOL_NOT_AVAILABLE";
    // Command errors
    ErrorCode["COMMAND_NOT_FOUND"] = "COMMAND_NOT_FOUND";
    ErrorCode["COMMAND_INVALID_ARGS"] = "COMMAND_INVALID_ARGS";
    ErrorCode["COMMAND_EXECUTION_FAILED"] = "COMMAND_EXECUTION_FAILED";
    // Network errors
    ErrorCode["NETWORK_ERROR"] = "NETWORK_ERROR";
    ErrorCode["CONNECTION_FAILED"] = "CONNECTION_FAILED";
    ErrorCode["DNS_RESOLUTION_FAILED"] = "DNS_RESOLUTION_FAILED";
    // File system errors
    ErrorCode["FILE_NOT_FOUND"] = "FILE_NOT_FOUND";
    ErrorCode["FILE_ACCESS_DENIED"] = "FILE_ACCESS_DENIED";
    ErrorCode["DIRECTORY_NOT_FOUND"] = "DIRECTORY_NOT_FOUND";
    ErrorCode["DISK_FULL"] = "DISK_FULL";
})(ErrorCode || (ErrorCode = {}));
/**
 * Base error class for all CLI errors
 */
export class CLIError extends Error {
    code;
    context;
    cause;
    constructor(message, code = ErrorCode.UNKNOWN, context, cause) {
        super(message);
        this.name = this.constructor.name;
        this.code = code;
        this.context = context;
        this.cause = cause;
        // Maintain proper stack trace
        if (Error.captureStackTrace) {
            Error.captureStackTrace(this, this.constructor);
        }
    }
    /**
     * Convert error to JSON-serializable object
     */
    toJSON() {
        return {
            name: this.name,
            message: this.message,
            code: this.code,
            context: this.context || {},
            stack: this.stack || null,
            cause: this.cause
                ? {
                    name: this.cause.name,
                    message: this.cause.message,
                    stack: this.cause.stack || null,
                }
                : null,
        };
    }
    /**
     * Create error from JSON object
     */
    static fromJSON(data) {
        const error = new CLIError(data.message, data.code, data.context);
        if (data.stack) {
            error.stack = data.stack;
        }
        return error;
    }
    /**
     * Check if error has specific code
     */
    hasCode(code) {
        return this.code === code;
    }
    /**
     * Check if error is retryable
     */
    isRetryable() {
        return [
            ErrorCode.TIMEOUT,
            ErrorCode.NETWORK_ERROR,
            ErrorCode.CONNECTION_FAILED,
            ErrorCode.PROVIDER_RATE_LIMITED,
        ].includes(this.code);
    }
    /**
     * Check if error is user-fixable
     */
    isUserFixable() {
        return [
            ErrorCode.INVALID_ARGUMENT,
            ErrorCode.CONFIG_INVALID,
            ErrorCode.COMMAND_INVALID_ARGS,
            ErrorCode.TOOL_INVALID_PARAMS,
            ErrorCode.PROVIDER_AUTH_FAILED,
        ].includes(this.code);
    }
}
/**
 * Error for validation failures
 */
export class ValidationError extends CLIError {
    constructor(message, context, cause) {
        super(message, ErrorCode.INVALID_ARGUMENT, context, cause);
    }
}
/**
 * Error for permission denied
 */
export class PermissionError extends CLIError {
    constructor(message, context, cause) {
        super(message, ErrorCode.PERMISSION_DENIED, context, cause);
    }
}
/**
 * Error for timeouts
 */
export class TimeoutError extends CLIError {
    constructor(message, timeout, context, cause) {
        super(message, ErrorCode.TIMEOUT, { ...context, timeout }, cause);
    }
}
/**
 * Error for cancelled operations
 */
export class CancellationError extends CLIError {
    constructor(message = "Operation was cancelled", context, cause) {
        super(message, ErrorCode.CANCELLED, context, cause);
    }
}
/**
 * Error for not found resources
 */
export class NotFoundError extends CLIError {
    constructor(resource, context, cause) {
        super(`${resource} not found`, ErrorCode.NOT_FOUND, { ...context, resource }, cause);
    }
}
//# sourceMappingURL=base.js.map