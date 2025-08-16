"""SuperClaude-style agent orchestration system for Plato."""

import asyncio
import json
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union, Callable, Set
from uuid import uuid4

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Task execution status."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskType(Enum):
    """Types of tasks for agent assignment."""

    CODE_ANALYSIS = "code_analysis"
    FILE_OPERATIONS = "file_operations"
    RESEARCH = "research"
    DATA_PROCESSING = "data_processing"
    COMMUNICATION = "communication"
    GENERAL = "general"


class AgentCapability(Enum):
    """Agent capabilities for matching with tasks."""

    FILE_MANIPULATION = "file_manipulation"
    CODE_ANALYSIS = "code_analysis"
    LANGUAGE_PROCESSING = "language_processing"
    DATA_ANALYSIS = "data_analysis"
    PLANNING = "planning"
    EXECUTION = "execution"
    RESEARCH = "research"
    COMMUNICATION = "communication"


@dataclass
class Task:
    """Represents a task in the orchestration system."""

    id: str = field(default_factory=lambda: str(uuid4()))
    description: str = ""
    task_type: TaskType = TaskType.GENERAL
    parameters: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    assigned_agent: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def duration(self) -> Optional[float]:
        """Get task execution duration."""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary."""
        return {
            "id": self.id,
            "description": self.description,
            "task_type": self.task_type.value,
            "parameters": self.parameters,
            "dependencies": self.dependencies,
            "status": self.status.value,
            "result": self.result,
            "error": self.error,
            "assigned_agent": self.assigned_agent,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "duration": self.duration,
            "metadata": self.metadata,
        }


@dataclass
class Agent:
    """Represents an agent in the orchestration system."""

    id: str
    name: str
    description: str
    capabilities: List[AgentCapability]
    task_types: List[TaskType]
    priority: int = 1  # Lower number = higher priority
    is_available: bool = True
    current_load: int = 0
    max_concurrent_tasks: int = 1
    execution_function: Optional[Callable] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def can_handle_task(self, task: Task) -> bool:
        """Check if agent can handle the given task."""
        if not self.is_available:
            return False

        if self.current_load >= self.max_concurrent_tasks:
            return False

        # Check if agent supports the task type
        if task.task_type not in self.task_types:
            return False

        # Additional capability-based checks could go here
        return True

    def get_compatibility_score(self, task: Task) -> float:
        """Get compatibility score for a task (0.0 to 1.0)."""
        if not self.can_handle_task(task):
            return 0.0

        score = 0.0

        # Base score for task type compatibility
        if task.task_type in self.task_types:
            score += 0.5

        # Priority bonus (higher priority agents get bonus)
        score += (10 - self.priority) / 10 * 0.3

        # Load penalty (less loaded agents get bonus)
        load_penalty = self.current_load / self.max_concurrent_tasks
        score += (1 - load_penalty) * 0.2

        return min(score, 1.0)

    def to_dict(self) -> Dict[str, Any]:
        """Convert agent to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "capabilities": [cap.value for cap in self.capabilities],
            "task_types": [tt.value for tt in self.task_types],
            "priority": self.priority,
            "is_available": self.is_available,
            "current_load": self.current_load,
            "max_concurrent_tasks": self.max_concurrent_tasks,
            "metadata": self.metadata,
        }


@dataclass
class OrchestrationResult:
    """Result of task orchestration."""

    success: bool
    task_results: List[Dict[str, Any]] = field(default_factory=list)
    execution_plan: List[str] = field(default_factory=list)
    total_duration: Optional[float] = None
    agents_used: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "success": self.success,
            "task_results": self.task_results,
            "execution_plan": self.execution_plan,
            "total_duration": self.total_duration,
            "agents_used": self.agents_used,
            "metadata": self.metadata,
            "error": self.error,
        }


