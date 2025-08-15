/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */
import { CLIError } from "@qwen-claude/core";
// Import built-in tools
import { ReadFileTool, WriteFileTool, ListDirectoryTool, CreateDirectoryTool, } from "./file-tools.js";
import { ExecuteCommandTool, WhichCommandTool } from "./shell-tools.js";
import { AnalyzeCodeTool, CountLinesTool, FindFilesTool, } from "./analysis-tools.js";
/**
 * Tool registry for managing and executing tools
 */
export class ToolRegistry {
    tools = new Map();
    config;
    constructor(config) {
        this.config = config;
        this.registerBuiltInTools();
    }
    /**
     * Register built-in tools
     */
    registerBuiltInTools() {
        const builtInTools = [
            // File tools
            new ReadFileTool(),
            new WriteFileTool(),
            new ListDirectoryTool(),
            new CreateDirectoryTool(),
            // Shell tools
            new ExecuteCommandTool(),
            new WhichCommandTool(),
            // Analysis tools
            new AnalyzeCodeTool(),
            new CountLinesTool(),
            new FindFilesTool(),
        ];
        for (const tool of builtInTools) {
            this.registerTool(tool);
        }
    }
    /**
     * Register a new tool
     */
    registerTool(tool) {
        if (this.tools.has(tool.name)) {
            throw new CLIError(`Tool '${tool.name}' is already registered`);
        }
        // Check if tool category is allowed
        if (!this.config.allowedCategories.includes(tool.category)) {
            throw new CLIError(`Tool category '${tool.category}' is not allowed. ` +
                `Allowed categories: ${this.config.allowedCategories.join(", ")}`);
        }
        this.tools.set(tool.name, tool);
    }
    /**
     * Unregister a tool
     */
    unregisterTool(name) {
        return this.tools.delete(name);
    }
    /**
     * Get a tool by name
     */
    getTool(name) {
        return this.tools.get(name);
    }
    /**
     * Get all available tools
     */
    getAvailableTools() {
        return Array.from(this.tools.values());
    }
    /**
     * Get tools by category
     */
    getToolsByCategory(category) {
        return Array.from(this.tools.values()).filter((tool) => tool.category === category);
    }
    /**
     * Execute a tool
     */
    async executeTool(name, params, contextOverrides) {
        const tool = this.tools.get(name);
        if (!tool) {
            throw new CLIError(`Tool '${name}' not found`);
        }
        // Build execution context
        const context = {
            workingDirectory: this.config.workingDirectory || process.cwd(),
            safeMode: this.config.safeMode,
            confirmDestructive: this.config.confirmDestructive,
            timeout: this.config.timeout,
            ...contextOverrides,
        };
        // Check safety constraints
        if (context.safeMode && tool.safetyLevel === "destructive") {
            throw new CLIError(`Tool '${name}' requires destructive operations but safe mode is enabled`);
        }
        // Check category permissions
        if (!this.config.allowedCategories.includes(tool.category)) {
            throw new CLIError(`Tool category '${tool.category}' is not allowed`);
        }
        try {
            const result = await tool.execute(params, context);
            // Add metadata about the execution
            return {
                ...result,
                metadata: {
                    ...result.metadata,
                    toolName: name,
                    toolCategory: tool.category,
                    safetyLevel: tool.safetyLevel,
                    executionTime: Date.now(),
                },
            };
        }
        catch (error) {
            return {
                success: false,
                error: error instanceof Error ? error.message : String(error),
                metadata: {
                    toolName: name,
                    toolCategory: tool.category,
                    safetyLevel: tool.safetyLevel,
                    executionTime: Date.now(),
                },
            };
        }
    }
    /**
     * Update configuration
     */
    updateConfig(config) {
        this.config = { ...this.config, ...config };
    }
    /**
     * Get current configuration
     */
    getConfig() {
        return { ...this.config };
    }
    /**
     * Validate tool name
     */
    validateToolName(name) {
        if (!name || typeof name !== "string") {
            throw new CLIError("Tool name must be a non-empty string");
        }
        if (!/^[a-zA-Z][a-zA-Z0-9_-]*$/.test(name)) {
            throw new CLIError("Tool name must start with a letter and contain only letters, numbers, underscores, and hyphens");
        }
    }
}
//# sourceMappingURL=registry.js.map