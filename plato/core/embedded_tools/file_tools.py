"""File operation tools - Claude Code-like functionality."""

import os
import re
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .base import EmbeddedTool, ParameterType, ToolError, ToolParameter, ToolResult


class ReadFileTool(EmbeddedTool):
    """Read the contents of a file with optional line number ranges."""

    def _define_parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="file_path",
                type=ParameterType.FILE_PATH,
                description="Path to the file to read (absolute or relative)",
                required=True,
            ),
            ToolParameter(
                name="start_line",
                type=ParameterType.INTEGER,
                description="Starting line number (1-indexed)",
                required=False,
                min_value=1,
            ),
            ToolParameter(
                name="end_line",
                type=ParameterType.INTEGER,
                description="Ending line number (inclusive)",
                required=False,
                min_value=1,
            ),
            ToolParameter(
                name="encoding",
                type=ParameterType.STRING,
                description="File encoding",
                required=False,
                default="utf-8",
            ),
        ]

    async def execute(self, **kwargs) -> ToolResult:
        """Read file contents."""
        try:
            params = self.validate_parameters(**kwargs)
            file_path = Path(params["file_path"]).resolve()

            # Security check - don't allow reading outside project
            if not self._is_safe_path(file_path):
                raise ToolError(f"Access denied: {file_path}")

            if not file_path.exists():
                raise ToolError(f"File not found: {file_path}")

            if not file_path.is_file():
                raise ToolError(f"Not a file: {file_path}")

            # Read file with encoding
            encoding = params.get("encoding", "utf-8")
            try:
                with open(file_path, "r", encoding=encoding) as f:
                    lines = f.readlines()
            except UnicodeDecodeError:
                # Try with different encodings
                for alt_encoding in ["latin-1", "cp1252", "utf-16"]:
                    try:
                        with open(file_path, "r", encoding=alt_encoding) as f:
                            lines = f.readlines()
                        encoding = alt_encoding
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    # Read as binary if all encodings fail
                    with open(file_path, "rb") as f:
                        content = f.read()
                    return ToolResult(
                        success=True,
                        data=f"Binary file ({len(content)} bytes)",
                        metadata={
                            "file_path": str(file_path),
                            "is_binary": True,
                            "size": len(content),
                        },
                    )

            # Apply line range if specified
            start_line = params.get("start_line")
            end_line = params.get("end_line")

            if start_line or end_line:
                start_idx = (start_line - 1) if start_line else 0
                end_idx = end_line if end_line else len(lines)
                lines = lines[start_idx:end_idx]

                # Add line numbers
                numbered_lines = []
                for i, line in enumerate(lines, start=start_idx + 1):
                    numbered_lines.append(f"{i:6d}→{line.rstrip()}")
                content = "\n".join(numbered_lines)
            else:
                # Add line numbers to all lines
                numbered_lines = []
                for i, line in enumerate(lines, start=1):
                    numbered_lines.append(f"{i:6d}→{line.rstrip()}")
                content = "\n".join(numbered_lines)

            return ToolResult(
                success=True,
                data=content,
                metadata={
                    "file_path": str(file_path),
                    "encoding": encoding,
                    "total_lines": len(lines),
                    "size": file_path.stat().st_size,
                },
            )

        except ToolError:
            raise
        except Exception as e:
            raise ToolError(f"Failed to read file: {e}")

    def _is_safe_path(self, path: Path) -> bool:
        """Check if path is safe to access."""
        # Allow access to project directories and home
        safe_prefixes = [
            Path.cwd(),
            Path.home(),
            Path("/opt/projects"),
            Path("/tmp"),
        ]

        try:
            resolved = path.resolve()
            return any(
                str(resolved).startswith(str(prefix)) for prefix in safe_prefixes
            )
        except Exception:
            return False


