#!/usr/bin/env python3
"""Simple Plato server for testing connectivity."""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create simple FastAPI app
app = FastAPI(
    title="Plato Test Server",
    description="Simple server for testing Plato connectivity",
    version="0.1.0",
)

# Add CORS middleware with secure configuration
# SECURITY: Only allow specific trusted origins, never use wildcard with credentials
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development frontend
        "http://localhost:5173",  # Vite dev server
        "https://plato.example.com",  # Production domain (update with actual domain)
    ],
    allow_credentials=True,  # Only safe with specific origins
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # Specify exact methods needed
    allow_headers=["Content-Type", "Authorization"],  # Only necessary headers
    max_age=3600,  # Cache preflight responses for 1 hour
)

import time

# Track startup time
startup_time = time.time()


@app.get("/health")
async def health_check():
    """Simple health check compatible with Plato CLI."""
    return {
        "status": "healthy",
        "version": "0.1.0",
        "server": "plato-test",
        "uptime": time.time() - startup_time,
        "ai_providers": {
            "gpt4": True,
            "gpt3.5": True,
            "gemini": True,
            "openrouter": True,
        },
        "mcp_servers": {"serena": False, "office-word": False, "archy": False},
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Plato Test Server is running!"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")
