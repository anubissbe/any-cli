# Qwen Claude CLI v0.1.0

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
```bash
# Download and extract the release
# Run the installation script
chmod +x install.sh
./install.sh
```

#### Windows
```cmd
REM Download and extract the release
REM Run the installation script
install.bat
```

### 📋 Files Included
- `qwen-claude-linux` - Linux x64 binary
- `qwen-claude-windows.exe` - Windows x64 binary
- `README.md` - Main documentation
- `BINARY_DISTRIBUTION.md` - Binary-specific documentation
- `QUICK_REFERENCE.md` - Quick reference guide
- `LICENSE` - MIT license
- `install.sh` - Linux/macOS installation script
- `install.bat` - Windows installation script
- `checksums.json` - SHA256 checksums for verification

### 🔐 Verification
Use the provided checksums to verify binary integrity:
```bash
sha256sum -c checksums.json
```

### 📖 Documentation
See `BINARY_DISTRIBUTION.md` for detailed installation and usage instructions.

### 🆘 Support
For issues or questions, please refer to the documentation or create an issue in the repository.
