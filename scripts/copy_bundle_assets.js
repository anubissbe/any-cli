#!/usr/bin/env node

/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */

import { copyFileSync, existsSync, mkdirSync, chmodSync } from "fs";
import path from "path";

const ROOT_DIR = path.resolve(process.cwd());
const BUNDLE_DIR = path.join(ROOT_DIR, "bundle");
const BUNDLE_FILE = path.join(BUNDLE_DIR, "qwen-claude.cjs");

/**
 * Copy bundle assets and set permissions
 */
function copyBundleAssets() {
  console.log("📦 Copying bundle assets...");

  // Ensure bundle directory exists
  if (!existsSync(BUNDLE_DIR)) {
    mkdirSync(BUNDLE_DIR, { recursive: true });
  }

  // Make bundle executable (Unix-like systems)
  if (existsSync(BUNDLE_FILE)) {
    try {
      chmodSync(BUNDLE_FILE, 0o755);
      console.log("✅ Made bundle executable");
    } catch (error) {
      console.warn("⚠️  Could not make bundle executable:", error.message);
    }
  }

  // Copy README and LICENSE to bundle directory for distribution
  const filesToCopy = ["README.md", "LICENSE"];

  filesToCopy.forEach((file) => {
    const source = path.join(ROOT_DIR, file);
    const target = path.join(BUNDLE_DIR, file);

    if (existsSync(source)) {
      copyFileSync(source, target);
      console.log(`📄 Copied ${file}`);
    }
  });

  console.log("✅ Bundle assets copied successfully!");
}

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  copyBundleAssets();
}
