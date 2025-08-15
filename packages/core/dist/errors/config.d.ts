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
export declare class ConfigError extends CLIError {
    readonly configPath?: string;
    constructor(message: string, code?: ErrorCode, configPath?: string, context?: Record<string, JsonValue>, cause?: Error);
}
/**
 * Error when configuration file is not found
 */
export declare class ConfigNotFoundError extends ConfigError {
    constructor(configPath: string, context?: Record<string, JsonValue>, cause?: Error);
}
/**
 * Error when configuration file cannot be parsed
 */
export declare class ConfigParseError extends ConfigError {
    readonly parseError: string;
    constructor(configPath: string, parseError: string, context?: Record<string, JsonValue>, cause?: Error);
}
/**
 * Error when configuration validation fails
 */
export declare class ConfigValidationError extends ConfigError {
    readonly validationErrors: ReadonlyArray<string>;
    constructor(validationErrors: ReadonlyArray<string>, configPath?: string, context?: Record<string, JsonValue>, cause?: Error);
}
/**
 * Error when configuration schema is invalid
 */
export declare class ConfigSchemaError extends ConfigError {
    constructor(message: string, configPath?: string, context?: Record<string, JsonValue>, cause?: Error);
}
/**
 * Error when configuration file access is denied
 */
export declare class ConfigAccessError extends ConfigError {
    constructor(configPath: string, operation: "read" | "write", context?: Record<string, JsonValue>, cause?: Error);
}
/**
 * Error when configuration value is missing
 */
export declare class ConfigMissingValueError extends ConfigError {
    readonly key: string;
    constructor(key: string, configPath?: string, context?: Record<string, JsonValue>, cause?: Error);
}
/**
 * Error when configuration value type is incorrect
 */
export declare class ConfigTypeError extends ConfigError {
    readonly key: string;
    readonly expectedType: string;
    readonly actualType: string;
    constructor(key: string, expectedType: string, actualType: string, configPath?: string, context?: Record<string, JsonValue>, cause?: Error);
}
//# sourceMappingURL=config.d.ts.map