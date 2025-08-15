/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */
import type { ProviderFactory, ProviderConfig, ModelProvider, Result } from "@qwen-claude/core";
/**
 * Factory for creating Qwen provider instances
 */
export declare class QwenProviderFactory implements ProviderFactory {
    readonly name = "qwen";
    readonly supportedTypes: readonly ["local"];
    create(config: ProviderConfig): Promise<Result<ModelProvider>>;
    validateConfig(config: unknown): Result<ProviderConfig>;
}
//# sourceMappingURL=qwen-factory.d.ts.map