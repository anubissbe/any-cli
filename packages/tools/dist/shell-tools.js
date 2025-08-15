/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */
import { spawn } from "child_process";
import { z } from "zod";
import { BaseTool } from "./base-tool.js";
import { getPlatform } from "@qwen-claude/utils";
import { SafetyLevel, ToolCategory } from "./types.js";
import { ShellCommandParamsSchema } from "./types.js";
/**
 * Execute shell command tool
 */
export class ExecuteCommandTool extends BaseTool {
    name = "execute_command";
    description = "Execute a shell command";
    category = ToolCategory.SHELL;
    safetyLevel = SafetyLevel.DESTRUCTIVE;
    parameters = {
        command: { type: "string", description: "Command to execute" },
        args: { type: "array", description: "Command arguments", default: [] },
        cwd: { type: "string", description: "Working directory", optional: true },
        env: {
            type: "object",
            description: "Environment variables",
            optional: true,
        },
        timeout: {
            type: "number",
            description: "Timeout in milliseconds",
            default: 30000,
        },
        shell: { type: "boolean", description: "Run in shell", default: true },
    };
    async execute(params, context) {
        this.checkSafety(context);
        const { command, args, cwd, env, timeout, shell } = this.validateParameters(params, ShellCommandParamsSchema);
        const workingDir = cwd || context.workingDirectory;
        const commandTimeout = Math.min(timeout, context.timeout || 60000);
        // Confirm destructive operations
        const confirmed = await this.confirmOperation(context, `Execute command: ${command} ${args.join(" ")}`);
        if (!confirmed) {
            return this.createErrorResult("Operation cancelled by user");
        }
        if (context.dryRun) {
            return this.createDryRunResult(`execute command: ${command} ${args.join(" ")} in ${workingDir}`, { command, args, cwd: workingDir, timeout: commandTimeout });
        }
        return new Promise((resolve) => {
            const platform = getPlatform();
            const shellConfig = { shell };
            // Platform-specific shell configuration
            if (shell) {
                if (platform === "windows") {
                    shellConfig.shell = process.env.COMSPEC || "cmd.exe";
                }
                else {
                    shellConfig.shell = process.env.SHELL || "/bin/sh";
                }
            }
            // Merge environment variables
            const processEnv = {
                ...process.env,
                ...context.environment,
                ...env,
            };
            const childProcess = spawn(command, args, {
                cwd: workingDir,
                env: processEnv,
                ...shellConfig,
                stdio: "pipe",
            });
            let stdout = "";
            let stderr = "";
            let killed = false;
            // Set up timeout
            const timeoutId = setTimeout(() => {
                killed = true;
                childProcess.kill("SIGTERM");
                // Force kill after additional timeout
                setTimeout(() => {
                    if (!childProcess.killed) {
                        childProcess.kill("SIGKILL");
                    }
                }, 5000);
            }, commandTimeout);
            // Collect output
            childProcess.stdout?.on("data", (data) => {
                stdout += data.toString();
            });
            childProcess.stderr?.on("data", (data) => {
                stderr += data.toString();
            });
            childProcess.on("close", (code, signal) => {
                clearTimeout(timeoutId);
                if (killed) {
                    resolve(this.createErrorResult(`Command timed out after ${commandTimeout}ms`, -1, {
                        command,
                        args,
                        timeout: commandTimeout,
                        killed: true,
                        signal,
                    }));
                    return;
                }
                const success = code === 0;
                const output = stdout.trim();
                const error = stderr.trim();
                if (success) {
                    resolve(this.createSuccessResult(output || "Command executed successfully", {
                        command,
                        args,
                        exitCode: code,
                        cwd: workingDir,
                        executionTime: Date.now(),
                        stdoutLength: stdout.length,
                        stderrLength: stderr.length,
                    }));
                }
                else {
                    resolve(this.createErrorResult(error || `Command failed with exit code ${code}`, code || -1, {
                        command,
                        args,
                        exitCode: code,
                        signal,
                        cwd: workingDir,
                        stdout: output,
                    }));
                }
            });
            childProcess.on("error", (error) => {
                clearTimeout(timeoutId);
                resolve(this.createErrorResult(`Failed to spawn command: ${error.message}`, -1, { command, args, spawnError: error.message }));
            });
        });
    }
}
/**
 * Which command tool - find executable in PATH
 */
export class WhichCommandTool extends BaseTool {
    name = "which_command";
    description = "Find the path of an executable command";
    category = ToolCategory.SHELL;
    safetyLevel = SafetyLevel.SAFE;
    parameters = {
        command: { type: "string", description: "Command to locate" },
    };
    async execute(params, context) {
        const schema = z.object({
            command: z.string(),
        });
        const { command } = this.validateParameters(params, schema);
        if (context.dryRun) {
            return this.createDryRunResult(`locate command: ${command}`);
        }
        try {
            const platform = getPlatform();
            const whichCommand = platform === "windows" ? "where" : "which";
            return new Promise((resolve) => {
                const childProcess = spawn(whichCommand, [command], {
                    stdio: "pipe",
                    shell: true,
                });
                let stdout = "";
                let stderr = "";
                childProcess.stdout?.on("data", (data) => {
                    stdout += data.toString();
                });
                childProcess.stderr?.on("data", (data) => {
                    stderr += data.toString();
                });
                childProcess.on("close", (code) => {
                    if (code === 0) {
                        const paths = stdout.trim().split("\n").filter(Boolean);
                        resolve(this.createSuccessResult(paths.join("\n"), {
                            command,
                            paths,
                            platform,
                            found: true,
                        }));
                    }
                    else {
                        resolve(this.createErrorResult(`Command '${command}' not found in PATH`, code || 1, {
                            command,
                            platform,
                            found: false,
                            stderr: stderr.trim(),
                        }));
                    }
                });
                childProcess.on("error", (error) => {
                    resolve(this.createErrorResult(`Failed to execute which command: ${error.message}`, -1, { command, error: error.message }));
                });
            });
        }
        catch (error) {
            return this.createErrorResult(`Failed to locate command: ${error instanceof Error ? error.message : String(error)}`);
        }
    }
}
//# sourceMappingURL=shell-tools.js.map