class WriteFileTool(EmbeddedTool):
    """Write content to a file, creating it if it doesn't exist."""

    def _define_parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="file_path",
                type=ParameterType.FILE_PATH,
                description="Path to the file to write",
                required=True,
            ),
            ToolParameter(
                name="content",
                type=ParameterType.STRING,
                description="Content to write to the file",
                required=True,
            ),
            ToolParameter(
                name="create_dirs",
                type=ParameterType.BOOLEAN,
                description="Create parent directories if they don't exist",
                required=False,
                default=True,
            ),
            ToolParameter(
                name="encoding",
                type=ParameterType.STRING,
                description="File encoding",
                required=False,
                default="utf-8",
            ),
        ]

    async def execute(self, **kwargs) -> ToolResult:
        """Write content to file."""
        try:
            params = self.validate_parameters(**kwargs)
            file_path = Path(params["file_path"]).resolve()

            # Security check
            if not self._is_safe_path(file_path):
                raise ToolError(f"Access denied: {file_path}")

            # Create parent directories if needed
            if params.get("create_dirs", True):
                file_path.parent.mkdir(parents=True, exist_ok=True)

            # Write content
            encoding = params.get("encoding", "utf-8")
            content = params["content"]

            # Remove line numbers if present (from read operations)
            if content and re.match(r"^\s*\d+→", content.split("\n")[0]):
                lines = []
                for line in content.split("\n"):
                    match = re.match(r"^\s*\d+→(.*)$", line)
                    if match:
                        lines.append(match.group(1))
                    else:
                        lines.append(line)
                content = "\n".join(lines)

            with open(file_path, "w", encoding=encoding) as f:
                f.write(content)

            return ToolResult(
                success=True,
                data=f"Successfully wrote {len(content)} characters to {file_path}",
                metadata={
                    "file_path": str(file_path),
                    "size": len(content),
                    "encoding": encoding,
                },
            )

        except ToolError:
            raise
        except Exception as e:
            raise ToolError(f"Failed to write file: {e}")

    def _is_safe_path(self, path: Path) -> bool:
        """Check if path is safe to access."""
        safe_prefixes = [
            Path.cwd(),
            Path.home(),
            Path("/opt/projects"),
            Path("/tmp"),
        ]

        try:
            resolved = path.resolve()
            return any(
                str(resolved).startswith(str(prefix)) for prefix in safe_prefixes
            )
        except Exception:
            return False


class EditFileTool(EmbeddedTool):
    """Edit specific lines or sections of a file."""

    def _define_parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="file_path",
                type=ParameterType.FILE_PATH,
                description="Path to the file to edit",
                required=True,
            ),
            ToolParameter(
                name="old_string",
                type=ParameterType.STRING,
                description="Content to replace (must match exactly)",
                required=True,
            ),
            ToolParameter(
                name="new_string",
                type=ParameterType.STRING,
                description="New content to insert",
                required=True,
            ),
            ToolParameter(
                name="occurrence",
                type=ParameterType.INTEGER,
                description="Which occurrence to replace (0 for all)",
                required=False,
                default=1,
                min_value=0,
            ),
        ]

    async def execute(self, **kwargs) -> ToolResult:
        """Edit file content."""
        try:
            params = self.validate_parameters(**kwargs)
            file_path = Path(params["file_path"]).resolve()

            # Security check
            if not self._is_safe_path(file_path):
                raise ToolError(f"Access denied: {file_path}")

            if not file_path.exists():
                raise ToolError(f"File not found: {file_path}")

            # Read current content
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            old_string = params["old_string"]
            new_string = params["new_string"]
            occurrence = params.get("occurrence", 1)

            # Strip line numbers if present
            if old_string and re.match(r"^\s*\d+→", old_string.split("\n")[0]):
                lines = []
                for line in old_string.split("\n"):
                    match = re.match(r"^\s*\d+→(.*)$", line)
                    if match:
                        lines.append(match.group(1))
                    else:
                        lines.append(line)
                old_string = "\n".join(lines)

            # Perform replacement
            if occurrence == 0:
                # Replace all occurrences
                if old_string not in content:
                    raise ToolError(f"Content to replace not found in {file_path}")
                new_file_content = content.replace(old_string, new_string)
                replacements = content.count(old_string)
            else:
                # Replace specific occurrence
                parts = content.split(old_string)
                if len(parts) <= occurrence:
                    raise ToolError(
                        f"Occurrence {occurrence} not found (only {len(parts)-1} found)"
                    )

                # Reconstruct with replacement
                result_parts = []
                for i in range(len(parts)):
                    result_parts.append(parts[i])
                    if i < len(parts) - 1:
                        if i == occurrence - 1:
                            result_parts.append(new_string)
                        else:
                            result_parts.append(old_string)

                new_file_content = "".join(result_parts)
                replacements = 1

            # Write back
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_file_content)

            return ToolResult(
                success=True,
                data=f"Successfully edited {file_path} ({replacements} replacement(s))",
                metadata={
                    "file_path": str(file_path),
                    "replacements": replacements,
                    "old_size": len(content),
                    "new_size": len(new_file_content),
                },
            )

        except ToolError:
            raise
        except Exception as e:
            raise ToolError(f"Failed to edit file: {e}")

    def _is_safe_path(self, path: Path) -> bool:
        """Check if path is safe to access."""
        safe_prefixes = [
            Path.cwd(),
            Path.home(),
            Path("/opt/projects"),
            Path("/tmp"),
        ]

        try:
            resolved = path.resolve()
            return any(
                str(resolved).startswith(str(prefix)) for prefix in safe_prefixes
            )
        except Exception:
            return False


