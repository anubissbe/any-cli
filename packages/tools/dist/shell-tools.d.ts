/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */
import { BaseTool } from "./base-tool.js";
import type { ToolExecutionContext, ToolExecutionResult } from "./types.js";
import { SafetyLevel, ToolCategory } from "./types.js";
/**
 * Execute shell command tool
 */
export declare class ExecuteCommandTool extends BaseTool {
    readonly name = "execute_command";
    readonly description = "Execute a shell command";
    readonly category = ToolCategory.SHELL;
    readonly safetyLevel = SafetyLevel.DESTRUCTIVE;
    readonly parameters: {
        command: {
            type: string;
            description: string;
        };
        args: {
            type: string;
            description: string;
            default: never[];
        };
        cwd: {
            type: string;
            description: string;
            optional: boolean;
        };
        env: {
            type: string;
            description: string;
            optional: boolean;
        };
        timeout: {
            type: string;
            description: string;
            default: number;
        };
        shell: {
            type: string;
            description: string;
            default: boolean;
        };
    };
    execute(params: Record<string, any>, context: ToolExecutionContext): Promise<ToolExecutionResult>;
}
/**
 * Which command tool - find executable in PATH
 */
export declare class WhichCommandTool extends BaseTool {
    readonly name = "which_command";
    readonly description = "Find the path of an executable command";
    readonly category = ToolCategory.SHELL;
    readonly safetyLevel = SafetyLevel.SAFE;
    readonly parameters: {
        command: {
            type: string;
            description: string;
        };
    };
    execute(params: Record<string, any>, context: ToolExecutionContext): Promise<ToolExecutionResult>;
}
//# sourceMappingURL=shell-tools.d.ts.map