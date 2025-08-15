/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */
import { CLIError, ErrorCode } from "./base.js";
/**
 * Base error for command-related issues
 */
export class CommandError extends CLIError {
    command;
    constructor(message, command, code = ErrorCode.COMMAND_EXECUTION_FAILED, context, cause) {
        super(message, code, { ...context, command }, cause);
        this.command = command;
    }
}
/**
 * Error when command is not found
 */
export class CommandNotFoundError extends CommandError {
    constructor(command, context, cause) {
        super(`Command '${command}' not found`, command, ErrorCode.COMMAND_NOT_FOUND, context, cause);
    }
}
/**
 * Error when command arguments are invalid
 */
export class CommandInvalidArgsError extends CommandError {
    invalidArgs;
    constructor(command, invalidArgs, context, cause) {
        const argsList = invalidArgs.join(", ");
        super(`Invalid arguments for command '${command}': ${argsList}`, command, ErrorCode.COMMAND_INVALID_ARGS, { ...context, invalidArgs: [...invalidArgs] }, cause);
        this.invalidArgs = invalidArgs;
    }
}
/**
 * Error when command execution fails
 */
export class CommandExecutionError extends CommandError {
    exitCode;
    constructor(command, message, exitCode, context, cause) {
        super(`Command '${command}' execution failed: ${message}`, command, ErrorCode.COMMAND_EXECUTION_FAILED, { ...context, exitCode: exitCode ?? null }, cause);
        this.exitCode = exitCode;
    }
}
/**
 * Error when required argument is missing
 */
export class CommandMissingArgError extends CommandError {
    missingArg;
    constructor(command, missingArg, context, cause) {
        super(`Required argument '${missingArg}' missing for command '${command}'`, command, ErrorCode.COMMAND_INVALID_ARGS, { ...context, missingArg }, cause);
        this.missingArg = missingArg;
    }
}
/**
 * Error when command parsing fails
 */
export class CommandParseError extends CommandError {
    rawInput;
    constructor(rawInput, parseError, context, cause) {
        super(`Failed to parse command: ${parseError}`, rawInput, ErrorCode.COMMAND_INVALID_ARGS, { ...context, rawInput, parseError }, cause);
        this.rawInput = rawInput;
    }
}
/**
 * Error when command option value is invalid
 */
export class CommandInvalidOptionError extends CommandError {
    option;
    value;
    constructor(command, option, value, reason, context, cause) {
        const message = reason
            ? `Invalid value '${value}' for option '${option}' in command '${command}': ${reason}`
            : `Invalid value '${value}' for option '${option}' in command '${command}'`;
        super(message, command, ErrorCode.COMMAND_INVALID_ARGS, { ...context, option, value, reason: reason ?? null }, cause);
        this.option = option;
        this.value = value;
    }
}
/**
 * Error when command help is requested
 */
export class CommandHelpError extends CommandError {
    constructor(command, helpText, context) {
        super(helpText, command, ErrorCode.INVALID_ARGUMENT, context);
    }
}
//# sourceMappingURL=command.js.map