class ListDirectoryTool(EmbeddedTool):
    """List contents of a directory with detailed information."""

    def _define_parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="directory_path",
                type=ParameterType.DIRECTORY_PATH,
                description="Path to the directory to list",
                required=False,
                default=".",
            ),
            ToolParameter(
                name="recursive",
                type=ParameterType.BOOLEAN,
                description="List recursively",
                required=False,
                default=False,
            ),
            ToolParameter(
                name="max_depth",
                type=ParameterType.INTEGER,
                description="Maximum depth for recursive listing",
                required=False,
                default=3,
                min_value=1,
                max_value=10,
            ),
            ToolParameter(
                name="show_hidden",
                type=ParameterType.BOOLEAN,
                description="Show hidden files/directories",
                required=False,
                default=False,
            ),
            ToolParameter(
                name="pattern",
                type=ParameterType.STRING,
                description="Filter pattern (glob style)",
                required=False,
            ),
        ]

    async def execute(self, **kwargs) -> ToolResult:
        """List directory contents."""
        try:
            params = self.validate_parameters(**kwargs)
            dir_path = Path(params.get("directory_path", ".")).resolve()

            # Security check
            if not self._is_safe_path(dir_path):
                raise ToolError(f"Access denied: {dir_path}")

            if not dir_path.exists():
                raise ToolError(f"Directory not found: {dir_path}")

            if not dir_path.is_dir():
                raise ToolError(f"Not a directory: {dir_path}")

            recursive = params.get("recursive", False)
            max_depth = params.get("max_depth", 3)
            show_hidden = params.get("show_hidden", False)
            pattern = params.get("pattern")

            # Collect entries
            entries = []

            if recursive:
                self._list_recursive(
                    dir_path, entries, 0, max_depth, show_hidden, pattern
                )
            else:
                self._list_flat(dir_path, entries, show_hidden, pattern)

            # Format output
            if recursive:
                output = self._format_tree(entries, dir_path)
            else:
                output = self._format_list(entries)

            return ToolResult(
                success=True,
                data=output,
                metadata={
                    "directory": str(dir_path),
                    "total_items": len(entries),
                    "recursive": recursive,
                },
            )

        except ToolError:
            raise
        except Exception as e:
            raise ToolError(f"Failed to list directory: {e}")

    def _list_flat(
        self,
        dir_path: Path,
        entries: List[Dict],
        show_hidden: bool,
        pattern: Optional[str],
    ):
        """List directory non-recursively."""
        import fnmatch

        for item in sorted(dir_path.iterdir()):
            # Skip hidden files if not requested
            if not show_hidden and item.name.startswith("."):
                continue

            # Apply pattern filter
            if pattern and not fnmatch.fnmatch(item.name, pattern):
                continue

            entry = {
                "path": item,
                "name": item.name,
                "type": "dir" if item.is_dir() else "file",
                "size": item.stat().st_size if item.is_file() else None,
                "depth": 0,
            }
            entries.append(entry)

    def _list_recursive(
        self,
        dir_path: Path,
        entries: List[Dict],
        current_depth: int,
        max_depth: int,
        show_hidden: bool,
        pattern: Optional[str],
    ):
        """List directory recursively."""
        import fnmatch

        if current_depth >= max_depth:
            return

        try:
            for item in sorted(dir_path.iterdir()):
                # Skip hidden files if not requested
                if not show_hidden and item.name.startswith("."):
                    continue

                # Skip common ignore patterns
                if item.name in {
                    "__pycache__",
                    "node_modules",
                    ".git",
                    "venv",
                    ".venv",
                    "dist",
                    "build",
                    "target",
                }:
                    continue

                # Apply pattern filter
                if pattern and not fnmatch.fnmatch(item.name, pattern):
                    if not item.is_dir():
                        continue

                entry = {
                    "path": item,
                    "name": item.name,
                    "type": "dir" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else None,
                    "depth": current_depth,
                }
                entries.append(entry)

                # Recurse into directories
                if item.is_dir():
                    self._list_recursive(
                        item,
                        entries,
                        current_depth + 1,
                        max_depth,
                        show_hidden,
                        pattern,
                    )
        except PermissionError:
            pass

    def _format_list(self, entries: List[Dict]) -> str:
        """Format as a simple list."""
        lines = []
        for entry in entries:
            if entry["type"] == "dir":
                lines.append(f"[DIR]  {entry['name']}/")
            else:
                size_str = self._format_size(entry.get("size", 0))
                lines.append(f"[FILE] {entry['name']} ({size_str})")

        return "\n".join(lines) if lines else "Empty directory"

    def _format_tree(self, entries: List[Dict], root: Path) -> str:
        """Format as a tree structure."""
        lines = [f"{root.name}/"]

        for entry in entries:
            indent = "  " * (entry["depth"] + 1)
            prefix = "├── " if entry["depth"] == 0 else "│   " * entry["depth"] + "├── "

            if entry["type"] == "dir":
                lines.append(f"{prefix}{entry['name']}/")
            else:
                size_str = self._format_size(entry.get("size", 0))
                lines.append(f"{prefix}{entry['name']} ({size_str})")

        return "\n".join(lines)

    def _format_size(self, size: int) -> str:
        """Format file size in human-readable form."""
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                return f"{size:.1f}{unit}"
            size /= 1024
        return f"{size:.1f}TB"

    def _is_safe_path(self, path: Path) -> bool:
        """Check if path is safe to access."""
        safe_prefixes = [
            Path.cwd(),
            Path.home(),
            Path("/opt/projects"),
            Path("/tmp"),
        ]

        try:
            resolved = path.resolve()
            return any(
                str(resolved).startswith(str(prefix)) for prefix in safe_prefixes
            )
        except Exception:
            return False


