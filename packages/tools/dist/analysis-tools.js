/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */
import fs from "fs-extra";
import path from "path";
import { glob } from "glob";
import { z } from "zod";
import { BaseTool } from "./base-tool.js";
import { SafetyLevel, ToolCategory } from "./types.js";
import { CodeAnalysisParamsSchema } from "./types.js";
/**
 * Code analysis tool
 */
export class AnalyzeCodeTool extends BaseTool {
    name = "analyze_code";
    description = "Analyze code files for metrics and structure";
    category = ToolCategory.ANALYSIS;
    safetyLevel = SafetyLevel.SAFE;
    parameters = {
        path: {
            type: "string",
            description: "Path to file or directory to analyze",
        },
        language: {
            type: "string",
            description: "Programming language",
            optional: true,
        },
        includeMetrics: {
            type: "boolean",
            description: "Include code metrics",
            default: true,
        },
        includeDependencies: {
            type: "boolean",
            description: "Include dependency analysis",
            default: false,
        },
    };
    async execute(params, context) {
        const { path: targetPath, language, includeMetrics, includeDependencies, } = this.validateParameters(params, CodeAnalysisParamsSchema);
        if (context.dryRun) {
            return this.createDryRunResult(`analyze code at: ${targetPath}`);
        }
        try {
            const absolutePath = path.resolve(context.workingDirectory, targetPath);
            // Security check
            if (!absolutePath.startsWith(context.workingDirectory)) {
                return this.createErrorResult(`Access denied: path outside working directory: ${targetPath}`);
            }
            const stats = await fs.stat(absolutePath);
            let analysis;
            if (stats.isFile()) {
                analysis = await this.analyzeFile(absolutePath, language, includeMetrics, includeDependencies);
            }
            else if (stats.isDirectory()) {
                analysis = await this.analyzeDirectory(absolutePath, language, includeMetrics, includeDependencies);
            }
            else {
                return this.createErrorResult(`Path is neither file nor directory: ${targetPath}`);
            }
            return this.createSuccessResult(JSON.stringify(analysis, null, 2), {
                targetPath: absolutePath,
                type: stats.isFile() ? "file" : "directory",
                includeMetrics,
                includeDependencies,
                language,
            });
        }
        catch (error) {
            return this.createErrorResult(`Failed to analyze code: ${error instanceof Error ? error.message : String(error)}`);
        }
    }
    async analyzeFile(filePath, language, includeMetrics, includeDependencies) {
        const content = await fs.readFile(filePath, "utf8");
        const ext = path.extname(filePath).toLowerCase();
        const detectedLanguage = language || this.detectLanguage(ext);
        const analysis = {
            file: path.basename(filePath),
            path: filePath,
            language: detectedLanguage,
            extension: ext,
            size: content.length,
        };
        if (includeMetrics) {
            analysis.metrics = this.calculateMetrics(content, detectedLanguage);
        }
        if (includeDependencies) {
            analysis.dependencies = this.extractDependencies(content, detectedLanguage);
        }
        return analysis;
    }
    async analyzeDirectory(dirPath, language, includeMetrics, includeDependencies) {
        const files = await glob("**/*", {
            cwd: dirPath,
            nodir: true,
            ignore: ["node_modules/**", ".git/**", "dist/**", "build/**", "*.log"],
        });
        const codeFiles = files.filter((file) => {
            const ext = path.extname(file).toLowerCase();
            return this.isCodeFile(ext);
        });
        const analysis = {
            directory: path.basename(dirPath),
            path: dirPath,
            totalFiles: files.length,
            codeFiles: codeFiles.length,
            languages: new Set(),
        };
        const fileAnalyses = [];
        let totalLines = 0;
        let totalSize = 0;
        for (const file of codeFiles) {
            const filePath = path.join(dirPath, file);
            const fileAnalysis = await this.analyzeFile(filePath, language, includeMetrics, includeDependencies);
            fileAnalyses.push(fileAnalysis);
            analysis.languages.add(fileAnalysis.language);
            if (fileAnalysis.metrics) {
                totalLines += fileAnalysis.metrics.lines;
                totalSize += fileAnalysis.size;
            }
        }
        analysis.languages = Array.from(analysis.languages);
        analysis.files = fileAnalyses;
        if (includeMetrics) {
            analysis.summary = {
                totalLines,
                totalSize,
                averageFileSize: codeFiles.length > 0 ? Math.round(totalSize / codeFiles.length) : 0,
                averageLinesPerFile: codeFiles.length > 0 ? Math.round(totalLines / codeFiles.length) : 0,
            };
        }
        return analysis;
    }
    calculateMetrics(content, language) {
        const lines = content.split("\n");
        const metrics = {
            lines: lines.length,
            nonEmptyLines: 0,
            commentLines: 0,
            codeLines: 0,
        };
        const commentPatterns = this.getCommentPatterns(language);
        for (const line of lines) {
            const trimmed = line.trim();
            if (trimmed.length === 0) {
                continue;
            }
            metrics.nonEmptyLines++;
            if (this.isCommentLine(trimmed, commentPatterns)) {
                metrics.commentLines++;
            }
            else {
                metrics.codeLines++;
            }
        }
        return metrics;
    }
    extractDependencies(content, language) {
        const dependencies = [];
        const patterns = this.getDependencyPatterns(language);
        for (const pattern of patterns) {
            const matches = content.match(new RegExp(pattern, "gm"));
            if (matches) {
                for (const match of matches) {
                    const depMatch = match.match(/'([^']+)'|"([^"]+)"/);
                    if (depMatch) {
                        dependencies.push(depMatch[1] || depMatch[2]);
                    }
                }
            }
        }
        return [...new Set(dependencies)].sort();
    }
    detectLanguage(extension) {
        const languageMap = {
            ".js": "javascript",
            ".jsx": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".py": "python",
            ".go": "go",
            ".rs": "rust",
            ".java": "java",
            ".c": "c",
            ".cpp": "cpp",
            ".cxx": "cpp",
            ".h": "c",
            ".hpp": "cpp",
            ".cs": "csharp",
            ".php": "php",
            ".rb": "ruby",
            ".swift": "swift",
            ".kt": "kotlin",
            ".scala": "scala",
            ".sh": "shell",
            ".bash": "shell",
            ".zsh": "shell",
            ".fish": "shell",
        };
        return languageMap[extension] || "unknown";
    }
    isCodeFile(extension) {
        const codeExtensions = [
            ".js",
            ".jsx",
            ".ts",
            ".tsx",
            ".py",
            ".go",
            ".rs",
            ".java",
            ".c",
            ".cpp",
            ".cxx",
            ".h",
            ".hpp",
            ".cs",
            ".php",
            ".rb",
            ".swift",
            ".kt",
            ".scala",
            ".sh",
            ".bash",
            ".zsh",
            ".fish",
        ];
        return codeExtensions.includes(extension);
    }
    getCommentPatterns(language) {
        const patterns = {
            javascript: ["//", "/*", "*"],
            typescript: ["//", "/*", "*"],
            python: ["#"],
            go: ["//", "/*", "*"],
            rust: ["//", "/*", "*"],
            java: ["//", "/*", "*"],
            c: ["//", "/*", "*"],
            cpp: ["//", "/*", "*"],
            csharp: ["//", "/*", "*"],
            php: ["//", "/*", "*", "#"],
            ruby: ["#"],
            swift: ["//", "/*", "*"],
            shell: ["#"],
        };
        return patterns[language] || ["//"];
    }
    isCommentLine(line, commentPatterns) {
        return commentPatterns.some((pattern) => line.startsWith(pattern));
    }
    getDependencyPatterns(language) {
        const patterns = {
            javascript: [
                "import\\s+.*\\s+from\\s+['\"]([^'\"]+)['\"]",
                "require\\s*\\(\\s*['\"]([^'\"]+)['\"]\\s*\\)",
            ],
            typescript: [
                "import\\s+.*\\s+from\\s+['\"]([^'\"]+)['\"]",
                "require\\s*\\(\\s*['\"]([^'\"]+)['\"]\\s*\\)",
            ],
            python: ["import\\s+([\\w\\.]+)", "from\\s+([\\w\\.]+)\\s+import"],
            go: ["import\\s+['\"]([^'\"]+)['\"]"],
            rust: ["use\\s+([\\w:]+)", "extern\\s+crate\\s+(\\w+)"],
        };
        return patterns[language] || [];
    }
}
/**
 * Count lines tool
 */