class AgentRegistry:
    """Registry for managing agents in the orchestration system."""

    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self._setup_default_agents()

    def _setup_default_agents(self):
        """Setup default agents based on available tools."""
        # File operations agent
        file_agent = Agent(
            id="file_ops_agent",
            name="File Operations Agent",
            description="Handles file and directory operations",
            capabilities=[AgentCapability.FILE_MANIPULATION, AgentCapability.EXECUTION],
            task_types=[TaskType.FILE_OPERATIONS],
            priority=1,
            max_concurrent_tasks=3,
        )
        self.register_agent(file_agent)

        # Code analysis agent
        code_agent = Agent(
            id="code_analysis_agent",
            name="Code Analysis Agent",
            description="Analyzes code structure and provides insights",
            capabilities=[
                AgentCapability.CODE_ANALYSIS,
                AgentCapability.LANGUAGE_PROCESSING,
                AgentCapability.DATA_ANALYSIS,
            ],
            task_types=[TaskType.CODE_ANALYSIS],
            priority=2,
            max_concurrent_tasks=2,
        )
        self.register_agent(code_agent)

        # General purpose agent
        general_agent = Agent(
            id="general_agent",
            name="General Purpose Agent",
            description="Handles general tasks and communication",
            capabilities=[
                AgentCapability.COMMUNICATION,
                AgentCapability.PLANNING,
                AgentCapability.EXECUTION,
            ],
            task_types=[TaskType.GENERAL, TaskType.COMMUNICATION, TaskType.RESEARCH],
            priority=3,
            max_concurrent_tasks=5,
        )
        self.register_agent(general_agent)

        # Data processing agent
        data_agent = Agent(
            id="data_processing_agent",
            name="Data Processing Agent",
            description="Processes and analyzes data",
            capabilities=[
                AgentCapability.DATA_ANALYSIS,
                AgentCapability.LANGUAGE_PROCESSING,
            ],
            task_types=[TaskType.DATA_PROCESSING],
            priority=2,
            max_concurrent_tasks=3,
        )
        self.register_agent(data_agent)

    def register_agent(self, agent: Agent):
        """Register a new agent."""
        self.agents[agent.id] = agent
        logger.info(f"Registered agent: {agent.name} ({agent.id})")

    def unregister_agent(self, agent_id: str):
        """Unregister an agent."""
        if agent_id in self.agents:
            agent = self.agents.pop(agent_id)
            logger.info(f"Unregistered agent: {agent.name} ({agent_id})")
        else:
            logger.warning(f"Agent {agent_id} not found for unregistration")

    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get agent by ID."""
        return self.agents.get(agent_id)

    def list_agents(self) -> List[Agent]:
        """List all registered agents."""
        return list(self.agents.values())

    def get_available_agents(self) -> List[Agent]:
        """Get all available agents."""
        return [agent for agent in self.agents.values() if agent.is_available]

    def get_agents_by_capability(self, capability: AgentCapability) -> List[Agent]:
        """Get agents with specific capability."""
        return [
            agent
            for agent in self.agents.values()
            if capability in agent.capabilities and agent.is_available
        ]

    def get_agents_by_task_type(self, task_type: TaskType) -> List[Agent]:
        """Get agents that can handle specific task type."""
        return [
            agent
            for agent in self.agents.values()
            if task_type in agent.task_types and agent.is_available
        ]

    def update_agent_load(self, agent_id: str, load_delta: int):
        """Update agent's current load."""
        if agent_id in self.agents:
            self.agents[agent_id].current_load += load_delta
            self.agents[agent_id].current_load = max(
                0, self.agents[agent_id].current_load
            )

    def set_agent_availability(self, agent_id: str, available: bool):
        """Set agent availability."""
        if agent_id in self.agents:
            self.agents[agent_id].is_available = available


