/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */
import { z } from "zod";
/**
 * Platform detection for cross-platform compatibility
 */
export type Platform = "linux" | "windows" | "darwin";
/**
 * Log levels for structured logging
 */
export type LogLevel = "debug" | "info" | "warn" | "error";
/**
 * Execution context for commands
 */
export interface ExecutionContext {
    readonly platform: Platform;
    readonly workingDirectory: string;
    readonly environment: Record<string, string | undefined>;
    readonly isInteractive: boolean;
    readonly debugMode: boolean;
}
/**
 * Generic result type for operations that can fail
 */
export type Result<T, E = Error> = {
    success: true;
    data: T;
} | {
    success: false;
    error: E;
};
/**
 * Configuration validation schemas
 */
export declare const PlatformSchema: z.ZodEnum<["linux", "windows", "darwin"]>;
export declare const LogLevelSchema: z.ZodEnum<["debug", "info", "warn", "error"]>;
/**
 * Utility type for making properties optional
 */
export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;
/**
 * Utility type for readonly arrays
 */
export type ReadonlyArray<T> = readonly T[];
/**
 * JSON-serializable values
 */
export type JsonValue = string | number | boolean | null | JsonValue[] | {
    [key: string]: JsonValue;
};
/**
 * Generic event type for event-driven architecture
 */
export interface Event<T = JsonValue> {
    readonly type: string;
    readonly timestamp: Date;
    readonly data: T;
}
/**
 * Cancellation token for long-running operations
 */
export interface CancellationToken {
    readonly isCancelled: boolean;
    readonly onCancelled: (callback: () => void) => void;
}
/**
 * Chat completion message types
 */
export interface ChatMessage {
    role: "system" | "user" | "assistant";
    content: string;
    name?: string;
}
/**
 * Chat completion request
 */
export interface ChatCompletionRequest {
    model: string;
    messages: ChatMessage[];
    temperature?: number;
    maxTokens?: number;
    stream?: boolean;
    stop?: string | string[];
    presencePenalty?: number;
    frequencyPenalty?: number;
    tools?: ToolDefinition[];
    toolChoice?: "auto" | "none" | {
        type: "function";
        function: {
            name: string;
        };
    };
}
/**
 * Chat completion response choice
 */
export interface ChatCompletionChoice {
    index: number;
    message?: ChatMessage;
    delta?: Partial<ChatMessage>;
    finishReason?: "stop" | "length" | "tool_calls" | "content_filter" | null;
}
/**
 * Chat completion response
 */
export interface ChatCompletionResponse {
    id: string;
    object: "chat.completion" | "chat.completion.chunk";
    created: number;
    model: string;
    choices: ChatCompletionChoice[];
    usage?: {
        promptTokens: number;
        completionTokens: number;
        totalTokens: number;
    };
}
/**
 * Streaming chat completion chunk
 */
export interface ChatCompletionChunk {
    id: string;
    object: "chat.completion.chunk";
    created: number;
    model: string;
    choices: ChatCompletionChoice[];
}
/**
 * Model information
 */
export interface ModelInfo {
    id: string;
    name?: string;
    description?: string;
    capabilities?: string[];
    contextLength?: number;
    pricing?: {
        input?: number;
        output?: number;
        unit?: string;
    };
    provider?: string;
}
/**
 * Tool definition for function calling
 */
export interface ToolDefinition {
    type: "function";
    function: {
        name: string;
        description?: string;
        parameters?: Record<string, any>;
    };
}
//# sourceMappingURL=common.d.ts.map