/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */
import { NotFoundError, ProviderUnavailableError } from "@qwen-claude/core";
/**
 * Default provider manager implementation
 */
export class DefaultProviderManager {
    registry;
    providerConfigs;
    providers = new Map();
    configs = new Map();
    initialized = false;
    constructor(registry, providerConfigs) {
        this.registry = registry;
        this.providerConfigs = providerConfigs;
    }
    async initialize() {
        if (this.initialized) {
            return { success: true, data: undefined };
        }
        const errors = [];
        // Initialize all configured providers
        for (const config of this.providerConfigs) {
            if (!config.enabled) {
                continue;
            }
            try {
                const result = await this.registry.create(config);
                if (!result.success) {
                    errors.push(result.error);
                    continue;
                }
                const provider = result.data;
                const initResult = await provider.initialize();
                if (initResult.success) {
                    this.providers.set(config.name, provider);
                    this.configs.set(config.name, config);
                }
                else {
                    errors.push(initResult.error);
                }
            }
            catch (error) {
                errors.push(error instanceof Error ? error : new Error(String(error)));
            }
        }
        this.initialized = true;
        // Return success if at least one provider was initialized
        if (this.providers.size > 0) {
            return { success: true, data: undefined };
        }
        return {
            success: false,
            error: new ProviderUnavailableError("all", `Failed to initialize any providers. Errors: ${errors.map((e) => e.message).join(", ")}`),
        };
    }
    async getBestProvider(strategy = "first-available", requirements) {
        if (!this.initialized) {
            return {
                success: false,
                error: new ProviderUnavailableError("all", "Provider manager not initialized"),
            };
        }
        const availableProviders = this.getAvailableProviders();
        if (availableProviders.length === 0) {
            return {
                success: false,
                error: new NotFoundError("No available providers"),
            };
        }
        // Filter providers by requirements
        let candidates = availableProviders;
        if (requirements) {
            candidates = await this.filterProvidersByRequirements(candidates, requirements);
        }
        if (candidates.length === 0) {
            return {
                success: false,
                error: new NotFoundError("No providers meet the specified requirements"),
            };
        }
        // Select provider based on strategy
        let selectedProvider;
        switch (strategy) {
            case "first-available":
                selectedProvider = this.selectFirstAvailable(candidates);
                break;
            case "fastest":
                selectedProvider = await this.selectFastest(candidates);
                break;
            case "cheapest":
                selectedProvider = await this.selectCheapest(candidates);
                break;
            case "most-capable":
                selectedProvider = await this.selectMostCapable(candidates);
                break;
            case "random":
                selectedProvider = this.selectRandom(candidates);
                break;
            default:
                selectedProvider = this.selectFirstAvailable(candidates);
        }
        return { success: true, data: selectedProvider };
    }
    getAvailableProviders() {
        return Array.from(this.providers.values()).filter((p) => p.isAvailable);
    }
    async healthCheck() {
        const healthChecks = Array.from(this.providers.values()).map(async (provider) => {
            try {
                return await provider.checkHealth();
            }
            catch (error) {
                return {
                    isHealthy: false,
                    error: error instanceof Error ? error.message : String(error),
                    lastChecked: new Date(),
                };
            }
        });
        return Promise.all(healthChecks);
    }
    async dispose() {
        const disposePromises = Array.from(this.providers.values()).map((p) => p.dispose());
        await Promise.allSettled(disposePromises);
        this.providers.clear();
        this.configs.clear();
        this.initialized = false;
    }
    /**
     * Filter providers by capability requirements
     */
    async filterProvidersByRequirements(providers, requirements) {
        const filtered = [];
        for (const provider of providers) {
            try {
                const modelsResult = await provider.getModels();
                if (!modelsResult.success) {
                    continue;
                }
                const hasCompatibleModel = modelsResult.data.some((model) => this.modelMeetsRequirements(model.capabilities, requirements));
                if (hasCompatibleModel) {
                    filtered.push(provider);
                }
            }
            catch {
                // Skip providers that fail to list models
                continue;
            }
        }
        return filtered;
    }
    /**
     * Check if model capabilities meet requirements
     */
    modelMeetsRequirements(capabilities, requirements) {
        return Object.entries(requirements).every(([key, value]) => {
            const capability = capabilities[key];
            if (typeof value === "boolean") {
                return !value || capability === value;
            }
            if (typeof value === "number") {
                return typeof capability === "number" && capability >= value;
            }
            return true;
        });
    }
    /**
     * Selection strategies
     */
    selectFirstAvailable(providers) {
        const sortedByPriority = [...providers].sort((a, b) => {
            const configA = this.configs.get(a.name);
            const configB = this.configs.get(b.name);
            return (configA?.priority || 0) - (configB?.priority || 0);
        });
        return sortedByPriority[0];
    }
    async selectFastest(providers) {
        const healthChecks = await Promise.all(providers.map(async (provider) => ({
            provider,
            health: await provider.checkHealth(),
        })));
        const healthyProviders = healthChecks
            .filter(({ health }) => health.isHealthy && health.latency !== undefined)
            .sort((a, b) => (a.health.latency || Infinity) - (b.health.latency || Infinity));
        return healthyProviders[0]?.provider || providers[0];
    }
    async selectCheapest(providers) {
        let cheapestProvider = providers[0];
        let lowestCost = Infinity;
        for (const provider of providers) {
            try {
                const modelsResult = await provider.getModels();
                if (!modelsResult.success) {
                    continue;
                }
                const avgCost = modelsResult.data
                    .filter((model) => model.pricing)
                    .reduce((sum, model) => sum +
                    (model.pricing.inputTokenPrice +
                        model.pricing.outputTokenPrice), 0) / modelsResult.data.length;
                if (avgCost < lowestCost) {
                    lowestCost = avgCost;
                    cheapestProvider = provider;
                }
            }
            catch {
                continue;
            }
        }
        return cheapestProvider;
    }
    async selectMostCapable(providers) {
        let bestProvider = providers[0];
        let highestScore = 0;
        for (const provider of providers) {
            try {
                const modelsResult = await provider.getModels();
                if (!modelsResult.success) {
                    continue;
                }
                const score = modelsResult.data.reduce((sum, model) => {
                    const caps = model.capabilities;
                    return (sum +
                        (caps.supportsTools ? 1 : 0) +
                        (caps.supportsImages ? 1 : 0) +
                        (caps.supportsCodeGeneration ? 1 : 0) +
                        (caps.supportsStreaming ? 1 : 0) +
                        Math.log10(caps.contextWindow) +
                        Math.log10(caps.maxTokens));
                }, 0);
                if (score > highestScore) {
                    highestScore = score;
                    bestProvider = provider;
                }
            }
            catch {
                continue;
            }
        }
        return bestProvider;
    }
    selectRandom(providers) {
        const index = Math.floor(Math.random() * providers.length);
        return providers[index];
    }
}
//# sourceMappingURL=manager.js.map