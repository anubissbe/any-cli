#!/bin/bash

# Plato AI Orchestration System - Uninstallation Script
# This script removes the Plato binary from the system

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
    print_message $BLUE "    Plato AI Orchestration System Uninstaller"
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

# Check if Plato is installed
check_installation() {
    if [[ ! -f "$TARGET_PATH" ]]; then
        print_warning "Plato is not installed at $TARGET_PATH"
        print_message $YELLOW "Nothing to uninstall."
        exit 0
    fi
    
    print_success "Found Plato installation at $TARGET_PATH"
}

# Show what will be removed
show_removal_info() {
    echo
    print_message $BLUE "The following will be removed:"
    echo
    print_message $YELLOW "  Binary: $TARGET_PATH"
    
    if [[ -f "$TARGET_PATH" ]]; then
        local size=$(du -h "$TARGET_PATH" | cut -f1)
        print_message $YELLOW "  Size: $size"
    fi
    
    echo
}

# Confirm uninstallation
confirm_uninstall() {
    read -p "Are you sure you want to uninstall Plato? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_message $YELLOW "Uninstallation cancelled"
        exit 0
    fi
}

# Remove the binary
remove_binary() {
    print_message $BLUE "Removing Plato binary..."
    
    if sudo rm -f "$TARGET_PATH"; then
        print_success "Binary removed from $TARGET_PATH"
    else
        print_error "Failed to remove binary from $TARGET_PATH"
        exit 1
    fi
}

# Verify removal
verify_removal() {
    print_message $BLUE "Verifying removal..."
    
    # Check if binary still exists
    if [[ -f "$TARGET_PATH" ]]; then
        print_error "Binary still exists at $TARGET_PATH"
        return 1
    else
        print_success "Binary successfully removed"
    fi
    
    # Check if binary is still in PATH
    if command -v plato >/dev/null 2>&1; then
        print_warning "Plato command still found in PATH"
        print_message $YELLOW "This might be another installation or a cached entry"
        print_message $YELLOW "Try restarting your shell or running 'hash -r'"
        return 1
    else
        print_success "Plato command no longer in PATH"
    fi
    
    return 0
}

# Show completion message
show_completion() {
    echo
    print_message $GREEN "================================================"
    print_message $GREEN "    Uninstallation completed successfully!"
    print_message $GREEN "================================================"
    echo
    print_message $BLUE "Plato has been removed from your system."
    echo
    print_message $YELLOW "Note: If you have other Plato installations or"
    print_message $YELLOW "configurations, they were not affected."
    echo
    print_message $BLUE "To reinstall Plato later, run:"
    print_message $YELLOW "  ./install.sh"
    echo
}

# Clean up shell cache (optional)
cleanup_shell() {
    print_message $BLUE "Cleaning up shell cache..."
    
    # Clear bash command hash
    if command -v hash >/dev/null 2>&1; then
        hash -r 2>/dev/null || true
        print_success "Cleared command hash"
    fi
    
    print_message $YELLOW "You may need to restart your shell for changes to take full effect"
}

# Main uninstallation process
main() {
    print_header
    
    print_message $BLUE "Starting Plato uninstallation process..."
    echo
    
    # Pre-uninstallation checks
    check_root
    check_installation
    
    # Show what will be removed
    show_removal_info
    
    # Confirm with user
    confirm_uninstall
    
    echo
    print_message $BLUE "Proceeding with uninstallation..."
    echo
    
    # Uninstallation
    remove_binary
    
    echo
    
    # Post-uninstallation
    if verify_removal; then
        cleanup_shell
        show_completion
    else
        print_error "Uninstallation completed but verification failed"
        print_message $YELLOW "Some components may still be present"
        print_message $YELLOW "Please check manually or contact support"
        exit 1
    fi
}

# Handle command line arguments
case "${1:-}" in
    --force)
        # Skip confirmation for automated usage
        confirm_uninstall() { return 0; }
        shift
        ;;
    --help|-h)
        echo "Plato Uninstaller"
        echo
        echo "Usage: $0 [options]"
        echo
        echo "Options:"
        echo "  --force    Skip confirmation prompt"
        echo "  --help     Show this help message"
        echo
        exit 0
        ;;
esac

# Run main function
main "$@"