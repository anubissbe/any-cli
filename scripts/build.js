#!/usr/bin/env node

/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */

import { execSync } from "child_process";
import { existsSync } from "fs";
import path from "path";

const ROOT_DIR = path.resolve(process.cwd());

/**
 * Execute command with error handling
 */
function exec(command, options = {}) {
  console.log(`\n🔧 Running: ${command}`);
  try {
    const result = execSync(command, {
      stdio: "inherit",
      cwd: ROOT_DIR,
      ...options,
    });
    return result;
  } catch {
    console.error(`❌ Command failed: ${command}`);
    process.exit(1);
  }
}

/**
 * Build all packages
 */
function buildPackages() {
  const packages = ["core", "utils", "providers", "tools", "cli"];

  console.log("📦 Building packages...");

  for (const pkg of packages) {
    const packageDir = path.join(ROOT_DIR, "packages", pkg);

    if (!existsSync(packageDir)) {
      console.log(`⚠️  Package ${pkg} does not exist, skipping...`);
      continue;
    }

    console.log(`\n📦 Building package: ${pkg}`);
    exec("npm run build", { cwd: packageDir });
  }
}

/**
 * Main build process
 */
function main() {
  console.log("🚀 Starting build process...");

  // Check if node_modules exists
  if (!existsSync(path.join(ROOT_DIR, "node_modules"))) {
    console.log("📥 Installing dependencies...");
    exec("npm ci");
  }

  // Build packages
  buildPackages();

  console.log("\n✅ Build completed successfully!");
}

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}
