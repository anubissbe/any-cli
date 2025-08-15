/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */

import { z } from "zod";

/**
 * Validation utilities using Zod
 */

/**
 * Validate URL format
 */
export const urlSchema = z.string().url();

/**
 * Validate file path
 */
export const filePathSchema = z.string().min(1, "File path cannot be empty");

/**
 * Validate API key format with enhanced security
 */
export const apiKeySchema = z
  .string()
  .min(8, "API key must be at least 8 characters")
  .max(512, "API key is too long")
  .regex(/^[a-zA-Z0-9._-]+$/, "API key contains invalid characters");

/**
 * Validate OpenRouter API key format
 */
export const openRouterApiKeySchema = z
  .string()
  .regex(/^sk-or-v1-[a-f0-9]{64}$/, "Invalid OpenRouter API key format");

/**
 * Validate OpenAI API key format
 */
export const openAiApiKeySchema = z
  .string()
  .regex(/^sk-[a-zA-Z0-9]{32,}$/, "Invalid OpenAI API key format");

/**
 * Validate port number
 */
export const portSchema = z.number().int().min(1).max(65535);

/**
 * Validate timeout value
 */
export const timeoutSchema = z.number().int().min(0);

/**
 * Validate positive integer
 */
export const positiveIntSchema = z.number().int().positive();

/**
 * Validate non-negative integer
 */
export const nonNegativeIntSchema = z.number().int().min(0);

/**
 * Validate temperature value for AI models
 */
export const temperatureSchema = z.number().min(0).max(2);

/**
 * Validate max tokens value
 */
export const maxTokensSchema = z.number().int().min(1).max(100000);

/**
 * Validate model name
 */
export const modelNameSchema = z.string().min(1, "Model name cannot be empty");

/**
 * Validate email address
 */
export const emailSchema = z.string().email();

/**
 * Validate JSON string
 */
export const jsonStringSchema = z.string().refine((val) => {
  try {
    JSON.parse(val);
    return true;
  } catch {
    return false;
  }
}, "Must be valid JSON");

/**
 * Validate semantic version
 */
export const semverSchema = z
  .string()
  .regex(
    /^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$/,
    "Must be a valid semantic version",
  );

/**
 * Validate hex color
 */
export const hexColorSchema = z
  .string()
  .regex(/^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$/, "Must be a valid hex color");

/**
 * Validate file extension
 */
export const fileExtensionSchema = z
  .string()
  .regex(/^\.[a-zA-Z0-9]+$/, "Must be a valid file extension");

/**
 * Validate directory path
 */
export const directoryPathSchema = z
  .string()
  .min(1, "Directory path cannot be empty");

/**
 * Validate command name (for shell commands)
 */
export const commandNameSchema = z
  .string()
  .regex(
    /^[a-zA-Z0-9_-]+$/,
    "Command name can only contain letters, numbers, underscores, and hyphens",
  );

/**
 * Validate environment variable name
 */
export const envVarNameSchema = z
  .string()
  .regex(
    /^[A-Z][A-Z0-9_]*$/,
    "Environment variable must be uppercase with underscores",
  );

/**
 * Create validation function from schema
 */
export function createValidator<T>(schema: z.ZodSchema<T>) {
  return (
    value: unknown,
  ): { success: true; data: T } | { success: false; error: string } => {
    try {
      const data = schema.parse(value);
      return { success: true, data };
    } catch (error) {
      if (error instanceof z.ZodError) {
        const messages = error.issues.map(
          (issue) => `${issue.path.join(".")}: ${issue.message}`,
        );
        return { success: false, error: messages.join(", ") };
      }
      return { success: false, error: String(error) };
    }
  };
}

/**
 * Validate and parse JSON safely with type checking
 */
