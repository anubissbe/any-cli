/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */

import { z } from "zod";
import type { CancellationToken, Result } from "./common.js";
import type {
  ChatCompletionRequest,
  ChatCompletionResponse,
  ChatCompletionChunk,
  ModelInfo,
} from "./models.js";

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
  chatCompletion(
    request: ChatCompletionRequest,
    cancellationToken?: CancellationToken,
  ): Promise<Result<ChatCompletionResponse>>;

  /**
   * Send streaming chat completion request
   */
  chatCompletionStream(
    request: ChatCompletionRequest,
    cancellationToken?: CancellationToken,
  ): AsyncIterable<Result<ChatCompletionChunk>>;

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
export type ProviderSelectionStrategy =
  | "first-available"
  | "fastest"
  | "cheapest"
  | "most-capable"
  | "random";

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
  getBestProvider(
    strategy?: ProviderSelectionStrategy,
    requirements?: Partial<ModelCapabilities>,
  ): Promise<Result<ModelProvider>>;

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
export const ProviderAuthSchema = z.object({
  type: z.enum(["api_key", "oauth", "none"]),
  apiKey: z.string().optional(),
  baseUrl: z.string().url().optional(),
  headers: z.record(z.string()).optional(),
});

export const ProviderConfigSchema = z.object({
  name: z.string(),
  type: z.enum(["local", "remote"]),
  priority: z.number().int().nonnegative(),
  enabled: z.boolean(),
  auth: ProviderAuthSchema,
  models: z.array(z.string()),
  endpoint: z.string().url().optional(),
  timeout: z.number().positive().optional(),
  retries: z.number().int().nonnegative().optional(),
});
