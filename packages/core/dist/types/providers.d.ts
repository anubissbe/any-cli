/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */
import { z } from "zod";
import type { CancellationToken, Result } from "./common.js";
import type { ChatCompletionRequest, ChatCompletionResponse, ChatCompletionChunk, ModelInfo } from "./models.js";
/**
 * Provider authentication configuration
 */
export interface ProviderAuth {
    readonly type: "api_key" | "oauth" | "none";
    readonly apiKey?: string;
    readonly baseUrl?: string;
    readonly headers?: Record<string, string>;
}
/**
 * Model capabilities
 */
export interface ModelCapabilities {
    supportsStreaming: boolean;
    supportsTools: boolean;
    supportsVision: boolean;
    maxTokens: number;
    contextWindow: number;
}
/**
 * Provider configuration
 */
export interface ProviderConfig {
    readonly name: string;
    readonly type: "local" | "remote";
    readonly priority: number;
    readonly enabled: boolean;
    readonly auth: ProviderAuth;
    readonly models: string[];
    readonly endpoint?: string;
    readonly timeout?: number;
    readonly retries?: number;
}
/**
 * Provider health status
 */
export interface ProviderHealth {
    readonly isHealthy: boolean;
    readonly latency?: number;
    readonly error?: string;
    readonly lastChecked: Date;
}
/**
 * Provider interface that all model providers must implement
 */
export interface ModelProvider {
    readonly name: string;
    readonly type: "local" | "remote";
    readonly isAvailable: boolean;
    /**
     * Initialize the provider
     */
    initialize(): Promise<Result<void>>;
    /**
     * Get available models
     */
    getModels(): Promise<Result<ReadonlyArray<ModelInfo>>>;
    /**
     * Check provider health
     */
    checkHealth(): Promise<ProviderHealth>;
    /**
     * Send chat completion request
     */
    chatCompletion(request: ChatCompletionRequest, cancellationToken?: CancellationToken): Promise<Result<ChatCompletionResponse>>;
    /**
     * Send streaming chat completion request
     */
    chatCompletionStream(request: ChatCompletionRequest, cancellationToken?: CancellationToken): AsyncIterable<Result<ChatCompletionChunk>>;
    /**
     * Clean up resources
     */
    dispose(): Promise<void>;
}
/**
 * Provider factory for creating provider instances
 */
export interface ProviderFactory {
    readonly name: string;
    readonly supportedTypes: ReadonlyArray<string>;
    create(config: ProviderConfig): Promise<Result<ModelProvider>>;
    validateConfig(config: unknown): Result<ProviderConfig>;
}
/**
 * Provider registry for managing multiple providers
 */
export interface ProviderRegistry {
    /**
     * Register a provider factory
     */
    register(factory: ProviderFactory): void;
    /**
     * Create provider instance from config
     */
    create(config: ProviderConfig): Promise<Result<ModelProvider>>;
    /**
     * Get all registered provider names
     */
    getRegisteredProviders(): ReadonlyArray<string>;
    /**
     * Validate provider configuration
     */
    validateConfig(config: unknown): Result<ProviderConfig>;
}
/**
 * Provider selection strategy
 */
export type ProviderSelectionStrategy = "first-available" | "fastest" | "cheapest" | "most-capable" | "random";
/**
 * Provider manager for handling multiple providers
 */
export interface ProviderManager {
    /**
     * Initialize all configured providers
     */
    initialize(): Promise<Result<void>>;
    /**
     * Get the best provider based on strategy
     */
    getBestProvider(strategy?: ProviderSelectionStrategy, requirements?: Partial<ModelCapabilities>): Promise<Result<ModelProvider>>;
    /**
     * Get all available providers
     */
    getAvailableProviders(): ReadonlyArray<ModelProvider>;
    /**
     * Health check all providers
     */
    healthCheck(): Promise<ReadonlyArray<ProviderHealth>>;
    /**
     * Dispose all providers
     */
    dispose(): Promise<void>;
}
/**
 * Validation schemas
 */
export declare const ProviderAuthSchema: z.ZodObject<{
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
export declare const ProviderConfigSchema: z.ZodObject<{
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
}>;
//# sourceMappingURL=providers.d.ts.map