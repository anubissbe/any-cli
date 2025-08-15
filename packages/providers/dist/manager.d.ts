/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */
import type { ProviderManager, ProviderRegistry, ProviderConfig, ModelProvider, ProviderHealth, ProviderSelectionStrategy, ModelCapabilities, Result } from "@qwen-claude/core";
/**
 * Default provider manager implementation
 */
export declare class DefaultProviderManager implements ProviderManager {
    private readonly registry;
    private readonly providerConfigs;
    private readonly providers;
    private readonly configs;
    private initialized;
    constructor(registry: ProviderRegistry, providerConfigs: ReadonlyArray<ProviderConfig>);
    initialize(): Promise<Result<void>>;
    getBestProvider(strategy?: ProviderSelectionStrategy, requirements?: Partial<ModelCapabilities>): Promise<Result<ModelProvider>>;
    getAvailableProviders(): ReadonlyArray<ModelProvider>;
    healthCheck(): Promise<ReadonlyArray<ProviderHealth>>;
    dispose(): Promise<void>;
    /**
     * Filter providers by capability requirements
     */
    private filterProvidersByRequirements;
    /**
     * Check if model capabilities meet requirements
     */
    private modelMeetsRequirements;
    /**
     * Selection strategies
     */
    private selectFirstAvailable;
    private selectFastest;
    private selectCheapest;
    private selectMostCapable;
    private selectRandom;
}
//# sourceMappingURL=manager.d.ts.map