/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */
/**
 * Main CLI application class
 */
export declare class CLIApplication {
    private config;
    private providers;
    private toolRegistry;
    private configManager;
    /**
     * Initialize the application
     */
    private initialize;
    /**
     * Initialize model providers
     */
    private initializeProviders;
    /**
     * Handle chat command
     */
    handleChatCommand(options: any): Promise<void>;
    /**
     * Handle ask command (one-shot)
     */
    handleAskCommand(question: string, options: any): Promise<void>;
    /**
     * Handle provider list command
     */
    handleProviderListCommand(): Promise<void>;
    /**
     * Handle provider test command
     */
    handleProviderTestCommand(providerName?: string): Promise<void>;
    /**
     * Handle model list command
     */
    handleModelListCommand(options: any): Promise<void>;
    /**
     * Handle tool run command
     */
    handleToolRunCommand(toolName: string, options: any): Promise<void>;
    /**
     * Handle tool list command
     */
    handleToolListCommand(options: any): Promise<void>;
    /**
     * Handle config show command
     */
    handleConfigShowCommand(): Promise<void>;
    /**
     * Handle config init command
     */
    handleConfigInitCommand(options: any): Promise<void>;
    /**
     * Handle version command
     */
    handleVersionCommand(): Promise<void>;
    /**
     * Select a provider based on preference or availability
     */
    private selectProvider;
    /**
     * Check provider health
     */
    private checkProviderHealth;
    /**
     * Prompt user for configuration
     */
    private promptForConfiguration;
    /**
     * Log message with appropriate formatting
     */
    private log;
}
//# sourceMappingURL=app.d.ts.map