/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */
import { NotFoundError, ValidationError } from "@qwen-claude/core";
import { QwenProviderFactory } from "./qwen/index.js";
import { OpenRouterProviderFactory } from "./openrouter/index.js";
/**
 * Default provider registry implementation
 */
export class DefaultProviderRegistry {
    factories = new Map();
    constructor() {
        // Register built-in provider factories
        this.register(new QwenProviderFactory());
        this.register(new OpenRouterProviderFactory());
    }
    register(factory) {
        this.factories.set(factory.name, factory);
    }
    async create(config) {
        const factory = this.getFactory(config);
        if (!factory) {
            return {
                success: false,
                error: new NotFoundError(`Provider factory for '${config.name}' not found`),
            };
        }
        return factory.create(config);
    }
    getRegisteredProviders() {
        return Array.from(this.factories.keys());
    }
    validateConfig(config) {
        try {
            // Basic type check
            if (!config || typeof config !== "object") {
                return {
                    success: false,
                    error: new ValidationError("Provider configuration must be an object"),
                };
            }
            const configObj = config;
            if (!configObj.name || typeof configObj.name !== "string") {
                return {
                    success: false,
                    error: new ValidationError("Provider configuration must have a name"),
                };
            }
            const factory = this.factories.get(configObj.name);
            if (!factory) {
                return {
                    success: false,
                    error: new NotFoundError(`Provider factory for '${configObj.name}' not found`),
                };
            }
            return factory.validateConfig(config);
        }
        catch (error) {
            return {
                success: false,
                error: new ValidationError("Failed to validate provider configuration", undefined, error instanceof Error ? error : new Error(String(error))),
            };
        }
    }
    /**
     * Get factory for provider configuration
     */
    getFactory(config) {
        // First try exact name match
        let factory = this.factories.get(config.name);
        if (factory) {
            return factory;
        }
        // Try to infer factory from provider name patterns
        const name = config.name.toLowerCase();
        if (name.includes("qwen") || name.includes("local")) {
            factory = this.factories.get("qwen");
        }
        else if (name.includes("openrouter") || name.includes("router")) {
            factory = this.factories.get("openrouter");
        }
        return factory;
    }
}
//# sourceMappingURL=registry.js.map