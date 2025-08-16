"""FastAPI server for Plato AI orchestration system."""

import asyncio
import json
import logging
import os
import time
from contextlib import asynccontextmanager
from typing import Any, Optional

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from ..core.ai_router import AIProvider, AIRequest, AIRouter, TaskType
from ..core.context_manager import (
    ContextManager,
    ContextType,
    ConversationMessage,
    Priority,
)

# Removed MCP manager import - using embedded tools only
from ..core.security import (
    SecurityConfig,
    APIKeyValidator,
    SecurityHeadersMiddleware,
    RateLimitMiddleware,
    create_secure_logger,
    mask_sensitive_data,
)
from ..integrations.serena_mcp import SerenaLanguage
from ..core.embedded_tools import ToolManager
from ..core.orchestration import (
    TaskOrchestrator,
    TaskType as OrchTaskType,
    OrchestrationResult,
)

# Load environment variables
load_dotenv()

# Configure secure logging
logging.basicConfig(level=logging.INFO)
logger = create_secure_logger(__name__)

# Global managers
ai_router: AIRouter | None = None
context_manager: ContextManager | None = None
# Removed external MCP managers - using embedded tools only
security_config: SecurityConfig | None = None
api_key_validator: APIKeyValidator | None = None
tool_manager: ToolManager | None = None
task_orchestrator: TaskOrchestrator | None = None


class ChatRequest(BaseModel):
    """Chat request from client."""

    message: str = Field(..., description="User message")
    session_id: str | None = Field(None, description="Session ID")
    task_type: TaskType = Field(TaskType.CHAT, description="Task type")
    preferred_provider: AIProvider | None = Field(
        None, description="Preferred AI provider"
    )
    stream: bool = Field(False, description="Stream response")
    context: dict[str, Any] | None = Field(None, description="Additional context")
    tools: list[dict[str, Any]] | None = Field(None, description="Available tools")


class ChatResponse(BaseModel):
    """Chat response to client."""

    message: str = Field(..., description="AI response")
    session_id: str = Field(..., description="Session ID")
    provider: str = Field(..., description="AI provider used")
    tokens_used: int = Field(0, description="Tokens consumed")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class ToolCallRequest(BaseModel):
    """Tool call request."""

    tool_name: str = Field(..., description="Tool name")
    arguments: dict[str, Any] = Field(
        default_factory=dict, description="Tool arguments"
    )
    session_id: str | None = Field(None, description="Session ID")


class ToolCallResponse(BaseModel):
    """Tool call response."""

    success: bool = Field(..., description="Whether tool call succeeded")
    result: Any = Field(None, description="Tool result")
    error: str | None = Field(None, description="Error message")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class ProjectRequest(BaseModel):
    """Project analysis request."""

    project_path: str = Field(..., description="Project path")
    language: SerenaLanguage | None = Field(None, description="Programming language")
    operation: str = Field(..., description="Operation to perform")
    parameters: dict[str, Any] = Field(
        default_factory=dict, description="Operation parameters"
    )


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="Health status")
    version: str = Field(..., description="Plato version")
    uptime: float = Field(..., description="Uptime in seconds")
    ai_providers: dict[str, bool] = Field(..., description="AI provider health")
    mcp_servers: dict[str, bool | int] = Field(..., description="MCP server health and metadata")


class OrchestrationRequest(BaseModel):
    """Request for task orchestration."""

    description: str = Field(..., description="Task description")
    task_type: str = Field("general", description="Task type")
    parameters: dict[str, Any] = Field(
        default_factory=dict, description="Task parameters"
    )
    session_id: str | None = Field(None, description="Session ID")


class OrchestrationResponse(BaseModel):
    """Response from task orchestration."""

    success: bool = Field(..., description="Whether orchestration succeeded")
    task_results: list[dict[str, Any]] = Field(
        default_factory=list, description="Individual task results"
    )
    execution_plan: list[str] = Field(
        default_factory=list, description="Execution plan"
    )
    total_duration: float | None = Field(None, description="Total execution time")
    agents_used: list[str] = Field(
        default_factory=list, description="Agents that were used"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )
    error: str | None = Field(None, description="Error message if failed")


