/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */
import { BaseTool } from "./base-tool.js";
import type { ToolExecutionContext, ToolExecutionResult } from "./types.js";
import { SafetyLevel, ToolCategory } from "./types.js";
/**
 * Read file tool
 */
export declare class ReadFileTool extends BaseTool {
    readonly name = "read_file";
    readonly description = "Read contents of a file";
    readonly category = ToolCategory.FILE;
    readonly safetyLevel = SafetyLevel.SAFE;
    readonly parameters: {
        path: {
            type: string;
            description: string;
        };
        encoding: {
            type: string;
            description: string;
            default: string;
        };
    };
    execute(params: Record<string, any>, context: ToolExecutionContext): Promise<ToolExecutionResult>;
}
/**
 * Write file tool
 */
export declare class WriteFileTool extends BaseTool {
    readonly name = "write_file";
    readonly description = "Write content to a file";
    readonly category = ToolCategory.FILE;
    readonly safetyLevel = SafetyLevel.DESTRUCTIVE;
    readonly parameters: {
        path: {
            type: string;
            description: string;
        };
        content: {
            type: string;
            description: string;
        };
        encoding: {
            type: string;
            description: string;
            default: string;
        };
        mode: {
            type: string;
            description: string;
            optional: boolean;
        };
    };
    execute(params: Record<string, any>, context: ToolExecutionContext): Promise<ToolExecutionResult>;
}
/**
 * List directory tool
 */
export declare class ListDirectoryTool extends BaseTool {
    readonly name = "list_directory";
    readonly description = "List contents of a directory";
    readonly category = ToolCategory.FILE;
    readonly safetyLevel = SafetyLevel.SAFE;
    readonly parameters: {
        path: {
            type: string;
            description: string;
        };
        includeHidden: {
            type: string;
            description: string;
            default: boolean;
        };
        recursive: {
            type: string;
            description: string;
            default: boolean;
        };
    };
    execute(params: Record<string, any>, context: ToolExecutionContext): Promise<ToolExecutionResult>;
    private listDirectory;
}
/**
 * Create directory tool
 */
export declare class CreateDirectoryTool extends BaseTool {
    readonly name = "create_directory";
    readonly description = "Create a directory (and parent directories if needed)";
    readonly category = ToolCategory.FILE;
    readonly safetyLevel = SafetyLevel.MODERATE;
    readonly parameters: {
        path: {
            type: string;
            description: string;
        };
        mode: {
            type: string;
            description: string;
            optional: boolean;
        };
    };
    execute(params: Record<string, any>, context: ToolExecutionContext): Promise<ToolExecutionResult>;
}
//# sourceMappingURL=file-tools.d.ts.map