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
export class ToolError extends CLIError {
  public readonly tool: string;

  constructor(
    message: string,
    tool: string,
    code: ErrorCode = ErrorCode.TOOL_EXECUTION_FAILED,
    context?: Record<string, JsonValue>,
    cause?: Error,
  ) {
    super(message, code, { ...context, tool }, cause);
    this.tool = tool;
  }
}

/**
 * Error when tool is not found
 */
export class ToolNotFoundError extends ToolError {
  constructor(
    tool: string,
    context?: Record<string, JsonValue>,
    cause?: Error,
  ) {
    super(
      `Tool '${tool}' not found`,
      tool,
      ErrorCode.TOOL_NOT_FOUND,
      context,
      cause,
    );
  }
}

/**
 * Error when tool execution fails
 */
export class ToolExecutionError extends ToolError {
  public readonly exitCode?: number;
  public readonly stderr?: string;

  constructor(
    tool: string,
    message: string,
    exitCode?: number,
    stderr?: string,
    context?: Record<string, JsonValue>,
    cause?: Error,
  ) {
    super(
      `Tool '${tool}' execution failed: ${message}`,
      tool,
      ErrorCode.TOOL_EXECUTION_FAILED,
      { ...context, exitCode: exitCode ?? null, stderr: stderr ?? null },
      cause,
    );
    this.exitCode = exitCode;
    this.stderr = stderr;
  }
}

/**
 * Error when tool parameters are invalid
 */
export class ToolInvalidParamsError extends ToolError {
  public readonly invalidParams: ReadonlyArray<string>;

  constructor(
    tool: string,
    invalidParams: ReadonlyArray<string>,
    context?: Record<string, JsonValue>,
    cause?: Error,
  ) {
    const paramsList = invalidParams.join(", ");
    super(
      `Invalid parameters for tool '${tool}': ${paramsList}`,
      tool,
      ErrorCode.TOOL_INVALID_PARAMS,
      { ...context, invalidParams: [...invalidParams] },
      cause,
    );
    this.invalidParams = invalidParams;
  }
}

/**
 * Error when tool access is denied
 */
export class ToolPermissionError extends ToolError {
  constructor(
    tool: string,
    resource?: string,
    context?: Record<string, JsonValue>,
    cause?: Error,
  ) {
    const message = resource
      ? `Permission denied for tool '${tool}' to access '${resource}'`
      : `Permission denied for tool '${tool}'`;
    super(
      message,
      tool,
      ErrorCode.TOOL_PERMISSION_DENIED,
      { ...context, resource: resource ?? null },
      cause,
    );
  }
}

/**
 * Error when tool is not available on current platform
 */
export class ToolNotAvailableError extends ToolError {
  public readonly platform: string;

  constructor(
    tool: string,
    platform: string,
    reason?: string,
    context?: Record<string, JsonValue>,
    cause?: Error,
  ) {
    const message = reason
      ? `Tool '${tool}' is not available on ${platform}: ${reason}`
      : `Tool '${tool}' is not available on ${platform}`;
    super(
      message,
      tool,
      ErrorCode.TOOL_NOT_AVAILABLE,
      { ...context, platform, reason: reason ?? null },
      cause,
    );
    this.platform = platform;
  }
}

/**
 * Error when tool times out
 */
export class ToolTimeoutError extends ToolError {
  public readonly timeout: number;

  constructor(
    tool: string,
    timeout: number,
    context?: Record<string, JsonValue>,
    cause?: Error,
  ) {
    super(
      `Tool '${tool}' timed out after ${timeout}ms`,
      tool,
      ErrorCode.TIMEOUT,
      { ...context, timeout },
      cause,
    );
    this.timeout = timeout;
  }
}

/**
 * Error when tool requires confirmation but none provided
 */
export class ToolConfirmationError extends ToolError {
  constructor(
    tool: string,
    action: string,
    context?: Record<string, JsonValue>,
    cause?: Error,
  ) {
    super(
      `Tool '${tool}' requires confirmation for destructive action: ${action}`,
      tool,
      ErrorCode.PERMISSION_DENIED,
      { ...context, action },
      cause,
    );
  }
}

/**
 * Error when tool dependency is missing
 */
export class ToolDependencyError extends ToolError {
  public readonly dependency: string;

  constructor(
    tool: string,
    dependency: string,
    context?: Record<string, JsonValue>,
    cause?: Error,
  ) {
    super(
      `Tool '${tool}' requires missing dependency: ${dependency}`,
      tool,
      ErrorCode.TOOL_NOT_AVAILABLE,
      { ...context, dependency },
      cause,
    );
    this.dependency = dependency;
  }
}