class AgentStatusResponse(BaseModel):
    """Response for agent status."""

    active_tasks: int = Field(..., description="Number of active tasks")
    total_agents: int = Field(..., description="Total number of agents")
    available_agents: int = Field(..., description="Number of available agents")
    task_history_count: int = Field(..., description="Number of tasks in history")
    agents: list[dict[str, Any]] = Field(..., description="Agent details")


# Startup/shutdown handlers
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global ai_router, context_manager, security_config, api_key_validator, tool_manager, task_orchestrator

    logger.info("Starting Plato server...")

    # Initialize security configuration
    security_config = SecurityConfig.from_environment()
    api_key_validator = APIKeyValidator(security_config)
    logger.info(
        f"Security configured with {len(security_config.allowed_origins)} allowed origins"
    )

    # Log security status (with sensitive data masked)
    logger.info(f"API Key required: {security_config.require_api_key}")
    logger.info(f"Rate limiting: {security_config.rate_limit_enabled}")
    logger.info(f"Security headers: {security_config.enable_security_headers}")

    # Initialize managers
    ai_router = AIRouter(config=load_ai_config())
    context_manager = ContextManager()
    tool_manager = ToolManager()  # Initialize embedded tools only
    task_orchestrator = TaskOrchestrator(
        tool_manager=tool_manager
    )  # Initialize orchestrator

    # Log embedded tools status
    available_tools = tool_manager.list_tools()
    logger.info(f"Embedded tools initialized: {len(available_tools)} tools available")
    logger.info(f"Available tools: {', '.join(available_tools)}")

    # Log orchestration status
    orch_status = task_orchestrator.get_orchestration_status()
    logger.info(
        f"Task orchestrator initialized: {orch_status['total_agents']} agents available"
    )
    logger.info(
        f"Available agents: {[agent['name'] for agent in orch_status['agents']]}"
    )

    logger.info(
        "Plato server started successfully (using embedded tools and orchestration)"
    )

    yield

    # Cleanup
    logger.info("Shutting down Plato server...")
    logger.info("Plato server shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Plato AI Orchestration System",
    description="AI orchestration system with MCP integration",
    version="0.1.0",
    lifespan=lifespan,
    docs_url=(
        "/docs" if os.getenv("PLATO_DEV_MODE", "false").lower() == "true" else None
    ),
    redoc_url=(
        "/redoc" if os.getenv("PLATO_DEV_MODE", "false").lower() == "true" else None
    ),
)

# Initialize security config early for middleware setup
_temp_security_config = SecurityConfig.from_environment()

# Add middlewares in correct order (reverse of execution order)
# These execute in reverse order: Rate Limit -> Security Headers -> CORS
app.add_middleware(RateLimitMiddleware, config=_temp_security_config)
app.add_middleware(SecurityHeadersMiddleware, config=_temp_security_config)
app.add_middleware(
    CORSMiddleware,
    allow_origins=_temp_security_config.allowed_origins,
    allow_credentials=_temp_security_config.allow_credentials,
    allow_methods=_temp_security_config.allowed_methods,
    allow_headers=_temp_security_config.allowed_headers,
    allow_origin_regex=_temp_security_config.allowed_origins_regex,
)

# Startup time for health checks
startup_time = time.time()


# Note: Middlewares will be added after security config is initialized


def load_ai_config() -> dict[str, Any]:
    """Load AI provider configuration securely."""
    config = {}

    # Load from environment variables
    if api_key := os.getenv("ANTHROPIC_API_KEY"):
        config["anthropic_api_key"] = api_key
        logger.info("Anthropic API key configured (masked)")

    # Skip OpenAI if it's a dummy key
    if api_key := os.getenv("OPENAI_API_KEY"):
        if not api_key.startswith("dummy"):
            config["openai_api_key"] = api_key
            logger.info("OpenAI API key configured (masked)")
        else:
            logger.info("Skipping dummy OpenAI API key")

    if api_key := os.getenv("GEMINI_API_KEY"):
        config["gemini_api_key"] = api_key
        logger.info("Gemini API key configured (masked)")

    if api_key := os.getenv("OPENROUTER_API_KEY"):
        config["openrouter_api_key"] = api_key
        logger.info("OpenRouter API key configured (masked)")

    # Set Qwen URL to point to the local server
    qwen_url = os.getenv("QWEN_BASE_URL", "http://192.168.1.28:8000")
    config["qwen_base_url"] = qwen_url
    logger.info(f"Qwen base URL configured: {qwen_url}")

    # Never log the actual keys
    if config:
        logger.info(f"Loaded {len(config)} AI provider configurations")

    return config


