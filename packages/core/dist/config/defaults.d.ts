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
export declare const DEFAULT_QWEN_PROVIDER: ProviderConfig;
/**
 * Default OpenRouter provider configuration
 */
export declare const DEFAULT_OPENROUTER_PROVIDER: ProviderConfig;
/**
 * Default application configuration
 */
export declare const DEFAULT_CONFIG: Partial<AppConfig>;
/**
 * Environment variable mappings
 */
export declare const ENV_MAPPINGS: {
    readonly QWEN_CLAUDE_DEBUG: "debug";
    readonly QWEN_CLAUDE_LOG_LEVEL: "logLevel";
    readonly QWEN_CLAUDE_INTERACTIVE: "interactive";
    readonly QWEN_CLAUDE_DEFAULT_PROVIDER: "defaultProvider";
    readonly QWEN_CLAUDE_QWEN_URL: "providers.0.endpoint";
    readonly QWEN_CLAUDE_OPENROUTER_API_KEY: "providers.1.auth.apiKey";
    readonly QWEN_CLAUDE_PROXY: "network.proxy";
    readonly QWEN_CLAUDE_TIMEOUT: "network.timeout";
    readonly NO_COLOR: "ui.colorOutput";
    readonly FORCE_COLOR: "ui.colorOutput";
};
/**
 * Configuration file names to search for
 */
export declare const CONFIG_FILENAMES: readonly ["qwen-claude.config.json", "qwen-claude.config.yaml", "qwen-claude.config.yml", ".qwen-claude.json", ".qwen-claude.yaml", ".qwen-claude.yml"];
/**
 * Default directories based on platform
 */
export declare const getDefaultDirectories: (platform: string, homeDir: string) => {
    config: string;
    data: string;
    cache: string;
};
//# sourceMappingURL=defaults.d.ts.map