class TaskDecomposer:
    """Decomposes complex tasks into smaller, manageable subtasks."""

    def __init__(self):
        self.decomposition_strategies = {
            TaskType.CODE_ANALYSIS: self._decompose_code_analysis,
            TaskType.FILE_OPERATIONS: self._decompose_file_operations,
            TaskType.RESEARCH: self._decompose_research,
            TaskType.DATA_PROCESSING: self._decompose_data_processing,
            TaskType.GENERAL: self._decompose_general,
        }

    async def decompose_task(self, task: Task) -> List[Task]:
        """Decompose a task into subtasks."""
        logger.info(f"Decomposing task: {task.description}")

        strategy = self.decomposition_strategies.get(
            task.task_type, self._decompose_general
        )

        subtasks = await strategy(task)

        # Set up dependencies
        for i, subtask in enumerate(subtasks):
            if i > 0:
                subtask.dependencies = [subtasks[i - 1].id]

        logger.info(f"Decomposed into {len(subtasks)} subtasks")
        return subtasks

    async def _decompose_code_analysis(self, task: Task) -> List[Task]:
        """Decompose code analysis tasks."""
        subtasks = []

        # Check if this is a multi-file analysis
        files = task.parameters.get("files", [])
        if isinstance(files, list) and len(files) > 1:
            # Create subtask for each file
            for file_path in files:
                subtask = Task(
                    description=f"Analyze file: {file_path}",
                    task_type=TaskType.CODE_ANALYSIS,
                    parameters={"file_path": file_path},
                    metadata={"parent_task_id": task.id},
                )
                subtasks.append(subtask)
        else:
            # Single task
            subtasks.append(task)

        return subtasks

    async def _decompose_file_operations(self, task: Task) -> List[Task]:
        """Decompose file operation tasks."""
        subtasks = []

        operation = task.parameters.get("operation", "")

        if operation == "batch_process":
            # Process multiple files
            files = task.parameters.get("files", [])
            for file_path in files:
                subtask = Task(
                    description=f"Process file: {file_path}",
                    task_type=TaskType.FILE_OPERATIONS,
                    parameters={
                        "operation": "single_process",
                        "file_path": file_path,
                        **{
                            k: v
                            for k, v in task.parameters.items()
                            if k not in ["operation", "files"]
                        },
                    },
                    metadata={"parent_task_id": task.id},
                )
                subtasks.append(subtask)
        else:
            # Single operation
            subtasks.append(task)

        return subtasks

    async def _decompose_research(self, task: Task) -> List[Task]:
        """Decompose research tasks."""
        subtasks = []

        # Break research into phases
        search_task = Task(
            description=f"Search for information: {task.description}",
            task_type=TaskType.RESEARCH,
            parameters={**task.parameters, "phase": "search"},
            metadata={"parent_task_id": task.id, "phase": "search"},
        )
        subtasks.append(search_task)

        analysis_task = Task(
            description=f"Analyze research results: {task.description}",
            task_type=TaskType.DATA_PROCESSING,
            parameters={**task.parameters, "phase": "analysis"},
            metadata={"parent_task_id": task.id, "phase": "analysis"},
        )
        subtasks.append(analysis_task)

        return subtasks

    async def _decompose_data_processing(self, task: Task) -> List[Task]:
        """Decompose data processing tasks."""
        subtasks = []

        # Check for batch processing
        data_sources = task.parameters.get("data_sources", [])
        if isinstance(data_sources, list) and len(data_sources) > 1:
            for source in data_sources:
                subtask = Task(
                    description=f"Process data source: {source}",
                    task_type=TaskType.DATA_PROCESSING,
                    parameters={"data_source": source},
                    metadata={"parent_task_id": task.id},
                )
                subtasks.append(subtask)
        else:
            subtasks.append(task)

        return subtasks

    async def _decompose_general(self, task: Task) -> List[Task]:
        """Default decomposition for general tasks."""
        # For now, return the task as-is
        # This could be enhanced with NLP analysis of the task description
        return [task]


class AgentSelector:
    """Selects the best agent for each task."""

    def __init__(self, agent_registry: AgentRegistry):
        self.agent_registry = agent_registry

    async def select_agent(self, task: Task) -> Optional[Agent]:
        """Select the best agent for a task."""
        logger.info(f"Selecting agent for task: {task.description}")

        # Get candidate agents
        candidates = self.agent_registry.get_agents_by_task_type(task.task_type)

        if not candidates:
            # Fallback to general agents
            candidates = self.agent_registry.get_agents_by_task_type(TaskType.GENERAL)

        if not candidates:
            logger.warning(f"No suitable agents found for task: {task.id}")
            return None

        # Score and rank candidates
        scored_candidates = []
        for agent in candidates:
            score = agent.get_compatibility_score(task)
            if score > 0:
                scored_candidates.append((agent, score))

        if not scored_candidates:
            logger.warning(f"No compatible agents found for task: {task.id}")
            return None

        # Sort by score (descending)
        scored_candidates.sort(key=lambda x: x[1], reverse=True)

        selected_agent = scored_candidates[0][0]
        logger.info(
            f"Selected agent: {selected_agent.name} (score: {scored_candidates[0][1]:.2f})"
        )

        return selected_agent

    async def select_agents_batch(
        self, tasks: List[Task]
    ) -> Dict[str, Optional[Agent]]:
        """Select agents for multiple tasks efficiently."""
        assignments = {}

        # Sort tasks by priority if available
        sorted_tasks = sorted(
            tasks, key=lambda t: t.metadata.get("priority", 5), reverse=True
        )

        for task in sorted_tasks:
            agent = await self.select_agent(task)
            assignments[task.id] = agent

            # Update agent load for future selections
            if agent:
                self.agent_registry.update_agent_load(agent.id, 1)

        return assignments


