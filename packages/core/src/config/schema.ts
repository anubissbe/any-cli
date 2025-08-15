/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */

import { z } from "zod";
import { ProviderConfigSchema } from "../types/providers.js";

/**
 * Tool configuration schema
 */
export const ToolConfigSchema = z.object({
  safetyLevel: z.enum(["safe", "cautious", "dangerous"]).default("cautious"),
  confirmDestructive: z.boolean().default(true),
  timeout: z.number().positive().default(30000), // 30 seconds
  maxRetries: z.number().int().nonnegative().default(3),
});

/**
 * UI configuration schema
 */
export const UIConfigSchema = z.object({
  theme: z.string().default("default"),
  colorOutput: z.boolean().default(true),
  spinner: z.boolean().default(true),
  progressBar: z.boolean().default(true),
});

/**
 * Network configuration schema
 */
export const NetworkConfigSchema = z.object({
  timeout: z.number().positive().default(30000), // 30 seconds
  retries: z.number().int().nonnegative().default(3),
  userAgent: z.string().default("qwen-claude-cli/0.1.0"),
  proxy: z.string().url().optional(),
});

/**
 * Main application configuration schema
 */
export const AppConfigSchema = z.object({
  version: z.string(),
  debug: z.boolean().default(false),
  logLevel: z.enum(["debug", "info", "warn", "error"]).default("info"),
  interactive: z.boolean().default(true),
  configDir: z.string(),
  dataDir: z.string(),
  cacheDir: z.string(),
  providers: z.array(ProviderConfigSchema).default([]),
  defaultProvider: z.string().optional(),
  tools: ToolConfigSchema.default({}),
  ui: UIConfigSchema.default({}),
  network: NetworkConfigSchema.default({}),
});

/**
 * Type inference from schema
 */
export type AppConfig = z.infer<typeof AppConfigSchema>;
export type ToolConfig = z.infer<typeof ToolConfigSchema>;
export type UIConfig = z.infer<typeof UIConfigSchema>;
export type NetworkConfig = z.infer<typeof NetworkConfigSchema>;
