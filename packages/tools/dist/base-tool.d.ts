/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */
import { z } from "zod";
import type { ToolDefinition, ToolExecutionContext, ToolExecutionResult, SafetyLevel, ToolCategory } from "./types.js";
/**
 * Base class for all tools
 */
export declare abstract class BaseTool implements ToolDefinition {
    abstract readonly name: string;
    abstract readonly description: string;
    abstract readonly category: ToolCategory;
    abstract readonly safetyLevel: SafetyLevel;
    abstract readonly parameters: Record<string, any>;
    /**
     * Validate parameters against schema
     */
    protected validateParameters(params: Record<string, any>, schema: z.ZodSchema): any;
    /**
     * Check if operation should be confirmed
     */
    protected confirmOperation(context: ToolExecutionContext, message: string): Promise<boolean>;
    /**
     * Create a successful result
     */
    protected createSuccessResult(output?: string, metadata?: Record<string, any>): ToolExecutionResult;
    /**
     * Create an error result
     */
    protected createErrorResult(error: string, exitCode?: number, metadata?: Record<string, any>): ToolExecutionResult;
    /**
     * Create a dry run result
     */
    protected createDryRunResult(operation: string, metadata?: Record<string, any>): ToolExecutionResult;
    /**
     * Check safety constraints
     */
    protected checkSafety(context: ToolExecutionContext): void;
    /**
     * Execute the tool with the given parameters and context
     */
    abstract execute(params: Record<string, any>, context: ToolExecutionContext): Promise<ToolExecutionResult>;
}
//# sourceMappingURL=base-tool.d.ts.map