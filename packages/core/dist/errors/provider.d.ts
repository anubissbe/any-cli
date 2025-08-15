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
export declare class ProviderError extends CLIError {
    readonly provider: string;
    constructor(message: string, provider: string, code?: ErrorCode, context?: Record<string, JsonValue>, cause?: Error);
}
/**
 * Error when provider is not found
 */
export declare class ProviderNotFoundError extends ProviderError {
    constructor(provider: string, context?: Record<string, JsonValue>, cause?: Error);
}
/**
 * Error when provider is unavailable
 */
export declare class ProviderUnavailableError extends ProviderError {
    constructor(provider: string, reason?: string, context?: Record<string, JsonValue>, cause?: Error);
}
/**
 * Error when provider authentication fails
 */
export declare class ProviderAuthError extends ProviderError {
    constructor(provider: string, context?: Record<string, JsonValue>, cause?: Error);
}
/**
 * Error when provider rate limit is exceeded
 */
export declare class ProviderRateLimitError extends ProviderError {
    readonly retryAfter?: number;
    constructor(provider: string, retryAfter?: number, context?: Record<string, JsonValue>, cause?: Error);
}
/**
 * Error when provider quota is exceeded
 */
export declare class ProviderQuotaError extends ProviderError {
    constructor(provider: string, context?: Record<string, JsonValue>, cause?: Error);
}
/**
 * Error when provider returns invalid response
 */
export declare class ProviderInvalidResponseError extends ProviderError {
    readonly response?: unknown;
    constructor(provider: string, response?: unknown, context?: Record<string, JsonValue>, cause?: Error);
}
/**
 * Error when model is not supported by provider
 */
export declare class ModelNotSupportedError extends ProviderError {
    readonly model: string;
    constructor(provider: string, model: string, context?: Record<string, JsonValue>, cause?: Error);
}
/**
 * Error when provider configuration is invalid
 */
export declare class ProviderConfigError extends ProviderError {
    constructor(provider: string, reason: string, context?: Record<string, JsonValue>, cause?: Error);
}
//# sourceMappingURL=provider.d.ts.map