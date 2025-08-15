#!/usr/bin/env node

/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */

import { execSync } from "child_process";
import { existsSync, mkdirSync, statSync } from "fs";
import path from "path";

const ROOT_DIR = path.resolve(process.cwd());
const DIST_DIR = path.join(ROOT_DIR, "dist");
const BUNDLE_PATH = path.join(ROOT_DIR, "bundle", "qwen-claude.cjs");

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
  } catch (error) {
    console.error(`❌ Command failed: ${command}`);
    throw error;
  }
}

/**
 * Check if pkg is installed globally
 */
function ensurePkgInstalled() {
  try {
    execSync("pkg --version", { stdio: "pipe" });
    console.log("✅ pkg is installed");
  } catch {
    console.log("📦 Installing pkg globally...");
    exec("npm install -g pkg");
  }
}

/**
 * Create distribution directory
 */
function createDistDir() {
  if (!existsSync(DIST_DIR)) {
    mkdirSync(DIST_DIR, { recursive: true });
    console.log(`📁 Created dist directory: ${DIST_DIR}`);
  }
}

/**
 * Verify bundle exists and get info
 */
function verifyBundle() {
  if (!existsSync(BUNDLE_PATH)) {
    throw new Error(`Bundle not found at: ${BUNDLE_PATH}. Run 'npm run bundle' first.`);
  }
  
  const stats = statSync(BUNDLE_PATH);
  const sizeMB = (stats.size / 1024 / 1024).toFixed(2);
  console.log(`📦 Bundle found: ${BUNDLE_PATH} (${sizeMB} MB)`);
  return BUNDLE_PATH;
}

/**
 * Build binary for specific platform
 */
function buildBinary(target, outputName) {
  const outputPath = path.join(DIST_DIR, outputName);
  
  console.log(`\n🏗️  Building ${target} binary...`);
  console.log(`   Target: ${target}`);
  console.log(`   Output: ${outputPath}`);
  
  const command = `pkg "${BUNDLE_PATH}" --target ${target} --output "${outputPath}"`;
  
  try {
    exec(command);
    
    if (existsSync(outputPath)) {
      const stats = statSync(outputPath);
      const sizeMB = (stats.size / 1024 / 1024).toFixed(2);
      console.log(`✅ Binary created: ${outputPath} (${sizeMB} MB)`);
      return outputPath;
    } else {
      throw new Error(`Binary not created at: ${outputPath}`);
    }
  } catch (error) {
    console.error(`❌ Failed to build ${target} binary:`, error.message);
    throw error;
  }
}

/**
 * Build all binaries
 */
function buildAllBinaries() {
  const targets = [
    {
      target: "node18-linux-x64",
      output: "qwen-claude-linux",
      platform: "Linux"
    },
    {
      target: "node18-win-x64",
      output: "qwen-claude-windows.exe",
      platform: "Windows"
    }
  ];

  const results = [];

  for (const { target, output, platform } of targets) {
    try {
      const binaryPath = buildBinary(target, output);
      results.push({
        platform,
        target,
        path: binaryPath,
        success: true
      });
    } catch (error) {
      results.push({
        platform,
        target,
        error: error.message,
        success: false
      });
    }
  }

  return results;
}

/**
 * Display build summary
 */
function displaySummary(results) {
  console.log("\n📊 Build Summary");
  console.log("================");
  
  for (const result of results) {
    if (result.success) {
      console.log(`✅ ${result.platform}: ${result.path}`);
    } else {
      console.log(`❌ ${result.platform}: ${result.error}`);
    }
  }
  
  const successful = results.filter(r => r.success).length;
  const total = results.length;
  
  console.log(`\n📈 Success Rate: ${successful}/${total} (${Math.round((successful/total) * 100)}%)`);
  
  if (successful > 0) {
    console.log("\n🎉 Binary distribution ready!");
    console.log("📁 Binaries located in:", DIST_DIR);
  }
}

/**
 * Main function
 */
async function main() {
  try {
    console.log("🚀 Starting binary build process...");
    
    // Verify prerequisites
    verifyBundle();
    ensurePkgInstalled();
    createDistDir();
    
    // Build binaries
    const results = buildAllBinaries();
    
    // Display results
    displaySummary(results);
    
    // Exit with appropriate code
    const hasFailures = results.some(r => !r.success);
    process.exit(hasFailures ? 1 : 0);
    
  } catch (error) {
    console.error("\n💥 Fatal error:", error.message);
    process.exit(1);
  }
}

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}