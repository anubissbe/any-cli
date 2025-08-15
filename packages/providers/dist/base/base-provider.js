/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */
import { ProviderError, ProviderUnavailableError } from "@qwen-claude/core";
/**
 * Abstract base class for model providers
 */
export class BaseProvider {
    name;
    type;
    config;
    initialized = false;
    constructor(config) {
        this.config = config;
        this.name = config.name;
        this.type = config.type;
    }
    get isAvailable() {
        return this.initialized && this.config.enabled;
    }
    /**
     * Initialize the provider
     */
    async initialize() {
        try {
            await this.doInitialize();
            this.initialized = true;
            return { success: true, data: undefined };
        }
        catch (error) {
            return {
                success: false,
                error: new ProviderError(`Failed to initialize provider ${this.name}`, this.name, undefined, undefined, error instanceof Error ? error : new Error(String(error))),
            };
        }
    }
    /**
     * Check provider health
     */
    async checkHealth() {
        const startTime = Date.now();
        try {
            await this.doHealthCheck();
            return {
                isHealthy: true,
                latency: Date.now() - startTime,
                lastChecked: new Date(),
            };
        }
        catch (error) {
            return {
                isHealthy: false,
                error: error instanceof Error ? error.message : String(error),
                lastChecked: new Date(),
            };
        }
    }
    /**
     * Clean up resources
     */
    async dispose() {
        await this.doDispose();
        this.initialized = false;
    }
    /**
     * Validate that provider is available
     */
    validateAvailable() {
        if (!this.isAvailable) {
            throw new ProviderUnavailableError(this.name, "Provider is not initialized or disabled");
        }
    }
    /**
     * Handle cancellation token
     */
    setupCancellation(cancellationToken) {
        const controller = new AbortController();
        if (cancellationToken) {
            if (cancellationToken.isCancelled) {
                controller.abort();
            }
            else {
                cancellationToken.onCancelled(() => controller.abort());
            }
        }
        return controller;
    }
}
//# sourceMappingURL=base-provider.js.map