# Removed setup_mcp_servers function - using embedded tools only


# Dependency injection
async def get_ai_router() -> AIRouter:
    """Get AI router instance."""
    if not ai_router:
        raise HTTPException(status_code=500, detail="AI router not initialized")
    return ai_router


async def get_context_manager() -> ContextManager:
    """Get context manager instance."""
    if not context_manager:
        raise HTTPException(status_code=500, detail="Context manager not initialized")
    return context_manager


async def get_tool_manager() -> ToolManager:
    """Get tool manager instance."""
    if not tool_manager:
        raise HTTPException(status_code=500, detail="Tool manager not initialized")
    return tool_manager


async def get_task_orchestrator() -> TaskOrchestrator:
    """Get task orchestrator instance."""
    if not task_orchestrator:
        raise HTTPException(status_code=500, detail="Task orchestrator not initialized")
    return task_orchestrator


def get_api_key_validator():
    """Get API key validator dependency."""
    if api_key_validator:
        return api_key_validator
    return APIKeyValidator(SecurityConfig())


async def verify_api_key(
    api_key: Optional[str] = Depends(get_api_key_validator()),
) -> Optional[str]:
    """Verify API key if required."""
    return api_key


# API Routes


@app.get("/health", response_model=HealthResponse)
async def health_check(
    router: AIRouter = Depends(get_ai_router),
    tools: ToolManager = Depends(get_tool_manager),
):
    """Health check endpoint."""
    # Check AI providers
    ai_health = await router.health_check()

    # Check embedded tools (report as healthy if initialized)
    embedded_tools = {}
    try:
        available_tools = tools.list_tools()
        embedded_tools["embedded_tools"] = True
        embedded_tools["tool_count"] = len(available_tools)
    except Exception:
        embedded_tools["embedded_tools"] = False
        embedded_tools["tool_count"] = 0

    return HealthResponse(
        status="healthy",
        version="0.1.0",
        uptime=time.time() - startup_time,
        ai_providers=ai_health,
        mcp_servers=embedded_tools,  # Report embedded tools status as "mcp_servers" for compatibility
    )


@app.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    router: AIRouter = Depends(get_ai_router),
    context: ContextManager = Depends(get_context_manager),
    api_key: Optional[str] = Depends(verify_api_key),
):
    """Send chat message to AI."""
    try:
        # Get or create session
        session_id = request.session_id
        if not session_id:
            session_id = await context.create_session()

        # Add user message to context
        user_message = ConversationMessage(role="user", content=request.message)
        await context.add_message(user_message, session_id)

        # Get conversation history
        history = context.get_conversation_history(session_id)

        # Create AI request
        ai_request = AIRequest(
            messages=[
                {
                    "role": msg.role,
                    "content": msg.content,
                    "name": msg.name,
                    "tool_calls": msg.tool_calls,
                    "tool_call_id": msg.tool_call_id,
                }
                for msg in history
            ],
            task_type=request.task_type,
            preferred_provider=request.preferred_provider,
            stream=request.stream,
            tools=request.tools,
            context=request.context,
        )

        # Get AI response
        ai_response = await router.chat(ai_request)

        # Add AI response to context
        ai_message = ConversationMessage(
            role="assistant",
            content=ai_response.content,
            ai_provider=ai_response.provider.value,
            tokens=ai_response.tokens_used,
            tool_calls=ai_response.tool_calls,
        )
        await context.add_message(ai_message, session_id)

        # Update current AI provider
        await context.switch_ai_provider(ai_response.provider.value, session_id)

        return ChatResponse(
            message=ai_response.content,
            session_id=session_id,
            provider=ai_response.provider.value,
            tokens_used=ai_response.tokens_used,
            metadata=ai_response.metadata,
        )

    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat/stream")
