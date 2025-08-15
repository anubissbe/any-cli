/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */
import type { Platform } from "@qwen-claude/core";
/**
 * Get the current platform
 */
export declare function getPlatform(): Platform;
/**
 * Check if running on Windows
 */
export declare function isWindows(): boolean;
/**
 * Check if running on macOS
 */
export declare function isMacOS(): boolean;
/**
 * Check if running on Linux
 */
export declare function isLinux(): boolean;
/**
 * Get platform-specific information
 */
export declare function getPlatformInfo(): Record<string, any>;
/**
 * Get platform-specific executable extension
 */
export declare function getExecutableExtension(): string;
/**
 * Get platform-specific path separator
 */
export declare function getPathSeparator(): string;
/**
 * Get platform-specific line ending
 */
export declare function getLineEnding(): string;
/**
 * Get platform-specific shell command
 */
export declare function getShellCommand(): string;
/**
 * Get platform-specific temporary directory
 */
export declare function getTempDir(): string;
/**
 * Get platform-specific home directory
 */
export declare function getHomeDir(): string;
/**
 * Get platform-specific config directory
 */
export declare function getConfigDir(): string;
/**
 * Get platform-specific cache directory
 */
export declare function getCacheDir(): string;
/**
 * Get platform-specific data directory
 */
export declare function getDataDir(): string;
//# sourceMappingURL=platform.d.ts.map