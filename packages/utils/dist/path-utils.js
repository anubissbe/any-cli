/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */
import path from "path";
import { isWindows } from "./platform.js";
/**
 * Normalize path for cross-platform compatibility
 */
export function normalizePath(filePath) {
    return path.normalize(filePath).replace(/\\/g, "/");
}
/**
 * Convert path to platform-specific format
 */
export function toPlatformPath(filePath) {
    if (isWindows()) {
        return filePath.replace(/\//g, "\\");
    }
    return filePath;
}
/**
 * Join paths with platform-specific separator
 */
export function joinPaths(...paths) {
    return path.join(...paths);
}
/**
 * Resolve path relative to base directory
 */
export function resolvePath(basePath, relativePath) {
    return path.resolve(basePath, relativePath);
}
/**
 * Get relative path between two absolute paths
 */
export function getRelativePath(from, to) {
    return path.relative(from, to);
}
/**
 * Check if path is absolute
 */
export function isAbsolute(filePath) {
    return path.isAbsolute(filePath);
}
/**
 * Get directory name from path
 */
export function getDirname(filePath) {
    return path.dirname(filePath);
}
/**
 * Get basename from path
 */
export function getBasename(filePath, ext) {
    return path.basename(filePath, ext);
}
/**
 * Get file extension from path
 */
export function getExtension(filePath) {
    return path.extname(filePath);
}
/**
 * Change file extension
 */
export function changeExtension(filePath, newExt) {
    const parsed = path.parse(filePath);
    return path.format({
        ...parsed,
        base: undefined,
        ext: newExt.startsWith(".") ? newExt : `.${newExt}`,
    });
}
/**
 * Parse path into components
 */
export function parsePath(filePath) {
    return path.parse(filePath);
}
/**
 * Format path from components
 */
export function formatPath(pathObject) {
    return path.format(pathObject);
}
/**
 * Check if path is within another path (security check)
 */
export function isWithinPath(childPath, parentPath) {
    const relativePath = path.relative(parentPath, childPath);
    return !relativePath.startsWith("..") && !path.isAbsolute(relativePath);
}
/**
 * Sanitize filename for cross-platform compatibility
 */
export function sanitizeFilename(filename) {
    // Remove or replace invalid characters
    // eslint-disable-next-line no-control-regex
    const invalidChars = /[<>:"/\\|?*\x00-\x1f]/g;
    let sanitized = filename.replace(invalidChars, "_");
    // Handle reserved names on Windows
    const reservedNames = [
        "CON",
        "PRN",
        "AUX",
        "NUL",
        "COM1",
        "COM2",
        "COM3",
        "COM4",
        "COM5",
        "COM6",
        "COM7",
        "COM8",
        "COM9",
        "LPT1",
        "LPT2",
        "LPT3",
        "LPT4",
        "LPT5",
        "LPT6",
        "LPT7",
        "LPT8",
        "LPT9",
    ];
    const baseName = getBasename(sanitized, getExtension(sanitized));
    if (reservedNames.includes(baseName.toUpperCase())) {
        const ext = getExtension(sanitized);
        sanitized = `${baseName}_${ext}`;
    }
    // Trim spaces and dots from the end
    sanitized = sanitized.replace(/[ .]+$/, "");
    // Ensure not empty
    if (!sanitized.trim()) {
        sanitized = "untitled";
    }
    return sanitized;
}
/**
 * Get common base path from multiple paths
 */
export function getCommonBasePath(paths) {
    if (paths.length === 0)
        return "";
    if (paths.length === 1)
        return getDirname(paths[0]);
    const normalizedPaths = paths.map((p) => normalizePath(path.resolve(p)));
    const segments = normalizedPaths.map((p) => p.split("/"));
    const minLength = Math.min(...segments.map((s) => s.length));
    const commonSegments = [];
    for (let i = 0; i < minLength; i++) {
        const segment = segments[0][i];
        if (segments.every((s) => s[i] === segment)) {
            commonSegments.push(segment);
        }
        else {
            break;
        }
    }
    return commonSegments.join("/") || "/";
}
/**
 * Expand tilde (~) to home directory
 */
export function expandTilde(filePath) {
    if (filePath.startsWith("~/")) {
        // eslint-disable-next-line @typescript-eslint/no-var-requires
        const os = require("os");
        return path.join(os.homedir(), filePath.slice(2));
    }
    return filePath;
}
/**
 * Create a safe file path by ensuring it doesn't overwrite existing files
 */
export function createSafeFilePath(basePath, filename, checkExists) {
    return new Promise((resolve) => {
        (async () => {
            const sanitized = sanitizeFilename(filename);
            const parsed = parsePath(sanitized);
            let counter = 0;
            let currentPath = joinPaths(basePath, sanitized);
            while (await checkExists(currentPath)) {
                counter++;
                const newName = `${parsed.name} (${counter})${parsed.ext}`;
                currentPath = joinPaths(basePath, newName);
            }
            resolve(currentPath);
        })();
    });
}
/**
 * Convert Windows path to POSIX path
 */
export function toPosixPath(filePath) {
    return filePath.replace(/\\/g, "/");
}
/**
 * Convert POSIX path to Windows path
 */
export function toWindowsPath(filePath) {
    return filePath.replace(/\//g, "\\");
}
/**
 * Get file size from path (if it exists)
 */
export async function getFileSize(filePath) {
    try {
        const fs = await import("fs/promises");
        const stats = await fs.stat(filePath);
        return stats.size;
    }
    catch {
        return null;
    }
}
/**
 * Check if path exists
 */
export async function pathExists(filePath) {
    try {
        const fs = await import("fs/promises");
        await fs.access(filePath);
        return true;
    }
    catch {
        return false;
    }
}
//# sourceMappingURL=path-utils.js.map