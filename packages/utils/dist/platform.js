/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */
import os from "os";
/**
 * Get the current platform
 */
export function getPlatform() {
    const platform = os.platform();
    switch (platform) {
        case "win32":
            return "windows";
        case "darwin":
            return "darwin";
        case "linux":
            return "linux";
        default:
            return "linux"; // Default fallback
    }
}
/**
 * Check if running on Windows
 */
export function isWindows() {
    return getPlatform() === "windows";
}
/**
 * Check if running on macOS
 */
export function isMacOS() {
    return getPlatform() === "darwin";
}
/**
 * Check if running on Linux
 */
export function isLinux() {
    return getPlatform() === "linux";
}
/**
 * Get platform-specific information
 */
export function getPlatformInfo() {
    return {
        platform: getPlatform(),
        arch: os.arch(),
        release: os.release(),
        version: os.version?.() ?? "unknown",
        hostname: os.hostname(),
        userInfo: os.userInfo(),
        homedir: os.homedir(),
        tmpdir: os.tmpdir(),
        cpus: os.cpus().length,
        totalmem: os.totalmem(),
        freemem: os.freemem(),
        uptime: os.uptime(),
    };
}
/**
 * Get platform-specific executable extension
 */
export function getExecutableExtension() {
    return isWindows() ? ".exe" : "";
}
/**
 * Get platform-specific path separator
 */
export function getPathSeparator() {
    return isWindows() ? ";" : ":";
}
/**
 * Get platform-specific line ending
 */
export function getLineEnding() {
    return isWindows() ? "\r\n" : "\n";
}
/**
 * Get platform-specific shell command
 */
export function getShellCommand() {
    if (isWindows()) {
        return process.env.COMSPEC ?? "cmd.exe";
    }
    return process.env.SHELL ?? "/bin/sh";
}
/**
 * Get platform-specific temporary directory
 */
export function getTempDir() {
    return os.tmpdir();
}
/**
 * Get platform-specific home directory
 */
export function getHomeDir() {
    return os.homedir();
}
/**
 * Get platform-specific config directory
 */
export function getConfigDir() {
    if (isWindows()) {
        return process.env.APPDATA ?? getHomeDir();
    }
    if (isMacOS()) {
        return `${getHomeDir()}/Library/Application Support`;
    }
    // Linux and others
    return process.env.XDG_CONFIG_HOME ?? `${getHomeDir()}/.config`;
}
/**
 * Get platform-specific cache directory
 */
export function getCacheDir() {
    if (isWindows()) {
        return process.env.LOCALAPPDATA ?? `${getHomeDir()}/AppData/Local`;
    }
    if (isMacOS()) {
        return `${getHomeDir()}/Library/Caches`;
    }
    // Linux and others
    return process.env.XDG_CACHE_HOME ?? `${getHomeDir()}/.cache`;
}
/**
 * Get platform-specific data directory
 */
export function getDataDir() {
    if (isWindows()) {
        return process.env.LOCALAPPDATA ?? `${getHomeDir()}/AppData/Local`;
    }
    if (isMacOS()) {
        return `${getHomeDir()}/Library/Application Support`;
    }
    // Linux and others
    return process.env.XDG_DATA_HOME ?? `${getHomeDir()}/.local/share`;
}
//# sourceMappingURL=platform.js.map