export function validateJSON<T = unknown>(
  jsonString: string,
  schema?: z.ZodSchema<T>,
): { success: true; data: T } | { success: false; error: string } {
  try {
    const data = JSON.parse(jsonString);
    
    if (schema) {
      const validation = schema.safeParse(data);
      if (!validation.success) {
        const errors = validation.error.issues.map(issue => 
          `${issue.path.join('.')}: ${issue.message}`
        ).join(', ');
        return { success: false, error: `JSON validation failed: ${errors}` };
      }
      return { success: true, data: validation.data };
    }
    
    return { success: true, data };
  } catch (error) {
    return { success: false, error: `Invalid JSON: ${error instanceof Error ? error.message : String(error)}` };
  }
}

/**
 * Validate object against schema and return result
 */
export function validateObject<T>(
  obj: unknown,
  schema: z.ZodSchema<T>,
): { success: true; data: T } | { success: false; errors: string[] } {
  try {
    const data = schema.parse(obj);
    return { success: true, data };
  } catch (error) {
    if (error instanceof z.ZodError) {
      const errors = error.issues.map((issue) => {
        const path = issue.path.length > 0 ? `${issue.path.join(".")}: ` : "";
        return `${path}${issue.message}`;
      });
      return { success: false, errors };
    }
    return { success: false, errors: [String(error)] };
  }
}

/**
 * Sanitize and validate user input
 */
export function sanitizeInput(
  input: string,
  options: {
    maxLength?: number;
    allowedChars?: RegExp;
    trim?: boolean;
    toLowerCase?: boolean;
    toUpperCase?: boolean;
  } = {},
): string {
  let sanitized = input;

  // Trim whitespace
  if (options.trim !== false) {
    sanitized = sanitized.trim();
  }

  // Case conversion
  if (options.toLowerCase) {
    sanitized = sanitized.toLowerCase();
  } else if (options.toUpperCase) {
    sanitized = sanitized.toUpperCase();
  }

  // Filter allowed characters (fix: use negated regex correctly)
  if (options.allowedChars) {
    sanitized = sanitized.replace(new RegExp(`[^${options.allowedChars.source}]`, 'g'), "");
  }

  // Limit length
  if (options.maxLength && sanitized.length > options.maxLength) {
    sanitized = sanitized.substring(0, options.maxLength);
  }

  return sanitized;
}

/**
 * Validate array of values against schema
 */
export function validateArray<T>(
  array: unknown[],
  itemSchema: z.ZodSchema<T>,
):
  | { success: true; data: T[] }
  | { success: false; errors: Array<{ index: number; error: string }> } {
  const results: T[] = [];
  const errors: Array<{ index: number; error: string }> = [];

  for (let i = 0; i < array.length; i++) {
    try {
      const item = itemSchema.parse(array[i]);
      results.push(item);
    } catch (error) {
      if (error instanceof z.ZodError) {
        const message = error.issues.map((issue) => issue.message).join(", ");
        errors.push({ index: i, error: message });
      } else {
        errors.push({ index: i, error: String(error) });
      }
    }
  }

  if (errors.length > 0) {
    return { success: false, errors };
  }

  return { success: true, data: results };
}

/**
 * Create a union schema from an array of possible values
 */
export function createEnumSchema<T extends readonly [string, ...string[]]>(
  values: T,
) {
  return z.enum(values);
}

/**
 * Create optional schema with default value
 */
export function createOptionalWithDefault<T>(
  schema: z.ZodSchema<T>,
  defaultValue: T,
) {
  return schema.optional().default(defaultValue as z.util.noUndefined<T>);
}

/**
 * Validate configuration object with detailed error reporting
 */
export function validateConfig<T>(
  config: unknown,
  schema: z.ZodSchema<T>,
  configName: string = "configuration",
): T {
  const result = validateObject(config, schema);

  if (!result.success) {
    const errorMessage = `Invalid ${configName}:\n${result.errors.map((e) => `  - ${e}`).join("\n")}`;
    throw new Error(errorMessage);
  }

  return result.data;
}
