#!/usr/bin/env python3
"""
Plato AI Orchestration System - Complete Demonstration

This script demonstrates all the key capabilities of the Plato system:
1. Multi-AI provider support (OpenAI, Anthropic, Google)
2. Serena MCP integration for code analysis
3. Context management and memory
4. CLI interface functionality
5. LSP operations via Serena

Prerequisites:
- Serena MCP server running on port 8765
- API keys configured in config.yaml
- Virtual environment activated
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from plato.core.ai_router import AIRouter, AIProvider
from plato.core.context_manager import ContextManager
from plato.integrations.serena_mcp import SerenaMCPClient
from plato.core.config import Config

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class PlatoDemonstration:
    """Complete demonstration of Plato system capabilities."""

    def __init__(self):
        """Initialize demonstration components."""
        self.config = Config()
        self.ai_router = AIRouter(self.config)
        self.context_manager = ContextManager()
        self.serena_client = SerenaMCPClient()
        self.demo_results: Dict[str, Any] = {}

    async def run_complete_demo(self) -> Dict[str, Any]:
        """Run complete system demonstration."""
        logger.info("🚀 Starting Plato AI Orchestration System Demonstration")

        try:
            # Phase 1: System Initialization
            await self._demo_system_initialization()

            # Phase 2: AI Provider Integration
            await self._demo_ai_providers()

            # Phase 3: Serena MCP Integration
            await self._demo_serena_mcp()

            # Phase 4: Context Management
            await self._demo_context_management()

            # Phase 5: Advanced Operations
            await self._demo_advanced_operations()

            # Generate final report
            await self._generate_final_report()

        except Exception as e:
            logger.error(f"Demo failed: {e}")
            self.demo_results["error"] = str(e)

        finally:
            await self._cleanup()

        return self.demo_results

    async def _demo_system_initialization(self):
        """Demonstrate system initialization."""
        logger.info("📋 Phase 1: System Initialization")

        phase_results = {
            "config_loaded": False,
            "ai_router_initialized": False,
            "context_manager_initialized": False,
            "serena_connection": False,
        }

        try:
            # Test config loading
            logger.info("  ✓ Loading configuration...")
            phase_results["config_loaded"] = bool(self.config.app.name)

            # Test AI router initialization
            logger.info("  ✓ Initializing AI router...")
            await self.ai_router.initialize()
            phase_results["ai_router_initialized"] = True

            # Test context manager
            logger.info("  ✓ Initializing context manager...")
            await self.context_manager.initialize()
            phase_results["context_manager_initialized"] = True

            # Test Serena connection
            logger.info("  ✓ Testing Serena MCP connection...")
            connected = await self.serena_client.connect()
            phase_results["serena_connection"] = connected
            if connected:
                logger.info("    → Serena MCP connected successfully")
            else:
                logger.warning("    → Serena MCP connection failed")

        except Exception as e:
            logger.error(f"  ✗ Initialization failed: {e}")
            phase_results["error"] = str(e)

        self.demo_results["phase_1_initialization"] = phase_results

    async def _demo_ai_providers(self):
        """Demonstrate AI provider capabilities."""
        logger.info("🤖 Phase 2: AI Provider Integration")

        phase_results = {"providers_available": [], "provider_tests": {}}

        # List available providers
        available_providers = await self.ai_router.list_providers()
        phase_results["providers_available"] = [p.value for p in available_providers]
        logger.info(
            f"  ✓ Available providers: {[p.value for p in available_providers]}"
        )

        # Test each provider with a simple request
        test_prompt = (
            "Hello! Please respond with 'Provider test successful' and nothing else."
        )

        for provider in available_providers:
            logger.info(f"  🔧 Testing {provider.value} provider...")
            try:
                response = await self.ai_router.chat_completion(
                    provider=provider,
                    messages=[{"role": "user", "content": test_prompt}],
                    max_tokens=50,
                )

                phase_results["provider_tests"][provider.value] = {
                    "success": True,
                    "response": response.get("content", "No content")[:100],
                    "tokens_used": response.get("usage", {}).get("total_tokens", 0),
                }
                logger.info(f"    → {provider.value} test successful")

            except Exception as e:
                phase_results["provider_tests"][provider.value] = {
                    "success": False,
                    "error": str(e),
                }
                logger.warning(f"    → {provider.value} test failed: {e}")

        self.demo_results["phase_2_ai_providers"] = phase_results

    async def _demo_serena_mcp(self):
        """Demonstrate Serena MCP integration."""
        logger.info("🔍 Phase 3: Serena MCP Integration")

        phase_results = {
            "connection_status": False,
            "tools_available": [],
            "operations_tested": {},
        }

        try:
            # Ensure connection
            if not self.serena_client._connected:
                connected = await self.serena_client.connect()
                if not connected:
                    raise Exception("Failed to connect to Serena MCP")

            phase_results["connection_status"] = True
            logger.info("  ✓ Serena MCP connection verified")

            # List available tools
            tools_response = await self.serena_client.list_tools()
            if tools_response.success:
                phase_results["tools_available"] = [
                    tool["name"] for tool in tools_response.data
                ]
                logger.info(f"  ✓ Found {len(tools_response.data)} tools available")

            # Test project activation
            logger.info("  🔧 Testing project activation...")
            project_path = "/opt/projects/plato"
            activate_response = await self.serena_client.activate_project(project_path)
            phase_results["operations_tested"]["activate_project"] = {
                "success": activate_response.success,
                "data": (
                    activate_response.data
                    if activate_response.success
                    else activate_response.error
                ),
            }

            # Test file reading
            logger.info("  🔧 Testing file operations...")
            file_path = "plato/__init__.py"
            read_response = await self.serena_client.read_file(file_path)
            phase_results["operations_tested"]["read_file"] = {
                "success": read_response.success,
                "content_length": (
                    len(read_response.data)
                    if read_response.success and read_response.data
                    else 0
                ),
            }

            # Test symbol operations
            logger.info("  🔧 Testing symbol operations...")
            symbols_response = await self.serena_client.get_symbols_overview(file_path)
            phase_results["operations_tested"]["get_symbols"] = {
                "success": symbols_response.success,
                "symbols_found": (
                    bool(symbols_response.data) if symbols_response.success else False
                ),
            }

            # Test directory listing
            logger.info("  🔧 Testing directory operations...")
            list_response = await self.serena_client.list_dir(".")
            phase_results["operations_tested"]["list_dir"] = {
                "success": list_response.success,
                "files_found": (
                    len(list_response.data)
                    if list_response.success and list_response.data
                    else 0
                ),
            }

            # Test search operations
            logger.info("  🔧 Testing search operations...")
            search_response = await self.serena_client.search_for_pattern("class.*:")
            phase_results["operations_tested"]["search_pattern"] = {
                "success": search_response.success,
                "matches_found": (
                    bool(search_response.data) if search_response.success else False
                ),
            }

        except Exception as e:
            logger.error(f"  ✗ Serena MCP demo failed: {e}")
            phase_results["error"] = str(e)

        self.demo_results["phase_3_serena_mcp"] = phase_results

    async def _demo_context_management(self):
        """Demonstrate context management capabilities."""
        logger.info("💾 Phase 4: Context Management")

        phase_results = {"context_operations": {}, "memory_operations": {}}

        try:
            # Test context storage and retrieval
            logger.info("  🔧 Testing context operations...")

            # Store context
            test_context = {
                "project": "plato",
                "task": "demonstration",
                "timestamp": "2024-08-15",
                "components": ["ai_router", "serena_mcp", "context_manager"],
            }

            await self.context_manager.store_context("demo_session", test_context)
            phase_results["context_operations"]["store"] = True

            # Retrieve context
            retrieved_context = await self.context_manager.get_context("demo_session")
            phase_results["context_operations"]["retrieve"] = {
                "success": retrieved_context is not None,
                "matches_stored": (
                    retrieved_context == test_context if retrieved_context else False
                ),
            }

            # Test memory operations via Serena (if connected)
            if self.serena_client._connected:
                logger.info("  🔧 Testing memory operations via Serena...")

                # Write memory
                memory_response = await self.serena_client.write_memory(
                    "demo_key", "Demo value for testing"
                )
                phase_results["memory_operations"]["write"] = memory_response.success

                # Read memory
                read_memory_response = await self.serena_client.read_memory("demo_key")
                phase_results["memory_operations"]["read"] = {
                    "success": read_memory_response.success,
                    "value_matches": (
                        read_memory_response.data == "Demo value for testing"
                        if read_memory_response.success
                        else False
                    ),
                }

                # List memories
                list_memories_response = await self.serena_client.list_memories()
                phase_results["memory_operations"]["list"] = {
                    "success": list_memories_response.success,
                    "contains_demo_key": (
                        "demo_key" in str(list_memories_response.data)
                        if list_memories_response.success
                        else False
                    ),
                }

                # Clean up
                await self.serena_client.delete_memory("demo_key")

        except Exception as e:
            logger.error(f"  ✗ Context management demo failed: {e}")
            phase_results["error"] = str(e)

        self.demo_results["phase_4_context_management"] = phase_results

    async def _demo_advanced_operations(self):
        """Demonstrate advanced system operations."""
        logger.info("⚡ Phase 5: Advanced Operations")

        phase_results = {
            "context_building": {},
            "ai_code_analysis": {},
            "integrated_workflow": {},
        }

        try:
            # Test comprehensive context building
            logger.info("  🔧 Testing comprehensive context building...")
            if self.serena_client._connected:
                file_context = await self.serena_client.build_file_context(
                    "plato/__init__.py"
                )
                phase_results["context_building"]["file_context"] = {
                    "success": "content" in file_context,
                    "has_symbols": file_context.get("symbols") is not None,
                    "error_count": len(file_context.get("errors", [])),
                }

                project_context = await self.serena_client.build_project_context(
                    "/opt/projects/plato"
                )
                phase_results["context_building"]["project_context"] = {
                    "success": project_context.get("activated", False),
                    "has_files": project_context.get("files") is not None,
                    "error_count": len(project_context.get("errors", [])),
                }

            # Test AI-assisted code analysis
            logger.info("  🔧 Testing AI-assisted code analysis...")
            if (
                self.serena_client._connected
                and phase_results["context_building"]["file_context"]["success"]
            ):
                # Get file content
                file_response = await self.serena_client.read_file("plato/__init__.py")
                if file_response.success and file_response.data:
                    # Use AI to analyze the code
                    analysis_prompt = f"""
                    Analyze this Python code and provide a brief summary:
                    
                    ```python
                    {file_response.data[:500]}...
                    ```
                    
                    Provide analysis in JSON format with keys: purpose, complexity, suggestions.
                    """

                    # Try with different providers
                    for provider in [AIProvider.OPENAI, AIProvider.ANTHROPIC]:
                        try:
                            response = await self.ai_router.chat_completion(
                                provider=provider,
                                messages=[{"role": "user", "content": analysis_prompt}],
                                max_tokens=200,
                            )

                            phase_results["ai_code_analysis"][provider.value] = {
                                "success": True,
                                "analysis_length": len(response.get("content", "")),
                                "tokens_used": response.get("usage", {}).get(
                                    "total_tokens", 0
                                ),
                            }
                            break

                        except Exception as e:
                            phase_results["ai_code_analysis"][provider.value] = {
                                "success": False,
                                "error": str(e),
                            }

            # Test integrated workflow
            logger.info("  🔧 Testing integrated workflow...")
            workflow_steps = []

            # Step 1: Use Serena to find Python files
            if self.serena_client._connected:
                find_response = await self.serena_client.find_file("*.py")
                workflow_steps.append(
                    {
                        "step": "find_python_files",
                        "success": find_response.success,
                        "files_found": (
                            len(find_response.data)
                            if find_response.success and find_response.data
                            else 0
                        ),
                    }
                )

            # Step 2: Store workflow state in context
            workflow_context = {
                "workflow_id": "demo_workflow",
                "steps_completed": len(workflow_steps),
                "status": "in_progress",
            }
            await self.context_manager.store_context("workflow_demo", workflow_context)
            workflow_steps.append({"step": "store_context", "success": True})

            # Step 3: Use AI to summarize findings
            if workflow_steps[0]["success"]:
                summary_prompt = f"Summarize: Found {workflow_steps[0]['files_found']} Python files in the project. What does this suggest about the project structure?"
                try:
                    response = await self.ai_router.chat_completion(
                        provider=AIProvider.OPENAI,
                        messages=[{"role": "user", "content": summary_prompt}],
                        max_tokens=100,
                    )
                    workflow_steps.append(
                        {
                            "step": "ai_summary",
                            "success": True,
                            "summary_length": len(response.get("content", "")),
                        }
                    )
                except Exception as e:
                    workflow_steps.append(
                        {"step": "ai_summary", "success": False, "error": str(e)}
                    )

            phase_results["integrated_workflow"]["steps"] = workflow_steps
            phase_results["integrated_workflow"]["total_steps"] = len(workflow_steps)
            phase_results["integrated_workflow"]["successful_steps"] = sum(
                1 for step in workflow_steps if step["success"]
            )

        except Exception as e:
            logger.error(f"  ✗ Advanced operations demo failed: {e}")
            phase_results["error"] = str(e)

        self.demo_results["phase_5_advanced_operations"] = phase_results

    async def _generate_final_report(self):
        """Generate comprehensive demonstration report."""
        logger.info("📊 Generating Final Report")

        report = {
            "demo_completed": True,
            "timestamp": "2024-08-15T19:39:00Z",
            "summary": {
                "total_phases": 5,
                "successful_phases": 0,
                "key_capabilities_verified": [],
                "issues_found": [],
            },
            "detailed_results": self.demo_results,
        }

        # Analyze results
        successful_phases = 0
        capabilities_verified = []
        issues_found = []

        # Phase 1: Initialization
        if self.demo_results.get("phase_1_initialization", {}).get("serena_connection"):
            successful_phases += 1
            capabilities_verified.append("Serena MCP Integration")

        if self.demo_results.get("phase_1_initialization", {}).get(
            "ai_router_initialized"
        ):
            capabilities_verified.append("AI Router Initialization")

        # Phase 2: AI Providers
        ai_providers = self.demo_results.get("phase_2_ai_providers", {}).get(
            "provider_tests", {}
        )
        working_providers = [
            p for p, result in ai_providers.items() if result.get("success")
        ]
        if working_providers:
            successful_phases += 1
            capabilities_verified.append(
                f"Multi-AI Support ({len(working_providers)} providers)"
            )

        # Phase 3: Serena MCP
        serena_ops = self.demo_results.get("phase_3_serena_mcp", {}).get(
            "operations_tested", {}
        )
        working_ops = [op for op, result in serena_ops.items() if result.get("success")]
        if len(working_ops) >= 3:  # At least 3 operations working
            successful_phases += 1
            capabilities_verified.append(
                f"LSP Operations ({len(working_ops)} operations)"
            )

        # Phase 4: Context Management
        context_ops = self.demo_results.get("phase_4_context_management", {})
        if context_ops.get("context_operations", {}).get("store") and context_ops.get(
            "memory_operations", {}
        ).get("write"):
            successful_phases += 1
            capabilities_verified.append("Context & Memory Management")

        # Phase 5: Advanced Operations
        advanced_ops = self.demo_results.get("phase_5_advanced_operations", {})
        if advanced_ops.get("integrated_workflow", {}).get("successful_steps", 0) >= 2:
            successful_phases += 1
            capabilities_verified.append("Integrated Workflows")

        # Check for issues
        for phase_name, phase_data in self.demo_results.items():
            if "error" in phase_data:
                issues_found.append(f"{phase_name}: {phase_data['error']}")

        report["summary"]["successful_phases"] = successful_phases
        report["summary"]["key_capabilities_verified"] = capabilities_verified
        report["summary"]["issues_found"] = issues_found

        # Save report
        report_path = Path("/opt/projects/plato/demo_report.json")
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        self.demo_results["final_report"] = report

        # Print summary
        logger.info("=" * 60)
        logger.info("🎯 PLATO DEMONSTRATION COMPLETE")
        logger.info("=" * 60)
        logger.info(f"✅ Successful Phases: {successful_phases}/5")
        logger.info(f"🔧 Capabilities Verified: {len(capabilities_verified)}")

        for capability in capabilities_verified:
            logger.info(f"  ✓ {capability}")

        if issues_found:
            logger.info(f"⚠️  Issues Found: {len(issues_found)}")
            for issue in issues_found:
                logger.info(f"  ! {issue}")

        logger.info(f"📄 Full report saved to: {report_path}")
        logger.info("=" * 60)

    async def _cleanup(self):
        """Clean up resources."""
        logger.info("🧹 Cleaning up resources...")

        try:
            if self.serena_client._connected:
                await self.serena_client.disconnect()

            # Clean up any temporary context
            await self.context_manager.clear_context("demo_session")
            await self.context_manager.clear_context("workflow_demo")

        except Exception as e:
            logger.warning(f"Cleanup warning: {e}")


async def main():
    """Main demonstration entry point."""
    demo = PlatoDemonstration()
    results = await demo.run_complete_demo()

    # Print key results
    print("\n🚀 PLATO DEMONSTRATION RESULTS:")
    print(
        f"Status: {'✅ SUCCESS' if results.get('final_report', {}).get('summary', {}).get('successful_phases', 0) >= 3 else '❌ PARTIAL'}"
    )
    print(
        f"Phases completed: {results.get('final_report', {}).get('summary', {}).get('successful_phases', 0)}/5"
    )
    print(
        f"Capabilities verified: {len(results.get('final_report', {}).get('summary', {}).get('key_capabilities_verified', []))}"
    )

    return results


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Demonstration interrupted by user")
    except Exception as e:
        print(f"\n💥 Demonstration failed: {e}")
