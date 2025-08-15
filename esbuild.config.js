/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */

import esbuild from "esbuild";
import path from "path";
import { fileURLToPath } from "url";
import { createRequire } from "module";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const require = createRequire(import.meta.url);
const pkg = require(path.resolve(__dirname, "package.json"));

const external = [
  // Node.js built-ins
  "fs",
  "path",
  "os",
  "crypto",
  "child_process",
  "readline",
  "stream",
  "util",
  "events",
  "url",
  "http",
  "https",
  "net",
  "tls",
  "zlib",
  // External dependencies that should remain external
  "node-fetch",
];

esbuild
  .build({
    entryPoints: ["packages/cli/index.ts"],
    bundle: true,
    outfile: "bundle/qwen-claude.cjs",
    platform: "node",
    format: "cjs",
    target: "node18",
    external,
    alias: {
      "@qwen-claude/core": path.resolve(__dirname, "packages/core/src"),
      "@qwen-claude/providers": path.resolve(
        __dirname,
        "packages/providers/src",
      ),
      "@qwen-claude/tools": path.resolve(__dirname, "packages/tools/src"),
      "@qwen-claude/utils": path.resolve(__dirname, "packages/utils/src"),
    },
    define: {
      "process.env.CLI_VERSION": JSON.stringify(pkg.version),
      "process.env.NODE_ENV": JSON.stringify(
        process.env.NODE_ENV || "production",
      ),
    },
    banner: {
      js: `#!/usr/bin/env node`,
    },
    minify: process.env.NODE_ENV === "production",
    sourcemap: process.env.NODE_ENV !== "production",
    keepNames: true,
    metafile: true,
  })
  .then((result) => {
    if (result.metafile) {
      require("fs").writeFileSync(
        "bundle/meta.json",
        JSON.stringify(result.metafile, null, 2),
      );
    }
    console.log("✅ Build completed successfully");
  })
  .catch((error) => {
    console.error("❌ Build failed:", error);
    process.exit(1);
  });
