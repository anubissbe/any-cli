"""Base classes for embedded tools."""

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union


class ParameterType(Enum):
    """Parameter types for tools."""

    STRING = "string"
    INTEGER = "integer"
    NUMBER = "number"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"
    FILE_PATH = "file_path"
    DIRECTORY_PATH = "directory_path"


@dataclass
class ToolParameter:
    """Definition of a tool parameter."""

    name: str
    type: ParameterType
    description: str
    required: bool = True
    default: Any = None
    enum: Optional[List[Any]] = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    pattern: Optional[str] = None

    def to_json_schema(self) -> Dict[str, Any]:
        """Convert to JSON schema format."""
        schema = {
            "type": self.type.value,
            "description": self.description,
        }

        if self.enum:
            schema["enum"] = self.enum
        if self.min_value is not None:
            schema["minimum"] = self.min_value
        if self.max_value is not None:
            schema["maximum"] = self.max_value
        if self.pattern:
            schema["pattern"] = self.pattern
        if self.default is not None:
            schema["default"] = self.default

        return schema


@dataclass
class ToolResult:
    """Result from a tool execution."""

    success: bool
    data: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "success": self.success,
            "data": self.data,
        }

        if self.error:
            result["error"] = self.error
        if self.metadata:
            result["metadata"] = self.metadata

        return result

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2, default=str)


class ToolError(Exception):
    """Exception raised by tools."""

    def __init__(self, message: str, code: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.code = code


class EmbeddedTool(ABC):
    """Base class for embedded tools."""

    def __init__(self):
        self.name = self.__class__.__name__
        self.description = self.__doc__ or "No description available"
        self.parameters = self._define_parameters()

    @abstractmethod
    def _define_parameters(self) -> List[ToolParameter]:
        """Define the parameters for this tool."""
        pass

    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """Execute the tool with the given parameters."""
        pass

    def validate_parameters(self, **kwargs) -> Dict[str, Any]:
        """Validate and normalize parameters."""
        validated = {}
        errors = []

        # Check required parameters
        for param in self.parameters:
            if param.required and param.name not in kwargs:
                if param.default is not None:
                    validated[param.name] = param.default
                else:
                    errors.append(f"Required parameter '{param.name}' is missing")
                continue

            if param.name in kwargs:
                value = kwargs[param.name]

                # Type validation
                if param.type == ParameterType.STRING:
                    if not isinstance(value, str):
                        errors.append(
                            f"Parameter '{param.name}' must be a string, got {type(value).__name__}"
                        )
                    else:
                        validated[param.name] = value

                elif param.type == ParameterType.INTEGER:
                    try:
                        validated[param.name] = int(value)
                    except (ValueError, TypeError):
                        errors.append(f"Parameter '{param.name}' must be an integer")

                elif param.type == ParameterType.NUMBER:
                    try:
                        validated[param.name] = float(value)
                    except (ValueError, TypeError):
                        errors.append(f"Parameter '{param.name}' must be a number")

                elif param.type == ParameterType.BOOLEAN:
                    if isinstance(value, bool):
                        validated[param.name] = value
                    elif isinstance(value, str):
                        validated[param.name] = value.lower() in ("true", "1", "yes")
                    else:
                        errors.append(f"Parameter '{param.name}' must be a boolean")

                elif param.type == ParameterType.ARRAY:
                    if not isinstance(value, (list, tuple)):
                        errors.append(f"Parameter '{param.name}' must be an array")
                    else:
                        validated[param.name] = list(value)

                elif param.type == ParameterType.OBJECT:
                    if not isinstance(value, dict):
                        errors.append(f"Parameter '{param.name}' must be an object")
                    else:
                        validated[param.name] = value

                elif param.type in (
                    ParameterType.FILE_PATH,
                    ParameterType.DIRECTORY_PATH,
                ):
                    if not isinstance(value, str):
                        errors.append(f"Parameter '{param.name}' must be a path string")
                    else:
                        validated[param.name] = value

                else:
                    validated[param.name] = value

                # Additional validations
                if param.name in validated:
                    value = validated[param.name]

                    if param.enum and value not in param.enum:
                        errors.append(
                            f"Parameter '{param.name}' must be one of {param.enum}"
                        )

                    if param.min_value is not None and value < param.min_value:
                        errors.append(
                            f"Parameter '{param.name}' must be at least {param.min_value}"
                        )

                    if param.max_value is not None and value > param.max_value:
                        errors.append(
                            f"Parameter '{param.name}' must be at most {param.max_value}"
                        )

        if errors:
            raise ToolError(f"Parameter validation failed: {'; '.join(errors)}")

        return validated

    def get_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for this tool."""
        properties = {}
        required = []

        for param in self.parameters:
            properties[param.name] = param.to_json_schema()
            if param.required and param.default is None:
                required.append(param.name)

        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        }

    def format_for_ai(self) -> str:
        """Format tool description for AI understanding."""
        lines = [
            f"Tool: {self.name}",
            f"Description: {self.description}",
            "",
            "Parameters:",
        ]

        for param in self.parameters:
            req_str = "required" if param.required else "optional"
            lines.append(
                f"  - {param.name} ({param.type.value}, {req_str}): {param.description}"
            )

            if param.default is not None:
                lines.append(f"    Default: {param.default}")
            if param.enum:
                lines.append(f"    Allowed values: {', '.join(map(str, param.enum))}")
            if param.min_value is not None or param.max_value is not None:
                range_str = (
                    f"    Range: {param.min_value or '-∞'} to {param.max_value or '∞'}"
                )
                lines.append(range_str)

        return "\n".join(lines)
