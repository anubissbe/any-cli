/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */
import type { JsonValue, Result } from "../types/common.js";
import type { AppConfig } from "../config/schema.js";
/**
 * Configuration source types
 */
export type ConfigSource = "file" | "environment" | "args" | "default";
/**
 * Configuration value with metadata
 */
export interface ConfigValue<T = JsonValue> {
    readonly value: T;
    readonly source: ConfigSource;
    readonly path: string;
}
/**
 * Configuration manager interface
 */
export interface ConfigManager {
    /**
     * Load configuration from all sources
     */
    load(): Promise<Result<AppConfig>>;
    /**
     * Get a configuration value by path
     */
    get<T = JsonValue>(path: string): ConfigValue<T> | undefined;
    /**
     * Set a configuration value
     */
    set(path: string, value: JsonValue, source?: ConfigSource): Result<void>;
    /**
     * Save configuration to file
     */
    save(): Promise<Result<void>>;
    /**
     * Validate configuration
     */
    validate(): Result<AppConfig>;
    /**
     * Get configuration file path
     */
    getConfigPath(): string;
    /**
     * Watch for configuration changes
     */
    watch(callback: (config: AppConfig) => void): () => void;
    /**
     * Reset configuration to defaults
     */
    reset(): Promise<Result<void>>;
}
/**
 * Configuration loader interface
 */
export interface ConfigLoader {
    /**
     * Load configuration from a source
     */
    load(source: string): Promise<Result<Partial<AppConfig>>>;
    /**
     * Check if source exists
     */
    exists(source: string): Promise<boolean>;
    /**
     * Get supported file extensions
     */
    getSupportedExtensions(): ReadonlyArray<string>;
}
/**
 * Configuration validator interface
 */
export interface ConfigValidator {
    /**
     * Validate configuration object
     */
    validate(config: unknown): Result<AppConfig>;
    /**
     * Get validation schema
     */
    getSchema(): JsonValue;
}
//# sourceMappingURL=config.d.ts.map