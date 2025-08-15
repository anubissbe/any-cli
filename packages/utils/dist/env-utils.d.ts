/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */
/**
 * Get environment variable with optional default value
 */
export declare function getEnv(key: string, defaultValue?: string): string | undefined;
/**
 * Get environment variable as string with required validation
 */
export declare function getEnvRequired(key: string): string;
/**
 * Get environment variable as boolean
 */
export declare function getEnvBoolean(key: string, defaultValue?: boolean): boolean;
/**
 * Get environment variable as number
 */
export declare function getEnvNumber(key: string, defaultValue?: number): number | undefined;
/**
 * Get environment variable as integer
 */
export declare function getEnvInteger(key: string, defaultValue?: number): number | undefined;
/**
 * Get environment variable as array (comma-separated values)
 */
export declare function getEnvArray(key: string, defaultValue?: string[]): string[];
/**
 * Get environment variable as JSON object
 */
export declare function getEnvJSON<T = any>(key: string, defaultValue?: T): T | undefined;
/**
 * Set environment variable
 */
export declare function setEnv(key: string, value: string): void;
/**
 * Delete environment variable
 */
export declare function deleteEnv(key: string): void;
/**
 * Check if environment variable exists
 */
export declare function hasEnv(key: string): boolean;
/**
 * Get all environment variables with a specific prefix
 */
export declare function getEnvWithPrefix(prefix: string): Record<string, string>;
/**
 * Validate required environment variables
 */
export declare function validateRequiredEnvVars(requiredVars: string[]): void;
/**
 * Get environment configuration with validation
 */
export declare function getEnvConfig<T extends Record<string, any>>(schema: Record<keyof T, {
    key: string;
    required?: boolean;
    type?: "string" | "number" | "boolean" | "array" | "json";
    defaultValue?: any;
    validator?: (value: any) => boolean;
}>): T;
/**
 * Create environment variable key from config path
 */
export declare function createEnvKey(prefix: string, ...path: string[]): string;
/**
 * Load environment variables from various sources
 */
export declare function loadEnvFromSources(sources: {
    inline?: Record<string, string>;
    prefixes?: string[];
}): Record<string, string>;
/**
 * Check if running in development mode
 */
export declare function isDevelopment(): boolean;
/**
 * Check if running in production mode
 */
export declare function isProduction(): boolean;
/**
 * Check if running in test mode
 */
export declare function isTest(): boolean;
/**
 * Get current node environment
 */
export declare function getNodeEnv(): string;
//# sourceMappingURL=env-utils.d.ts.map