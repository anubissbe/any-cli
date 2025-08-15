/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */
import type { ProviderRegistry, ProviderFactory, ProviderConfig, ModelProvider, Result } from "@qwen-claude/core";
/**
 * Default provider registry implementation
 */
export declare class DefaultProviderRegistry implements ProviderRegistry {
    private readonly factories;
    constructor();
    register(factory: ProviderFactory): void;
    create(config: ProviderConfig): Promise<Result<ModelProvider>>;
    getRegisteredProviders(): ReadonlyArray<string>;
    validateConfig(config: unknown): Result<ProviderConfig>;
    /**
     * Get factory for provider configuration
     */
    private getFactory;
}
//# sourceMappingURL=registry.d.ts.map