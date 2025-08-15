/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */
import { CLIError, ErrorCode } from "./base.js";
/**
 * Base error for provider-related issues
 */
export class ProviderError extends CLIError {
    provider;
    constructor(message, provider, code = ErrorCode.PROVIDER_UNAVAILABLE, context, cause) {
        super(message, code, { ...context, provider }, cause);
        this.provider = provider;
    }
}
/**
 * Error when provider is not found
 */
export class ProviderNotFoundError extends ProviderError {
    constructor(provider, context, cause) {
        super(`Provider '${provider}' not found`, provider, ErrorCode.PROVIDER_NOT_FOUND, context, cause);
    }
}
/**
 * Error when provider is unavailable
 */
export class ProviderUnavailableError extends ProviderError {
    constructor(provider, reason, context, cause) {
        const message = reason
            ? `Provider '${provider}' is unavailable: ${reason}`
            : `Provider '${provider}' is unavailable`;
        super(message, provider, ErrorCode.PROVIDER_UNAVAILABLE, { ...context, reason: reason ?? null }, cause);
    }
}
/**
 * Error when provider authentication fails
 */
export class ProviderAuthError extends ProviderError {
    constructor(provider, context, cause) {
        super(`Authentication failed for provider '${provider}'`, provider, ErrorCode.PROVIDER_AUTH_FAILED, context, cause);
    }
}
/**
 * Error when provider rate limit is exceeded
 */
export class ProviderRateLimitError extends ProviderError {
    retryAfter; // seconds
    constructor(provider, retryAfter, context, cause) {
        const message = retryAfter
            ? `Rate limit exceeded for provider '${provider}'. Retry after ${retryAfter} seconds`
            : `Rate limit exceeded for provider '${provider}'`;
        super(message, provider, ErrorCode.PROVIDER_RATE_LIMITED, { ...context, retryAfter: retryAfter ?? null }, cause);
        this.retryAfter = retryAfter;
    }
}
/**
 * Error when provider quota is exceeded
 */
export class ProviderQuotaError extends ProviderError {
    constructor(provider, context, cause) {
        super(`Quota exceeded for provider '${provider}'`, provider, ErrorCode.PROVIDER_QUOTA_EXCEEDED, context, cause);
    }
}
/**
 * Error when provider returns invalid response
 */
export class ProviderInvalidResponseError extends ProviderError {
    response;
    constructor(provider, response, context, cause) {
        super(`Invalid response from provider '${provider}'`, provider, ErrorCode.PROVIDER_INVALID_RESPONSE, { ...context, response: JSON.stringify(response) }, cause);
        this.response = response;
    }
}
/**
 * Error when model is not supported by provider
 */
export class ModelNotSupportedError extends ProviderError {
    model;
    constructor(provider, model, context, cause) {
        super(`Model '${model}' is not supported by provider '${provider}'`, provider, ErrorCode.PROVIDER_UNAVAILABLE, { ...context, model }, cause);
        this.model = model;
    }
}
/**
 * Error when provider configuration is invalid
 */
export class ProviderConfigError extends ProviderError {
    constructor(provider, reason, context, cause) {
        super(`Invalid configuration for provider '${provider}': ${reason}`, provider, ErrorCode.CONFIG_INVALID, context, cause);
    }
}
//# sourceMappingURL=provider.js.map