async def chat_stream(
    request: ChatRequest,
    router: AIRouter = Depends(get_ai_router),
    context: ContextManager = Depends(get_context_manager),
):
    """Stream chat response from AI."""
    try:
        # Force streaming
        request.stream = True

        async def generate():
            # Get or create session
            session_id = request.session_id
            if not session_id:
                session_id = await context.create_session()

            # Add user message to context
            user_message = ConversationMessage(role="user", content=request.message)
            await context.add_message(user_message, session_id)

            # Get conversation history
            history = context.get_conversation_history(session_id)

            # Create AI request
            ai_request = AIRequest(
                messages=[
                    {
                        "role": msg.role,
                        "content": msg.content,
                        "name": msg.name,
                        "tool_calls": msg.tool_calls,
                        "tool_call_id": msg.tool_call_id,
                    }
                    for msg in history
                ],
                task_type=request.task_type,
                preferred_provider=request.preferred_provider,
                stream=True,
                tools=request.tools,
                context=request.context,
            )

            # Stream AI response
            ai_response = await router.chat(ai_request)

            # Yield response chunks
            response_data = {
                "session_id": session_id,
                "provider": ai_response.provider.value,
                "content": ai_response.content,
                "tokens_used": ai_response.tokens_used,
                "metadata": ai_response.metadata,
            }

            yield f"data: {json.dumps(response_data)}\n\n"

            # Add AI response to context
            ai_message = ConversationMessage(
                role="assistant",
                content=ai_response.content,
                ai_provider=ai_response.provider.value,
                tokens=ai_response.tokens_used,
                tool_calls=ai_response.tool_calls,
            )
            await context.add_message(ai_message, session_id)

        return StreamingResponse(
            generate(), media_type="text/plain", headers={"Cache-Control": "no-cache"}
        )

    except Exception as e:
        logger.error(f"Stream chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tools/call", response_model=ToolCallResponse)
async def call_tool(
    request: ToolCallRequest,
    tools: ToolManager = Depends(get_tool_manager),
    context: ContextManager = Depends(get_context_manager),
    api_key: Optional[str] = Depends(verify_api_key),
):
    """Call an embedded tool."""
    try:
        # Call the embedded tool
        result = await tools.execute_tool(request.tool_name, **request.arguments)

        # Add tool result to context
        if request.session_id:
            await context.add_context(
                content=f"Tool call: {request.tool_name}\nResult: {json.dumps(result.data if result.success else result.error, indent=2)}",
                context_type=ContextType.TOOL_RESULT,
                priority=Priority.MEDIUM,
                metadata={
                    "tool_name": request.tool_name,
                    "arguments": request.arguments,
                    "timestamp": time.time(),
                },
                session_id=request.session_id,
            )

        return ToolCallResponse(
            success=result.success,
            result=result.data if result.success else None,
            error=result.error if not result.success else None,
            metadata={"tool_name": request.tool_name},
        )

    except Exception as e:
        logger.error(f"Tool call error: {e}")
        return ToolCallResponse(
            success=False, error=str(e), metadata={"tool_name": request.tool_name}
        )


@app.get("/tools")
async def list_tools(tools: ToolManager = Depends(get_tool_manager)):
    """List available embedded tools."""
    tools_list = []

    # Get embedded tools only
    for tool_schema in tools.get_tool_schemas():
        tools_list.append(
            {
                "name": tool_schema["name"],
                "description": tool_schema["description"],
                "server": "embedded",
                "type": "embedded",
                "input_schema": tool_schema.get("parameters", {}),
            }
        )

    return {"tools": tools_list}


@app.post("/tools/embedded/{tool_name}")
async def execute_embedded_tool(
    tool_name: str,
    parameters: dict[str, Any] = None,
):
    """Execute an embedded tool."""
    if not tool_manager:
        raise HTTPException(status_code=500, detail="Tool manager not initialized")

    if parameters is None:
        parameters = {}

    try:
        result = await tool_manager.execute_tool(tool_name, **parameters)
        return {
            "success": result.success,
            "data": result.data,
            "error": result.error,
            "metadata": result.metadata,
        }
    except Exception as e:
        logger.error(f"Embedded tool execution error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze", response_model=dict[str, Any])
