/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */

import type { AppConfig } from "./schema.js";
import type { ProviderConfig } from "../types/providers.js";

/**
 * Default Qwen provider configuration
 */
export const DEFAULT_QWEN_PROVIDER: ProviderConfig = {
  name: "qwen-local",
  type: "local",
  priority: 1,
  enabled: true,
  auth: {
    type: "none",
    baseUrl: "http://192.168.1.28:8000",
  },
  models: ["qwen3-coder-30b"] as string[],
  endpoint: "http://192.168.1.28:8000/v1",
  timeout: 60000, // 60 seconds for local model
  retries: 2,
};

/**
 * Default OpenRouter provider configuration
 */
export const DEFAULT_OPENROUTER_PROVIDER: ProviderConfig = {
  name: "openrouter",
  type: "remote",
  priority: 2,
  enabled: true,
  auth: {
    type: "api_key",
    baseUrl: "https://openrouter.ai/api",
    headers: {
      "HTTP-Referer": "https://github.com/your-org/qwen-claude-cli",
      "X-Title": "Qwen Claude CLI",
    },
  },
  models: [
    "openai/gpt-4o-mini",
    "anthropic/claude-3-haiku",
    "qwen/qwen-2.5-coder-32b-instruct",
    "deepseek/deepseek-coder",
    "meta-llama/llama-3.1-8b-instruct:free",
  ] as string[],
  endpoint: "https://openrouter.ai/api/v1",
  timeout: 30000, // 30 seconds
  retries: 3,
};

/**
 * Default application configuration
 */
export const DEFAULT_CONFIG: Partial<AppConfig> = {
  version: "0.1.0",
  debug: false,
  logLevel: "info",
  interactive: true,
  providers: [DEFAULT_QWEN_PROVIDER, DEFAULT_OPENROUTER_PROVIDER],
  defaultProvider: "qwen-local",
  tools: {
    safetyLevel: "cautious",
    confirmDestructive: true,
    timeout: 30000,
    maxRetries: 3,
  },
  ui: {
    theme: "default",
    colorOutput: true,
    spinner: true,
    progressBar: true,
  },
  network: {
    timeout: 30000,
    retries: 3,
    userAgent: "qwen-claude-cli/0.1.0",
  },
};

/**
 * Environment variable mappings
 */
export const ENV_MAPPINGS = {
  QWEN_CLAUDE_DEBUG: "debug",
  QWEN_CLAUDE_LOG_LEVEL: "logLevel",
  QWEN_CLAUDE_INTERACTIVE: "interactive",
  QWEN_CLAUDE_DEFAULT_PROVIDER: "defaultProvider",
  QWEN_CLAUDE_QWEN_URL: "providers.0.endpoint",
  QWEN_CLAUDE_OPENROUTER_API_KEY: "providers.1.auth.apiKey",
  QWEN_CLAUDE_PROXY: "network.proxy",
  QWEN_CLAUDE_TIMEOUT: "network.timeout",
  NO_COLOR: "ui.colorOutput", // Standard NO_COLOR env var
  FORCE_COLOR: "ui.colorOutput", // Standard FORCE_COLOR env var
} as const;

/**
 * Configuration file names to search for
 */
export const CONFIG_FILENAMES = [
  "qwen-claude.config.json",
  "qwen-claude.config.yaml",
  "qwen-claude.config.yml",
  ".qwen-claude.json",
  ".qwen-claude.yaml",
  ".qwen-claude.yml",
] as const;

/**
 * Default directories based on platform
 */
export const getDefaultDirectories = (platform: string, homeDir: string) => {
  const appName = "qwen-claude-cli";

  switch (platform) {
    case "win32":
      return {
        config: process.env.APPDATA
          ? `${process.env.APPDATA}/${appName}`
          : `${homeDir}/.config/${appName}`,
        data: process.env.LOCALAPPDATA
          ? `${process.env.LOCALAPPDATA}/${appName}`
          : `${homeDir}/.local/share/${appName}`,
        cache: process.env.TEMP
          ? `${process.env.TEMP}/${appName}`
          : `${homeDir}/.cache/${appName}`,
      };
    case "darwin":
      return {
        config: `${homeDir}/Library/Application Support/${appName}`,
        data: `${homeDir}/Library/Application Support/${appName}`,
        cache: `${homeDir}/Library/Caches/${appName}`,
      };
    default: // linux and others
      return {
        config: process.env.XDG_CONFIG_HOME
          ? `${process.env.XDG_CONFIG_HOME}/${appName}`
          : `${homeDir}/.config/${appName}`,
        data: process.env.XDG_DATA_HOME
          ? `${process.env.XDG_DATA_HOME}/${appName}`
          : `${homeDir}/.local/share/${appName}`,
        cache: process.env.XDG_CACHE_HOME
          ? `${process.env.XDG_CACHE_HOME}/${appName}`
          : `${homeDir}/.cache/${appName}`,
      };
  }
};
