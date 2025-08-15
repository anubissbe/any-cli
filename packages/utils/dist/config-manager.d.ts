/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */
import { type AppConfig } from "@qwen-claude/core";
/**
 * Configuration manager for loading and saving CLI configuration
 */
export declare class ConfigManager {
    private configPath;
    private config;
    constructor(configPath?: string);
    load(): Promise<AppConfig>;
    save(config: AppConfig): Promise<void>;
    update(updates: Partial<AppConfig>): Promise<void>;
    get(): Promise<AppConfig>;
    validate(config: unknown): AppConfig;
    getDefaults(): AppConfig;
    private applyEnvironmentOverrides;
}
//# sourceMappingURL=config-manager.d.ts.map