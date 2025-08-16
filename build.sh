#!/bin/bash

# Plato AI Orchestration System - Build Script
# This script builds the Plato binary using PyInstaller

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored messages
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

print_header() {
    echo
    print_message $BLUE "================================================"
    print_message $BLUE "         Plato AI Binary Builder"
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

# Check dependencies
check_dependencies() {
    print_message $BLUE "Checking dependencies..."
    
    # Check Python
    if ! command -v python3 >/dev/null 2>&1; then
        print_error "Python 3 is not installed"
        exit 1
    fi
    print_success "Python 3 found"
    
    # Check pip
    if ! command -v pip >/dev/null 2>&1 && ! command -v pip3 >/dev/null 2>&1; then
        print_error "pip is not installed"
        exit 1
    fi
    print_success "pip found"
    
    # Check PyInstaller
    if ! python3 -c "import PyInstaller" 2>/dev/null; then
        print_warning "PyInstaller not found, installing..."
        pip install pyinstaller
        print_success "PyInstaller installed"
    else
        print_success "PyInstaller found"
    fi
}

# Check project files
check_project_files() {
    print_message $BLUE "Checking project files..."
    
    local required_files=(
        "plato_launcher.py"
        "plato.spec"
        "plato/__init__.py"
        "plato/cli.py"
        "plato/interactive_cli.py"
        "pyproject.toml"
    )
    
    for file in "${required_files[@]}"; do
        if [[ ! -f "$file" ]]; then
            print_error "Required file not found: $file"
            exit 1
        fi
    done
    
    print_success "All required files found"
}

# Install Plato package in development mode
install_package() {
    print_message $BLUE "Installing Plato package in development mode..."
    
    if pip install -e . >/dev/null 2>&1; then
        print_success "Plato package installed"
    else
        print_error "Failed to install Plato package"
        exit 1
    fi
}

# Clean previous builds
clean_build() {
    print_message $BLUE "Cleaning previous builds..."
    
    if [[ -d "build" ]]; then
        rm -rf build
        print_success "Removed build directory"
    fi
    
    if [[ -d "dist" ]]; then
        rm -rf dist
        print_success "Removed dist directory"
    fi
    
    if [[ -f "plato.spec.bak" ]]; then
        rm -f plato.spec.bak
        print_success "Removed backup spec file"
    fi
}

# Build the binary
build_binary() {
    print_message $BLUE "Building Plato binary with PyInstaller..."
    echo
    
    if pyinstaller plato.spec --clean --noconfirm; then
        echo
        print_success "Binary built successfully"
    else
        echo
        print_error "Failed to build binary"
        exit 1
    fi
}

# Test the binary
test_binary() {
    print_message $BLUE "Testing the binary..."
    
    local binary_path="./dist/plato"
    
    if [[ ! -f "$binary_path" ]]; then
        print_error "Binary not found at $binary_path"
        exit 1
    fi
    
    if [[ ! -x "$binary_path" ]]; then
        print_error "Binary is not executable"
        exit 1
    fi
    
    # Test version command
    if "$binary_path" --version >/dev/null 2>&1; then
        print_success "Version command works"
    else
        print_error "Version command failed"
        exit 1
    fi
    
    # Test help command
    if "$binary_path" --help >/dev/null 2>&1; then
        print_success "Help command works"
    else
        print_error "Help command failed"
        exit 1
    fi
    
    print_success "Binary tests passed"
}

# Show build information
show_build_info() {
    local binary_path="./dist/plato"
    local size=$(du -h "$binary_path" | cut -f1)
    
    echo
    print_message $GREEN "================================================"
    print_message $GREEN "           Build completed successfully!"
    print_message $GREEN "================================================"
    echo
    print_message $BLUE "Binary location: $binary_path"
    print_message $BLUE "Binary size: $size"
    echo
    print_message $YELLOW "To install system-wide, run:"
    print_message $YELLOW "  ./install.sh"
    echo
    print_message $YELLOW "To test locally, run:"
    print_message $YELLOW "  ./dist/plato --help"
    print_message $YELLOW "  ./dist/plato --version"
    echo
}

# Handle command line arguments
CLEAN_ONLY=false
SKIP_TESTS=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --clean)
            CLEAN_ONLY=true
            shift
            ;;
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        --help|-h)
            echo "Plato Binary Builder"
            echo
            echo "Usage: $0 [options]"
            echo
            echo "Options:"
            echo "  --clean       Only clean build directories and exit"
            echo "  --skip-tests  Skip binary testing"
            echo "  --help        Show this help message"
            echo
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            print_message $YELLOW "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Main build process
main() {
    print_header
    
    if [[ "$CLEAN_ONLY" == true ]]; then
        clean_build
        print_message $GREEN "Clean completed"
        exit 0
    fi
    
    print_message $BLUE "Starting Plato binary build process..."
    echo
    
    # Pre-build checks
    check_dependencies
    check_project_files
    
    # Preparation
    install_package
    clean_build
    
    echo
    
    # Build
    build_binary
    
    echo
    
    # Post-build
    if [[ "$SKIP_TESTS" != true ]]; then
        test_binary
    else
        print_warning "Skipping binary tests"
    fi
    
    show_build_info
}

# Run main function
main "$@"