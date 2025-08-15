/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */
import fs from "fs/promises";
import path from "path";
import { z } from "zod";
import { ConfigError, AppConfigSchema, } from "@qwen-claude/core";
import { getConfigDir } from "./platform.js";
/**
 * Configuration manager for loading and saving CLI configuration
 */
export class ConfigManager {
    configPath;
    config = null;
    constructor(configPath) {
        this.configPath = configPath ?? path.join(getConfigDir(), "config.json");
    }
    async load() {
        try {
            await fs.access(this.configPath);
            const content = await fs.readFile(this.configPath, "utf-8");
            const parsedConfig = JSON.parse(content);
            // Validate against schema
            const validatedConfig = AppConfigSchema.parse(parsedConfig);
            this.config = this.applyEnvironmentOverrides(validatedConfig);
            return this.config;
        }
        catch (error) {
            if (error instanceof z.ZodError) {
                const issues = error.errors
                    .map((e) => `${e.path.join(".")}: ${e.message}`)
                    .join(", ");
                throw new ConfigError(`Invalid configuration: ${issues}`);
            }
            throw new ConfigError(`Failed to load configuration from ${this.configPath}: ${error instanceof Error ? error.message : String(error)}`);
        }
    }
    async save(config) {
        try {
            // Validate before saving
            const validatedConfig = AppConfigSchema.parse(config);
            // Ensure directory exists
            await fs.mkdir(path.dirname(this.configPath), { recursive: true });
            // Write config file
            await fs.writeFile(this.configPath, JSON.stringify(validatedConfig, null, 2), "utf-8");
            this.config = validatedConfig;
        }
        catch (error) {
            if (error instanceof z.ZodError) {
                const issues = error.errors
                    .map((e) => `${e.path.join(".")}: ${e.message}`)
                    .join(", ");
                throw new ConfigError(`Invalid configuration: ${issues}`);
            }
            throw new ConfigError(`Failed to save configuration to ${this.configPath}: ${error instanceof Error ? error.message : String(error)}`);
        }
    }
    async update(updates) {
        const currentConfig = await this.get();
        const updatedConfig = { ...currentConfig, ...updates };
        await this.save(updatedConfig);
    }
    async get() {
        if (!this.config) {
            return this.load();
        }
        return this.config;
    }
    validate(config) {
        return AppConfigSchema.parse(config);
    }
    getDefaults() {
        return {
            version: "0.1.0",
            debug: false,
            logLevel: "info",
            interactive: true,
            configDir: getConfigDir(),
            dataDir: path.join(getConfigDir(), "data"),
            cacheDir: path.join(getConfigDir(), "cache"),
            providers: [],
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
    }
    applyEnvironmentOverrides(config) {
        const overrides = {};
        // Debug mode override
        if (process.env.DEBUG === "1" || process.env.DEBUG === "true") {
            overrides.debug = true;
        }
        // Log level override
        if (process.env.LOG_LEVEL) {
            const logLevel = process.env.LOG_LEVEL.toLowerCase();
            if (["debug", "info", "warn", "error"].includes(logLevel)) {
                overrides.logLevel = logLevel;
            }
        }
        // Default provider override
        if (process.env.DEFAULT_PROVIDER) {
            overrides.defaultProvider = process.env.DEFAULT_PROVIDER;
        }
        return { ...config, ...overrides };
    }
}
//# sourceMappingURL=config-manager.js.map