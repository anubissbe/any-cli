/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */
import { z } from "zod";
/**
 * Validation schemas
 */
export const CommandArgumentSchema = z.object({
    name: z.string(),
    description: z.string(),
    type: z.enum(["string", "number", "boolean", "array"]),
    required: z.boolean(),
    default: z.unknown().optional(),
    choices: z.array(z.string()).optional(),
    alias: z.string().optional(),
});
export const CommandOptionSchema = CommandArgumentSchema.extend({
    short: z.string().length(1).optional(),
    long: z.string(),
});
export const CommandMetadataSchema = z.object({
    name: z.string(),
    description: z.string(),
    usage: z.string(),
    examples: z.array(z.string()),
    category: z.enum(["chat", "file", "config", "tool", "provider", "utility"]),
    aliases: z.array(z.string()),
    hidden: z.boolean(),
});
export const ParsedCommandSchema = z.object({
    command: z.string(),
    subcommand: z.string().optional(),
    arguments: z.record(z.unknown()),
    options: z.record(z.unknown()),
    flags: z.array(z.string()),
    raw: z.array(z.string()),
});
//# sourceMappingURL=commands.js.map