/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */
import { z } from "zod";
/**
 * Configuration validation schemas
 */
export const PlatformSchema = z.enum(["linux", "windows", "darwin"]);
export const LogLevelSchema = z.enum(["debug", "info", "warn", "error"]);
//# sourceMappingURL=common.js.map