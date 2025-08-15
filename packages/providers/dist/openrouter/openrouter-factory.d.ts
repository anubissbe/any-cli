/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */
import type { ProviderFactory, ProviderConfig, ModelProvider, Result } from "@qwen-claude/core";
/**
 * Factory for creating OpenRouter provider instances
 */
export declare class OpenRouterProviderFactory implements ProviderFactory {
    readonly name = "openrouter";
    readonly supportedTypes: readonly ["remote"];
    create(config: ProviderConfig): Promise<Result<ModelProvider>>;
    validateConfig(config: unknown): Result<ProviderConfig>;
}
//# sourceMappingURL=openrouter-factory.d.ts.map