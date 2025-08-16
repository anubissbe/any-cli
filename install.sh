#!/bin/bash

# Plato AI Orchestration System - Installation Script
# This script installs the Plato binary to make it available system-wide

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BINARY_NAME="plato"
INSTALL_DIR="/usr/local/bin"
BINARY_PATH="./dist/$BINARY_NAME"
TARGET_PATH="$INSTALL_DIR/$BINARY_NAME"

# Function to print colored messages
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

print_header() {
    echo
    print_message $BLUE "================================================"
    print_message $BLUE "    Plato AI Orchestration System Installer"
    print_message $BLUE "================================================"
    echo
}

print_success() {
    print_message $GREEN "✓ $1"
}

print_warning() {
    print_message $YELLOW "⚠ $1"
}

print_error() {
    print_message $RED "✗ $1"
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_error "This script should not be run as root!"
        print_message $YELLOW "Please run without sudo. The script will ask for privileges when needed."
        exit 1
    fi
}

# Check if binary exists
check_binary() {
    if [[ ! -f "$BINARY_PATH" ]]; then
        print_error "Binary not found at $BINARY_PATH"
        print_message $YELLOW "Please run 'pyinstaller plato.spec' first to build the binary"
        exit 1
    fi
    
    if [[ ! -x "$BINARY_PATH" ]]; then
        print_error "Binary at $BINARY_PATH is not executable"
        exit 1
    fi
    
    print_success "Found Plato binary at $BINARY_PATH"
}

# Check if target directory exists and is writable
check_install_dir() {
    if [[ ! -d "$INSTALL_DIR" ]]; then
        print_error "Installation directory $INSTALL_DIR does not exist"
        exit 1
    fi
    
    print_success "Installation directory $INSTALL_DIR exists"
}

# Check if binary is already installed
check_existing() {
    if [[ -f "$TARGET_PATH" ]]; then
        print_warning "Plato is already installed at $TARGET_PATH"
        read -p "Do you want to overwrite it? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_message $YELLOW "Installation cancelled"
            exit 0
        fi
    fi
}

# Install the binary
install_binary() {
    print_message $BLUE "Installing Plato binary..."
    
    # Copy the binary (requires sudo)
    if sudo cp "$BINARY_PATH" "$TARGET_PATH"; then
        print_success "Binary copied to $TARGET_PATH"
    else
        print_error "Failed to copy binary to $TARGET_PATH"
        exit 1
    fi
    
    # Set executable permissions
    if sudo chmod +x "$TARGET_PATH"; then
        print_success "Set executable permissions"
    else
        print_error "Failed to set executable permissions"
        exit 1
    fi
    
    # Set ownership to root
    if sudo chown root:root "$TARGET_PATH"; then
        print_success "Set ownership to root:root"
    else
        print_error "Failed to set ownership"
        exit 1
    fi
}

# Test the installation
test_installation() {
    print_message $BLUE "Testing installation..."
    
    # Check if binary exists at target location
    if [[ -f "$TARGET_PATH" ]]; then
        print_success "Binary installed at $TARGET_PATH"
    else
        print_error "Binary not found at $TARGET_PATH"
        return 1
    fi
    
    # Check if binary is executable
    if [[ -x "$TARGET_PATH" ]]; then
        print_success "Binary is executable"
    else
        print_error "Binary is not executable"
        return 1
    fi
    
    # Test version command using the specific installed binary
    if "$TARGET_PATH" --version >/dev/null 2>&1; then
        print_success "Version command works"
    else
        print_error "Version command failed"
        return 1
    fi
    
    # Test help command using the specific installed binary
    if "$TARGET_PATH" --help >/dev/null 2>&1; then
        print_success "Help command works"
    else
        print_error "Help command failed"
        return 1
    fi
    
    # Check if binary is in PATH (informational only)
    if command -v plato >/dev/null 2>&1; then
        local found_path=$(which plato)
        if [[ "$found_path" == "$TARGET_PATH" ]]; then
            print_success "Plato is available in PATH and points to the correct installation"
        else
            print_warning "Plato is in PATH but points to $found_path"
            print_message $YELLOW "The system installation is at $TARGET_PATH"
            print_message $YELLOW "You may have multiple Plato installations"
        fi
    else
        print_warning "Plato is not found in PATH"
        print_message $YELLOW "You may need to restart your shell or add $INSTALL_DIR to your PATH"
    fi
    
    return 0
}

# Create uninstall information
create_uninstall_info() {
    local uninstall_script="./uninstall.sh"
    
    if [[ -f "$uninstall_script" ]]; then
        print_success "Uninstall script already exists at $uninstall_script"
    else
        print_warning "Uninstall script not found. Please keep the uninstall.sh script for future removal."
    fi
}

# Show post-installation information
show_completion() {
    echo
    print_message $GREEN "================================================"
    print_message $GREEN "    Installation completed successfully!"
    print_message $GREEN "================================================"
    echo
    print_message $BLUE "You can now use Plato from anywhere by typing:"
    echo
    print_message $YELLOW "  plato                    # Start interactive interface"
    print_message $YELLOW "  plato --help             # Show help"
    print_message $YELLOW "  plato health             # Check server health"
    print_message $YELLOW "  plato chat \"Hello\"       # Send single message"
    echo
    print_message $BLUE "To uninstall Plato later, run:"
    print_message $YELLOW "  ./uninstall.sh"
    echo
    print_message $BLUE "Binary installed at: $TARGET_PATH"
    print_message $BLUE "Binary size: $(du -h "$TARGET_PATH" | cut -f1)"
    echo
}

# Main installation process
main() {
    print_header
    
    print_message $BLUE "Starting Plato installation process..."
    echo
    
    # Pre-installation checks
    check_root
    check_binary
    check_install_dir
    check_existing
    
    echo
    print_message $BLUE "All checks passed. Proceeding with installation..."
    echo
    
    # Installation
    install_binary
    
    echo
    
    # Post-installation
    if test_installation; then
        create_uninstall_info
        show_completion
    else
        print_error "Installation completed but testing failed"
        print_message $YELLOW "The binary was installed but may not work correctly"
        print_message $YELLOW "Try running 'plato --help' manually to test"
        exit 1
    fi
}

# Run main function
main "$@"