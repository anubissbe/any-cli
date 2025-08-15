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
  readonly inputTokenPrice: number; // per 1k tokens
  readonly outputTokenPrice: number; // per 1k tokens
  readonly currency: string; // USD, etc.
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
  readonly parameters: Record<string, JsonValue>; // JSON Schema
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
export const MessageRoleSchema = z.enum([
  "system",
  "user",
  "assistant",
  "tool",
]);

export const ChatMessageSchema = z.object({
  role: MessageRoleSchema,
  content: z.string(),
  metadata: z.record(z.unknown()).optional(),
  timestamp: z.date().optional(),
});

export const ModelCapabilitiesSchema = z.object({
  supportsStreaming: z.boolean(),
  supportsTools: z.boolean(),
  supportsImages: z.boolean(),
  supportsCodeGeneration: z.boolean(),
  maxTokens: z.number().positive(),
  contextWindow: z.number().positive(),
});

export const ModelInfoSchema = z.object({
  id: z.string(),
  name: z.string(),
  description: z.string(),
  provider: z.string(),
  version: z.string(),
  capabilities: ModelCapabilitiesSchema,
  pricing: z
    .object({
      inputTokenPrice: z.number().nonnegative(),
      outputTokenPrice: z.number().nonnegative(),
      currency: z.string(),
    })
    .optional(),
  isLocal: z.boolean(),
});
