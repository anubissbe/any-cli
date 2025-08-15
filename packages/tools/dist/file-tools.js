/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */
import fs from "fs-extra";
import path from "path";
import { z } from "zod";
import { BaseTool } from "./base-tool.js";
import { SafetyLevel, ToolCategory } from "./types.js";
import { FileOperationParamsSchema } from "./types.js";
/**
 * Read file tool
 */
export class ReadFileTool extends BaseTool {
    name = "read_file";
    description = "Read contents of a file";
    category = ToolCategory.FILE;
    safetyLevel = SafetyLevel.SAFE;
    parameters = {
        path: { type: "string", description: "Path to the file to read" },
        encoding: {
            type: "string",
            description: "File encoding (default: utf8)",
            default: "utf8",
        },
    };
    async execute(params, context) {
        const { path: filePath, encoding } = this.validateParameters(params, FileOperationParamsSchema.pick({ path: true, encoding: true }));
        if (context.dryRun) {
            return this.createDryRunResult(`read file: ${filePath}`);
        }
        try {
            const absolutePath = path.resolve(context.workingDirectory, filePath);
            // Security check: ensure file is within working directory or explicitly allowed
            if (!absolutePath.startsWith(context.workingDirectory)) {
                return this.createErrorResult(`Access denied: file outside working directory: ${filePath}`);
            }
            const content = await fs.readFile(absolutePath, encoding);
            const stats = await fs.stat(absolutePath);
            return this.createSuccessResult(content, {
                filePath: absolutePath,
                size: stats.size,
                modified: stats.mtime,
                encoding,
            });
        }
        catch (error) {
            return this.createErrorResult(`Failed to read file: ${error instanceof Error ? error.message : String(error)}`);
        }
    }
}
/**
 * Write file tool
 */
export class WriteFileTool extends BaseTool {
    name = "write_file";
    description = "Write content to a file";
    category = ToolCategory.FILE;
    safetyLevel = SafetyLevel.DESTRUCTIVE;
    parameters = {
        path: { type: "string", description: "Path to the file to write" },
        content: { type: "string", description: "Content to write to the file" },
        encoding: {
            type: "string",
            description: "File encoding (default: utf8)",
            default: "utf8",
        },
        mode: {
            type: "number",
            description: "File mode/permissions",
            optional: true,
        },
    };
    async execute(params, context) {
        this.checkSafety(context);
        const { path: filePath, content, encoding, mode, } = this.validateParameters(params, FileOperationParamsSchema);
        const absolutePath = path.resolve(context.workingDirectory, filePath);
        // Security check
        if (!absolutePath.startsWith(context.workingDirectory)) {
            return this.createErrorResult(`Access denied: file outside working directory: ${filePath}`);
        }
        // Check if file exists and confirm overwrite
        const fileExists = await fs.pathExists(absolutePath);
        if (fileExists) {
            const confirmed = await this.confirmOperation(context, `Overwrite existing file: ${filePath}?`);
            if (!confirmed) {
                return this.createErrorResult("Operation cancelled by user");
            }
        }
        if (context.dryRun) {
            return this.createDryRunResult(`write ${content.length} characters to file: ${filePath}`, { fileExists, contentLength: content.length });
        }
        try {
            // Ensure directory exists
            await fs.ensureDir(path.dirname(absolutePath));
            // Write file
            await fs.writeFile(absolutePath, content, { encoding, mode });
            const stats = await fs.stat(absolutePath);
            return this.createSuccessResult(`Successfully wrote ${content.length} characters to ${filePath}`, {
                filePath: absolutePath,
                size: stats.size,
                encoding,
                contentLength: content.length,
            });
        }
        catch (error) {
            return this.createErrorResult(`Failed to write file: ${error instanceof Error ? error.message : String(error)}`);
        }
    }
}
/**
 * List directory tool
 */
