/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */

import axios, {
  type AxiosInstance,
  type AxiosRequestConfig,
  type AxiosResponse,
} from "axios";
import type {
  ProviderConfig,
  CancellationToken,
  Result,
} from "@qwen-claude/core";
import {
  ProviderError,
  ProviderAuthError,
  ProviderRateLimitError,
  ProviderQuotaError,
  ProviderInvalidResponseError,
  TimeoutError,
  CancellationError,
} from "@qwen-claude/core";
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
export abstract class HttpProvider extends BaseProvider {
  protected client: AxiosInstance;
  private responseCache = new Map<string, { data: unknown; timestamp: number }>();
  private readonly CACHE_TTL = 60000; // 1 minute cache TTL

  constructor(config: ProviderConfig) {
    super(config);
    this.client = this.createHttpClient();
  }

  /**
   * Create HTTP client with configuration
   */
  protected createHttpClient(): AxiosInstance {
    const client = axios.create({
      baseURL: this.config.auth.baseUrl,
      timeout: this.config.timeout || 30000,
      maxRedirects: 5,
      maxContentLength: 50 * 1024 * 1024, // 50MB limit
      maxBodyLength: 50 * 1024 * 1024, // 50MB limit
      headers: {
        "Content-Type": "application/json",
        "User-Agent": "qwen-claude-cli/0.1.0",
        "Connection": "keep-alive",
        "Keep-Alive": "timeout=30, max=100",
        ...this.config.auth.headers,
      },
      // Performance optimizations
      validateStatus: (status) => status < 500, // Don't reject on 4xx errors, handle them properly
      transitional: {
        silentJSONParsing: false, // Throw errors for invalid JSON
        forcedJSONParsing: true,
        clarifyTimeoutError: false,
      },
    });

    // Add request interceptors
    client.interceptors.request.use(
      (config) => {
        // Add authentication
        if (this.config.auth.type === "api_key" && this.config.auth.apiKey) {
          config.headers.Authorization = `Bearer ${this.config.auth.apiKey}`;
        }
        return config;
      },
      (error) => Promise.reject(error),
    );

    // Add response interceptors
    client.interceptors.response.use(
      (response) => response,
      (error) => {
        throw this.handleHttpError(error);
      },
    );

    return client;
  }

  /**
   * Make HTTP request with proper error handling
   */
  protected async makeRequest<T>(
    config: AxiosRequestConfig,
    cancellationToken?: CancellationToken,
  ): Promise<Result<HttpResponse<T>>> {
    try {
      const controller = this.setupCancellation(cancellationToken);

      const response: AxiosResponse<T> = await this.client.request({
        ...config,
        signal: controller.signal,
      });

      return {
        success: true,
        data: {
          data: response.data,
          status: response.status,
          headers: response.headers as Record<string, string>,
        },
      };
    } catch (error) {
      if (axios.isCancel(error)) {
        return {
          success: false,
          error: new CancellationError("Request was cancelled"),
        };
      }

      return {
        success: false,
        error: error instanceof Error ? error : new Error(String(error)),
      };
    }
  }

  /**
   * Get cached response if available and not expired
   */
  private getCachedResponse<T>(cacheKey: string): T | null {
    const cached = this.responseCache.get(cacheKey);
    if (cached && Date.now() - cached.timestamp < this.CACHE_TTL) {
      return cached.data as T;
    }
    if (cached) {
      this.responseCache.delete(cacheKey); // Remove expired cache
    }
    return null;
  }

  /**
   * Cache response with timestamp
   */
  private setCachedResponse(cacheKey: string, data: unknown): void {
    // Limit cache size to prevent memory leaks
    if (this.responseCache.size > 100) {
      const firstKey = this.responseCache.keys().next().value;
      if (firstKey) this.responseCache.delete(firstKey);
    }
    this.responseCache.set(cacheKey, { data, timestamp: Date.now() });
  }

  /**
   * Clear all cached responses
   */
  protected clearCache(): void {
    this.responseCache.clear();
  }

  /**
   * Make streaming request
   */
  protected async *makeStreamingRequest<T>(
    config: AxiosRequestConfig,
    cancellationToken?: CancellationToken,
  ): AsyncIterable<Result<T>> {
    try {
      const controller = this.setupCancellation(cancellationToken);

      const response = await this.client.request({
        ...config,
        responseType: "stream",
        signal: controller.signal,
      });

      const reader = response.data;
      let buffer = "";

      for await (const chunk of reader) {
        if (controller.signal.aborted) {
          yield { success: false, error: new CancellationError() };
          return;
        }

        buffer += chunk.toString();
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          const trimmed = line.trim();
          if (trimmed.startsWith("data: ")) {
            const data = trimmed.substring(6);
            if (data === "[DONE]") {
              return;
            }

            try {
              const parsed = JSON.parse(data) as T;
              yield { success: true, data: parsed };
            } catch (parseError) {
              yield {
                success: false,
                error: new ProviderInvalidResponseError(
                  this.name,
                  data,
                  undefined,
                  parseError instanceof Error
                    ? parseError
                    : new Error(String(parseError)),
                ),
              };
            }
          }
        }
      }
    } catch (error) {
      if (axios.isCancel(error)) {
        yield {
          success: false,
          error: new CancellationError("Request was cancelled"),
        };
        return;
      }

      yield {
        success: false,
        error: error instanceof Error ? error : new Error(String(error)),
      };
    }
  }

  /**
   * Handle HTTP errors and convert to appropriate provider errors
   */
  protected handleHttpError(error: unknown): Error {
    if (axios.isAxiosError(error)) {
      const status = error.response?.status;
      const message = error.response?.data?.error?.message || error.message;

      switch (status) {
        case 401:
          return new ProviderAuthError(this.name, { status, message });

        case 429:
          const retryAfter = error.response?.headers["retry-after"];
          return new ProviderRateLimitError(
            this.name,
            retryAfter ? parseInt(retryAfter, 10) : undefined,
            { status, message },
          );

        case 402:
        case 403:
          return new ProviderQuotaError(this.name, { status, message });

        case 422:
          return new ProviderInvalidResponseError(
            this.name,
            error.response?.data,
            { status, message },
          );

        default:
          if (error.code === "ECONNABORTED") {
            return new TimeoutError(
              `Request to ${this.name} timed out`,
              this.config.timeout || 30000,
              { status: status ?? null, message },
            );
          }

          return new ProviderError(
            `HTTP error from ${this.name}: ${message}`,
            this.name,
            undefined,
            { status: status ?? null, message },
          );
      }
    }

    return error instanceof Error ? error : new Error(String(error));
  }

  /**
   * Default health check implementation
   */
  protected async doHealthCheck(): Promise<void> {
    const response = await this.makeRequest({
      method: "GET",
      url: "/health",
      timeout: 5000,
    });

    if (!response.success) {
      throw response.error;
    }
  }

  /**
   * Default dispose implementation
   */
  protected async doDispose(): Promise<void> {
    // HTTP clients don't typically need explicit cleanup
  }
}
