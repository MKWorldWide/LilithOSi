#!/bin/bash

# LilithOS Creator Script
# This script automates the entire process of creating a custom LilithOS IPSW

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Function to print status messages
print_status() {
    echo -e "${GREEN}[*]${NC} $1"
}

# Function to print error messages
print_error() {
    echo -e "${RED}[!]${NC} $1"
}

# Function to print warning messages
print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Check if running on macOS
check_os() {
    if [[ "$OSTYPE" != "darwin"* ]]; then
        print_error "This script must be run on macOS"
        exit 1
    fi
}

# Install dependencies
install_dependencies() {
    print_status "Installing dependencies..."
    
    # Check if Homebrew is installed
    if ! command -v brew &> /dev/null; then
        print_status "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    
    # Install required packages
    print_status "Installing required packages..."
    brew install libimobiledevice
    pip3 install Pillow imageio
    
    # Install Xcode Command Line Tools if not present
    if ! xcode-select -p &> /dev/null; then
        print_status "Installing Xcode Command Line Tools..."
        xcode-select --install
    fi
}

# Create necessary directories
setup_directories() {
    print_status "Setting up project structure..."
    mkdir -p build resources tools src/{kernel,system,patches}
}

# Copy base IPSW
copy_base_ipsw() {
    print_status "Copying base IPSW..."
    if [ ! -f "iPhone4,1_9.3.6_13G37_Restore.ipsw" ]; then
        print_error "Base IPSW not found. Please place iPhone4,1_9.3.6_13G37_Restore.ipsw in the current directory."
        exit 1
    fi
}

# Build LilithOS
build_lilithos() {
    print_status "Building LilithOS..."
    chmod +x scripts/build_ipsw.sh
    ./scripts/build_ipsw.sh
}

# Main execution
main() {
    print_status "Starting LilithOS creation process..."
    
    check_os
    install_dependencies
    setup_directories
    copy_base_ipsw
    build_lilithos
    
    print_status "LilithOS creation completed!"
    print_status "You can find the custom IPSW in the build directory."
    print_status "To install LilithOS, run: ./scripts/install.sh"
}

# Run main function
main 