class ResultAggregator:
    """Aggregates and processes results from multiple agents."""

    def __init__(self):
        self.aggregation_strategies = {
            TaskType.CODE_ANALYSIS: self._aggregate_code_analysis,
            TaskType.FILE_OPERATIONS: self._aggregate_file_operations,
            TaskType.RESEARCH: self._aggregate_research,
            TaskType.DATA_PROCESSING: self._aggregate_data_processing,
            TaskType.GENERAL: self._aggregate_general,
        }

    async def aggregate_results(
        self, tasks: List[Task], primary_task_type: TaskType
    ) -> OrchestrationResult:
        """Aggregate results from multiple related tasks."""
        logger.info(f"Aggregating results from {len(tasks)} tasks")

        # Separate successful and failed tasks
        successful_tasks = [t for t in tasks if t.status == TaskStatus.COMPLETED]
        failed_tasks = [t for t in tasks if t.status == TaskStatus.FAILED]

        if not successful_tasks and failed_tasks:
            return OrchestrationResult(
                success=False,
                error=f"All {len(failed_tasks)} tasks failed",
                metadata={"failed_count": len(failed_tasks)},
            )

        # Use appropriate aggregation strategy
        strategy = self.aggregation_strategies.get(
            primary_task_type, self._aggregate_general
        )

        result = await strategy(successful_tasks, failed_tasks)

        # Extract agents used
        agents_used = list(set(t.assigned_agent for t in tasks if t.assigned_agent))
        result.agents_used = agents_used

        # Add common metadata
        result.metadata.update(
            {
                "total_tasks": len(tasks),
                "successful_tasks": len(successful_tasks),
                "failed_tasks": len(failed_tasks),
                "agents_used": agents_used,
            }
        )

        return result

    async def _aggregate_code_analysis(
        self, successful_tasks: List[Task], failed_tasks: List[Task]
    ) -> OrchestrationResult:
        """Aggregate code analysis results."""
        combined_results = {
            "files_analyzed": [],
            "summary": {
                "total_files": len(successful_tasks),
                "total_lines": 0,
                "languages": set(),
                "issues_found": 0,
            },
            "details": [],
        }

        for task in successful_tasks:
            if task.result and isinstance(task.result, dict):
                # Extract file analysis data
                file_info = {
                    "file": task.parameters.get("file_path", "unknown"),
                    "result": task.result,
                }
                combined_results["files_analyzed"].append(file_info)
                combined_results["details"].append(task.result)

                # Update summary
                if "lines" in task.result:
                    combined_results["summary"]["total_lines"] += task.result["lines"]
                if "language" in task.result:
                    combined_results["summary"]["languages"].add(
                        task.result["language"]
                    )
                if "issues" in task.result:
                    combined_results["summary"]["issues_found"] += len(
                        task.result["issues"]
                    )

        # Convert set to list for JSON serialization
        combined_results["summary"]["languages"] = list(
            combined_results["summary"]["languages"]
        )

        return OrchestrationResult(
            success=True,
            task_results=[t.to_dict() for t in successful_tasks],
            metadata={"aggregated_analysis": combined_results},
        )

    async def _aggregate_file_operations(
        self, successful_tasks: List[Task], failed_tasks: List[Task]
    ) -> OrchestrationResult:
        """Aggregate file operation results."""
        operations_summary = {
            "files_processed": len(successful_tasks),
            "operations": {},
            "total_size": 0,
        }

        for task in successful_tasks:
            operation = task.parameters.get("operation", "unknown")
            if operation not in operations_summary["operations"]:
                operations_summary["operations"][operation] = 0
            operations_summary["operations"][operation] += 1

            # Add file size if available
            if task.result and isinstance(task.result, dict):
                size = task.result.get("size", 0)
                operations_summary["total_size"] += size

        return OrchestrationResult(
            success=True,
            task_results=[t.to_dict() for t in successful_tasks],
            metadata={"operations_summary": operations_summary},
        )

    async def _aggregate_research(
        self, successful_tasks: List[Task], failed_tasks: List[Task]
    ) -> OrchestrationResult:
        """Aggregate research results."""
        research_summary = {
            "sources_found": 0,
            "key_findings": [],
            "search_phases": len(
                [t for t in successful_tasks if t.metadata.get("phase") == "search"]
            ),
            "analysis_phases": len(
                [t for t in successful_tasks if t.metadata.get("phase") == "analysis"]
            ),
        }

        for task in successful_tasks:
            if task.result and isinstance(task.result, dict):
                if "sources" in task.result:
                    research_summary["sources_found"] += len(task.result["sources"])
                if "findings" in task.result:
                    research_summary["key_findings"].extend(task.result["findings"])

        return OrchestrationResult(
            success=True,
            task_results=[t.to_dict() for t in successful_tasks],
            metadata={"research_summary": research_summary},
        )

    async def _aggregate_data_processing(
        self, successful_tasks: List[Task], failed_tasks: List[Task]
    ) -> OrchestrationResult:
        """Aggregate data processing results."""
        processing_summary = {
            "datasets_processed": len(successful_tasks),
            "total_records": 0,
            "processing_time": sum(t.duration or 0 for t in successful_tasks),
        }

        for task in successful_tasks:
            if task.result and isinstance(task.result, dict):
                records = task.result.get("records_processed", 0)
                processing_summary["total_records"] += records

        return OrchestrationResult(
            success=True,
            task_results=[t.to_dict() for t in successful_tasks],
            metadata={"processing_summary": processing_summary},
        )

    async def _aggregate_general(
        self, successful_tasks: List[Task], failed_tasks: List[Task]
    ) -> OrchestrationResult:
        """Default aggregation for general tasks."""
        return OrchestrationResult(
            success=True,
            task_results=[t.to_dict() for t in successful_tasks],
            metadata={
                "task_summaries": [
                    {"id": t.id, "description": t.description, "duration": t.duration}
                    for t in successful_tasks
                ]
            },
        )


