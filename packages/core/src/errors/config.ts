/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */

import { CLIError, ErrorCode } from "./base.js";
import type { JsonValue } from "../types/common.js";

/**
 * Base error for configuration-related issues
 */
export class ConfigError extends CLIError {
  public readonly configPath?: string;

  constructor(
    message: string,
    code: ErrorCode = ErrorCode.CONFIG_INVALID,
    configPath?: string,
    context?: Record<string, JsonValue>,
    cause?: Error,
  ) {
    super(message, code, { ...context, configPath: configPath ?? null }, cause);
    this.configPath = configPath;
  }
}

/**
 * Error when configuration file is not found
 */
export class ConfigNotFoundError extends ConfigError {
  constructor(
    configPath: string,
    context?: Record<string, JsonValue>,
    cause?: Error,
  ) {
    super(
      `Configuration file not found: ${configPath}`,
      ErrorCode.CONFIG_NOT_FOUND,
      configPath,
      context,
      cause,
    );
  }
}

/**
 * Error when configuration file cannot be parsed
 */
export class ConfigParseError extends ConfigError {
  public readonly parseError: string;

  constructor(
    configPath: string,
    parseError: string,
    context?: Record<string, JsonValue>,
    cause?: Error,
  ) {
    super(
      `Failed to parse configuration file ${configPath}: ${parseError}`,
      ErrorCode.CONFIG_PARSE_ERROR,
      configPath,
      { ...context, parseError },
      cause,
    );
    this.parseError = parseError;
  }
}

/**
 * Error when configuration validation fails
 */
export class ConfigValidationError extends ConfigError {
  public readonly validationErrors: ReadonlyArray<string>;

  constructor(
    validationErrors: ReadonlyArray<string>,
    configPath?: string,
    context?: Record<string, JsonValue>,
    cause?: Error,
  ) {
    const errorList = validationErrors.join(", ");
    const message = configPath
      ? `Configuration validation failed for ${configPath}: ${errorList}`
      : `Configuration validation failed: ${errorList}`;
    super(
      message,
      ErrorCode.CONFIG_INVALID,
      configPath,
      { ...context, validationErrors: [...validationErrors] },
      cause,
    );
    this.validationErrors = validationErrors;
  }
}

/**
 * Error when configuration schema is invalid
 */
export class ConfigSchemaError extends ConfigError {
  constructor(
    message: string,
    configPath?: string,
    context?: Record<string, JsonValue>,
    cause?: Error,
  ) {
    super(
      `Configuration schema error: ${message}`,
      ErrorCode.CONFIG_INVALID,
      configPath,
      context,
      cause,
    );
  }
}

/**
 * Error when configuration file access is denied
 */
export class ConfigAccessError extends ConfigError {
  constructor(
    configPath: string,
    operation: "read" | "write",
    context?: Record<string, JsonValue>,
    cause?: Error,
  ) {
    super(
      `Access denied for ${operation} operation on configuration file: ${configPath}`,
      ErrorCode.PERMISSION_DENIED,
      configPath,
      { ...context, operation },
      cause,
    );
  }
}

/**
 * Error when configuration value is missing
 */
export class ConfigMissingValueError extends ConfigError {
  public readonly key: string;

  constructor(
    key: string,
    configPath?: string,
    context?: Record<string, JsonValue>,
    cause?: Error,
  ) {
    super(
      `Required configuration value missing: ${key}`,
      ErrorCode.CONFIG_INVALID,
      configPath,
      { ...context, key },
      cause,
    );
    this.key = key;
  }
}

/**
 * Error when configuration value type is incorrect
 */
export class ConfigTypeError extends ConfigError {
  public readonly key: string;
  public readonly expectedType: string;
  public readonly actualType: string;

  constructor(
    key: string,
    expectedType: string,
    actualType: string,
    configPath?: string,
    context?: Record<string, JsonValue>,
    cause?: Error,
  ) {
    super(
      `Configuration value '${key}' has incorrect type. Expected ${expectedType}, got ${actualType}`,
      ErrorCode.CONFIG_INVALID,
      configPath,
      { ...context, key, expectedType, actualType },
      cause,
    );
    this.key = key;
    this.expectedType = expectedType;
    this.actualType = actualType;
  }
}
