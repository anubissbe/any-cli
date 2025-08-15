/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */
import type { ModelInfo, ChatCompletionRequest, ChatCompletionResponse, ChatCompletionChunk, CancellationToken, Result } from "@qwen-claude/core";
import { HttpProvider } from "../base/http-provider.js";
/**
 * OpenRouter provider for accessing multiple models
 */
export declare class OpenRouterProvider extends HttpProvider {
    private modelsCache;
    private modelsCacheExpiry;
    private static readonly CACHE_DURATION;
    protected doInitialize(): Promise<void>;
    protected doHealthCheck(): Promise<void>;
    getModels(): Promise<Result<ReadonlyArray<ModelInfo>>>;
    chatCompletion(request: ChatCompletionRequest, cancellationToken?: CancellationToken): Promise<Result<ChatCompletionResponse>>;
    chatCompletionStream(request: ChatCompletionRequest, cancellationToken?: CancellationToken): AsyncIterable<Result<ChatCompletionChunk>>;
    /**
     * Check if model is supported by our configuration
     */
    private isModelSupported;
    /**
     * Transform OpenRouter model to our format
     */
    private transformModel;
    /**
     * Get model capabilities from OpenRouter model info
     */
    private getModelCapabilities;
    /**
     * Get model pricing from OpenRouter model info
     */
    private getModelPricing;
    /**
     * Check if model supports tools/function calling
     */
    private modelSupportsTools;
    /**
     * Check if model supports images
     */
    private modelSupportsImages;
    /**
     * Check if model supports code generation
     */
    private modelSupportsCodeGeneration;
    /**
     * Transform our request format to OpenRouter's expected format
     */
    private transformRequest;
    /**
     * Transform OpenRouter's response to our format
     */
    private transformResponse;
    /**
     * Transform OpenRouter's stream chunk to our format
     */
    private transformStreamChunk;
    /**
     * Map OpenRouter's finish reasons to our format
     */
    private mapFinishReason;
}
//# sourceMappingURL=openrouter-provider.d.ts.map