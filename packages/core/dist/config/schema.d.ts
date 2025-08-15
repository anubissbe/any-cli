/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */
import { z } from "zod";
/**
 * Tool configuration schema
 */
export declare const ToolConfigSchema: z.ZodObject<{
    safetyLevel: z.ZodDefault<z.ZodEnum<["safe", "cautious", "dangerous"]>>;
    confirmDestructive: z.ZodDefault<z.ZodBoolean>;
    timeout: z.ZodDefault<z.ZodNumber>;
    maxRetries: z.ZodDefault<z.ZodNumber>;
}, "strip", z.ZodTypeAny, {
    timeout: number;
    safetyLevel: "safe" | "cautious" | "dangerous";
    confirmDestructive: boolean;
    maxRetries: number;
}, {
    timeout?: number | undefined;
    safetyLevel?: "safe" | "cautious" | "dangerous" | undefined;
    confirmDestructive?: boolean | undefined;
    maxRetries?: number | undefined;
}>;
/**
 * UI configuration schema
 */
export declare const UIConfigSchema: z.ZodObject<{
    theme: z.ZodDefault<z.ZodString>;
    colorOutput: z.ZodDefault<z.ZodBoolean>;
    spinner: z.ZodDefault<z.ZodBoolean>;
    progressBar: z.ZodDefault<z.ZodBoolean>;
}, "strip", z.ZodTypeAny, {
    theme: string;
    colorOutput: boolean;
    spinner: boolean;
    progressBar: boolean;
}, {
    theme?: string | undefined;
    colorOutput?: boolean | undefined;
    spinner?: boolean | undefined;
    progressBar?: boolean | undefined;
}>;
/**
 * Network configuration schema
 */
export declare const NetworkConfigSchema: z.ZodObject<{
    timeout: z.ZodDefault<z.ZodNumber>;
    retries: z.ZodDefault<z.ZodNumber>;
    userAgent: z.ZodDefault<z.ZodString>;
    proxy: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    timeout: number;
    retries: number;
    userAgent: string;
    proxy?: string | undefined;
}, {
    timeout?: number | undefined;
    retries?: number | undefined;
    userAgent?: string | undefined;
    proxy?: string | undefined;
}>;
/**
 * Main application configuration schema
 */
