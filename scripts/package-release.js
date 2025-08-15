#!/usr/bin/env node

/**
 * @license
 * Copyright 2025 Qwen Claude CLI Contributors
 * SPDX-License-Identifier: MIT
 */

import { execSync } from "child_process";
import { existsSync, mkdirSync, copyFileSync, writeFileSync } from "fs";
import path from "path";
import { createRequire } from "module";

const require = createRequire(import.meta.url);
const ROOT_DIR = path.resolve(process.cwd());
const DIST_DIR = path.join(ROOT_DIR, "dist");
const RELEASE_DIR = path.join(ROOT_DIR, "release");

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
 * Get package version
 */
function getVersion() {
  const pkg = require(path.join(ROOT_DIR, "package.json"));
  return pkg.version;
}

/**
 * Create release directory structure
 */
function createReleaseStructure() {
  const version = getVersion();
  const releaseVersionDir = path.join(RELEASE_DIR, `v${version}`);
  
  if (!existsSync(RELEASE_DIR)) {
    mkdirSync(RELEASE_DIR, { recursive: true });
  }
  
  if (!existsSync(releaseVersionDir)) {
    mkdirSync(releaseVersionDir, { recursive: true });
  }
  
  console.log(`📁 Created release directory: ${releaseVersionDir}`);
  return releaseVersionDir;
}

/**
 * Copy binaries to release directory
 */
function copyBinaries(releaseDir) {
  const binaries = [
    { src: "qwen-claude-linux", dest: "qwen-claude-linux" },
    { src: "qwen-claude-windows.exe", dest: "qwen-claude-windows.exe" }
  ];
  
  for (const { src, dest } of binaries) {
    const srcPath = path.join(DIST_DIR, src);
    const destPath = path.join(releaseDir, dest);
    
    if (existsSync(srcPath)) {
      copyFileSync(srcPath, destPath);
      console.log(`📦 Copied: ${src} → ${dest}`);
    } else {
      console.warn(`⚠️  Binary not found: ${srcPath}`);
    }
  }
}

/**
 * Copy documentation
 */
function copyDocumentation(releaseDir) {
  const docs = [
    "README.md",
    "LICENSE",
    "docs/BINARY_DISTRIBUTION.md",
    "docs/QUICK_REFERENCE.md"
  ];
  
  for (const doc of docs) {
    const srcPath = path.join(ROOT_DIR, doc);
    const fileName = path.basename(doc);
    const destPath = path.join(releaseDir, fileName);
    
    if (existsSync(srcPath)) {
      copyFileSync(srcPath, destPath);
      console.log(`📄 Copied: ${doc}`);
    } else {
      console.warn(`⚠️  Documentation not found: ${srcPath}`);
    }
  }
}

/**
 * Generate checksums
 */
function generateChecksums(releaseDir) {
  const files = ["qwen-claude-linux", "qwen-claude-windows.exe"];
  const checksums = {};
  
  for (const file of files) {
    const filePath = path.join(releaseDir, file);
    if (existsSync(filePath)) {
      try {
        const result = execSync(`sha256sum "${filePath}"`, { 
          encoding: "utf-8", 
          cwd: releaseDir 
        });
        const [hash, fullPath] = result.trim().split(/\s+/);
        const filename = path.basename(fullPath);
        checksums[filename] = hash;
        console.log(`🔐 Generated checksum for: ${filename}`);
      } catch {
        console.warn(`⚠️  Failed to generate checksum for: ${file}`);
      }
    }
  }
  
  const checksumFile = path.join(releaseDir, "checksums.json");
  writeFileSync(checksumFile, JSON.stringify(checksums, null, 2));
  console.log(`✅ Checksums saved to: checksums.json`);
}

/**
 * Create installation scripts
 */
