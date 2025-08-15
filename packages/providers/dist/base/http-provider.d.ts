/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */
import { type AxiosInstance, type AxiosRequestConfig } from "axios";
import type { ProviderConfig, CancellationToken, Result } from "@qwen-claude/core";
import { BaseProvider } from "./base-provider.js";
/**
 * HTTP response wrapper
 */
export interface HttpResponse<T = unknown> {
    readonly data: T;
    readonly status: number;
    readonly headers: Record<string, string>;
}
/**
 * Base class for HTTP-based providers
 */
export declare abstract class HttpProvider extends BaseProvider {
    protected client: AxiosInstance;
    private responseCache;
    private readonly CACHE_TTL;
    constructor(config: ProviderConfig);
    /**
     * Create HTTP client with configuration
     */
    protected createHttpClient(): AxiosInstance;
    /**
     * Make HTTP request with proper error handling
     */
    protected makeRequest<T>(config: AxiosRequestConfig, cancellationToken?: CancellationToken): Promise<Result<HttpResponse<T>>>;
    /**
     * Get cached response if available and not expired
     */
    private getCachedResponse;
    /**
     * Cache response with timestamp
     */
    private setCachedResponse;
    /**
     * Clear all cached responses
     */
    protected clearCache(): void;
    /**
     * Make streaming request
     */
    protected makeStreamingRequest<T>(config: AxiosRequestConfig, cancellationToken?: CancellationToken): AsyncIterable<Result<T>>;
    /**
     * Handle HTTP errors and convert to appropriate provider errors
     */
    protected handleHttpError(error: unknown): Error;
    /**
     * Default health check implementation
     */
    protected doHealthCheck(): Promise<void>;
    /**
     * Default dispose implementation
     */
    protected doDispose(): Promise<void>;
}
//# sourceMappingURL=http-provider.d.ts.map