/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */
import { z } from "zod";
/**
 * Validation schemas
 */
export const ToolParameterSchema = z.lazy(() => z.object({
    name: z.string(),
    type: z.enum(["string", "number", "boolean", "array", "object"]),
    description: z.string(),
    required: z.boolean(),
    default: z
        .union([z.string(), z.number(), z.boolean(), z.null()])
        .optional(),
    enum: z
        .array(z.union([z.string(), z.number(), z.boolean(), z.null()]))
        .optional(),
    pattern: z.string().optional(),
    minimum: z.number().optional(),
    maximum: z.number().optional(),
    items: ToolParameterSchema.optional(),
    properties: z.record(ToolParameterSchema).optional(),
}));
export const ToolMetadataSchema = z.object({
    name: z.string(),
    description: z.string(),
    version: z.string(),
    author: z.string().optional(),
    category: z.enum([
        "file",
        "shell",
        "network",
        "analysis",
        "utility",
        "system",
    ]),
    tags: z.array(z.string()),
    platforms: z.array(z.enum(["linux", "windows", "darwin", "all"])),
    requiresAuth: z.boolean(),
    isDestructive: z.boolean(),
    estimatedDuration: z
        .enum(["instant", "fast", "slow", "very-slow"])
        .optional(),
});
export const SafetyLevelSchema = z.enum(["safe", "cautious", "dangerous"]);
//# sourceMappingURL=tools.js.map