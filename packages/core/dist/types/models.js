/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */
import { z } from "zod";
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
//# sourceMappingURL=models.js.map