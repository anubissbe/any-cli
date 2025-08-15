/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */

/**
 * Get environment variable with optional default value
 */
export function getEnv(key: string, defaultValue?: string): string | undefined {
  return process.env[key] ?? defaultValue;
}

/**
 * Get environment variable as string with required validation
 */
export function getEnvRequired(key: string): string {
  const value = process.env[key];
  if (!value) {
    throw new Error(`Required environment variable ${key} is not set`);
  }
  return value;
}

/**
 * Get environment variable as boolean
 */
export function getEnvBoolean(
  key: string,
  defaultValue: boolean = false,
): boolean {
  const value = process.env[key];
  if (!value) return defaultValue;

  const lowercaseValue = value.toLowerCase();
  return (
    lowercaseValue === "true" ||
    lowercaseValue === "1" ||
    lowercaseValue === "yes"
  );
}

/**
 * Get environment variable as number
 */
export function getEnvNumber(
  key: string,
  defaultValue?: number,
): number | undefined {
  const value = process.env[key];
  if (!value) return defaultValue;

  const parsed = Number(value);
  if (isNaN(parsed)) {
    throw new Error(
      `Environment variable ${key} is not a valid number: ${value}`,
    );
  }

  return parsed;
}

/**
 * Get environment variable as integer
 */
export function getEnvInteger(
  key: string,
  defaultValue?: number,
): number | undefined {
  const value = getEnvNumber(key, defaultValue);
  if (value !== undefined && !Number.isInteger(value)) {
    throw new Error(
      `Environment variable ${key} is not a valid integer: ${value}`,
    );
  }
  return value;
}

/**
 * Get environment variable as array (comma-separated values)
 */
export function getEnvArray(
  key: string,
  defaultValue: string[] = [],
): string[] {
  const value = process.env[key];
  if (!value) return defaultValue;

  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

/**
 * Get environment variable as JSON object
 */
export function getEnvJSON<T = any>(
  key: string,
  defaultValue?: T,
): T | undefined {
  const value = process.env[key];
  if (!value) return defaultValue;

  try {
    return JSON.parse(value);
  } catch (error) {
    throw new Error(`Environment variable ${key} is not valid JSON: ${error}`);
  }
}

/**
 * Set environment variable
 */
export function setEnv(key: string, value: string): void {
  process.env[key] = value;
}

/**
 * Delete environment variable
 */
export function deleteEnv(key: string): void {
  delete process.env[key];
}

/**
 * Check if environment variable exists
 */
export function hasEnv(key: string): boolean {
  return key in process.env;
}

/**
 * Get all environment variables with a specific prefix
 */
export function getEnvWithPrefix(prefix: string): Record<string, string> {
  const result: Record<string, string> = {};

  for (const [key, value] of Object.entries(process.env)) {
    if (key.startsWith(prefix) && value !== undefined) {
      // Remove prefix and convert to camelCase
      const cleanKey = key
        .slice(prefix.length)
        .toLowerCase()
        .replace(/_(.)/g, (_, char) => char.toUpperCase());
      result[cleanKey] = value;
    }
  }

  return result;
}

/**
 * Validate required environment variables
 */
export function validateRequiredEnvVars(requiredVars: string[]): void {
  const missing = requiredVars.filter((key) => !hasEnv(key));

  if (missing.length > 0) {
    throw new Error(
      `Missing required environment variables: ${missing.join(", ")}`,
    );
  }
}

/**
 * Get environment configuration with validation
 */
export function getEnvConfig<T extends Record<string, any>>(
  schema: Record<
    keyof T,
    {
      key: string;
      required?: boolean;
      type?: "string" | "number" | "boolean" | "array" | "json";
      defaultValue?: any;
      validator?: (value: any) => boolean;
    }
  >,
): T {
  const config = {} as T;

  for (const [configKey, options] of Object.entries(schema)) {
    const {
      key,
      required = false,
      type = "string",
      defaultValue,
      validator,
    } = options;

    let value: any;

    try {
      switch (type) {
        case "string":
          value = required ? getEnvRequired(key) : getEnv(key, defaultValue);
          break;
        case "number":
          value = getEnvNumber(key, defaultValue);
          if (required && value === undefined) {
            throw new Error(`Required environment variable ${key} is not set`);
          }
          break;
        case "boolean":
          value = getEnvBoolean(key, defaultValue);
          break;
        case "array":
          value = getEnvArray(key, defaultValue);
          break;
        case "json":
          value = getEnvJSON(key, defaultValue);
          if (required && value === undefined) {
            throw new Error(`Required environment variable ${key} is not set`);
          }
          break;
        default:
          throw new Error(
            `Unknown type ${type} for environment variable ${key}`,
          );
      }

      // Custom validation
      if (value !== undefined && validator && !validator(value)) {
        throw new Error(`Environment variable ${key} failed validation`);
      }

      if (value !== undefined) {
        (config as any)[configKey] = value;
      }
    } catch (error) {
      throw new Error(`Failed to parse environment variable ${key}: ${error}`);
    }
  }

  return config;
}

/**
 * Create environment variable key from config path
 */
export function createEnvKey(prefix: string, ...path: string[]): string {
  return [prefix, ...path]
    .join("_")
    .toUpperCase()
    .replace(/[^A-Z0-9_]/g, "_");
}

/**
 * Load environment variables from various sources
 */
export function loadEnvFromSources(sources: {
  inline?: Record<string, string>;
  prefixes?: string[];
}): Record<string, string> {
  const env: Record<string, string> = {};

  // Load inline environment variables
  if (sources.inline) {
    Object.assign(env, sources.inline);
  }

  // Load environment variables with prefixes
  if (sources.prefixes) {
    for (const prefix of sources.prefixes) {
      const prefixedEnv = getEnvWithPrefix(prefix);
      Object.assign(env, prefixedEnv);
    }
  }

  return env;
}

/**
 * Check if running in development mode
 */
export function isDevelopment(): boolean {
  return getEnv("NODE_ENV") === "development";
}

/**
 * Check if running in production mode
 */
export function isProduction(): boolean {
  return getEnv("NODE_ENV") === "production";
}

/**
 * Check if running in test mode
 */
export function isTest(): boolean {
  return getEnv("NODE_ENV") === "test";
}

/**
 * Get current node environment
 */
export function getNodeEnv(): string {
  return getEnv("NODE_ENV", "development") ?? "development";
}
