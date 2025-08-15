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
export class CommandError extends CLIError {
  public readonly command: string;

  constructor(
    message: string,
    command: string,
    code: ErrorCode = ErrorCode.COMMAND_EXECUTION_FAILED,
    context?: Record<string, JsonValue>,
    cause?: Error,
  ) {
    super(message, code, { ...context, command }, cause);
    this.command = command;
  }
}

/**
 * Error when command is not found
 */
export class CommandNotFoundError extends CommandError {
  constructor(
    command: string,
    context?: Record<string, JsonValue>,
    cause?: Error,
  ) {
    super(
      `Command '${command}' not found`,
      command,
      ErrorCode.COMMAND_NOT_FOUND,
      context,
      cause,
    );
  }
}

/**
 * Error when command arguments are invalid
 */
export class CommandInvalidArgsError extends CommandError {
  public readonly invalidArgs: ReadonlyArray<string>;

  constructor(
    command: string,
    invalidArgs: ReadonlyArray<string>,
    context?: Record<string, JsonValue>,
    cause?: Error,
  ) {
    const argsList = invalidArgs.join(", ");
    super(
      `Invalid arguments for command '${command}': ${argsList}`,
      command,
      ErrorCode.COMMAND_INVALID_ARGS,
      { ...context, invalidArgs: [...invalidArgs] },
      cause,
    );
    this.invalidArgs = invalidArgs;
  }
}

/**
 * Error when command execution fails
 */
export class CommandExecutionError extends CommandError {
  public readonly exitCode?: number;

  constructor(
    command: string,
    message: string,
    exitCode?: number,
    context?: Record<string, JsonValue>,
    cause?: Error,
  ) {
    super(
      `Command '${command}' execution failed: ${message}`,
      command,
      ErrorCode.COMMAND_EXECUTION_FAILED,
      { ...context, exitCode: exitCode ?? null },
      cause,
    );
    this.exitCode = exitCode;
  }
}

/**
 * Error when required argument is missing
 */
export class CommandMissingArgError extends CommandError {
  public readonly missingArg: string;

  constructor(
    command: string,
    missingArg: string,
    context?: Record<string, JsonValue>,
    cause?: Error,
  ) {
    super(
      `Required argument '${missingArg}' missing for command '${command}'`,
      command,
      ErrorCode.COMMAND_INVALID_ARGS,
      { ...context, missingArg },
      cause,
    );
    this.missingArg = missingArg;
  }
}

/**
 * Error when command parsing fails
 */
export class CommandParseError extends CommandError {
  public readonly rawInput: string;

  constructor(
    rawInput: string,
    parseError: string,
    context?: Record<string, JsonValue>,
    cause?: Error,
  ) {
    super(
      `Failed to parse command: ${parseError}`,
      rawInput,
      ErrorCode.COMMAND_INVALID_ARGS,
      { ...context, rawInput, parseError },
      cause,
    );
    this.rawInput = rawInput;
  }
}

/**
 * Error when command option value is invalid
 */
export class CommandInvalidOptionError extends CommandError {
  public readonly option: string;
  public readonly value: string;

  constructor(
    command: string,
    option: string,
    value: string,
    reason?: string,
    context?: Record<string, JsonValue>,
    cause?: Error,
  ) {
    const message = reason
      ? `Invalid value '${value}' for option '${option}' in command '${command}': ${reason}`
      : `Invalid value '${value}' for option '${option}' in command '${command}'`;
    super(
      message,
      command,
      ErrorCode.COMMAND_INVALID_ARGS,
      { ...context, option, value, reason: reason ?? null },
      cause,
    );
    this.option = option;
    this.value = value;
  }
}

/**
 * Error when command help is requested
 */
export class CommandHelpError extends CommandError {
  constructor(
    command: string,
    helpText: string,
    context?: Record<string, JsonValue>,
  ) {
    super(helpText, command, ErrorCode.INVALID_ARGUMENT, context);
  }
}
