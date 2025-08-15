#!/usr/bin/env node

/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */

import { rmSync, existsSync } from "fs";
import path from "path";
import { glob } from "glob";

const ROOT_DIR = path.resolve(process.cwd());

/**
 * Remove directory or file if it exists
 */
function removeIfExists(target) {
  if (existsSync(target)) {
    console.log(`🗑️  Removing: ${target}`);
    rmSync(target, { recursive: true, force: true });
  }
}

/**
 * Clean build artifacts
 */
function clean() {
  console.log("🧹 Cleaning build artifacts...");

  // Remove main build directories
  const cleanTargets = ["dist", "bundle", "coverage", ".nyc_output", "build"];

  cleanTargets.forEach((target) => {
    removeIfExists(path.join(ROOT_DIR, target));
  });

  // Clean package build directories
  const packages = glob.sync("packages/*/dist", { cwd: ROOT_DIR });
  packages.forEach((pkg) => {
    removeIfExists(path.join(ROOT_DIR, pkg));
  });

  // Clean package build files
  const buildFiles = glob.sync("packages/*/tsconfig.tsbuildinfo", {
    cwd: ROOT_DIR,
  });
  buildFiles.forEach((file) => {
    removeIfExists(path.join(ROOT_DIR, file));
  });

  console.log("✅ Clean completed!");
}

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  clean();
}