export declare const AppConfigSchema: z.ZodObject<{
    version: z.ZodString;
    debug: z.ZodDefault<z.ZodBoolean>;
    logLevel: z.ZodDefault<z.ZodEnum<["debug", "info", "warn", "error"]>>;
    interactive: z.ZodDefault<z.ZodBoolean>;
    configDir: z.ZodString;
    dataDir: z.ZodString;
    cacheDir: z.ZodString;
    providers: z.ZodDefault<z.ZodArray<z.ZodObject<{
        name: z.ZodString;
        type: z.ZodEnum<["local", "remote"]>;
        priority: z.ZodNumber;
        enabled: z.ZodBoolean;
        auth: z.ZodObject<{
            type: z.ZodEnum<["api_key", "oauth", "none"]>;
            apiKey: z.ZodOptional<z.ZodString>;
            baseUrl: z.ZodOptional<z.ZodString>;
            headers: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodString>>;
        }, "strip", z.ZodTypeAny, {
            type: "none" | "api_key" | "oauth";
            apiKey?: string | undefined;
            baseUrl?: string | undefined;
            headers?: Record<string, string> | undefined;
        }, {
            type: "none" | "api_key" | "oauth";
            apiKey?: string | undefined;
            baseUrl?: string | undefined;
            headers?: Record<string, string> | undefined;
        }>;
        models: z.ZodArray<z.ZodString, "many">;
        endpoint: z.ZodOptional<z.ZodString>;
        timeout: z.ZodOptional<z.ZodNumber>;
        retries: z.ZodOptional<z.ZodNumber>;
    }, "strip", z.ZodTypeAny, {
        type: "local" | "remote";
        name: string;
        priority: number;
        enabled: boolean;
        auth: {
            type: "none" | "api_key" | "oauth";
            apiKey?: string | undefined;
            baseUrl?: string | undefined;
            headers?: Record<string, string> | undefined;
        };
        models: string[];
        endpoint?: string | undefined;
        timeout?: number | undefined;
        retries?: number | undefined;
    }, {
        type: "local" | "remote";
        name: string;
        priority: number;
        enabled: boolean;
        auth: {
            type: "none" | "api_key" | "oauth";
            apiKey?: string | undefined;
            baseUrl?: string | undefined;
            headers?: Record<string, string> | undefined;
        };
        models: string[];
        endpoint?: string | undefined;
        timeout?: number | undefined;
        retries?: number | undefined;
    }>, "many">>;
    defaultProvider: z.ZodOptional<z.ZodString>;
    tools: z.ZodDefault<z.ZodObject<{
        safetyLevel: z.ZodDefault<z.ZodEnum<["safe", "cautious", "dangerous"]>>;
        confirmDestructive: z.ZodDefault<z.ZodBoolean>;
        timeout: z.ZodDefault<z.ZodNumber>;
        maxRetries: z.ZodDefault<z.ZodNumber>;
    }, "strip", z.ZodTypeAny, {
        timeout: number;
        safetyLevel: "safe" | "cautious" | "dangerous";
        confirmDestructive: boolean;
        maxRetries: number;
    }, {
        timeout?: number | undefined;
        safetyLevel?: "safe" | "cautious" | "dangerous" | undefined;
        confirmDestructive?: boolean | undefined;
        maxRetries?: number | undefined;
    }>>;
    ui: z.ZodDefault<z.ZodObject<{
        theme: z.ZodDefault<z.ZodString>;
        colorOutput: z.ZodDefault<z.ZodBoolean>;
        spinner: z.ZodDefault<z.ZodBoolean>;
        progressBar: z.ZodDefault<z.ZodBoolean>;
    }, "strip", z.ZodTypeAny, {
        theme: string;
        colorOutput: boolean;
        spinner: boolean;
        progressBar: boolean;
    }, {
        theme?: string | undefined;
        colorOutput?: boolean | undefined;
        spinner?: boolean | undefined;
        progressBar?: boolean | undefined;
    }>>;
    network: z.ZodDefault<z.ZodObject<{
        timeout: z.ZodDefault<z.ZodNumber>;
        retries: z.ZodDefault<z.ZodNumber>;
        userAgent: z.ZodDefault<z.ZodString>;
        proxy: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        timeout: number;
        retries: number;
        userAgent: string;
        proxy?: string | undefined;
    }, {
        timeout?: number | undefined;
        retries?: number | undefined;
        userAgent?: string | undefined;
        proxy?: string | undefined;
    }>>;
}, "strip", z.ZodTypeAny, {
    debug: boolean;
    version: string;
    network: {
        timeout: number;
        retries: number;
        userAgent: string;
        proxy?: string | undefined;
    };
    logLevel: "debug" | "info" | "warn" | "error";
    interactive: boolean;
    configDir: string;
    dataDir: string;
    cacheDir: string;
    providers: {
        type: "local" | "remote";
        name: string;
        priority: number;
        enabled: boolean;
        auth: {
            type: "none" | "api_key" | "oauth";
            apiKey?: string | undefined;
            baseUrl?: string | undefined;
            headers?: Record<string, string> | undefined;
        };
        models: string[];
        endpoint?: string | undefined;
        timeout?: number | undefined;
        retries?: number | undefined;
    }[];
    tools: {
        timeout: number;
        safetyLevel: "safe" | "cautious" | "dangerous";
        confirmDestructive: boolean;
        maxRetries: number;
    };
    ui: {
        theme: string;
        colorOutput: boolean;
        spinner: boolean;
        progressBar: boolean;
    };
    defaultProvider?: string | undefined;
}, {
    version: string;
    configDir: string;
    dataDir: string;
    cacheDir: string;
    debug?: boolean | undefined;
    network?: {
        timeout?: number | undefined;
        retries?: number | undefined;
        userAgent?: string | undefined;
        proxy?: string | undefined;
    } | undefined;
    logLevel?: "debug" | "info" | "warn" | "error" | undefined;
    interactive?: boolean | undefined;
    providers?: {
        type: "local" | "remote";
        name: string;
        priority: number;
        enabled: boolean;
        auth: {
            type: "none" | "api_key" | "oauth";
            apiKey?: string | undefined;
            baseUrl?: string | undefined;
            headers?: Record<string, string> | undefined;
        };
        models: string[];
        endpoint?: string | undefined;
        timeout?: number | undefined;
        retries?: number | undefined;
    }[] | undefined;
    defaultProvider?: string | undefined;
    tools?: {
        timeout?: number | undefined;
        safetyLevel?: "safe" | "cautious" | "dangerous" | undefined;
        confirmDestructive?: boolean | undefined;
        maxRetries?: number | undefined;
    } | undefined;
    ui?: {
        theme?: string | undefined;
        colorOutput?: boolean | undefined;
        spinner?: boolean | undefined;
        progressBar?: boolean | undefined;
    } | undefined;
}>;
/**
 * Type inference from schema
 */
export type AppConfig = z.infer<typeof AppConfigSchema>;
export type ToolConfig = z.infer<typeof ToolConfigSchema>;
export type UIConfig = z.infer<typeof UIConfigSchema>;
export type NetworkConfig = z.infer<typeof NetworkConfigSchema>;
//# sourceMappingURL=schema.d.ts.map