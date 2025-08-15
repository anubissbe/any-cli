/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */
import type { ToolDefinition, ToolExecutionContext, ToolExecutionResult, ToolConfig, ToolCategory } from "./types.js";
/**
 * Tool registry for managing and executing tools
 */
export declare class ToolRegistry {
    private tools;
    private config;
    constructor(config: ToolConfig);
    /**
     * Register built-in tools
     */
    private registerBuiltInTools;
    /**
     * Register a new tool
     */
    registerTool(tool: ToolDefinition): void;
    /**
     * Unregister a tool
     */
    unregisterTool(name: string): boolean;
    /**
     * Get a tool by name
     */
    getTool(name: string): ToolDefinition | undefined;
    /**
     * Get all available tools
     */
    getAvailableTools(): ToolDefinition[];
    /**
     * Get tools by category
     */
    getToolsByCategory(category: ToolCategory): ToolDefinition[];
    /**
     * Execute a tool
     */
    executeTool(name: string, params: Record<string, any>, contextOverrides?: Partial<ToolExecutionContext>): Promise<ToolExecutionResult>;
    /**
     * Update configuration
     */
    updateConfig(config: Partial<ToolConfig>): void;
    /**
     * Get current configuration
     */
    getConfig(): ToolConfig;
    /**
     * Validate tool name
     */
    private validateToolName;
}
//# sourceMappingURL=registry.d.ts.map