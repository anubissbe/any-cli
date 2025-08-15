/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */

import type {
  ModelProvider,
  ProviderConfig,
  ProviderHealth,
  ModelInfo,
  ChatCompletionRequest,
  ChatCompletionResponse,
  ChatCompletionChunk,
  CancellationToken,
  Result,
} from "@qwen-claude/core";
import { ProviderError, ProviderUnavailableError } from "@qwen-claude/core";

/**
 * Abstract base class for model providers
 */
export abstract class BaseProvider implements ModelProvider {
  public readonly name: string;
  public readonly type: "local" | "remote";
  protected readonly config: ProviderConfig;
  protected initialized = false;

  constructor(config: ProviderConfig) {
    this.config = config;
    this.name = config.name;
    this.type = config.type;
  }

  public get isAvailable(): boolean {
    return this.initialized && this.config.enabled;
  }

  /**
   * Initialize the provider
   */
  public async initialize(): Promise<Result<void>> {
    try {
      await this.doInitialize();
      this.initialized = true;
      return { success: true, data: undefined };
    } catch (error) {
      return {
        success: false,
        error: new ProviderError(
          `Failed to initialize provider ${this.name}`,
          this.name,
          undefined,
          undefined,
          error instanceof Error ? error : new Error(String(error)),
        ),
      };
    }
  }

  /**
   * Get available models
   */
  public abstract getModels(): Promise<Result<ReadonlyArray<ModelInfo>>>;

  /**
   * Check provider health
   */
  public async checkHealth(): Promise<ProviderHealth> {
    const startTime = Date.now();

    try {
      await this.doHealthCheck();
      return {
        isHealthy: true,
        latency: Date.now() - startTime,
        lastChecked: new Date(),
      };
    } catch (error) {
      return {
        isHealthy: false,
        error: error instanceof Error ? error.message : String(error),
        lastChecked: new Date(),
      };
    }
  }

  /**
   * Send chat completion request
   */
  public abstract chatCompletion(
    request: ChatCompletionRequest,
    cancellationToken?: CancellationToken,
  ): Promise<Result<ChatCompletionResponse>>;

  /**
   * Send streaming chat completion request
   */
  public abstract chatCompletionStream(
    request: ChatCompletionRequest,
    cancellationToken?: CancellationToken,
  ): AsyncIterable<Result<ChatCompletionChunk>>;

  /**
   * Clean up resources
   */
  public async dispose(): Promise<void> {
    await this.doDispose();
    this.initialized = false;
  }

  /**
   * Validate that provider is available
   */
  protected validateAvailable(): void {
    if (!this.isAvailable) {
      throw new ProviderUnavailableError(
        this.name,
        "Provider is not initialized or disabled",
      );
    }
  }

  /**
   * Handle cancellation token
   */
  protected setupCancellation(
    cancellationToken?: CancellationToken,
  ): AbortController {
    const controller = new AbortController();

    if (cancellationToken) {
      if (cancellationToken.isCancelled) {
        controller.abort();
      } else {
        cancellationToken.onCancelled(() => controller.abort());
      }
    }

    return controller;
  }

  /**
   * Abstract methods for subclasses to implement
   */
  protected abstract doInitialize(): Promise<void>;
  protected abstract doHealthCheck(): Promise<void>;
  protected abstract doDispose(): Promise<void>;
}
