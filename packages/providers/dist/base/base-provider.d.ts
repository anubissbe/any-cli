/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */
import type { ModelProvider, ProviderConfig, ProviderHealth, ModelInfo, ChatCompletionRequest, ChatCompletionResponse, ChatCompletionChunk, CancellationToken, Result } from "@qwen-claude/core";
/**
 * Abstract base class for model providers
 */
export declare abstract class BaseProvider implements ModelProvider {
    readonly name: string;
    readonly type: "local" | "remote";
    protected readonly config: ProviderConfig;
    protected initialized: boolean;
    constructor(config: ProviderConfig);
    get isAvailable(): boolean;
    /**
     * Initialize the provider
     */
    initialize(): Promise<Result<void>>;
    /**
     * Get available models
     */
    abstract getModels(): Promise<Result<ReadonlyArray<ModelInfo>>>;
    /**
     * Check provider health
     */
    checkHealth(): Promise<ProviderHealth>;
    /**
     * Send chat completion request
     */
    abstract chatCompletion(request: ChatCompletionRequest, cancellationToken?: CancellationToken): Promise<Result<ChatCompletionResponse>>;
    /**
     * Send streaming chat completion request
     */
    abstract chatCompletionStream(request: ChatCompletionRequest, cancellationToken?: CancellationToken): AsyncIterable<Result<ChatCompletionChunk>>;
    /**
     * Clean up resources
     */
    dispose(): Promise<void>;
    /**
     * Validate that provider is available
     */
    protected validateAvailable(): void;
    /**
     * Handle cancellation token
     */
    protected setupCancellation(cancellationToken?: CancellationToken): AbortController;
    /**
     * Abstract methods for subclasses to implement
     */
    protected abstract doInitialize(): Promise<void>;
    protected abstract doHealthCheck(): Promise<void>;
    protected abstract doDispose(): Promise<void>;
}
//# sourceMappingURL=base-provider.d.ts.map