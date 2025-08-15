/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */
import { z } from "zod";
import type { JsonValue } from "./common.js";
/**
 * Model capabilities and features
 */
export interface ModelCapabilities {
    readonly supportsStreaming: boolean;
    readonly supportsTools: boolean;
    readonly supportsImages: boolean;
    readonly supportsCodeGeneration: boolean;
    readonly maxTokens: number;
    readonly contextWindow: number;
}
/**
 * Model pricing information
 */
export interface ModelPricing {
    readonly inputTokenPrice: number;
    readonly outputTokenPrice: number;
    readonly currency: string;
}
/**
 * Model metadata
 */
export interface ModelInfo {
    readonly id: string;
    readonly name: string;
    readonly description: string;
    readonly provider: string;
    readonly version: string;
    readonly capabilities: ModelCapabilities;
    readonly pricing?: ModelPricing;
    readonly isLocal: boolean;
}
/**
 * Chat message roles
 */
export type MessageRole = "system" | "user" | "assistant" | "tool";
/**
 * Individual chat message
 */
export interface ChatMessage {
    readonly role: MessageRole;
    readonly content: string;
    readonly metadata?: Record<string, JsonValue>;
    readonly timestamp?: Date;
}
/**
 * Tool call in a message
 */
export interface ToolCall {
    readonly id: string;
    readonly name: string;
    readonly arguments: Record<string, JsonValue>;
}
/**
 * Tool response
 */
export interface ToolResponse {
    readonly toolCallId: string;
    readonly content: string;
    readonly success: boolean;
    readonly metadata?: Record<string, JsonValue>;
}
/**
 * Chat completion request
 */
export interface ChatCompletionRequest {
    readonly messages: ReadonlyArray<ChatMessage>;
    readonly model: string;
    readonly temperature?: number;
    readonly maxTokens?: number;
    readonly stream?: boolean;
    readonly tools?: ReadonlyArray<ToolDefinition>;
    readonly toolChoice?: "none" | "auto" | string;
    readonly stop?: string | string[];
}
/**
 * Chat completion response
 */
export interface ChatCompletionResponse {
    readonly id: string;
    readonly model: string;
    readonly message: ChatMessage;
    readonly finishReason: "stop" | "length" | "tool_calls" | "content_filter";
    readonly usage: {
        readonly promptTokens: number;
        readonly completionTokens: number;
        readonly totalTokens: number;
    };
    readonly toolCalls?: ReadonlyArray<ToolCall>;
}
/**
 * Streaming response chunk
 */
export interface ChatCompletionChunk {
    readonly id: string;
    readonly model: string;
    readonly delta: {
        readonly role?: MessageRole;
        readonly content?: string;
        readonly toolCalls?: ReadonlyArray<Partial<ToolCall>>;
    };
    readonly finishReason?: "stop" | "length" | "tool_calls" | "content_filter";
}
/**
 * Tool function definition
 */
export interface ToolFunction {
    readonly name: string;
    readonly description: string;
    readonly parameters: Record<string, JsonValue>;
}
/**
 * Tool definition
 */
export interface ToolDefinition {
    readonly type: "function";
    readonly function: ToolFunction;
}
/**
 * Validation schemas
 */
export declare const MessageRoleSchema: z.ZodEnum<["system", "user", "assistant", "tool"]>;
export declare const ChatMessageSchema: z.ZodObject<{
    role: z.ZodEnum<["system", "user", "assistant", "tool"]>;
    content: z.ZodString;
    metadata: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodUnknown>>;
    timestamp: z.ZodOptional<z.ZodDate>;
}, "strip", z.ZodTypeAny, {
    role: "system" | "user" | "assistant" | "tool";
    content: string;
    metadata?: Record<string, unknown> | undefined;
    timestamp?: Date | undefined;
}, {
    role: "system" | "user" | "assistant" | "tool";
    content: string;
    metadata?: Record<string, unknown> | undefined;
    timestamp?: Date | undefined;
}>;
export declare const ModelCapabilitiesSchema: z.ZodObject<{
    supportsStreaming: z.ZodBoolean;
    supportsTools: z.ZodBoolean;
    supportsImages: z.ZodBoolean;
    supportsCodeGeneration: z.ZodBoolean;
    maxTokens: z.ZodNumber;
    contextWindow: z.ZodNumber;
}, "strip", z.ZodTypeAny, {
    supportsStreaming: boolean;
    supportsTools: boolean;
    supportsImages: boolean;
    supportsCodeGeneration: boolean;
    maxTokens: number;
    contextWindow: number;
}, {
    supportsStreaming: boolean;
    supportsTools: boolean;
    supportsImages: boolean;
    supportsCodeGeneration: boolean;
    maxTokens: number;
    contextWindow: number;
}>;
export declare const ModelInfoSchema: z.ZodObject<{
    id: z.ZodString;
    name: z.ZodString;
    description: z.ZodString;
    provider: z.ZodString;
    version: z.ZodString;
    capabilities: z.ZodObject<{
        supportsStreaming: z.ZodBoolean;
        supportsTools: z.ZodBoolean;
        supportsImages: z.ZodBoolean;
        supportsCodeGeneration: z.ZodBoolean;
        maxTokens: z.ZodNumber;
        contextWindow: z.ZodNumber;
    }, "strip", z.ZodTypeAny, {
        supportsStreaming: boolean;
        supportsTools: boolean;
        supportsImages: boolean;
        supportsCodeGeneration: boolean;
        maxTokens: number;
        contextWindow: number;
    }, {
        supportsStreaming: boolean;
        supportsTools: boolean;
        supportsImages: boolean;
        supportsCodeGeneration: boolean;
        maxTokens: number;
        contextWindow: number;
    }>;
    pricing: z.ZodOptional<z.ZodObject<{
        inputTokenPrice: z.ZodNumber;
        outputTokenPrice: z.ZodNumber;
        currency: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        inputTokenPrice: number;
        outputTokenPrice: number;
        currency: string;
    }, {
        inputTokenPrice: number;
        outputTokenPrice: number;
        currency: string;
    }>>;
    isLocal: z.ZodBoolean;
}, "strip", z.ZodTypeAny, {
    id: string;
    name: string;
    description: string;
    provider: string;
    version: string;
    capabilities: {
        supportsStreaming: boolean;
        supportsTools: boolean;
        supportsImages: boolean;
        supportsCodeGeneration: boolean;
        maxTokens: number;
        contextWindow: number;
    };
    isLocal: boolean;
    pricing?: {
        inputTokenPrice: number;
        outputTokenPrice: number;
        currency: string;
    } | undefined;
}, {
    id: string;
    name: string;
    description: string;
    provider: string;
    version: string;
    capabilities: {
        supportsStreaming: boolean;
        supportsTools: boolean;
        supportsImages: boolean;
        supportsCodeGeneration: boolean;
        maxTokens: number;
        contextWindow: number;
    };
    isLocal: boolean;
    pricing?: {
        inputTokenPrice: number;
        outputTokenPrice: number;
        currency: string;
    } | undefined;
}>;
//# sourceMappingURL=models.d.ts.map