"""Security configuration and utilities for Plato API server."""

import hashlib
import hmac
import logging
import os
import secrets
import time
from dataclasses import dataclass, field
from typing import Any, Optional

from fastapi import HTTPException, Request, Security, status
from fastapi.security import APIKeyHeader
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

# Security headers that should be applied to all responses
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
}

# Content Security Policy configuration
CSP_POLICY = {
    "default-src": "'self'",
    "script-src": "'self' 'unsafe-inline'",  # Allow inline scripts for development
    "style-src": "'self' 'unsafe-inline'",  # Allow inline styles for development
    "img-src": "'self' data: https:",
    "font-src": "'self' data:",
    "connect-src": "'self'",
    "frame-ancestors": "'none'",
    "base-uri": "'self'",
    "form-action": "'self'",
}


@dataclass
class SecurityConfig:
    """Security configuration for the API server."""

    # CORS configuration
    allowed_origins: list[str] = field(
        default_factory=lambda: ["http://localhost:3000"]
    )
    allowed_origins_regex: Optional[str] = None
    allow_credentials: bool = True
    allowed_methods: list[str] = field(
        default_factory=lambda: ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    )
    allowed_headers: list[str] = field(default_factory=lambda: ["*"])

    # API Key configuration
    api_keys: dict[str, str] = field(default_factory=dict)  # key_id -> hashed_key
    require_api_key: bool = False
    api_key_header_name: str = "X-API-Key"

    # Rate limiting configuration (per IP)
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100  # requests per window
    rate_limit_window: int = 60  # seconds

    # Security headers
    enable_security_headers: bool = True
    csp_enabled: bool = True

    @classmethod
    def from_environment(cls) -> "SecurityConfig":
        """Create security configuration from environment variables."""
        config = cls()

        # Parse allowed origins from environment
        origins_env = os.getenv("PLATO_ALLOWED_ORIGINS", "")
        if origins_env:
            config.allowed_origins = [
                origin.strip() for origin in origins_env.split(",")
            ]
        else:
            # Default to localhost for development
            config.allowed_origins = [
                "http://localhost:3000",
                "http://localhost:3001",
                "http://localhost:8080",
                "http://127.0.0.1:3000",
                "http://127.0.0.1:3001",
                "http://127.0.0.1:8080",
            ]

        # Add production origins if configured
        if prod_origin := os.getenv("PLATO_PRODUCTION_ORIGIN"):
            config.allowed_origins.append(prod_origin)

        # API key configuration
        config.require_api_key = (
            os.getenv("PLATO_REQUIRE_API_KEY", "false").lower() == "true"
        )

        # Load API keys from environment (format: KEY_ID:KEY_SECRET,KEY_ID2:KEY_SECRET2)
        if api_keys_env := os.getenv("PLATO_API_KEYS"):
            for key_pair in api_keys_env.split(","):
                if ":" in key_pair:
                    key_id, key_secret = key_pair.split(":", 1)
                    # Store hashed version of the key
                    config.api_keys[key_id.strip()] = hash_api_key(key_secret.strip())

        # Rate limiting
        config.rate_limit_enabled = (
            os.getenv("PLATO_RATE_LIMIT_ENABLED", "true").lower() == "true"
        )
        config.rate_limit_requests = int(os.getenv("PLATO_RATE_LIMIT_REQUESTS", "100"))
        config.rate_limit_window = int(os.getenv("PLATO_RATE_LIMIT_WINDOW", "60"))

        # Security headers
        config.enable_security_headers = (
            os.getenv("PLATO_SECURITY_HEADERS", "true").lower() == "true"
        )
        config.csp_enabled = os.getenv("PLATO_CSP_ENABLED", "true").lower() == "true"

        return config

    def build_csp_header(self) -> str:
        """Build Content-Security-Policy header value."""
        if not self.csp_enabled:
            return ""

        # Add allowed origins to CSP connect-src
        connect_sources = ["'self'"] + self.allowed_origins
        csp = dict(CSP_POLICY)
        csp["connect-src"] = " ".join(connect_sources)

        return "; ".join(f"{key} {value}" for key, value in csp.items())


def hash_api_key(api_key: str) -> str:
    """Hash an API key for secure storage."""
    return hashlib.sha256(api_key.encode()).hexdigest()


def verify_api_key(provided_key: str, stored_hash: str) -> bool:
    """Verify an API key against its stored hash."""
    provided_hash = hash_api_key(provided_key)
    return hmac.compare_digest(provided_hash, stored_hash)


def generate_api_key() -> tuple[str, str]:
    """Generate a new API key pair (key_id, key_secret)."""
    key_id = f"plato_{secrets.token_hex(8)}"
    key_secret = secrets.token_urlsafe(32)
    return key_id, key_secret


