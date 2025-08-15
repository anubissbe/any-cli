/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */
import { z } from "zod";
import { CLIError } from "@qwen-claude/core";
/**
 * Base class for all tools
 */
export class BaseTool {
    /**
     * Validate parameters against schema
     */
    validateParameters(params, schema) {
        try {
            return schema.parse(params);
        }
        catch (error) {
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
    async confirmOperation(context, message) {
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
    createSuccessResult(output, metadata) {
        return {
            success: true,
            output,
            metadata,
        };
    }
    /**
     * Create an error result
     */
    createErrorResult(error, exitCode, metadata) {
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
    createDryRunResult(operation, metadata) {
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
    checkSafety(context) {
        if (context.safeMode && this.safetyLevel === "destructive") {
            throw new CLIError(`Tool '${this.name}' requires destructive operations but safe mode is enabled`);
        }
    }
}
//# sourceMappingURL=base-tool.js.map