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
export declare const urlSchema: z.ZodString;
/**
 * Validate file path
 */
export declare const filePathSchema: z.ZodString;
/**
 * Validate API key format with enhanced security
 */
export declare const apiKeySchema: z.ZodString;
/**
 * Validate OpenRouter API key format
 */
export declare const openRouterApiKeySchema: z.ZodString;
/**
 * Validate OpenAI API key format
 */
export declare const openAiApiKeySchema: z.ZodString;
/**
 * Validate port number
 */
export declare const portSchema: z.ZodNumber;
/**
 * Validate timeout value
 */
export declare const timeoutSchema: z.ZodNumber;
/**
 * Validate positive integer
 */
export declare const positiveIntSchema: z.ZodNumber;
/**
 * Validate non-negative integer
 */
export declare const nonNegativeIntSchema: z.ZodNumber;
/**
 * Validate temperature value for AI models
 */
export declare const temperatureSchema: z.ZodNumber;
/**
 * Validate max tokens value
 */
export declare const maxTokensSchema: z.ZodNumber;
/**
 * Validate model name
 */
export declare const modelNameSchema: z.ZodString;
/**
 * Validate email address
 */
export declare const emailSchema: z.ZodString;
/**
 * Validate JSON string
 */
export declare const jsonStringSchema: z.ZodEffects<z.ZodString, string, string>;
/**
 * Validate semantic version
 */
export declare const semverSchema: z.ZodString;
/**
 * Validate hex color
 */
export declare const hexColorSchema: z.ZodString;
/**
 * Validate file extension
 */
export declare const fileExtensionSchema: z.ZodString;
/**
 * Validate directory path
 */
export declare const directoryPathSchema: z.ZodString;
/**
 * Validate command name (for shell commands)
 */
export declare const commandNameSchema: z.ZodString;
/**
 * Validate environment variable name
 */
export declare const envVarNameSchema: z.ZodString;
/**
 * Create validation function from schema
 */
export declare function createValidator<T>(schema: z.ZodSchema<T>): (value: unknown) => {
    success: true;
    data: T;
} | {
    success: false;
    error: string;
};
/**
 * Validate and parse JSON safely with type checking
 */
export declare function validateJSON<T = unknown>(jsonString: string, schema?: z.ZodSchema<T>): {
    success: true;
    data: T;
} | {
    success: false;
    error: string;
};
/**
 * Validate object against schema and return result
 */
export declare function validateObject<T>(obj: unknown, schema: z.ZodSchema<T>): {
    success: true;
    data: T;
} | {
    success: false;
    errors: string[];
};
/**
 * Sanitize and validate user input
 */
export declare function sanitizeInput(input: string, options?: {
    maxLength?: number;
    allowedChars?: RegExp;
    trim?: boolean;
    toLowerCase?: boolean;
    toUpperCase?: boolean;
}): string;
/**
 * Validate array of values against schema
 */
export declare function validateArray<T>(array: unknown[], itemSchema: z.ZodSchema<T>): {
    success: true;
    data: T[];
} | {
    success: false;
    errors: Array<{
        index: number;
        error: string;
    }>;
};
/**
 * Create a union schema from an array of possible values
 */
export declare function createEnumSchema<T extends readonly [string, ...string[]]>(values: T): z.ZodEnum<z.Writeable<T>>;
/**
 * Create optional schema with default value
 */
export declare function createOptionalWithDefault<T>(schema: z.ZodSchema<T>, defaultValue: T): z.ZodDefault<z.ZodOptional<z.ZodType<T, z.ZodTypeDef, T>>>;
/**
 * Validate configuration object with detailed error reporting
 */
export declare function validateConfig<T>(config: unknown, schema: z.ZodSchema<T>, configName?: string): T;
//# sourceMappingURL=validation.d.ts.map