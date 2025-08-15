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
import { OpenRouterProvider } from "./openrouter-provider.js";

/**
 * Factory for creating OpenRouter provider instances
 */
export class OpenRouterProviderFactory implements ProviderFactory {
  public readonly name = "openrouter";
  public readonly supportedTypes = ["remote"] as const;

  public async create(config: ProviderConfig): Promise<Result<ModelProvider>> {
    try {
      // Validate configuration
      const validationResult = this.validateConfig(config);
      if (!validationResult.success) {
        return validationResult;
      }

      const provider = new OpenRouterProvider(config);
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

      // OpenRouter-specific validation
      if (parsed.type !== "remote") {
        return {
          success: false,
          error: new ValidationError(
            'OpenRouter provider must be of type "remote"',
          ),
        };
      }

      if (parsed.auth.type !== "api_key") {
        return {
          success: false,
          error: new ValidationError(
            "OpenRouter provider requires API key authentication",
          ),
        };
      }

      if (!parsed.auth.apiKey) {
        return {
          success: false,
          error: new ValidationError(
            "OpenRouter provider requires apiKey in auth configuration",
          ),
        };
      }

      // Set default values
      if (!parsed.auth.baseUrl) {
        parsed.auth.baseUrl = "https://openrouter.ai";
      }

      if (!parsed.endpoint) {
        parsed.endpoint = "https://openrouter.ai/api/v1";
      }

      // Ensure required headers are set
      if (!parsed.auth.headers) {
        parsed.auth.headers = {};
      }

      if (!parsed.auth.headers["HTTP-Referer"]) {
        parsed.auth.headers["HTTP-Referer"] =
          "https://github.com/your-org/qwen-claude-cli";
      }

      if (!parsed.auth.headers["X-Title"]) {
        parsed.auth.headers["X-Title"] = "Qwen Claude CLI";
      }

      return { success: true, data: parsed };
    } catch (error) {
      return {
        success: false,
        error: new ValidationError(
          "Invalid OpenRouter provider configuration",
          undefined,
          error instanceof Error ? error : new Error(String(error)),
        ),
      };
    }
  }
}
