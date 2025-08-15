/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */

import type { JsonValue } from "../types/common.js";

/**
 * Error codes for different error types
 */
export enum ErrorCode {
  // Generic errors
  UNKNOWN = "UNKNOWN",
  INVALID_ARGUMENT = "INVALID_ARGUMENT",
  NOT_FOUND = "NOT_FOUND",
  PERMISSION_DENIED = "PERMISSION_DENIED",
  TIMEOUT = "TIMEOUT",
  CANCELLED = "CANCELLED",

  // Configuration errors
  CONFIG_INVALID = "CONFIG_INVALID",
  CONFIG_NOT_FOUND = "CONFIG_NOT_FOUND",
  CONFIG_PARSE_ERROR = "CONFIG_PARSE_ERROR",

  // Provider errors
  PROVIDER_NOT_FOUND = "PROVIDER_NOT_FOUND",
  PROVIDER_UNAVAILABLE = "PROVIDER_UNAVAILABLE",
  PROVIDER_AUTH_FAILED = "PROVIDER_AUTH_FAILED",
  PROVIDER_RATE_LIMITED = "PROVIDER_RATE_LIMITED",
  PROVIDER_QUOTA_EXCEEDED = "PROVIDER_QUOTA_EXCEEDED",
  PROVIDER_INVALID_RESPONSE = "PROVIDER_INVALID_RESPONSE",

  // Tool errors
  TOOL_NOT_FOUND = "TOOL_NOT_FOUND",
  TOOL_EXECUTION_FAILED = "TOOL_EXECUTION_FAILED",
  TOOL_INVALID_PARAMS = "TOOL_INVALID_PARAMS",
  TOOL_PERMISSION_DENIED = "TOOL_PERMISSION_DENIED",
  TOOL_NOT_AVAILABLE = "TOOL_NOT_AVAILABLE",

  // Command errors
  COMMAND_NOT_FOUND = "COMMAND_NOT_FOUND",
  COMMAND_INVALID_ARGS = "COMMAND_INVALID_ARGS",
  COMMAND_EXECUTION_FAILED = "COMMAND_EXECUTION_FAILED",

  // Network errors
  NETWORK_ERROR = "NETWORK_ERROR",
  CONNECTION_FAILED = "CONNECTION_FAILED",
  DNS_RESOLUTION_FAILED = "DNS_RESOLUTION_FAILED",

  // File system errors
  FILE_NOT_FOUND = "FILE_NOT_FOUND",
  FILE_ACCESS_DENIED = "FILE_ACCESS_DENIED",
  DIRECTORY_NOT_FOUND = "DIRECTORY_NOT_FOUND",
  DISK_FULL = "DISK_FULL",
}

/**
 * Base error class for all CLI errors
 */
export class CLIError extends Error {
  public readonly code: ErrorCode;
  public readonly context?: Record<string, JsonValue>;
  public readonly cause?: Error;

  constructor(
    message: string,
    code: ErrorCode = ErrorCode.UNKNOWN,
    context?: Record<string, JsonValue>,
    cause?: Error,
  ) {
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
  toJSON(): Record<string, JsonValue> {
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
  static fromJSON(data: Record<string, JsonValue>): CLIError {
    const error = new CLIError(
      data.message as string,
      data.code as ErrorCode,
      data.context as Record<string, JsonValue>,
    );

    if (data.stack) {
      error.stack = data.stack as string;
    }

    return error;
  }

  /**
   * Check if error has specific code
   */
  hasCode(code: ErrorCode): boolean {
    return this.code === code;
  }

  /**
   * Check if error is retryable
   */
  isRetryable(): boolean {
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
  isUserFixable(): boolean {
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
  constructor(
    message: string,
    context?: Record<string, JsonValue>,
    cause?: Error,
  ) {
    super(message, ErrorCode.INVALID_ARGUMENT, context, cause);
  }
}

/**
 * Error for permission denied
 */
export class PermissionError extends CLIError {
  constructor(
    message: string,
    context?: Record<string, JsonValue>,
    cause?: Error,
  ) {
    super(message, ErrorCode.PERMISSION_DENIED, context, cause);
  }
}

/**
 * Error for timeouts
 */
export class TimeoutError extends CLIError {
  constructor(
    message: string,
    timeout: number,
    context?: Record<string, JsonValue>,
    cause?: Error,
  ) {
    super(message, ErrorCode.TIMEOUT, { ...context, timeout }, cause);
  }
}

/**
 * Error for cancelled operations
 */
export class CancellationError extends CLIError {
  constructor(
    message: string = "Operation was cancelled",
    context?: Record<string, JsonValue>,
    cause?: Error,
  ) {
    super(message, ErrorCode.CANCELLED, context, cause);
  }
}

/**
 * Error for not found resources
 */
export class NotFoundError extends CLIError {
  constructor(
    resource: string,
    context?: Record<string, JsonValue>,
    cause?: Error,
  ) {
    super(
      `${resource} not found`,
      ErrorCode.NOT_FOUND,
      { ...context, resource },
      cause,
    );
  }
}
