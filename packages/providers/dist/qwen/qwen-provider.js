/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */
import { HttpProvider } from "../base/http-provider.js";
/**
 * Qwen local model provider
 */
export class QwenProvider extends HttpProvider {
    static DEFAULT_MODELS = [
        "qwen3-coder-30b",
        "qwen2.5-coder-32b-instruct",
        "qwen2.5-72b-instruct",
    ];
    async doInitialize() {
        // Test connection to Qwen server
        await this.doHealthCheck();
    }
    async doHealthCheck() {
        const response = await this.makeRequest({
            method: "GET",
            url: "/v1/models",
            timeout: 5000,
        });
        if (!response.success) {
            throw response.error;
        }
    }
    async getModels() {
        this.validateAvailable();
        try {
            const response = await this.makeRequest({
                method: "GET",
                url: "/v1/models",
            });
            if (!response.success) {
                return response;
            }
            const models = response.data.data.map((model) => ({
                id: model.id,
                name: model.id,
                description: `Qwen local model: ${model.id}`,
                provider: this.name,
                version: "1.0.0",
                capabilities: this.getModelCapabilities(model.id),
                isLocal: true,
            }));
            return { success: true, data: models };
        }
        catch (error) {
            // Fallback to default models if API doesn't support model listing
            const defaultModels = QwenProvider.DEFAULT_MODELS.map((modelId) => ({
                id: modelId,
                name: modelId,
                description: `Qwen local model: ${modelId}`,
                provider: this.name,
                version: "1.0.0",
                capabilities: this.getModelCapabilities(modelId),
                isLocal: true,
            }));
            return { success: true, data: defaultModels };
        }
    }
    async chatCompletion(request, cancellationToken) {
        this.validateAvailable();
        const qwenRequest = this.transformRequest(request);
        const response = await this.makeRequest({
            method: "POST",
            url: "/v1/chat/completions",
            data: qwenRequest,
        }, cancellationToken);
        if (!response.success) {
            return response;
        }
        const transformed = this.transformResponse(response.data.data);
        return { success: true, data: transformed };
    }
    async *chatCompletionStream(request, cancellationToken) {
        this.validateAvailable();
        const qwenRequest = this.transformRequest({ ...request, stream: true });
        for await (const result of this.makeStreamingRequest({
            method: "POST",
            url: "/v1/chat/completions",
            data: qwenRequest,
        }, cancellationToken)) {
            if (!result.success) {
                yield result;
                continue;
            }
            const transformed = this.transformStreamChunk(result.data);
            yield { success: true, data: transformed };
        }
    }
    /**
     * Transform our request format to Qwen's expected format
     */
    transformRequest(request) {
        return {
            model: request.model,
            messages: request.messages.map((msg) => ({
                role: msg.role,
                content: msg.content,
            })),
            temperature: request.temperature,
            max_tokens: request.maxTokens,
            stream: request.stream,
            tools: request.tools?.map((tool) => ({
                type: tool.type,
                function: {
                    name: tool.function.name,
                    description: tool.function.description,
                    parameters: tool.function.parameters,
                },
            })),
            tool_choice: request.toolChoice,
            stop: request.stop,
        };
    }
    /**
     * Transform Qwen's response to our format
     */
    transformResponse(response) {
        const choice = response.choices[0];
        return {
            id: response.id,
            model: response.model,
            message: {
                role: choice.message.role,
                content: choice.message.content,
                timestamp: new Date(),
            },
            finishReason: this.mapFinishReason(choice.finish_reason),
            usage: {
                promptTokens: response.usage.prompt_tokens,
                completionTokens: response.usage.completion_tokens,
                totalTokens: response.usage.total_tokens,
            },
            toolCalls: choice.message.tool_calls?.map((call) => ({
                id: call.id,
                name: call.function.name,
                arguments: JSON.parse(call.function.arguments),
            })),
        };
    }
    /**
     * Transform Qwen's stream chunk to our format
     */
    transformStreamChunk(chunk) {
        const choice = chunk.choices[0];
        return {
            id: chunk.id,
            model: chunk.model,
            delta: {
                role: choice.delta.role,
                content: choice.delta.content,
                toolCalls: choice.delta.tool_calls?.map((call) => ({
                    id: call.id,
                    name: call.function?.name,
                    arguments: call.function?.arguments
                        ? JSON.parse(call.function.arguments)
                        : undefined,
                })),
            },
            finishReason: choice.finish_reason
                ? this.mapFinishReason(choice.finish_reason)
                : undefined,
        };
    }
    /**
     * Map Qwen's finish reasons to our format
     */
    mapFinishReason(reason) {
        switch (reason) {
            case "stop":
                return "stop";
            case "length":
                return "length";
            case "tool_calls":
                return "tool_calls";
            case "content_filter":
                return "content_filter";
            default:
                return "stop";
        }
    }
    /**
     * Get model capabilities based on model ID
     */
    getModelCapabilities(modelId) {
        // Base capabilities for Qwen models
        const baseCapabilities = {
            supportsStreaming: true,
            supportsTools: true,
            supportsImages: false,
            supportsCodeGeneration: true,
            maxTokens: 8192,
            contextWindow: 32768,
        };
        // Adjust capabilities based on specific model
        if (modelId.includes("coder")) {
            return {
                ...baseCapabilities,
                supportsCodeGeneration: true,
                maxTokens: 16384,
                contextWindow: 131072, // 128k context for coder models
            };
        }
        if (modelId.includes("72b")) {
            return {
                ...baseCapabilities,
                maxTokens: 32768,
                contextWindow: 131072,
            };
        }
        return baseCapabilities;
    }
}
//# sourceMappingURL=qwen-provider.js.map