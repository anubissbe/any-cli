/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */
import type { ModelInfo, ChatCompletionRequest, ChatCompletionResponse, ChatCompletionChunk, CancellationToken, Result } from "@qwen-claude/core";
import { HttpProvider } from "../base/http-provider.js";
/**
 * Qwen local model provider
 */
export declare class QwenProvider extends HttpProvider {
    private static readonly DEFAULT_MODELS;
    protected doInitialize(): Promise<void>;
    protected doHealthCheck(): Promise<void>;
    getModels(): Promise<Result<ReadonlyArray<ModelInfo>>>;
    chatCompletion(request: ChatCompletionRequest, cancellationToken?: CancellationToken): Promise<Result<ChatCompletionResponse>>;
    chatCompletionStream(request: ChatCompletionRequest, cancellationToken?: CancellationToken): AsyncIterable<Result<ChatCompletionChunk>>;
    /**
     * Transform our request format to Qwen's expected format
     */
    private transformRequest;
    /**
     * Transform Qwen's response to our format
     */
    private transformResponse;
    /**
     * Transform Qwen's stream chunk to our format
     */
    private transformStreamChunk;
    /**
     * Map Qwen's finish reasons to our format
     */
    private mapFinishReason;
    /**
     * Get model capabilities based on model ID
     */
    private getModelCapabilities;
}
//# sourceMappingURL=qwen-provider.d.ts.map