export class CountLinesTool extends BaseTool {
    name = "count_lines";
    description = "Count lines of code in files or directories";
    category = ToolCategory.ANALYSIS;
    safetyLevel = SafetyLevel.SAFE;
    parameters = {
        path: { type: "string", description: "Path to file or directory" },
        includeComments: {
            type: "boolean",
            description: "Include comment lines",
            default: true,
        },
        includeEmpty: {
            type: "boolean",
            description: "Include empty lines",
            default: true,
        },
    };
    async execute(params, context) {
        const schema = z.object({
            path: z.string(),
            includeComments: z.boolean().optional().default(true),
            includeEmpty: z.boolean().optional().default(true),
        });
        const { path: targetPath, includeComments, includeEmpty, } = this.validateParameters(params, schema);
        if (context.dryRun) {
            return this.createDryRunResult(`count lines in: ${targetPath}`);
        }
        try {
            const absolutePath = path.resolve(context.workingDirectory, targetPath);
            // Security check
            if (!absolutePath.startsWith(context.workingDirectory)) {
                return this.createErrorResult(`Access denied: path outside working directory: ${targetPath}`);
            }
            const stats = await fs.stat(absolutePath);
            let result;
            if (stats.isFile()) {
                result = await this.countFileLines(absolutePath, includeComments, includeEmpty);
            }
            else if (stats.isDirectory()) {
                result = await this.countDirectoryLines(absolutePath, includeComments, includeEmpty);
            }
            else {
                return this.createErrorResult(`Path is neither file nor directory: ${targetPath}`);
            }
            return this.createSuccessResult(JSON.stringify(result, null, 2), {
                targetPath: absolutePath,
                type: stats.isFile() ? "file" : "directory",
                includeComments,
                includeEmpty,
            });
        }
        catch (error) {
            return this.createErrorResult(`Failed to count lines: ${error instanceof Error ? error.message : String(error)}`);
        }
    }
    async countFileLines(filePath, includeComments, includeEmpty) {
        const content = await fs.readFile(filePath, "utf8");
        const lines = content.split("\n");
        const totalLines = lines.length;
        let codeLines = 0;
        let commentLines = 0;
        let emptyLines = 0;
        const ext = path.extname(filePath).toLowerCase();
        const language = this.detectLanguage(ext);
        const commentPatterns = this.getCommentPatterns(language);
        for (const line of lines) {
            const trimmed = line.trim();
            if (trimmed.length === 0) {
                emptyLines++;
            }
            else if (this.isCommentLine(trimmed, commentPatterns)) {
                commentLines++;
            }
            else {
                codeLines++;
            }
        }
        let countedLines = codeLines;
        if (includeComments)
            countedLines += commentLines;
        if (includeEmpty)
            countedLines += emptyLines;
        return {
            file: path.basename(filePath),
            language,
            totalLines,
            codeLines,
            commentLines,
            emptyLines,
            countedLines,
        };
    }
    async countDirectoryLines(dirPath, includeComments, includeEmpty) {
        const files = await glob("**/*", {
            cwd: dirPath,
            nodir: true,
            ignore: ["node_modules/**", ".git/**", "dist/**", "build/**", "*.log"],
        });
        const codeFiles = files.filter((file) => {
            const ext = path.extname(file).toLowerCase();
            return this.isCodeFile(ext);
        });
        const result = {
            directory: path.basename(dirPath),
            totalFiles: codeFiles.length,
            fileBreakdown: [],
            summary: {
                totalLines: 0,
                codeLines: 0,
                commentLines: 0,
                emptyLines: 0,
                countedLines: 0,
            },
            languageBreakdown: {},
        };
        for (const file of codeFiles) {
            const filePath = path.join(dirPath, file);
            const fileResult = await this.countFileLines(filePath, includeComments, includeEmpty);
            result.fileBreakdown.push(fileResult);
            // Update summary
            result.summary.totalLines += fileResult.totalLines;
            result.summary.codeLines += fileResult.codeLines;
            result.summary.commentLines += fileResult.commentLines;
            result.summary.emptyLines += fileResult.emptyLines;
            result.summary.countedLines += fileResult.countedLines;
            // Update language breakdown
            if (!result.languageBreakdown[fileResult.language]) {
                result.languageBreakdown[fileResult.language] = {
                    files: 0,
                    totalLines: 0,
                    codeLines: 0,
                    commentLines: 0,
                    emptyLines: 0,
                    countedLines: 0,
                };
            }
            const langStats = result.languageBreakdown[fileResult.language];
            langStats.files++;
            langStats.totalLines += fileResult.totalLines;
            langStats.codeLines += fileResult.codeLines;
            langStats.commentLines += fileResult.commentLines;
            langStats.emptyLines += fileResult.emptyLines;
            langStats.countedLines += fileResult.countedLines;
        }
        return result;
    }
    detectLanguage(extension) {
        // Reuse the same logic from AnalyzeCodeTool
        const languageMap = {
            ".js": "javascript",
            ".jsx": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".py": "python",
            ".go": "go",
            ".rs": "rust",
            ".java": "java",
            ".c": "c",
            ".cpp": "cpp",
            ".cxx": "cpp",
            ".h": "c",
            ".hpp": "cpp",
            ".cs": "csharp",
            ".php": "php",
            ".rb": "ruby",
            ".swift": "swift",
            ".sh": "shell",
        };
        return languageMap[extension] || "unknown";
    }
    isCodeFile(extension) {
        const codeExtensions = [
            ".js",
            ".jsx",
            ".ts",
            ".tsx",
            ".py",
            ".go",
            ".rs",
            ".java",
            ".c",
            ".cpp",
            ".cxx",
            ".h",
            ".hpp",
            ".cs",
            ".php",
            ".rb",
            ".swift",
            ".sh",
            ".bash",
            ".zsh",
            ".fish",
        ];
        return codeExtensions.includes(extension);
    }
    getCommentPatterns(language) {
        const patterns = {
            javascript: ["//", "/*", "*"],
            typescript: ["//", "/*", "*"],
            python: ["#"],
            go: ["//", "/*", "*"],
            rust: ["//", "/*", "*"],
            java: ["//", "/*", "*"],
            c: ["//", "/*", "*"],
            cpp: ["//", "/*", "*"],
            csharp: ["//", "/*", "*"],
            php: ["//", "/*", "*", "#"],
            ruby: ["#"],
            swift: ["//", "/*", "*"],
            shell: ["#"],
        };
        return patterns[language] || ["//"];
    }
    isCommentLine(line, commentPatterns) {
        return commentPatterns.some((pattern) => line.startsWith(pattern));
    }
}
/**
 * Find files tool
 */
