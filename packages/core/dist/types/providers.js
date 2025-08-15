/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */
import { z } from "zod";
/**
 * Validation schemas
 */
export const ProviderAuthSchema = z.object({
    type: z.enum(["api_key", "oauth", "none"]),
    apiKey: z.string().optional(),
    baseUrl: z.string().url().optional(),
    headers: z.record(z.string()).optional(),
});
export const ProviderConfigSchema = z.object({
    name: z.string(),
    type: z.enum(["local", "remote"]),
    priority: z.number().int().nonnegative(),
    enabled: z.boolean(),
    auth: ProviderAuthSchema,
    models: z.array(z.string()),
    endpoint: z.string().url().optional(),
    timeout: z.number().positive().optional(),
    retries: z.number().int().nonnegative().optional(),
});
//# sourceMappingURL=providers.js.map