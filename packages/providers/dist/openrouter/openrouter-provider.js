/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */
import { HttpProvider } from "../base/http-provider.js";
import { validateJSON } from "@qwen-claude/utils";
/**
 * OpenRouter provider for accessing multiple models
 */
export class OpenRouterProvider extends HttpProvider {
    modelsCache = null;
    modelsCacheExpiry = 0;
    static CACHE_DURATION = 5 * 60 * 1000; // 5 minutes
    async doInitialize() {
        // Test connection and authentication
        await this.doHealthCheck();
    }
    async doHealthCheck() {
        const response = await this.makeRequest({
            method: "GET",
            url: "/api/v1/models",
            timeout: 5000,
        });
        if (!response.success) {
            throw response.error;
        }
    }
    async getModels() {
        this.validateAvailable();
        // Return cached models if still valid
        if (this.modelsCache && Date.now() < this.modelsCacheExpiry) {
            return { success: true, data: this.modelsCache };
        }
        try {
            const response = await this.makeRequest({
                method: "GET",
                url: "/api/v1/models",
            });
            if (!response.success) {
                return response;
            }
            const models = response.data.data
                .filter((model) => this.isModelSupported(model))
                .map((model) => this.transformModel(model));
            // Cache the results
            this.modelsCache = models;
            this.modelsCacheExpiry = Date.now() + OpenRouterProvider.CACHE_DURATION;
            return { success: true, data: models };
        }
        catch (error) {
            return {
                success: false,
                error: error instanceof Error ? error : new Error(String(error)),
            };
        }
    }
    async chatCompletion(request, cancellationToken) {
        this.validateAvailable();
        const openRouterRequest = this.transformRequest(request);
        const response = await this.makeRequest({
            method: "POST",
            url: "/api/v1/chat/completions",
            data: openRouterRequest,
        }, cancellationToken);
        if (!response.success) {
            return response;
        }
        const transformed = this.transformResponse(response.data.data);
        return { success: true, data: transformed };
    }
    async *chatCompletionStream(request, cancellationToken) {
        this.validateAvailable();
        const openRouterRequest = this.transformRequest({
            ...request,
            stream: true,
        });
        for await (const result of this.makeStreamingRequest({
            method: "POST",
            url: "/api/v1/chat/completions",
            data: openRouterRequest,
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
     * Check if model is supported by our configuration
     */
    isModelSupported(model) {
        return (this.config.models.length === 0 || this.config.models.includes(model.id));
    }
    /**
     * Transform OpenRouter model to our format
     */
    transformModel(model) {
        return {
            id: model.id,
            name: model.name || model.id,
            description: model.description || `OpenRouter model: ${model.id}`,
            provider: this.name,
            version: "1.0.0",
            capabilities: this.getModelCapabilities(model),
            pricing: this.getModelPricing(model),
            isLocal: false,
        };
    }
    /**
     * Get model capabilities from OpenRouter model info
     */
    getModelCapabilities(model) {
        const maxTokens = model.top_provider.max_completion_tokens ||
            parseInt(model.per_request_limits?.completion_tokens || "4096", 10);
        return {
            supportsStreaming: true,
            supportsTools: this.modelSupportsTools(model.id),
            supportsImages: this.modelSupportsImages(model.id),
            supportsCodeGeneration: this.modelSupportsCodeGeneration(model.id),
            maxTokens,
            contextWindow: model.context_length || model.top_provider.context_length,
        };
    }
    /**
     * Get model pricing from OpenRouter model info
     */
    getModelPricing(model) {
        return {
            inputTokenPrice: parseFloat(model.pricing.prompt) * 1000, // Convert to per 1k tokens
            outputTokenPrice: parseFloat(model.pricing.completion) * 1000,
            currency: "USD",
        };
    }
    /**
     * Check if model supports tools/function calling
     */
    modelSupportsTools(modelId) {
        const toolSupportedModels = [
            "openai/gpt-4",
            "openai/gpt-3.5-turbo",
            "anthropic/claude-3",
            "anthropic/claude-3.5",
        ];
        return toolSupportedModels.some((pattern) => modelId.includes(pattern));
    }
    /**
     * Check if model supports images
     */
    modelSupportsImages(modelId) {
        const imageSupportedModels = [
            "openai/gpt-4o",
            "anthropic/claude-3",
            "google/gemini",
        ];
        return imageSupportedModels.some((pattern) => modelId.includes(pattern));
    }
    /**
     * Check if model supports code generation
     */
    modelSupportsCodeGeneration(modelId) {
        const codingModels = ["coder", "code", "deepseek", "qwen", "codestral"];
        return codingModels.some((pattern) => modelId.toLowerCase().includes(pattern));
    }
    /**
     * Transform our request format to OpenRouter's expected format
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
     * Transform OpenRouter's response to our format
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
            toolCalls: choice.message.tool_calls?.map((call) => {
                const argsResult = validateJSON(call.function.arguments);
                if (!argsResult.success) {
                    console.warn(`Failed to parse tool call arguments: ${argsResult.error}`);
                    return {
                        id: call.id,
                        name: call.function.name,
                        arguments: {},
                    };
                }
                return {
                    id: call.id,
                    name: call.function.name,
                    arguments: argsResult.data,
                };
            }),
        };
    }
    /**
     * Transform OpenRouter's stream chunk to our format
     */
    transformStreamChunk(chunk) {
        const choice = chunk.choices[0];
        return {
            id: chunk.id,
            model: chunk.model,
            delta: {
                role: choice.delta.role,
                content: choice.delta.content,
                toolCalls: choice.delta.tool_calls?.map((call) => {
                    if (!call.function?.arguments) {
                        return {
                            id: call.id,
                            name: call.function?.name,
                            arguments: undefined,
                        };
                    }
                    const argsResult = validateJSON(call.function.arguments);
                    if (!argsResult.success) {
                        console.warn(`Failed to parse streaming tool call arguments: ${argsResult.error}`);
                        return {
                            id: call.id,
                            name: call.function.name,
                            arguments: {},
                        };
                    }
                    return {
                        id: call.id,
                        name: call.function.name,
                        arguments: argsResult.data,
                    };
                }),
            },
            finishReason: choice.finish_reason
                ? this.mapFinishReason(choice.finish_reason)
                : undefined,
        };
    }
    /**
     * Map OpenRouter's finish reasons to our format
     */
    mapFinishReason(reason) {
        switch (reason) {
            case "stop":
                return "stop";
            case "length":
                return "length";
            case "tool_calls":
            case "function_call":
                return "tool_calls";
            case "content_filter":
                return "content_filter";
            default:
                return "stop";
        }
    }
}
//# sourceMappingURL=openrouter-provider.js.map