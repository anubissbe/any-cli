/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */

import type { Platform, Result } from "../types/common.js";

/**
 * Platform-specific path information
 */
export interface PlatformPaths {
  readonly home: string;
  readonly config: string;
  readonly data: string;
  readonly cache: string;
  readonly temp: string;
  readonly logs: string;
}

/**
 * System information
 */
export interface SystemInfo {
  readonly platform: Platform;
  readonly arch: string;
  readonly version: string;
  readonly hostname: string;
  readonly username: string;
  readonly shell?: string;
  readonly terminal?: string;
}

/**
 * Platform abstraction interface
 */
export interface PlatformAdapter {
  /**
   * Get current platform
   */
  getPlatform(): Platform;

  /**
   * Get system information
   */
  getSystemInfo(): Promise<SystemInfo>;

  /**
   * Get platform-specific paths
   */
  getPaths(): PlatformPaths;

  /**
   * Check if running in interactive terminal
   */
  isInteractive(): boolean;

  /**
   * Check if running with elevated privileges
   */
  isElevated(): Promise<boolean>;

  /**
   * Get environment variable
   */
  getEnv(name: string): string | undefined;

  /**
   * Set environment variable
   */
  setEnv(name: string, value: string): void;

  /**
   * Execute shell command
   */
  exec(
    command: string,
    options?: {
      cwd?: string;
      env?: Record<string, string>;
      timeout?: number;
    },
  ): Promise<
    Result<{
      stdout: string;
      stderr: string;
      exitCode: number;
    }>
  >;

  /**
   * Open file/URL with default application
   */
  open(target: string): Promise<Result<void>>;

  /**
   * Check if command exists in PATH
   */
  commandExists(command: string): Promise<boolean>;

  /**
   * Get terminal size
   */
  getTerminalSize(): { width: number; height: number } | undefined;

  /**
   * Check if output supports colors
   */
  supportsColor(): boolean;
}
