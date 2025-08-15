#!/usr/bin/env node

/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */

import { spawn } from "child_process";
import { existsSync } from "fs";
import path from "path";

const ROOT_DIR = path.resolve(process.cwd());
const BUNDLE_PATH = path.join(ROOT_DIR, "bundle", "qwen-claude.js");

/**
 * Start the CLI
 */
function start() {
  // Check if bundle exists
  if (!existsSync(BUNDLE_PATH)) {
    console.error('❌ Bundle not found. Please run "npm run build" first.');
    process.exit(1);
  }

  // Get command line arguments (skip node and script name)
  const args = process.argv.slice(2);

  // Start the CLI with arguments
  const child = spawn("node", [BUNDLE_PATH, ...args], {
    stdio: "inherit",
    cwd: ROOT_DIR,
  });

  child.on("exit", (code) => {
    process.exit(code || 0);
  });

  child.on("error", (error) => {
    console.error("❌ Failed to start CLI:", error.message);
    process.exit(1);
  });
}

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  start();
}
