/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */
import path from "path";
/**
 * Normalize path for cross-platform compatibility
 */
export declare function normalizePath(filePath: string): string;
/**
 * Convert path to platform-specific format
 */
export declare function toPlatformPath(filePath: string): string;
/**
 * Join paths with platform-specific separator
 */
export declare function joinPaths(...paths: string[]): string;
/**
 * Resolve path relative to base directory
 */
export declare function resolvePath(basePath: string, relativePath: string): string;
/**
 * Get relative path between two absolute paths
 */
export declare function getRelativePath(from: string, to: string): string;
/**
 * Check if path is absolute
 */
export declare function isAbsolute(filePath: string): boolean;
/**
 * Get directory name from path
 */
export declare function getDirname(filePath: string): string;
/**
 * Get basename from path
 */
export declare function getBasename(filePath: string, ext?: string): string;
/**
 * Get file extension from path
 */
export declare function getExtension(filePath: string): string;
/**
 * Change file extension
 */
export declare function changeExtension(filePath: string, newExt: string): string;
/**
 * Parse path into components
 */
export declare function parsePath(filePath: string): path.ParsedPath;
/**
 * Format path from components
 */
export declare function formatPath(pathObject: path.FormatInputPathObject): string;
/**
 * Check if path is within another path (security check)
 */
export declare function isWithinPath(childPath: string, parentPath: string): boolean;
/**
 * Sanitize filename for cross-platform compatibility
 */
export declare function sanitizeFilename(filename: string): string;
/**
 * Get common base path from multiple paths
 */
export declare function getCommonBasePath(paths: string[]): string;
/**
 * Expand tilde (~) to home directory
 */
export declare function expandTilde(filePath: string): string;
/**
 * Create a safe file path by ensuring it doesn't overwrite existing files
 */
export declare function createSafeFilePath(basePath: string, filename: string, checkExists: (filePath: string) => Promise<boolean>): Promise<string>;
/**
 * Convert Windows path to POSIX path
 */
export declare function toPosixPath(filePath: string): string;
/**
 * Convert POSIX path to Windows path
 */
export declare function toWindowsPath(filePath: string): string;
/**
 * Get file size from path (if it exists)
 */
export declare function getFileSize(filePath: string): Promise<number | null>;
/**
 * Check if path exists
 */
export declare function pathExists(filePath: string): Promise<boolean>;
//# sourceMappingURL=path-utils.d.ts.map