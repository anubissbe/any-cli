/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */
import { CLIError, ErrorCode } from "./base.js";
import type { JsonValue } from "../types/common.js";
/**
 * Base error for command-related issues
 */
export declare class CommandError extends CLIError {
    readonly command: string;
    constructor(message: string, command: string, code?: ErrorCode, context?: Record<string, JsonValue>, cause?: Error);
}
/**
 * Error when command is not found
 */
export declare class CommandNotFoundError extends CommandError {
    constructor(command: string, context?: Record<string, JsonValue>, cause?: Error);
}
/**
 * Error when command arguments are invalid
 */
export declare class CommandInvalidArgsError extends CommandError {
    readonly invalidArgs: ReadonlyArray<string>;
    constructor(command: string, invalidArgs: ReadonlyArray<string>, context?: Record<string, JsonValue>, cause?: Error);
}
/**
 * Error when command execution fails
 */
export declare class CommandExecutionError extends CommandError {
    readonly exitCode?: number;
    constructor(command: string, message: string, exitCode?: number, context?: Record<string, JsonValue>, cause?: Error);
}
/**
 * Error when required argument is missing
 */
export declare class CommandMissingArgError extends CommandError {
    readonly missingArg: string;
    constructor(command: string, missingArg: string, context?: Record<string, JsonValue>, cause?: Error);
}
/**
 * Error when command parsing fails
 */
export declare class CommandParseError extends CommandError {
    readonly rawInput: string;
    constructor(rawInput: string, parseError: string, context?: Record<string, JsonValue>, cause?: Error);
}
/**
 * Error when command option value is invalid
 */
export declare class CommandInvalidOptionError extends CommandError {
    readonly option: string;
    readonly value: string;
    constructor(command: string, option: string, value: string, reason?: string, context?: Record<string, JsonValue>, cause?: Error);
}
/**
 * Error when command help is requested
 */
export declare class CommandHelpError extends CommandError {
    constructor(command: string, helpText: string, context?: Record<string, JsonValue>);
}
//# sourceMappingURL=command.d.ts.map