function createInstallationScripts(releaseDir) {
  // Linux/macOS installation script
  const installScript = `#!/bin/bash
set -e

# Qwen Claude CLI Installation Script
# Version: ${getVersion()}

echo "🚀 Installing Qwen Claude CLI..."

# Detect system
OS="$(uname -s)"
ARCH="$(uname -m)"

case $OS in
  Linux*)
    BINARY="qwen-claude-linux"
    ;;
  *)
    echo "❌ Unsupported operating system: $OS"
    exit 1
    ;;
esac

# Check if binary exists
if [ ! -f "$BINARY" ]; then
  echo "❌ Binary not found: $BINARY"
  echo "Please ensure you're running this script from the release directory."
  exit 1
fi

# Install location
INSTALL_DIR="$HOME/.local/bin"
INSTALL_PATH="$INSTALL_DIR/qwen-claude"

# Create install directory
mkdir -p "$INSTALL_DIR"

# Copy binary
cp "$BINARY" "$INSTALL_PATH"
chmod +x "$INSTALL_PATH"

echo "✅ Installed to: $INSTALL_PATH"

# Check if in PATH
if echo "$PATH" | grep -q "$INSTALL_DIR"; then
  echo "✅ $INSTALL_DIR is already in your PATH"
else
  echo "⚠️  Please add $INSTALL_DIR to your PATH:"
  echo "   echo 'export PATH=\"$HOME/.local/bin:$PATH\"' >> ~/.bashrc"
  echo "   source ~/.bashrc"
fi

echo ""
echo "🎉 Installation complete!"
echo "Run 'qwen-claude --help' to get started."
`;

  const installScriptPath = path.join(releaseDir, "install.sh");
  writeFileSync(installScriptPath, installScript);
  exec(`chmod +x "${installScriptPath}"`);
  console.log("📝 Created: install.sh");

  // Windows installation batch file
  const installBat = `@echo off
REM Qwen Claude CLI Windows Installation Script
REM Version: ${getVersion()}

echo 🚀 Installing Qwen Claude CLI...

if not exist "qwen-claude-windows.exe" (
    echo ❌ Binary not found: qwen-claude-windows.exe
    echo Please ensure you're running this script from the release directory.
    pause
    exit /b 1
)

REM Default installation directory
set INSTALL_DIR=%USERPROFILE%\\AppData\\Local\\Programs\\Qwen Claude CLI
set INSTALL_PATH=%INSTALL_DIR%\\qwen-claude.exe

REM Create install directory
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

REM Copy binary
copy "qwen-claude-windows.exe" "%INSTALL_PATH%"

echo ✅ Installed to: %INSTALL_PATH%

echo.
echo ⚠️ Please add the following directory to your PATH:
echo    %INSTALL_DIR%
echo.
echo 🎉 Installation complete!
echo Run 'qwen-claude --help' to get started.
pause
`;

  const installBatPath = path.join(releaseDir, "install.bat");
  writeFileSync(installBatPath, installBat);
  console.log("📝 Created: install.bat");
}

/**
 * Generate release notes
 */
function generateReleaseNotes(releaseDir) {
  const version = getVersion();
  const releaseNotes = `# Qwen Claude CLI v${version}

## 📦 Binary Release

This release includes pre-built binaries for Linux and Windows platforms.

### ✨ Features
- Advanced TypeScript CLI tool with AI model integration
- Local Qwen3-Coder 30B model support (192.168.1.28:8000)
- OpenRouter.ai free models integration
- Cross-platform tool execution system
- Interactive chat and one-shot question modes

### 📊 Binary Information
- **Linux**: qwen-claude-linux (~47 MB)
- **Windows**: qwen-claude-windows.exe (~39 MB)
- **Node.js**: Built with Node.js 18.x runtime
- **Architecture**: x64 only

### 🚀 Quick Installation

#### Linux/macOS
\`\`\`bash
# Download and extract the release
# Run the installation script
chmod +x install.sh
./install.sh
\`\`\`

#### Windows
\`\`\`cmd
REM Download and extract the release
REM Run the installation script
install.bat
\`\`\`

### 📋 Files Included
- \`qwen-claude-linux\` - Linux x64 binary
- \`qwen-claude-windows.exe\` - Windows x64 binary
- \`README.md\` - Main documentation
- \`BINARY_DISTRIBUTION.md\` - Binary-specific documentation
- \`QUICK_REFERENCE.md\` - Quick reference guide
- \`LICENSE\` - MIT license
- \`install.sh\` - Linux/macOS installation script
- \`install.bat\` - Windows installation script
- \`checksums.json\` - SHA256 checksums for verification

### 🔐 Verification
Use the provided checksums to verify binary integrity:
\`\`\`bash
sha256sum -c checksums.json
\`\`\`

### 📖 Documentation
See \`BINARY_DISTRIBUTION.md\` for detailed installation and usage instructions.

### 🆘 Support
For issues or questions, please refer to the documentation or create an issue in the repository.
`;

  const releaseNotesPath = path.join(releaseDir, "RELEASE_NOTES.md");
  writeFileSync(releaseNotesPath, releaseNotes);
  console.log("📝 Created: RELEASE_NOTES.md");
}

/**
 * Main packaging function
 */
async function main() {
  try {
    console.log("📦 Starting release packaging...");
    
    const version = getVersion();
    console.log(`📊 Version: ${version}`);
    
    // Verify binaries exist
    if (!existsSync(DIST_DIR)) {
      throw new Error("Distribution directory not found. Run 'npm run build:binaries' first.");
    }
    
    // Create release structure
    const releaseDir = createReleaseStructure();
    
    // Copy files
    copyBinaries(releaseDir);
    copyDocumentation(releaseDir);
    
    // Generate additional files
    generateChecksums(releaseDir);
    createInstallationScripts(releaseDir);
    generateReleaseNotes(releaseDir);
    
    console.log(`\n🎉 Release package created successfully!`);
    console.log(`📁 Location: ${releaseDir}`);
    console.log(`📊 Version: v${version}`);
    
    // Show release contents
    console.log("\n📋 Release Contents:");
    exec(`ls -la "${releaseDir}"`);
    
  } catch (error) {
    console.error("\n💥 Packaging failed:", error.message);
    process.exit(1);
  }
}

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}