async def analyze_code(
    request: ProjectRequest,
    tools: ToolManager = Depends(get_tool_manager),
    context: ContextManager = Depends(get_context_manager),
):
    """Analyze code using embedded tools."""
    try:
        result = None

        if request.operation == "read_file":
            file_path = request.parameters.get("file_path")
            if not file_path:
                raise ValueError("file_path required for read operation")
            result = await tools.execute_tool("ReadFileTool", file_path=file_path)

        elif request.operation == "list_directory":
            directory_path = request.parameters.get(
                "directory_path", request.project_path
            )
            result = await tools.execute_tool(
                "ListDirectoryTool", directory_path=directory_path
            )

        elif request.operation == "search_files":
            pattern = request.parameters.get("pattern", "")
            directory = request.parameters.get("directory", request.project_path)
            result = await tools.execute_tool(
                "SearchFilesTool", pattern=pattern, directory=directory
            )

        else:
            raise ValueError(
                f"Unknown operation: {request.operation}. Available: read_file, list_directory, search_files"
            )

        if not result or not result.success:
            raise Exception(result.error if result else "Operation failed")

        return {"success": True, "data": result.data, "metadata": result.metadata}

    except Exception as e:
        logger.error(f"Code analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sessions/{session_id}")
async def get_session(
    session_id: str, context: ContextManager = Depends(get_context_manager)
):
    """Get session information."""
    session = context.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "session": session.model_dump(),
        "summary": context.get_current_context_summary(session_id),
    }


@app.get("/sessions")
async def list_sessions(context: ContextManager = Depends(get_context_manager)):
    """List all sessions."""
    return {
        "sessions": [
            {
                "id": session_id,
                "created_at": session.created_at,
                "updated_at": session.updated_at,
                "message_count": len(session.messages),
                "total_tokens": session.total_tokens(),
            }
            for session_id, session in context.sessions.items()
        ]
    }


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
    context: ContextManager = Depends(get_context_manager),
    router: AIRouter = Depends(get_ai_router),
):
    """WebSocket endpoint for real-time chat."""
    await websocket.accept()

    try:
        # Get or create session
        if not context.get_session(session_id):
            await context.create_session(session_id)

        while True:
            # Receive message
            data = await websocket.receive_text()
            message_data = json.loads(data)

            if message_data.get("type") == "chat":
                # Process chat message
                user_message = ConversationMessage(
                    role="user", content=message_data["content"]
                )
                await context.add_message(user_message, session_id)

                # Get AI response
                history = context.get_conversation_history(session_id)
                ai_request = AIRequest(
                    messages=[
                        {"role": msg.role, "content": msg.content} for msg in history
                    ],
                    task_type=TaskType(message_data.get("task_type", "chat")),
                    stream=False,
                )

                ai_response = await router.chat(ai_request)

                # Add AI response to context
                ai_message = ConversationMessage(
                    role="assistant",
                    content=ai_response.content,
                    ai_provider=ai_response.provider.value,
                    tokens=ai_response.tokens_used,
                )
                await context.add_message(ai_message, session_id)

                # Send response
                await websocket.send_text(
                    json.dumps(
                        {
                            "type": "response",
                            "content": ai_response.content,
                            "provider": ai_response.provider.value,
                            "tokens_used": ai_response.tokens_used,
                        }
                    )
                )

            elif message_data.get("type") == "context_request":
                # Send context summary
                summary = context.get_current_context_summary(session_id)
                await websocket.send_text(
                    json.dumps({"type": "context_summary", "data": summary})
                )

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close()


# Orchestration Endpoints


