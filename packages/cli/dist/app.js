/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */
import chalk from "chalk";
import ora from "ora";
import inquirer from "inquirer";
import { CLIError, ConfigError, ProviderError, } from "@qwen-claude/core";
import { QwenProvider } from "@qwen-claude/providers";
import { OpenRouterProvider } from "@qwen-claude/providers";
import { ConfigManager } from "@qwen-claude/utils";
import { ToolRegistry } from "@qwen-claude/tools";
import { GIT_INFO } from "./generated/git-info.js";
/**
 * Main CLI application class
 */
export class CLIApplication {
    config = null;
    providers = new Map();
    toolRegistry = null;
    configManager = null;
    /**
     * Initialize the application
     */
    async initialize() {
        if (this.config)
            return; // Already initialized
        try {
            // Initialize configuration manager
            this.configManager = new ConfigManager();
            this.config = await this.configManager.load();
            // Initialize providers
            await this.initializeProviders();
            // Initialize tool registry
            this.toolRegistry = new ToolRegistry({
                safeMode: this.config.tools.safetyLevel !== "dangerous",
                confirmDestructive: this.config.tools.confirmDestructive,
                allowedCategories: ["file", "shell", "analysis"],
                timeout: this.config.tools.timeout,
            });
        }
        catch (error) {
            throw new ConfigError(`Failed to initialize application: ${error instanceof Error ? error.message : String(error)}`);
        }
    }
    /**
     * Initialize model providers
     */
    async initializeProviders() {
        if (!this.config)
            throw new ConfigError("Configuration not loaded");
        // Initialize providers from config array
        for (const providerConfig of this.config.providers) {
            if (!providerConfig.enabled)
                continue;
            try {
                let provider;
                if (providerConfig.name === "qwen") {
                    provider = new QwenProvider(providerConfig);
                }
                else if (providerConfig.name === "openrouter") {
                    provider = new OpenRouterProvider(providerConfig);
                }
                else {
                    this.log(`Unknown provider: ${providerConfig.name}`, "warn");
                    continue;
                }
                this.providers.set(providerConfig.name, provider);
            }
            catch (error) {
                this.log(`Failed to create provider ${providerConfig.name}: ${error}`, "error");
            }
        }
        // Health check providers
        for (const [name, provider] of this.providers) {
            try {
                await provider.initialize();
                this.log(`✅ Provider ${name} initialized successfully`, "info");
            }
            catch (error) {
                this.log(`❌ Provider ${name} failed to initialize: ${error}`, "warn");
            }
        }
    }
    /**
     * Handle chat command
     */
    async handleChatCommand(options) {
        await this.initialize();
        const spinner = ora("Starting chat session...").start();
        try {
            const provider = await this.selectProvider(options.provider);
            const model = options.model ?? "qwen-coder-30b";
            spinner.stop();
            console.log(chalk.green('🤖 Chat session started. Type "exit" to quit.\n'));
            const messages = [];
            // Add system message if provided
            if (options.system) {
                messages.push({ role: "system", content: options.system });
            }
            while (true) {
                const { message } = await inquirer.prompt([
                    {
                        type: "input",
                        name: "message",
                        message: chalk.blue("You:"),
                        validate: (input) => input.trim().length > 0 || "Please enter a message",
                    },
                ]);
                if (message.toLowerCase() === "exit") {
                    console.log(chalk.yellow("👋 Chat session ended."));
                    break;
                }
                messages.push({ role: "user", content: message });
                const chatSpinner = ora("Thinking...").start();
                try {
                    const request = {
                        model,
                        messages,
                        stream: options.stream ?? false,
                        maxTokens: 2048,
                        temperature: 0.7,
                    };
                    const response = await provider.chatCompletion(request);
                    chatSpinner.stop();
                    if (!response.success) {
                        throw response.error;
                    }
                    const assistantMessage = response.data.message.content || "No response";
                    console.log(chalk.green("Assistant:"), assistantMessage);
                    console.log(); // Empty line for readability
                    messages.push({ role: "assistant", content: assistantMessage });
                }
                catch (error) {
                    chatSpinner.stop();
                    console.error(chalk.red("Error:"), error instanceof Error ? error.message : String(error));
                }
            }
        }
        catch (error) {
            spinner.stop();
            throw error;
        }
    }
    /**
     * Handle ask command (one-shot)
     */
    async handleAskCommand(question, options) {
        await this.initialize();
        const spinner = ora("Processing question...").start();
        try {
            const provider = await this.selectProvider(options.provider);
            const model = options.model ?? "qwen-coder-30b";
            const request = {
                model,
                messages: [{ role: "user", content: question }],
                stream: options.stream ?? false,
                maxTokens: 2048,
                temperature: 0.7,
            };
            const response = await provider.chatCompletion(request);
            spinner.stop();
            if (!response.success) {
                throw response.error;
            }
            const answer = response.data.message.content || "No response";
            console.log(chalk.green("Answer:"), answer);
        }
        catch (error) {
            spinner.stop();
            throw error;
        }
    }
    /**
     * Handle provider list command
     */
    async handleProviderListCommand() {
        await this.initialize();
        console.log(chalk.blue("📋 Available Providers:\n"));
        for (const [name, provider] of this.providers) {
            const status = await this.checkProviderHealth(provider);
            const statusIcon = status ? "✅" : "❌";
            const statusText = status
                ? chalk.green("Available")
                : chalk.red("Unavailable");
            console.log(`${statusIcon} ${chalk.bold(name)} - ${statusText}`);
            try {
                const modelsResult = await provider.getModels();
                if (modelsResult.success) {
                    const models = modelsResult.data;
                    console.log(`   Models: ${models.length} available`);
                    if (models.length > 0) {
                        console.log(`   Examples: ${models
                            .slice(0, 3)
                            .map((m) => m.id)
                            .join(", ")}${models.length > 3 ? "..." : ""}`);
                    }
                }
                else {
                    console.log("   Models: Unable to fetch");
                }
            }
            catch {
                console.log("   Models: Unable to fetch");
            }
            console.log();
        }
    }
    /**
     * Handle provider test command
     */
    async handleProviderTestCommand(providerName) {
        await this.initialize();
        const providersToTest = providerName
            ? [providerName]
            : Array.from(this.providers.keys());
        for (const name of providersToTest) {
            const provider = this.providers.get(name);
            if (!provider) {
                console.error(chalk.red(`❌ Provider '${name}' not found`));
                continue;
            }
            const spinner = ora(`Testing provider ${name}...`).start();
            try {
                const modelsResult = await provider.getModels();
                if (!modelsResult.success) {
                    throw modelsResult.error;
                }
                spinner.succeed(chalk.green(`✅ Provider ${name} is working`));
                console.log(`   Models available: ${modelsResult.data.length}`);
            }
            catch (error) {
                spinner.fail(chalk.red(`❌ Provider ${name} failed`));
                console.log(`   Error: ${error instanceof Error ? error.message : String(error)}`);
            }
        }
    }
    /**
     * Handle model list command
     */
    async handleModelListCommand(options) {
        await this.initialize();
        const spinner = ora("Fetching models...").start();
        try {
            const providersToCheck = options.provider
                ? [options.provider]
                : Array.from(this.providers.keys());
            const allModels = [];
            for (const providerName of providersToCheck) {
                const provider = this.providers.get(providerName);
                if (!provider)
                    continue;
                try {
                    const modelsResult = await provider.getModels();
                    if (modelsResult.success) {
                        for (const model of modelsResult.data) {
                            allModels.push({
                                provider: providerName,
                                id: model.id,
                                name: model.name || model.id,
                                capabilities: model.capabilities
                                    ? Object.keys(model.capabilities).filter((key) => model.capabilities[key])
                                    : [],
                                pricing: model.pricing
                                    ? {
                                        input: model.pricing.inputTokenPrice,
                                        output: model.pricing.outputTokenPrice,
                                    }
                                    : undefined,
                            });
                        }
                    }
                }
                catch (error) {
                    this.log(`Failed to fetch models from ${providerName}: ${error}`, "warn");
                }
            }
            spinner.stop();
            if (allModels.length === 0) {
                console.log(chalk.yellow("No models found"));
                return;
            }
            console.log(chalk.blue(`📋 Available Models (${allModels.length} total):\n`));
            // Group by provider
            const modelsByProvider = allModels.reduce((acc, model) => {
                if (!acc[model.provider])
                    acc[model.provider] = [];
                acc[model.provider].push(model);
                return acc;
            }, {});
            for (const [providerName, models] of Object.entries(modelsByProvider)) {
                console.log(chalk.bold(`${providerName.toUpperCase()} (${models.length} models):`));
                for (const model of models) {
                    const capabilities = model.capabilities.length > 0
                        ? ` [${model.capabilities.join(", ")}]`
                        : "";
                    const pricing = model.pricing
                        ? ` (${model.pricing.input || 0}/${model.pricing.output || 0} per 1K tokens)`
                        : "";
                    console.log(`  • ${model.id}${capabilities}${pricing}`);
                }
                console.log();
            }
        }
        catch (error) {
            spinner.stop();
            throw error;
        }
    }
    /**
     * Handle tool run command
     */
    async handleToolRunCommand(toolName, options) {
        await this.initialize();
        if (!this.toolRegistry) {
            throw new CLIError("Tool registry not initialized");
        }
        const spinner = ora(`Running tool: ${toolName}...`).start();
        try {
            const params = options.params ? JSON.parse(options.params) : {};
            if (options.dryRun) {
                spinner.info(`Would run tool '${toolName}' with params: ${JSON.stringify(params, null, 2)}`);
                return;
            }
            const result = await this.toolRegistry.executeTool(toolName, params, {
                confirmDestructive: options.confirm || false,
                safeMode: !options.confirm,
            });
            spinner.succeed(`Tool '${toolName}' completed successfully`);
            if (result.output) {
                console.log(chalk.green("Output:"));
                console.log(result.output);
            }
        }
        catch (error) {
            spinner.stop();
            throw error;
        }
    }
    /**
     * Handle tool list command
     */
    async handleToolListCommand(options) {
        await this.initialize();
        if (!this.toolRegistry) {
            throw new CLIError("Tool registry not initialized");
        }
        const tools = this.toolRegistry.getAvailableTools();
        const filteredTools = options.category
            ? tools.filter((tool) => tool.category === options.category)
            : tools;
        console.log(chalk.blue(`🔧 Available Tools (${filteredTools.length} total):\n`));
        // Group by category
        const toolsByCategory = filteredTools.reduce((acc, tool) => {
            const category = tool.category || "Other";
            if (!acc[category])
                acc[category] = [];
            acc[category].push(tool);
            return acc;
        }, {});
        for (const [category, categoryTools] of Object.entries(toolsByCategory)) {
            console.log(chalk.bold(`${category.toUpperCase()}:`));
            for (const tool of categoryTools) {
                const description = tool.description || "No description";
                const params = tool.parameters
                    ? ` (${Object.keys(tool.parameters).join(", ")})`
                    : "";
                console.log(`  • ${chalk.cyan(tool.name)}${params}: ${description}`);
            }
            console.log();
        }
    }
    /**
     * Handle config show command
     */
    async handleConfigShowCommand() {
        await this.initialize();
        if (!this.config) {
            throw new ConfigError("Configuration not loaded");
        }
        console.log(chalk.blue("📋 Current Configuration:\n"));
        // Mask sensitive information
        const sanitizedConfig = JSON.parse(JSON.stringify(this.config));
        if (sanitizedConfig.providers?.openrouter?.apiKey) {
            sanitizedConfig.providers.openrouter.apiKey = "***MASKED***";
        }
        console.log(JSON.stringify(sanitizedConfig, null, 2));
    }
    /**
     * Handle config init command
     */
    async handleConfigInitCommand(options) {
        if (!this.configManager) {
            this.configManager = new ConfigManager();
        }
        // Check if config file exists by trying to load it
        let existingConfig = false;
        try {
            await this.configManager.load();
            existingConfig = true;
        }
        catch {
            // Config file doesn't exist or is invalid, which is fine for init
            existingConfig = false;
        }
        if (existingConfig && !options.force) {
            const { overwrite } = await inquirer.prompt([
                {
                    type: "confirm",
                    name: "overwrite",
                    message: "Configuration already exists. Overwrite?",
                    default: false,
                },
            ]);
            if (!overwrite) {
                console.log(chalk.yellow("Configuration initialization cancelled."));
                return;
            }
        }
        console.log(chalk.blue("🔧 Initializing configuration...\n"));
        const config = await this.promptForConfiguration();
        const spinner = ora("Saving configuration...").start();
        await this.configManager.save(config);
        spinner.succeed("Configuration saved successfully!");
        console.log(chalk.green("\n✅ Configuration initialized. You can now use the CLI!"));
    }
    /**
     * Handle version command
     */
    async handleVersionCommand() {
        const version = process.env.CLI_VERSION || "0.1.0";
        console.log(chalk.blue("🚀 Qwen Claude CLI"));
        console.log(`Version: ${chalk.green(version)}`);
        console.log(`Git Commit: ${chalk.gray(GIT_INFO.shortCommit)}`);
        console.log(`Git Branch: ${chalk.gray(GIT_INFO.branch)}`);
        if (GIT_INFO.tag) {
            console.log(`Git Tag: ${chalk.gray(GIT_INFO.tag)}`);
        }
        console.log(`Build Time: ${chalk.gray(GIT_INFO.buildTime)}`);
        console.log(`Working Directory Clean: ${GIT_INFO.isDirty ? chalk.red("No") : chalk.green("Yes")}`);
    }
    // Helper methods
    /**
     * Select a provider based on preference or availability
     */
    async selectProvider(preferredProvider) {
        if (preferredProvider) {
            const provider = this.providers.get(preferredProvider);
            if (!provider) {
                throw new ProviderError(`Provider '${preferredProvider}' not found`, preferredProvider);
            }
            return provider;
        }
        // Select first available provider
        for (const [name, provider] of this.providers) {
            try {
                // Try to get models to verify provider is working
                const result = await provider.getModels();
                if (result.success) {
                    return provider;
                }
            }
            catch {
                this.log(`Provider ${name} is not available, trying next...`, "debug");
            }
        }
        throw new ProviderError("No providers are available", "unknown");
    }
    /**
     * Check provider health
     */
    async checkProviderHealth(provider) {
        try {
            const result = await provider.getModels();
            return result.success;
        }
        catch {
            return false;
        }
    }
    /**
     * Prompt user for configuration
     */
    async promptForConfiguration() {
        const { ConfigManager } = await import("@qwen-claude/utils");
        const configManager = new ConfigManager();
        const defaults = configManager.getDefaults();
        const answers = await inquirer.prompt([
            {
                type: "input",
                name: "qwenBaseUrl",
                message: "Qwen server base URL:",
                default: "http://192.168.1.28:8000",
                validate: (input) => input.trim().length > 0 || "Please enter a valid URL",
            },
            {
                type: "confirm",
                name: "enableQwen",
                message: "Enable Qwen provider?",
                default: true,
            },
            {
                type: "input",
                name: "openrouterApiKey",
                message: "OpenRouter API key (optional):",
                when: (answers) => !answers.enableQwen,
            },
            {
                type: "confirm",
                name: "enableOpenRouter",
                message: "Enable OpenRouter provider?",
                default: false,
            },
        ]);
        const providers = [];
        if (answers.enableQwen) {
            providers.push({
                name: "qwen",
                type: "local",
                priority: 1,
                enabled: true,
                auth: {
                    type: "none",
                    baseUrl: answers.qwenBaseUrl,
                },
                models: ["qwen-coder-30b", "qwen-chat"],
                endpoint: answers.qwenBaseUrl,
                timeout: 30000,
                retries: 3,
            });
        }
        if (answers.enableOpenRouter && answers.openrouterApiKey) {
            providers.push({
                name: "openrouter",
                type: "remote",
                priority: 2,
                enabled: true,
                auth: {
                    type: "api_key",
                    apiKey: answers.openrouterApiKey,
                    baseUrl: "https://openrouter.ai/api/v1",
                },
                models: [],
                endpoint: "https://openrouter.ai/api/v1",
                timeout: 30000,
                retries: 3,
            });
        }
        return {
            ...defaults,
            providers,
            defaultProvider: providers.length > 0 ? providers[0].name : undefined,
        };
    }
    /**
     * Log message with appropriate formatting
     */
    log(message, level) {
        const timestamp = new Date().toISOString();
        const prefix = this.config?.debug ? `[${timestamp}] ` : "";
        switch (level) {
            case "error":
                console.error(chalk.red(`${prefix}ERROR: ${message}`));
                break;
            case "warn":
                console.warn(chalk.yellow(`${prefix}WARN: ${message}`));
                break;
            case "info":
                console.log(chalk.blue(`${prefix}INFO: ${message}`));
                break;
            case "debug":
                if (this.config?.logLevel === "debug") {
                    console.log(chalk.gray(`${prefix}DEBUG: ${message}`));
                }
                break;
        }
    }
}
//# sourceMappingURL=app.js.map