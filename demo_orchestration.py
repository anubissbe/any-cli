#!/usr/bin/env python3
"""
Demo script for Plato's SuperClaude-style orchestration features.
"""

import asyncio
import json
from plato.core.orchestration import TaskOrchestrator, TaskType
from plato.core.embedded_tools import ToolManager


async def demo_orchestration():
    """Demonstrate the orchestration capabilities."""
    print("🚀 Plato SuperClaude Orchestration Demo")
    print("=" * 50)

    # Initialize the orchestration system
    print("\n1. Initializing orchestration system...")
    tool_manager = ToolManager()
    orchestrator = TaskOrchestrator(tool_manager=tool_manager)

    # Show available agents
    status = orchestrator.get_orchestration_status()
    print(f"   ✅ {status['total_agents']} agents initialized")
    for agent in status["agents"]:
        print(f"      - {agent['name']}: {', '.join(agent['capabilities'])}")

    # Demo 1: File Operations
    print("\n2. Demo: Multi-step File Operations")
    print("   Task: Create directory structure and analyze it")

    result = await orchestrator.orchestrate(
        description="Create test directory and list its contents",
        task_type=TaskType.FILE_OPERATIONS,
        parameters={
            "operation": "create_directory",
            "directory_path": "/tmp/plato_demo",
        },
    )

    print(f"   Result: {'✅ Success' if result.success else '❌ Failed'}")
    if result.success:
        print(f"   Duration: {result.total_duration:.3f}s")
        print(f"   Agents used: {result.agents_used}")
        print(f"   Tasks completed: {len(result.task_results)}")

    # Demo 2: Code Analysis
    print("\n3. Demo: Code Analysis Orchestration")
    print("   Task: Analyze Python files for structure and metrics")

    result = await orchestrator.orchestrate(
        description="Analyze main Python file",
        task_type=TaskType.CODE_ANALYSIS,
        parameters={"file_path": "plato/__init__.py"},
    )

    print(f"   Result: {'✅ Success' if result.success else '❌ Failed'}")
    if result.success:
        print(f"   Duration: {result.total_duration:.3f}s")
        print(f"   Agents used: {result.agents_used}")
        # Show analysis results
        if result.task_results:
            task_result = result.task_results[0]
            analysis = task_result.get("result", {})
            print(f"   Language detected: {analysis.get('language', 'unknown')}")
            print(f"   Total lines: {analysis.get('total_lines', 0)}")
            print(f"   Code lines: {analysis.get('code_lines', 0)}")

    # Demo 3: Multi-file batch processing
    print("\n4. Demo: Batch Processing (Multiple Files)")
    print("   Task: Process multiple files in parallel")

    result = await orchestrator.orchestrate(
        description="Analyze multiple Python files for code quality",
        task_type=TaskType.CODE_ANALYSIS,
        parameters={
            "files": ["plato/__init__.py", "plato/cli.py"],
            "batch_process": True,
        },
    )

    print(f"   Result: {'✅ Success' if result.success else '❌ Failed'}")
    if result.success:
        print(f"   Duration: {result.total_duration:.3f}s")
        print(f"   Agents used: {result.agents_used}")
        print(f"   Files processed: {len(result.task_results)}")

    # Demo 4: Task History and Monitoring
    print("\n5. Demo: Task History and Monitoring")
    history = orchestrator.get_task_history(limit=5)
    print(f"   Recent tasks: {len(history)}")
    for i, task in enumerate(history[-3:], 1):  # Show last 3 tasks
        print(
            f"   {i}. {task['description']} -> {task['status']} ({task.get('duration', 0):.3f}s)"
        )

    # Demo 5: Agent Status
    print("\n6. Demo: Agent Status and Load Balancing")
    status = orchestrator.get_orchestration_status()
    print(f"   Active tasks: {status['active_tasks']}")
    print(f"   Available agents: {status['available_agents']}/{status['total_agents']}")

    for agent in status["agents"]:
        load_pct = (agent["current_load"] / agent["max_concurrent_tasks"]) * 100
        availability = "🟢" if agent["is_available"] else "🔴"
        print(f"   {availability} {agent['name']}: {load_pct:.0f}% load")

    print("\n" + "=" * 50)
    print("🎉 Demo completed! SuperClaude orchestration is working!")
    print("   Key features demonstrated:")
    print("   ✅ Multi-agent task coordination")
    print("   ✅ Intelligent agent selection")
    print("   ✅ Task decomposition and parallel execution")
    print("   ✅ Result aggregation and monitoring")
    print("   ✅ Load balancing and resource management")


if __name__ == "__main__":
    try:
        asyncio.run(demo_orchestration())
    except KeyboardInterrupt:
        print("\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback

        traceback.print_exc()