export class FindFilesTool extends BaseTool {
    name = "find_files";
    description = "Find files matching patterns";
    category = ToolCategory.ANALYSIS;
    safetyLevel = SafetyLevel.SAFE;
    parameters = {
        pattern: { type: "string", description: "Glob pattern to search for" },
        path: {
            type: "string",
            description: "Directory to search in",
            default: ".",
        },
        includeHidden: {
            type: "boolean",
            description: "Include hidden files",
            default: false,
        },
        maxDepth: {
            type: "number",
            description: "Maximum search depth",
            optional: true,
        },
    };
    async execute(params, context) {
        const schema = z.object({
            pattern: z.string(),
            path: z.string().optional().default("."),
            includeHidden: z.boolean().optional().default(false),
            maxDepth: z.number().optional(),
        });
        const { pattern, path: searchPath, includeHidden, maxDepth, } = this.validateParameters(params, schema);
        if (context.dryRun) {
            return this.createDryRunResult(`find files matching "${pattern}" in ${searchPath}`);
        }
        try {
            const absolutePath = path.resolve(context.workingDirectory, searchPath);
            // Security check
            if (!absolutePath.startsWith(context.workingDirectory)) {
                return this.createErrorResult(`Access denied: path outside working directory: ${searchPath}`);
            }
            const globOptions = {
                cwd: absolutePath,
                nodir: true,
                ignore: ["node_modules/**", ".git/**"],
            };
            if (!includeHidden) {
                globOptions.dot = false;
            }
            if (maxDepth !== undefined) {
                globOptions.maxDepth = maxDepth;
            }
            const files = await glob(pattern, globOptions);
            // Get file stats for each match
            const results = await Promise.all(files.map(async (file) => {
                const filePath = path.join(absolutePath, file);
                const stats = await fs.stat(filePath);
                return {
                    path: file,
                    absolutePath: filePath,
                    size: stats.size,
                    modified: stats.mtime,
                    type: stats.isDirectory() ? "directory" : "file",
                };
            }));
            return this.createSuccessResult(JSON.stringify(results, null, 2), {
                pattern,
                searchPath: absolutePath,
                matchCount: results.length,
                includeHidden,
                maxDepth,
            });
        }
        catch (error) {
            return this.createErrorResult(`Failed to find files: ${error instanceof Error ? error.message : String(error)}`);
        }
    }
}
//# sourceMappingURL=analysis-tools.js.map