#!/usr/bin/env node

/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */

import { execSync } from "child_process";
import { writeFileSync, mkdirSync, existsSync } from "fs";
import path from "path";

const ROOT_DIR = path.resolve(process.cwd());
const OUTPUT_DIR = path.join(ROOT_DIR, "src", "generated");
const OUTPUT_FILE = path.join(OUTPUT_DIR, "git-info.ts");

/**
 * Execute git command safely
 */
function gitCommand(command, fallback = "unknown") {
  try {
    return execSync(command, {
      encoding: "utf8",
      cwd: ROOT_DIR,
      stdio: ["ignore", "pipe", "ignore"],
    }).trim();
  } catch {
    return fallback;
  }
}

/**
 * Generate git commit information
 */
function generateGitInfo() {
  console.log("📝 Generating git commit info...");

  const gitInfo = {
    commit: gitCommand("git rev-parse HEAD"),
    shortCommit: gitCommand("git rev-parse --short HEAD"),
    branch: gitCommand("git rev-parse --abbrev-ref HEAD"),
    tag: gitCommand("git describe --tags --exact-match", null),
    isDirty: gitCommand("git status --porcelain") !== "",
    buildTime: new Date().toISOString(),
  };

  // Ensure output directory exists
  if (!existsSync(OUTPUT_DIR)) {
    mkdirSync(OUTPUT_DIR, { recursive: true });
  }

  // Generate TypeScript file
  const content = `/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 * 
 * This file is auto-generated. Do not edit manually.
 */

export const GIT_INFO = {
  commit: '${gitInfo.commit}',
  shortCommit: '${gitInfo.shortCommit}',
  branch: '${gitInfo.branch}',
  tag: ${gitInfo.tag ? `'${gitInfo.tag}'` : "null"},
  isDirty: ${gitInfo.isDirty},
  buildTime: '${gitInfo.buildTime}',
} as const;

export default GIT_INFO;
`;

  writeFileSync(OUTPUT_FILE, content, "utf8");

  console.log("✅ Git info generated:", {
    commit: gitInfo.shortCommit,
    branch: gitInfo.branch,
    isDirty: gitInfo.isDirty,
  });
}

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  generateGitInfo();
}
