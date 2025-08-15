/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */
import type { LogLevel, JsonValue } from "../types/common.js";
/**
 * Structured log entry
 */
export interface LogEntry {
    readonly level: LogLevel;
    readonly message: string;
    readonly timestamp: Date;
    readonly context?: Record<string, JsonValue>;
    readonly error?: Error;
    readonly component?: string;
}
/**
 * Logger interface for structured logging
 */
export interface Logger {
    /**
     * Log a debug message
     */
    debug(message: string, context?: Record<string, JsonValue>): void;
    /**
     * Log an info message
     */
    info(message: string, context?: Record<string, JsonValue>): void;
    /**
     * Log a warning message
     */
    warn(message: string, context?: Record<string, JsonValue>): void;
    /**
     * Log an error message
     */
    error(message: string, error?: Error, context?: Record<string, JsonValue>): void;
    /**
     * Create a child logger with additional context
     */
    child(component: string, additionalContext?: Record<string, JsonValue>): Logger;
    /**
     * Set the minimum log level
     */
    setLevel(level: LogLevel): void;
    /**
     * Get the current log level
     */
    getLevel(): LogLevel;
    /**
     * Check if a level is enabled
     */
    isLevelEnabled(level: LogLevel): boolean;
}
/**
 * Log formatter interface
 */
export interface LogFormatter {
    /**
     * Format a log entry to a string
     */
    format(entry: LogEntry): string;
}
/**
 * Log transport interface for outputting logs
 */
export interface LogTransport {
    /**
     * Write a log entry
     */
    write(entry: LogEntry): Promise<void>;
    /**
     * Flush any pending log entries
     */
    flush(): Promise<void>;
    /**
     * Close the transport
     */
    close(): Promise<void>;
}
//# sourceMappingURL=logger.d.ts.map