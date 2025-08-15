/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */

import os from "os";
import type { Platform } from "@qwen-claude/core";

/**
 * Get the current platform
 */
export function getPlatform(): Platform {
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
export function isWindows(): boolean {
  return getPlatform() === "windows";
}

/**
 * Check if running on macOS
 */
export function isMacOS(): boolean {
  return getPlatform() === "darwin";
}

/**
 * Check if running on Linux
 */
export function isLinux(): boolean {
  return getPlatform() === "linux";
}

/**
 * Get platform-specific information
 */
export function getPlatformInfo(): Record<string, any> {
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
export function getExecutableExtension(): string {
  return isWindows() ? ".exe" : "";
}

/**
 * Get platform-specific path separator
 */
export function getPathSeparator(): string {
  return isWindows() ? ";" : ":";
}

/**
 * Get platform-specific line ending
 */
export function getLineEnding(): string {
  return isWindows() ? "\r\n" : "\n";
}

/**
 * Get platform-specific shell command
 */
export function getShellCommand(): string {
  if (isWindows()) {
    return process.env.COMSPEC ?? "cmd.exe";
  }
  return process.env.SHELL ?? "/bin/sh";
}

/**
 * Get platform-specific temporary directory
 */
export function getTempDir(): string {
  return os.tmpdir();
}

/**
 * Get platform-specific home directory
 */
export function getHomeDir(): string {
  return os.homedir();
}

/**
 * Get platform-specific config directory
 */
export function getConfigDir(): string {
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
export function getCacheDir(): string {
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
export function getDataDir(): string {
  if (isWindows()) {
    return process.env.LOCALAPPDATA ?? `${getHomeDir()}/AppData/Local`;
  }

  if (isMacOS()) {
    return `${getHomeDir()}/Library/Application Support`;
  }

  // Linux and others
  return process.env.XDG_DATA_HOME ?? `${getHomeDir()}/.local/share`;
}
