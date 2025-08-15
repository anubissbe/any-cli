/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */

import { z } from "zod";
import { CLIError } from "@qwen-claude/core";
import type {
  ToolDefinition,
  ToolExecutionContext,
  ToolExecutionResult,
  SafetyLevel,
  ToolCategory,
} from "./types.js";

/**
 * Base class for all tools
 */
export abstract class BaseTool implements ToolDefinition {
  abstract readonly name: string;
  abstract readonly description: string;
  abstract readonly category: ToolCategory;
  abstract readonly safetyLevel: SafetyLevel;
  abstract readonly parameters: Record<string, any>;

  /**
   * Validate parameters against schema
   */
  protected validateParameters(
    params: Record<string, any>,
    schema: z.ZodSchema,
  ): any {
    try {
      return schema.parse(params);
    } catch (error) {
      if (error instanceof z.ZodError) {
        const issues = error.issues
          .map((issue) => `${issue.path.join(".")}: ${issue.message}`)
          .join(", ");
        throw new CLIError(`Invalid parameters: ${issues}`);
      }
      throw error;
    }
  }

  /**
   * Check if operation should be confirmed
   */
  protected async confirmOperation(
    context: ToolExecutionContext,
    message: string,
  ): Promise<boolean> {
    if (!context.confirmDestructive || context.dryRun) {
      return true;
    }

    // In a real implementation, this would prompt the user
    // For now, we'll assume confirmation if confirmDestructive is required
    return context.confirmDestructive;
  }

  /**
   * Create a successful result
   */
  protected createSuccessResult(
    output?: string,
    metadata?: Record<string, any>,
  ): ToolExecutionResult {
    return {
      success: true,
      output,
      metadata,
    };
  }

  /**
   * Create an error result
   */
  protected createErrorResult(
    error: string,
    exitCode?: number,
    metadata?: Record<string, any>,
  ): ToolExecutionResult {
    return {
      success: false,
      error,
      exitCode,
      metadata,
    };
  }

  /**
   * Create a dry run result
   */
  protected createDryRunResult(
    operation: string,
    metadata?: Record<string, any>,
  ): ToolExecutionResult {
    return {
      success: true,
      output: `[DRY RUN] Would ${operation}`,
      metadata: {
        ...metadata,
        dryRun: true,
      },
    };
  }

  /**
   * Check safety constraints
   */
  protected checkSafety(context: ToolExecutionContext): void {
    if (context.safeMode && this.safetyLevel === "destructive") {
      throw new CLIError(
        `Tool '${this.name}' requires destructive operations but safe mode is enabled`,
      );
    }
  }

  /**
   * Execute the tool with the given parameters and context
   */
  abstract execute(
    params: Record<string, any>,
    context: ToolExecutionContext,
  ): Promise<ToolExecutionResult>;
}