class SearchFilesTool(EmbeddedTool):
    """Search for patterns in files."""

    def _define_parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="pattern",
                type=ParameterType.STRING,
                description="Search pattern (regex or plain text)",
                required=True,
            ),
            ToolParameter(
                name="directory",
                type=ParameterType.DIRECTORY_PATH,
                description="Directory to search in",
                required=False,
                default=".",
            ),
            ToolParameter(
                name="file_pattern",
                type=ParameterType.STRING,
                description="File pattern to match (glob style)",
                required=False,
                default="*",
            ),
            ToolParameter(
                name="case_sensitive",
                type=ParameterType.BOOLEAN,
                description="Case-sensitive search",
                required=False,
                default=False,
            ),
            ToolParameter(
                name="regex",
                type=ParameterType.BOOLEAN,
                description="Use regex pattern",
                required=False,
                default=False,
            ),
            ToolParameter(
                name="max_results",
                type=ParameterType.INTEGER,
                description="Maximum number of results",
                required=False,
                default=100,
                min_value=1,
                max_value=1000,
            ),
        ]

    async def execute(self, **kwargs) -> ToolResult:
        """Search for patterns in files."""
        try:
            params = self.validate_parameters(**kwargs)
            pattern = params["pattern"]
            directory = Path(params.get("directory", ".")).resolve()
            file_pattern = params.get("file_pattern", "*")
            case_sensitive = params.get("case_sensitive", False)
            use_regex = params.get("regex", False)
            max_results = params.get("max_results", 100)

            # Security check
            if not self._is_safe_path(directory):
                raise ToolError(f"Access denied: {directory}")

            if not directory.exists():
                raise ToolError(f"Directory not found: {directory}")

            # Compile pattern
            if use_regex:
                flags = 0 if case_sensitive else re.IGNORECASE
                regex = re.compile(pattern, flags)
            else:
                if not case_sensitive:
                    pattern = pattern.lower()

            # Search files
            results = []
            files_searched = 0

            for file_path in directory.rglob(file_pattern):
                if not file_path.is_file():
                    continue

                if file_path.name.startswith("."):
                    continue

                # Skip binary files
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        lines = content.splitlines()
                except (UnicodeDecodeError, PermissionError):
                    continue

                files_searched += 1

                # Search in file
                for line_num, line in enumerate(lines, start=1):
                    if use_regex:
                        if regex.search(line):
                            results.append(
                                {
                                    "file": str(file_path.relative_to(directory)),
                                    "line": line_num,
                                    "content": line.strip(),
                                }
                            )
                    else:
                        search_line = line if case_sensitive else line.lower()
                        if pattern in search_line:
                            results.append(
                                {
                                    "file": str(file_path.relative_to(directory)),
                                    "line": line_num,
                                    "content": line.strip(),
                                }
                            )

                    if len(results) >= max_results:
                        break

                if len(results) >= max_results:
                    break

            # Format results
            if results:
                output_lines = [
                    f"Found {len(results)} matches in {files_searched} files:"
                ]
                for result in results:
                    output_lines.append(
                        f"{result['file']}:{result['line']}: {result['content']}"
                    )
                output = "\n".join(output_lines)
            else:
                output = f"No matches found (searched {files_searched} files)"

            return ToolResult(
                success=True,
                data=output,
                metadata={
                    "pattern": pattern,
                    "directory": str(directory),
                    "matches": len(results),
                    "files_searched": files_searched,
                },
            )

        except ToolError:
            raise
        except Exception as e:
            raise ToolError(f"Search failed: {e}")

    def _is_safe_path(self, path: Path) -> bool:
        """Check if path is safe to access."""
        safe_prefixes = [
            Path.cwd(),
            Path.home(),
            Path("/opt/projects"),
            Path("/tmp"),
        ]

        try:
            resolved = path.resolve()
            return any(
                str(resolved).startswith(str(prefix)) for prefix in safe_prefixes
            )
        except Exception:
            return False


