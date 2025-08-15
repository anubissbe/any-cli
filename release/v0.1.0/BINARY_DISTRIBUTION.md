# Binary Distribution Guide

This document provides information about the pre-built binaries and distribution of the Qwen Claude CLI tool.

## 📦 Available Binaries

The Qwen Claude CLI is packaged as standalone executables for the following platforms:

### Linux (x64)
- **File**: `qwen-claude-linux`
- **Size**: ~47 MB
- **Target**: Node.js 18.x (x64)
- **Compatibility**: Most Linux distributions (glibc 2.17+)

### Windows (x64)
- **File**: `qwen-claude-windows.exe`
- **Size**: ~39 MB
- **Target**: Node.js 18.x (x64)
- **Compatibility**: Windows 10/11 (x64)

## 🚀 Installation

### Linux

1. **Download the binary**:
   ```bash
   # From the dist directory
   cp /opt/projects/qwen-claude-cli/dist/qwen-claude-linux ~/bin/qwen-claude
   
   # Or create a system-wide installation
   sudo cp /opt/projects/qwen-claude-cli/dist/qwen-claude-linux /usr/local/bin/qwen-claude
   ```

2. **Make it executable**:
   ```bash
   chmod +x ~/bin/qwen-claude
   # or for system-wide
   sudo chmod +x /usr/local/bin/qwen-claude
   ```

3. **Add to PATH** (if using ~/bin):
   ```bash
   echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc
   source ~/.bashrc
   ```

### Windows

1. **Download the binary**:
   - Copy `qwen-claude-windows.exe` from the dist directory
   - Place it in a directory like `C:\\tools\\` or `C:\\Program Files\\Qwen Claude CLI\\`

2. **Add to PATH**:
   - Open System Properties → Advanced → Environment Variables
   - Add the installation directory to your PATH variable
   - Or rename the file to `qwen-claude.exe` and place it in an existing PATH directory

## ✅ Verification

Test your installation:

```bash
# Check version
qwen-claude --version

# Show help
qwen-claude --help

# Show configuration
qwen-claude config show
```

## 🔧 Configuration

The CLI will automatically create configuration files on first run:

- **Linux**: `~/.config/config.json`
- **Windows**: `%APPDATA%\\config.json`

### Initial Setup

1. **Initialize configuration**:
   ```bash
   qwen-claude config init
   ```

2. **Configure providers**:
   The tool comes pre-configured with:
   - Local Qwen3-Coder 30B (192.168.1.28:8000)
   - OpenRouter.ai free models
   
   Update the configuration as needed:
   ```bash
   qwen-claude config show
   ```

## 🎯 Usage Examples

### Basic Chat
```bash
qwen-claude chat
```

### One-shot Questions
```bash
qwen-claude ask "How do I implement a binary search in Python?"
```

### Provider Management
```bash
# List providers
qwen-claude provider list

# Test connectivity
qwen-claude provider test
```

### Tool Execution
```bash
# List available tools
qwen-claude tool list

# Run a specific tool
qwen-claude tool run file-read --params '{"path": "/etc/hosts"}'
```

## 📊 Binary Information

### Build Details
- **Build Tool**: pkg (Node.js binary packaging)
- **Node.js Version**: 18.x
- **Bundle Format**: CommonJS
- **Compression**: None (for faster startup)

### Dependencies Included
- Commander.js (CLI framework)
- Chalk (colored output)
- Axios (HTTP requests)
- Inquirer (interactive prompts)
- All internal packages (core, providers, tools, utils)

### External Dependencies
The following are included as Node.js built-ins:
- `fs`, `path`, `os`, `crypto`
- `child_process`, `readline`, `stream`
- `http`, `https`, `net`, `tls`

## 🐛 Troubleshooting

### Linux Issues

1. **Permission Denied**:
   ```bash
   chmod +x qwen-claude-linux
   ```

2. **Library Missing (glibc)**:
   - Ensure your system has glibc 2.17 or newer
   - Most modern distributions should work

3. **Command Not Found**:
   - Check if the binary is in your PATH
   - Verify the file is executable

### Windows Issues

1. **Windows Defender/Antivirus**:
   - The binary might be flagged as unknown software
   - Add it to your antivirus whitelist if needed

2. **Access Denied**:
   - Run Command Prompt as Administrator for installation
   - Or install to user directory instead of Program Files

3. **DLL Issues**:
   - Ensure you have Visual C++ Redistributable installed
   - The binary includes Node.js runtime, so no additional Node.js installation needed

## 🔄 Updates

To update to a newer version:

1. Download the new binary
2. Replace the existing binary
3. Run `qwen-claude --version` to verify

Configuration files are generally backward compatible.

## 📝 Build Information

These binaries were built with:
- **Source**: TypeScript monorepo with 5 packages
- **Target**: Node.js 18.x for maximum compatibility
- **Bundle Size**: 2.3 MB (before packaging)
- **Final Size**: 39-47 MB (includes Node.js runtime)

For development or custom builds, see the main README.md file.

## 🆘 Support

If you encounter issues:

1. Check this troubleshooting guide
2. Verify your system meets the requirements
3. Review the main documentation
4. Check the GitHub repository for known issues

## 📄 License

This software is licensed under the MIT License. See LICENSE file for details.