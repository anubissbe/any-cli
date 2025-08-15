/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */
import { BaseTool } from "./base-tool.js";
import type { ToolExecutionContext, ToolExecutionResult } from "./types.js";
import { SafetyLevel, ToolCategory } from "./types.js";
/**
 * Code analysis tool
 */
export declare class AnalyzeCodeTool extends BaseTool {
    readonly name = "analyze_code";
    readonly description = "Analyze code files for metrics and structure";
    readonly category = ToolCategory.ANALYSIS;
    readonly safetyLevel = SafetyLevel.SAFE;
    readonly parameters: {
        path: {
            type: string;
            description: string;
        };
        language: {
            type: string;
            description: string;
            optional: boolean;
        };
        includeMetrics: {
            type: string;
            description: string;
            default: boolean;
        };
        includeDependencies: {
            type: string;
            description: string;
            default: boolean;
        };
    };
    execute(params: Record<string, any>, context: ToolExecutionContext): Promise<ToolExecutionResult>;
    private analyzeFile;
    private analyzeDirectory;
    private calculateMetrics;
    private extractDependencies;
    private detectLanguage;
    private isCodeFile;
    private getCommentPatterns;
    private isCommentLine;
    private getDependencyPatterns;
}
/**
 * Count lines tool
 */
export declare class CountLinesTool extends BaseTool {
    readonly name = "count_lines";
    readonly description = "Count lines of code in files or directories";
    readonly category = ToolCategory.ANALYSIS;
    readonly safetyLevel = SafetyLevel.SAFE;
    readonly parameters: {
        path: {
            type: string;
            description: string;
        };
        includeComments: {
            type: string;
            description: string;
            default: boolean;
        };
        includeEmpty: {
            type: string;
            description: string;
            default: boolean;
        };
    };
    execute(params: Record<string, any>, context: ToolExecutionContext): Promise<ToolExecutionResult>;
    private countFileLines;
    private countDirectoryLines;
    private detectLanguage;
    private isCodeFile;
    private getCommentPatterns;
    private isCommentLine;
}
/**
 * Find files tool
 */
export declare class FindFilesTool extends BaseTool {
    readonly name = "find_files";
    readonly description = "Find files matching patterns";
    readonly category = ToolCategory.ANALYSIS;
    readonly safetyLevel = SafetyLevel.SAFE;
    readonly parameters: {
        pattern: {
            type: string;
            description: string;
        };
        path: {
            type: string;
            description: string;
            default: string;
        };
        includeHidden: {
            type: string;
            description: string;
            default: boolean;
        };
        maxDepth: {
            type: string;
            description: string;
            optional: boolean;
        };
    };
    execute(params: Record<string, any>, context: ToolExecutionContext): Promise<ToolExecutionResult>;
}
//# sourceMappingURL=analysis-tools.d.ts.map