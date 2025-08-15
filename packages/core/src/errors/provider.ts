/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */

import { CLIError, ErrorCode } from "./base.js";
import type { JsonValue } from "../types/common.js";

/**
 * Base error for provider-related issues
 */
export class ProviderError extends CLIError {
  public readonly provider: string;

  constructor(
    message: string,
    provider: string,
    code: ErrorCode = ErrorCode.PROVIDER_UNAVAILABLE,
    context?: Record<string, JsonValue>,
    cause?: Error,
  ) {
    super(message, code, { ...context, provider }, cause);
    this.provider = provider;
  }
}

/**
 * Error when provider is not found
 */
export class ProviderNotFoundError extends ProviderError {
  constructor(
    provider: string,
    context?: Record<string, JsonValue>,
    cause?: Error,
  ) {
    super(
      `Provider '${provider}' not found`,
      provider,
      ErrorCode.PROVIDER_NOT_FOUND,
      context,
      cause,
    );
  }
}

/**
 * Error when provider is unavailable
 */
export class ProviderUnavailableError extends ProviderError {
  constructor(
    provider: string,
    reason?: string,
    context?: Record<string, JsonValue>,
    cause?: Error,
  ) {
    const message = reason
      ? `Provider '${provider}' is unavailable: ${reason}`
      : `Provider '${provider}' is unavailable`;
    super(
      message,
      provider,
      ErrorCode.PROVIDER_UNAVAILABLE,
      { ...context, reason: reason ?? null },
      cause,
    );
  }
}

/**
 * Error when provider authentication fails
 */
export class ProviderAuthError extends ProviderError {
  constructor(
    provider: string,
    context?: Record<string, JsonValue>,
    cause?: Error,
  ) {
    super(
      `Authentication failed for provider '${provider}'`,
      provider,
      ErrorCode.PROVIDER_AUTH_FAILED,
      context,
      cause,
    );
  }
}

/**
 * Error when provider rate limit is exceeded
 */
export class ProviderRateLimitError extends ProviderError {
  public readonly retryAfter?: number; // seconds

  constructor(
    provider: string,
    retryAfter?: number,
    context?: Record<string, JsonValue>,
    cause?: Error,
  ) {
    const message = retryAfter
      ? `Rate limit exceeded for provider '${provider}'. Retry after ${retryAfter} seconds`
      : `Rate limit exceeded for provider '${provider}'`;
    super(
      message,
      provider,
      ErrorCode.PROVIDER_RATE_LIMITED,
      { ...context, retryAfter: retryAfter ?? null },
      cause,
    );
    this.retryAfter = retryAfter;
  }
}

/**
 * Error when provider quota is exceeded
 */
export class ProviderQuotaError extends ProviderError {
  constructor(
    provider: string,
    context?: Record<string, JsonValue>,
    cause?: Error,
  ) {
    super(
      `Quota exceeded for provider '${provider}'`,
      provider,
      ErrorCode.PROVIDER_QUOTA_EXCEEDED,
      context,
      cause,
    );
  }
}

/**
 * Error when provider returns invalid response
 */
export class ProviderInvalidResponseError extends ProviderError {
  public readonly response?: unknown;

  constructor(
    provider: string,
    response?: unknown,
    context?: Record<string, JsonValue>,
    cause?: Error,
  ) {
    super(
      `Invalid response from provider '${provider}'`,
      provider,
      ErrorCode.PROVIDER_INVALID_RESPONSE,
      { ...context, response: JSON.stringify(response) },
      cause,
    );
    this.response = response;
  }
}

/**
 * Error when model is not supported by provider
 */
export class ModelNotSupportedError extends ProviderError {
  public readonly model: string;

  constructor(
    provider: string,
    model: string,
    context?: Record<string, JsonValue>,
    cause?: Error,
  ) {
    super(
      `Model '${model}' is not supported by provider '${provider}'`,
      provider,
      ErrorCode.PROVIDER_UNAVAILABLE,
      { ...context, model },
      cause,
    );
    this.model = model;
  }
}

/**
 * Error when provider configuration is invalid
 */
export class ProviderConfigError extends ProviderError {
  constructor(
    provider: string,
    reason: string,
    context?: Record<string, JsonValue>,
    cause?: Error,
  ) {
    super(
      `Invalid configuration for provider '${provider}': ${reason}`,
      provider,
      ErrorCode.CONFIG_INVALID,
      context,
      cause,
    );
  }
}