class CreateDirectoryTool(EmbeddedTool):
    """Create a new directory."""

    def _define_parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="directory_path",
                type=ParameterType.DIRECTORY_PATH,
                description="Path to the directory to create",
                required=True,
            ),
            ToolParameter(
                name="parents",
                type=ParameterType.BOOLEAN,
                description="Create parent directories if they don't exist",
                required=False,
                default=True,
            ),
            ToolParameter(
                name="exist_ok",
                type=ParameterType.BOOLEAN,
                description="Don't raise error if directory already exists",
                required=False,
                default=True,
            ),
        ]

    async def execute(self, **kwargs) -> ToolResult:
        """Create directory."""
        try:
            params = self.validate_parameters(**kwargs)
            dir_path = Path(params["directory_path"]).resolve()

            # Security check
            if not self._is_safe_path(dir_path):
                raise ToolError(f"Access denied: {dir_path}")

            parents = params.get("parents", True)
            exist_ok = params.get("exist_ok", True)

            # Create directory
            dir_path.mkdir(parents=parents, exist_ok=exist_ok)

            return ToolResult(
                success=True,
                data=f"Successfully created directory: {dir_path}",
                metadata={
                    "directory_path": str(dir_path),
                    "created": True,
                },
            )

        except FileExistsError:
            raise ToolError(f"Directory already exists: {params['directory_path']}")
        except ToolError:
            raise
        except Exception as e:
            raise ToolError(f"Failed to create directory: {e}")

    def _is_safe_path(self, path: Path) -> bool:
        """Check if path is safe to access."""
        safe_prefixes = [
            Path.cwd(),
            Path.home(),
            Path("/opt/projects"),
            Path("/tmp"),
        ]

        try:
            resolved = path.resolve()
            return any(
                str(resolved).startswith(str(prefix)) for prefix in safe_prefixes
            )
        except Exception:
            return False
