#!/usr/bin/env python3
"""Security test script for Plato API server."""

import asyncio
import os
import sys
from typing import Any

import httpx
from rich.console import Console
from rich.table import Table

console = Console()


class SecurityAuditor:
    """Test security configuration of Plato API server."""

    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.results = []

    async def test_cors_headers(self):
        """Test CORS configuration."""
        console.print("\n[bold cyan]Testing CORS Configuration...[/bold cyan]")

        # Test from allowed origin
        async with httpx.AsyncClient() as client:
            response = await client.options(
                f"{self.base_url}/chat",
                headers={
                    "Origin": "http://localhost:3000",
                    "Access-Control-Request-Method": "POST",
                },
            )

            if response.status_code == 200:
                cors_headers = {
                    k: v
                    for k, v in response.headers.items()
                    if k.lower().startswith("access-control")
                }
                console.print("[green]✓[/green] Allowed origin accepted")
                self.results.append(
                    ("CORS - Allowed Origin", "PASS", str(cors_headers))
                )
            else:
                console.print("[red]✗[/red] Allowed origin rejected")
                self.results.append(
                    ("CORS - Allowed Origin", "FAIL", "Origin rejected")
                )

        # Test from disallowed origin
        async with httpx.AsyncClient() as client:
            response = await client.options(
                f"{self.base_url}/chat",
                headers={
                    "Origin": "http://evil-site.com",
                    "Access-Control-Request-Method": "POST",
                },
            )

            cors_headers = response.headers.get("access-control-allow-origin", "")
            if cors_headers != "http://evil-site.com" and cors_headers != "*":
                console.print("[green]✓[/green] Disallowed origin rejected")
                self.results.append(
                    ("CORS - Disallowed Origin", "PASS", "Origin blocked")
                )
            else:
                console.print("[red]✗[/red] Disallowed origin accepted!")
                self.results.append(
                    (
                        "CORS - Disallowed Origin",
                        "FAIL",
                        f"Origin allowed: {cors_headers}",
                    )
                )

    async def test_security_headers(self):
        """Test security headers."""
        console.print("\n[bold cyan]Testing Security Headers...[/bold cyan]")

        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/health")

            security_headers = {
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY",
                "X-XSS-Protection": "1; mode=block",
                "Referrer-Policy": "strict-origin-when-cross-origin",
                "Content-Security-Policy": None,  # Check presence
            }

            for header, expected in security_headers.items():
                actual = response.headers.get(header)
                if expected is None:
                    # Just check presence
                    if actual:
                        console.print(f"[green]✓[/green] {header} present")
                        self.results.append(
                            (
                                f"Security Header - {header}",
                                "PASS",
                                actual[:50] + "..." if len(actual) > 50 else actual,
                            )
                        )
                    else:
                        console.print(f"[yellow]⚠[/yellow] {header} missing")
                        self.results.append(
                            (f"Security Header - {header}", "WARN", "Missing")
                        )
                else:
                    if actual == expected:
                        console.print(f"[green]✓[/green] {header}: {expected}")
                        self.results.append(
                            (f"Security Header - {header}", "PASS", actual)
                        )
                    else:
                        console.print(
                            f"[red]✗[/red] {header}: Expected '{expected}', got '{actual}'"
                        )
                        self.results.append(
                            (
                                f"Security Header - {header}",
                                "FAIL",
                                f"Expected: {expected}, Got: {actual}",
                            )
                        )

    async def test_api_key_protection(self):
        """Test API key protection."""
        console.print("\n[bold cyan]Testing API Key Protection...[/bold cyan]")

        # Test without API key
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat", json={"message": "test", "stream": False}
                )

                if os.getenv("PLATO_REQUIRE_API_KEY", "false").lower() == "true":
                    if response.status_code == 401:
                        console.print(
                            "[green]✓[/green] Request without API key rejected"
                        )
                        self.results.append(
                            ("API Key - No Key", "PASS", "Rejected (401)")
                        )
                    else:
                        console.print("[red]✗[/red] Request without API key accepted!")
                        self.results.append(
                            (
                                "API Key - No Key",
                                "FAIL",
                                f"Accepted ({response.status_code})",
                            )
                        )
                else:
                    console.print("[yellow]⚠[/yellow] API key protection disabled")
                    self.results.append(
                        ("API Key - No Key", "INFO", "API key not required")
                    )
            except Exception as e:
                console.print(f"[yellow]⚠[/yellow] Could not test API key: {e}")
                self.results.append(("API Key - No Key", "ERROR", str(e)))

    async def test_rate_limiting(self):
        """Test rate limiting."""
        console.print("\n[bold cyan]Testing Rate Limiting...[/bold cyan]")

        if os.getenv("PLATO_RATE_LIMIT_ENABLED", "true").lower() != "true":
            console.print("[yellow]⚠[/yellow] Rate limiting disabled")
            self.results.append(("Rate Limiting", "INFO", "Disabled"))
            return

        rate_limit = int(os.getenv("PLATO_RATE_LIMIT_REQUESTS", "100"))
        test_requests = min(rate_limit + 5, 20)  # Test a reasonable number

        async with httpx.AsyncClient() as client:
            exceeded = False
            for i in range(test_requests):
                try:
                    response = await client.get(f"{self.base_url}/tools")
                    if response.status_code == 429:
                        console.print(
                            f"[green]✓[/green] Rate limit enforced after {i} requests"
                        )
                        self.results.append(
                            ("Rate Limiting", "PASS", f"Enforced after {i} requests")
                        )
                        exceeded = True
                        break
                except Exception:
                    pass

            if not exceeded and test_requests > rate_limit:
                console.print(
                    f"[yellow]⚠[/yellow] Rate limit not enforced in {test_requests} requests"
                )
                self.results.append(
                    (
                        "Rate Limiting",
                        "WARN",
                        f"Not enforced in {test_requests} requests",
                    )
                )

    async def test_sensitive_data_masking(self):
        """Test that sensitive data is masked in responses."""
        console.print("\n[bold cyan]Testing Sensitive Data Masking...[/bold cyan]")

        async with httpx.AsyncClient() as client:
            try:
                # Health endpoint should not expose sensitive data
                response = await client.get(f"{self.base_url}/health")
                response_text = response.text.lower()

                sensitive_patterns = [
                    "sk-",
                    "api_key",
                    "secret",
                    "password",
                    "token",
                    (
                        os.getenv("ANTHROPIC_API_KEY", "")[:10]
                        if os.getenv("ANTHROPIC_API_KEY")
                        else None
                    ),
                ]

                exposed = []
                for pattern in sensitive_patterns:
                    if pattern and pattern in response_text:
                        exposed.append(pattern)

                if not exposed:
                    console.print(
                        "[green]✓[/green] No sensitive data exposed in health endpoint"
                    )
                    self.results.append(
                        ("Sensitive Data - Health", "PASS", "No exposure")
                    )
                else:
                    console.print(f"[red]✗[/red] Sensitive patterns found: {exposed}")
                    self.results.append(
                        ("Sensitive Data - Health", "FAIL", f"Exposed: {exposed}")
                    )

            except Exception as e:
                console.print(f"[yellow]⚠[/yellow] Could not test data masking: {e}")
                self.results.append(("Sensitive Data - Health", "ERROR", str(e)))

    def print_summary(self):
        """Print test summary."""
        console.print("\n[bold cyan]Security Audit Summary[/bold cyan]")

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Test", style="cyan")
        table.add_column("Result", justify="center")
        table.add_column("Details", style="dim")

        pass_count = 0
        fail_count = 0
        warn_count = 0

        for test, result, details in self.results:
            if result == "PASS":
                result_str = "[green]PASS[/green]"
                pass_count += 1
            elif result == "FAIL":
                result_str = "[red]FAIL[/red]"
                fail_count += 1
            elif result == "WARN":
                result_str = "[yellow]WARN[/yellow]"
                warn_count += 1
            else:
                result_str = f"[dim]{result}[/dim]"

            table.add_row(test, result_str, details)

        console.print(table)

        console.print(f"\n[bold]Results:[/bold]")
        console.print(f"  [green]Passed:[/green] {pass_count}")
        console.print(f"  [red]Failed:[/red] {fail_count}")
        console.print(f"  [yellow]Warnings:[/yellow] {warn_count}")

        if fail_count > 0:
            console.print("\n[bold red]⚠️  CRITICAL SECURITY ISSUES FOUND![/bold red]")
            console.print("Please review and fix the failed tests immediately.")
            return False
        elif warn_count > 0:
            console.print(
                "\n[bold yellow]⚠️  Some security improvements recommended[/bold yellow]"
            )
            return True
        else:
            console.print("\n[bold green]✅ All security tests passed![/bold green]")
            return True

    async def run_audit(self):
        """Run complete security audit."""
        console.print("[bold magenta]Starting Plato API Security Audit[/bold magenta]")
        console.print(f"Target: {self.base_url}")

        await self.test_cors_headers()
        await self.test_security_headers()
        await self.test_api_key_protection()
        await self.test_rate_limiting()
        await self.test_sensitive_data_masking()

        return self.print_summary()


async def main():
    """Main entry point."""
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8080"

    auditor = SecurityAuditor(base_url)
    success = await auditor.run_audit()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
