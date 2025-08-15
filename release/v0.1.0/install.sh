#!/bin/bash
set -e

# Qwen Claude CLI Installation Script
# Version: 0.1.0

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
  echo "   echo 'export PATH="\$HOME/.local/bin:\$PATH"' >> ~/.bashrc"
  echo "   source ~/.bashrc"
fi

echo ""
echo "🎉 Installation complete!"
echo "Run 'qwen-claude --help' to get started."
