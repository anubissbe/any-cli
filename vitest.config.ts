/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */

import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    environment: "node",
    globals: true,
    coverage: {
      provider: "v8",
      reporter: ["text", "json", "html"],
      include: ["packages/**/src/**/*.{ts,tsx}"],
      exclude: [
        "packages/**/src/**/*.d.ts",
        "packages/**/src/**/*.test.{ts,tsx}",
        "packages/**/src/**/*.spec.{ts,tsx}",
        "packages/**/src/**/generated/**"
      ],
      thresholds: {
        global: {
          branches: 50,
          functions: 50,
          lines: 50,
          statements: 50
        }
      }
    }
  },
  resolve: {
    alias: {
      "@qwen-claude/core": "/opt/projects/qwen-claude-cli/packages/core/src",
      "@qwen-claude/utils": "/opt/projects/qwen-claude-cli/packages/utils/src",
      "@qwen-claude/providers": "/opt/projects/qwen-claude-cli/packages/providers/src",
      "@qwen-claude/tools": "/opt/projects/qwen-claude-cli/packages/tools/src",
      "@qwen-claude/cli": "/opt/projects/qwen-claude-cli/packages/cli/src"
    }
  }
});