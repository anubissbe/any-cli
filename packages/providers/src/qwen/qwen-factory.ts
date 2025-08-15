/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */

import type {
  ProviderFactory,
  ProviderConfig,
  ModelProvider,
  Result,
} from "@qwen-claude/core";
import { ProviderConfigSchema, ValidationError } from "@qwen-claude/core";
import { QwenProvider } from "./qwen-provider.js";

/**
 * Factory for creating Qwen provider instances
 */
export class QwenProviderFactory implements ProviderFactory {
  public readonly name = "qwen";
  public readonly supportedTypes = ["local"] as const;

  public async create(config: ProviderConfig): Promise<Result<ModelProvider>> {
    try {
      // Validate configuration
      const validationResult = this.validateConfig(config);
      if (!validationResult.success) {
        return validationResult;
      }

      const provider = new QwenProvider(config);
      return { success: true, data: provider };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error : new Error(String(error)),
      };
    }
  }

  public validateConfig(config: unknown): Result<ProviderConfig> {
    try {
      // Basic schema validation
      const parsed = ProviderConfigSchema.parse(config);

      // Qwen-specific validation
      if (parsed.type !== "local") {
        return {
          success: false,
          error: new ValidationError('Qwen provider must be of type "local"'),
        };
      }

      if (!parsed.auth.baseUrl) {
        return {
          success: false,
          error: new ValidationError(
            "Qwen provider requires baseUrl in auth configuration",
          ),
        };
      }

      // Validate base URL format
      try {
        new URL(parsed.auth.baseUrl);
      } catch {
        return {
          success: false,
          error: new ValidationError(
            "Invalid baseUrl format in Qwen provider configuration",
          ),
        };
      }

      // Set default endpoint if not provided
      if (!parsed.endpoint) {
        parsed.endpoint = `${parsed.auth.baseUrl}/v1`;
      }

      return { success: true, data: parsed };
    } catch (error) {
      return {
        success: false,
        error: new ValidationError(
          "Invalid Qwen provider configuration",
          undefined,
          error instanceof Error ? error : new Error(String(error)),
        ),
      };
    }
  }
}