class APIKeyValidator:
    """FastAPI dependency for API key validation."""

    def __init__(self, config: SecurityConfig):
        self.config = config
        self.header_scheme = APIKeyHeader(
            name=config.api_key_header_name, auto_error=False
        )

    async def __call__(
        self,
        api_key: Optional[str] = Security(
            APIKeyHeader(name="X-API-Key", auto_error=False)
        ),
    ) -> Optional[str]:
        """Validate API key from request header."""
        if not self.config.require_api_key:
            return None

        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key required",
                headers={"WWW-Authenticate": "ApiKey"},
            )

        # Extract key_id and key_secret from the provided key
        # Format: key_id:key_secret
        if ":" not in api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key format",
            )

        key_id, key_secret = api_key.split(":", 1)

        # Check if key_id exists
        if key_id not in self.config.api_keys:
            # Log the attempt but don't reveal which part failed
            logger.warning(f"Invalid API key attempt from key_id: {key_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key",
            )

        # Verify the key
        if not verify_api_key(key_secret, self.config.api_keys[key_id]):
            logger.warning(f"Invalid API key secret for key_id: {key_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key",
            )

        return key_id


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to all responses."""

    def __init__(self, app, config: SecurityConfig):
        super().__init__(app)
        self.config = config

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        if self.config.enable_security_headers:
            # Add security headers
            for header, value in SECURITY_HEADERS.items():
                response.headers[header] = value

            # Add CSP header if enabled
            if csp_header := self.config.build_csp_header():
                response.headers["Content-Security-Policy"] = csp_header

        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiting middleware."""

    def __init__(self, app, config: SecurityConfig):
        super().__init__(app)
        self.config = config
        self.requests: dict[str, list[float]] = {}  # IP -> timestamps

    def _clean_old_requests(self, ip: str, current_time: float):
        """Remove requests older than the rate limit window."""
        if ip in self.requests:
            cutoff = current_time - self.config.rate_limit_window
            self.requests[ip] = [t for t in self.requests[ip] if t > cutoff]

    async def dispatch(self, request: Request, call_next):
        if not self.config.rate_limit_enabled:
            return await call_next(request)

        # Get client IP
        client_ip = request.client.host if request.client else "unknown"

        # Special case for health check endpoint
        if request.url.path == "/health":
            return await call_next(request)

        current_time = time.time()

        # Clean old requests
        self._clean_old_requests(client_ip, current_time)

        # Check rate limit
        if client_ip in self.requests:
            if len(self.requests[client_ip]) >= self.config.rate_limit_requests:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded. Max {self.config.rate_limit_requests} requests per {self.config.rate_limit_window} seconds.",
                )

        # Record this request
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        self.requests[client_ip].append(current_time)

        return await call_next(request)


def mask_sensitive_data(data: Any, keys_to_mask: Optional[list[str]] = None) -> Any:
    """Mask sensitive data in logs and responses."""
    if keys_to_mask is None:
        keys_to_mask = [
            "api_key",
            "api_keys",
            "key",
            "secret",
            "password",
            "token",
            "authorization",
            "auth",
            "credentials",
            "private_key",
            "ANTHROPIC_API_KEY",
            "OPENAI_API_KEY",
            "GEMINI_API_KEY",
            "OPENROUTER_API_KEY",
        ]

    if isinstance(data, dict):
        masked = {}
        for key, value in data.items():
            if any(sensitive in key.lower() for sensitive in keys_to_mask):
                if isinstance(value, str) and len(value) > 0:
                    # Show first 4 chars and mask the rest
                    visible_chars = min(4, len(value) // 4)
                    masked[key] = value[:visible_chars] + "*" * (
                        len(value) - visible_chars
                    )
                else:
                    masked[key] = "***MASKED***"
            elif isinstance(value, (dict, list)):
                masked[key] = mask_sensitive_data(value, keys_to_mask)
            else:
                masked[key] = value
        return masked
    elif isinstance(data, list):
        return [mask_sensitive_data(item, keys_to_mask) for item in data]
    else:
        return data


def create_secure_logger(name: str) -> logging.Logger:
    """Create a logger that masks sensitive information."""
    logger = logging.getLogger(name)

    class SensitiveDataFilter(logging.Filter):
        def filter(self, record):
            # Mask sensitive data in log messages
            if hasattr(record, "msg"):
                record.msg = str(mask_sensitive_data(record.msg))
            if hasattr(record, "args") and record.args:
                record.args = tuple(mask_sensitive_data(arg) for arg in record.args)
            return True

    logger.addFilter(SensitiveDataFilter())
    return logger