export class ListDirectoryTool extends BaseTool {
    name = "list_directory";
    description = "List contents of a directory";
    category = ToolCategory.FILE;
    safetyLevel = SafetyLevel.SAFE;
    parameters = {
        path: { type: "string", description: "Path to the directory to list" },
        includeHidden: {
            type: "boolean",
            description: "Include hidden files",
            default: false,
        },
        recursive: {
            type: "boolean",
            description: "List recursively",
            default: false,
        },
    };
    async execute(params, context) {
        const schema = z.object({
            path: z.string(),
            includeHidden: z.boolean().optional().default(false),
            recursive: z.boolean().optional().default(false),
        });
        const { path: dirPath, includeHidden, recursive, } = this.validateParameters(params, schema);
        if (context.dryRun) {
            return this.createDryRunResult(`list directory: ${dirPath}`);
        }
        try {
            const absolutePath = path.resolve(context.workingDirectory, dirPath);
            // Security check
            if (!absolutePath.startsWith(context.workingDirectory)) {
                return this.createErrorResult(`Access denied: directory outside working directory: ${dirPath}`);
            }
            const entries = await this.listDirectory(absolutePath, includeHidden, recursive);
            return this.createSuccessResult(JSON.stringify(entries, null, 2), {
                directoryPath: absolutePath,
                entryCount: entries.length,
                includeHidden,
                recursive,
            });
        }
        catch (error) {
            return this.createErrorResult(`Failed to list directory: ${error instanceof Error ? error.message : String(error)}`);
        }
    }
    async listDirectory(dirPath, includeHidden, recursive) {
        const entries = await fs.readdir(dirPath);
        const result = [];
        for (const entry of entries) {
            if (!includeHidden && entry.startsWith(".")) {
                continue;
            }
            const entryPath = path.join(dirPath, entry);
            const stats = await fs.stat(entryPath);
            const item = {
                name: entry,
                type: stats.isDirectory() ? "directory" : "file",
                size: stats.isFile() ? stats.size : undefined,
                modified: stats.mtime,
            };
            result.push(item);
            if (recursive && stats.isDirectory()) {
                const subEntries = await this.listDirectory(entryPath, includeHidden, recursive);
                for (const subEntry of subEntries) {
                    result.push({
                        ...subEntry,
                        name: path.join(entry, subEntry.name),
                    });
                }
            }
        }
        return result.sort((a, b) => a.name.localeCompare(b.name));
    }
}
/**
 * Create directory tool
 */
export class CreateDirectoryTool extends BaseTool {
    name = "create_directory";
    description = "Create a directory (and parent directories if needed)";
    category = ToolCategory.FILE;
    safetyLevel = SafetyLevel.MODERATE;
    parameters = {
        path: { type: "string", description: "Path to the directory to create" },
        mode: {
            type: "number",
            description: "Directory mode/permissions",
            optional: true,
        },
    };
    async execute(params, context) {
        const schema = z.object({
            path: z.string(),
            mode: z.number().optional(),
        });
        const { path: dirPath, mode } = this.validateParameters(params, schema);
        const absolutePath = path.resolve(context.workingDirectory, dirPath);
        // Security check
        if (!absolutePath.startsWith(context.workingDirectory)) {
            return this.createErrorResult(`Access denied: directory outside working directory: ${dirPath}`);
        }
        if (context.dryRun) {
            return this.createDryRunResult(`create directory: ${dirPath}`);
        }
        try {
            await fs.ensureDir(absolutePath, mode);
            const stats = await fs.stat(absolutePath);
            return this.createSuccessResult(`Successfully created directory: ${dirPath}`, {
                directoryPath: absolutePath,
                created: stats.birthtime,
                mode: stats.mode,
            });
        }
        catch (error) {
            return this.createErrorResult(`Failed to create directory: ${error instanceof Error ? error.message : String(error)}`);
        }
    }
}
//# sourceMappingURL=file-tools.js.map