@app.post("/orchestrate", response_model=OrchestrationResponse)
async def orchestrate_task(
    request: OrchestrationRequest,
    orchestrator: TaskOrchestrator = Depends(get_task_orchestrator),
    context: ContextManager = Depends(get_context_manager),
    api_key: Optional[str] = Depends(verify_api_key),
):
    """Orchestrate a complex task using multiple agents."""
    try:
        # Map string task type to enum
        task_type_mapping = {
            "code_analysis": OrchTaskType.CODE_ANALYSIS,
            "file_operations": OrchTaskType.FILE_OPERATIONS,
            "research": OrchTaskType.RESEARCH,
            "data_processing": OrchTaskType.DATA_PROCESSING,
            "communication": OrchTaskType.COMMUNICATION,
            "general": OrchTaskType.GENERAL,
        }

        task_type = task_type_mapping.get(
            request.task_type.lower(), OrchTaskType.GENERAL
        )

        # Execute orchestration
        result = await orchestrator.orchestrate(
            description=request.description,
            task_type=task_type,
            parameters=request.parameters,
        )

        # Add orchestration result to context if session provided
        if request.session_id:
            await context.add_context(
                content=f"Orchestrated task: {request.description}\nResult: {'SUCCESS' if result.success else 'FAILED'}",
                context_type=ContextType.TOOL_RESULT,
                priority=Priority.HIGH,
                metadata={
                    "orchestration_id": str(time.time()),
                    "task_type": request.task_type,
                    "agents_used": result.agents_used,
                    "duration": result.total_duration,
                },
                session_id=request.session_id,
            )

        return OrchestrationResponse(
            success=result.success,
            task_results=result.task_results,
            execution_plan=result.execution_plan,
            total_duration=result.total_duration,
            agents_used=result.agents_used,
            metadata=result.metadata,
            error=result.error,
        )

    except Exception as e:
        logger.error(f"Orchestration error: {e}")
        return OrchestrationResponse(
            success=False, error=str(e), metadata={"task_type": request.task_type}
        )


@app.get("/orchestration/status", response_model=AgentStatusResponse)
async def get_orchestration_status(
    orchestrator: TaskOrchestrator = Depends(get_task_orchestrator),
):
    """Get current orchestration system status."""
    try:
        status = orchestrator.get_orchestration_status()
        return AgentStatusResponse(
            active_tasks=status["active_tasks"],
            total_agents=status["total_agents"],
            available_agents=status["available_agents"],
            task_history_count=status["task_history_count"],
            agents=status["agents"],
        )
    except Exception as e:
        logger.error(f"Status retrieval error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/orchestration/history")
async def get_task_history(
    limit: int = 50,
    orchestrator: TaskOrchestrator = Depends(get_task_orchestrator),
):
    """Get recent task execution history."""
    try:
        history = orchestrator.get_task_history(limit=limit)
        return {"task_history": history}
    except Exception as e:
        logger.error(f"History retrieval error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/orchestration/agents")
async def list_agents(
    orchestrator: TaskOrchestrator = Depends(get_task_orchestrator),
):
    """List all available agents and their capabilities."""
    try:
        agents = orchestrator.agent_registry.list_agents()
        return {
            "agents": [agent.to_dict() for agent in agents],
            "total_count": len(agents),
            "available_count": len([a for a in agents if a.is_available]),
        }
    except Exception as e:
        logger.error(f"Agent listing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Examples and Documentation Endpoints


@app.get("/orchestration/examples")
async def get_orchestration_examples():
    """Get examples of orchestration requests."""
    return {
        "examples": [
            {
                "name": "Analyze Python Project",
                "description": "Analyze all Python files in a directory",
                "request": {
                    "description": "Analyze all Python files in the project for code quality and structure",
                    "task_type": "code_analysis",
                    "parameters": {
                        "files": ["src/main.py", "src/utils.py", "src/models.py"],
                        "include_metrics": True,
                    },
                },
            },
            {
                "name": "File Organization",
                "description": "Organize files in a directory structure",
                "request": {
                    "description": "Create directory structure and organize files",
                    "task_type": "file_operations",
                    "parameters": {
                        "operation": "batch_process",
                        "files": ["file1.txt", "file2.txt"],
                        "target_directory": "/organized/",
                    },
                },
            },
            {
                "name": "Research Task",
                "description": "Research a technical topic",
                "request": {
                    "description": "Research latest trends in AI orchestration systems",
                    "task_type": "research",
                    "parameters": {
                        "topic": "AI orchestration",
                        "depth": "comprehensive",
                    },
                },
            },
            {
                "name": "Data Processing",
                "description": "Process multiple data sources",
                "request": {
                    "description": "Process and analyze multiple datasets",
                    "task_type": "data_processing",
                    "parameters": {
                        "data_sources": ["dataset1.csv", "dataset2.json"],
                        "operation": "analyze",
                    },
                },
            },
        ]
    }


def main():
    """Main entry point for the server."""
    uvicorn.run(
        "plato.server.api:app",
        host="0.0.0.0",
        port=8080,
        reload=False,
        log_level="info",
    )


if __name__ == "__main__":
    main()