class TaskOrchestrator:
    """Main orchestrator that coordinates agents to execute complex tasks."""

    def __init__(self, tool_manager=None):
        self.agent_registry = AgentRegistry()
        self.task_decomposer = TaskDecomposer()
        self.agent_selector = AgentSelector(self.agent_registry)
        self.result_aggregator = ResultAggregator()
        self.tool_manager = tool_manager

        # Task tracking
        self.active_tasks: Dict[str, Task] = {}
        self.task_history: List[Task] = []

        # Setup execution functions for agents
        self._setup_agent_execution_functions()

    def _setup_agent_execution_functions(self):
        """Setup execution functions for each agent."""
        # File operations agent
        file_agent = self.agent_registry.get_agent("file_ops_agent")
        if file_agent:
            file_agent.execution_function = self._execute_file_operation_task

        # Code analysis agent
        code_agent = self.agent_registry.get_agent("code_analysis_agent")
        if code_agent:
            code_agent.execution_function = self._execute_code_analysis_task

        # General agent
        general_agent = self.agent_registry.get_agent("general_agent")
        if general_agent:
            general_agent.execution_function = self._execute_general_task

        # Data processing agent
        data_agent = self.agent_registry.get_agent("data_processing_agent")
        if data_agent:
            data_agent.execution_function = self._execute_data_processing_task

    async def orchestrate(
        self,
        description: str,
        task_type: TaskType = TaskType.GENERAL,
        parameters: Dict[str, Any] = None,
    ) -> OrchestrationResult:
        """Main orchestration method."""
        logger.info(f"Starting orchestration: {description}")
        start_time = time.time()

        if parameters is None:
            parameters = {}

        try:
            # Create main task
            main_task = Task(
                description=description, task_type=task_type, parameters=parameters
            )

            # Decompose into subtasks
            subtasks = await self.task_decomposer.decompose_task(main_task)

            # Select agents for subtasks
            agent_assignments = await self.agent_selector.select_agents_batch(subtasks)

            # Execute tasks
            execution_results = await self._execute_tasks(subtasks, agent_assignments)

            # Aggregate results
            result = await self.result_aggregator.aggregate_results(subtasks, task_type)

            # Update timing and metadata
            result.total_duration = time.time() - start_time
            result.execution_plan = [
                f"Task {t.id}: {t.description} -> Agent {agent_assignments.get(t.id, 'None')}"
                for t in subtasks
            ]

            logger.info(f"Orchestration completed in {result.total_duration:.2f}s")
            return result

        except Exception as e:
            logger.error(f"Orchestration failed: {e}")
            return OrchestrationResult(
                success=False, error=str(e), total_duration=time.time() - start_time
            )

    async def _execute_tasks(
        self, tasks: List[Task], agent_assignments: Dict[str, Optional[Agent]]
    ) -> List[Task]:
        """Execute tasks with their assigned agents."""
        # Create dependency map
        dependency_map = {task.id: set(task.dependencies) for task in tasks}
        completed_tasks = set()

        # Execute tasks in dependency order
        while len(completed_tasks) < len(tasks):
            # Find tasks ready to execute (dependencies satisfied)
            ready_tasks = [
                task
                for task in tasks
                if (
                    task.id not in completed_tasks
                    and task.status == TaskStatus.PENDING
                    and dependency_map[task.id].issubset(completed_tasks)
                )
            ]

            if not ready_tasks:
                # Check for circular dependencies or other issues
                remaining_tasks = [t for t in tasks if t.id not in completed_tasks]
                if remaining_tasks:
                    logger.error(
                        f"Circular dependency detected or execution failed for tasks: {[t.id for t in remaining_tasks]}"
                    )
                    for task in remaining_tasks:
                        task.status = TaskStatus.FAILED
                        task.error = "Circular dependency or execution failure"
                        completed_tasks.add(task.id)
                break

            # Execute ready tasks in parallel
            execution_tasks = []
            for task in ready_tasks:
                agent = agent_assignments.get(task.id)
                if agent:
                    execution_tasks.append(self._execute_single_task(task, agent))
                else:
                    task.status = TaskStatus.FAILED
                    task.error = "No suitable agent found"
                    completed_tasks.add(task.id)

            if execution_tasks:
                await asyncio.gather(*execution_tasks, return_exceptions=True)

            # Update completed tasks
            for task in ready_tasks:
                if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                    completed_tasks.add(task.id)

        return tasks

    async def _execute_single_task(self, task: Task, agent: Agent):
        """Execute a single task with the assigned agent."""
        logger.info(f"Executing task {task.id} with agent {agent.name}")

        try:
            # Update task status
            task.status = TaskStatus.IN_PROGRESS
            task.started_at = time.time()
            task.assigned_agent = agent.id

            # Update agent load
            self.agent_registry.update_agent_load(agent.id, 1)

            # Execute the task
            if agent.execution_function:
                result = await agent.execution_function(task)
                task.result = result
                task.status = TaskStatus.COMPLETED
            else:
                raise Exception(f"No execution function defined for agent {agent.name}")

        except Exception as e:
            logger.error(f"Task {task.id} failed: {e}")
            task.status = TaskStatus.FAILED
            task.error = str(e)

        finally:
            # Update timing and cleanup
            task.completed_at = time.time()
            self.agent_registry.update_agent_load(agent.id, -1)

            # Store in history
            self.task_history.append(task)

    async def _execute_file_operation_task(self, task: Task) -> Any:
        """Execute file operation task using embedded tools."""
        if not self.tool_manager:
            raise Exception("Tool manager not available")

        operation = task.parameters.get("operation", "")

        if operation == "read_file":
            file_path = task.parameters.get("file_path")
            result = await self.tool_manager.execute_tool(
                "ReadFileTool", file_path=file_path
            )

        elif operation == "write_file":
            file_path = task.parameters.get("file_path")
            content = task.parameters.get("content", "")
            result = await self.tool_manager.execute_tool(
                "WriteFileTool", file_path=file_path, content=content
            )

        elif operation == "list_directory":
            directory_path = task.parameters.get("directory_path", ".")
            result = await self.tool_manager.execute_tool(
                "ListDirectoryTool", directory_path=directory_path
            )

        elif operation == "create_directory":
            directory_path = task.parameters.get("directory_path")
            result = await self.tool_manager.execute_tool(
                "CreateDirectoryTool", directory_path=directory_path
            )

        elif operation == "search_files":
            pattern = task.parameters.get("pattern", "")
            directory = task.parameters.get("directory", ".")
            result = await self.tool_manager.execute_tool(
                "SearchFilesTool", pattern=pattern, directory=directory
            )

        else:
            raise Exception(f"Unknown file operation: {operation}")

        if not result.success:
            raise Exception(result.error)

        return {
            "operation": operation,
            "success": True,
            "data": result.data,
            "metadata": result.metadata,
        }

    async def _execute_code_analysis_task(self, task: Task) -> Any:
        """Execute code analysis task."""
        file_path = task.parameters.get("file_path")
        if not file_path:
            raise Exception("file_path required for code analysis")

        if not self.tool_manager:
            raise Exception("Tool manager not available")

        # Read the file first
        read_result = await self.tool_manager.execute_tool(
            "ReadFileTool", file_path=file_path
        )
        if not read_result.success:
            raise Exception(f"Failed to read file: {read_result.error}")

        # Basic analysis
        content = read_result.data
        lines = content.split("\n") if isinstance(content, str) else []

        # Detect language based on file extension
        language = "unknown"
        if file_path.endswith((".py", ".pyx")):
            language = "python"
        elif file_path.endswith((".js", ".jsx", ".ts", ".tsx")):
            language = "javascript/typescript"
        elif file_path.endswith((".java", ".class")):
            language = "java"
        elif file_path.endswith((".c", ".h", ".cpp", ".hpp")):
            language = "c/c++"
        elif file_path.endswith((".go",)):
            language = "go"
        elif file_path.endswith((".rs",)):
            language = "rust"

        # Basic code metrics
        code_lines = [
            line for line in lines if line.strip() and not line.strip().startswith("#")
        ]
        comment_lines = [line for line in lines if line.strip().startswith("#")]

        return {
            "file_path": file_path,
            "language": language,
            "total_lines": len(lines),
            "code_lines": len(code_lines),
            "comment_lines": len(comment_lines),
            "blank_lines": len(lines) - len(code_lines) - len(comment_lines),
            "size": read_result.metadata.get("size", 0),
            "analysis_timestamp": time.time(),
        }

    async def _execute_data_processing_task(self, task: Task) -> Any:
        """Execute data processing task."""
        data_source = task.parameters.get("data_source")
        operation = task.parameters.get("operation", "process")

        # Simulate data processing
        records_processed = task.parameters.get("record_count", 100)

        return {
            "data_source": data_source,
            "operation": operation,
            "records_processed": records_processed,
            "processing_time": 0.1,  # Simulated time
            "success": True,
        }

    async def _execute_general_task(self, task: Task) -> Any:
        """Execute general task."""
        # For general tasks, return basic execution info
        return {
            "task_id": task.id,
            "description": task.description,
            "parameters": task.parameters,
            "execution_time": time.time(),
            "success": True,
        }

    def get_orchestration_status(self) -> Dict[str, Any]:
        """Get current orchestration status."""
        return {
            "active_tasks": len(self.active_tasks),
            "total_agents": len(self.agent_registry.agents),
            "available_agents": len(self.agent_registry.get_available_agents()),
            "task_history_count": len(self.task_history),
            "agents": [agent.to_dict() for agent in self.agent_registry.list_agents()],
        }

    def get_task_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent task history."""
        recent_tasks = sorted(
            self.task_history, key=lambda t: t.created_at, reverse=True
        )[:limit]

        return [task.to_dict() for task in recent_tasks]
