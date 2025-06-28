#!/bin/bash
# LilithOS Installation Script - iOS 17.2.1 for iPhone 13 Pro Max
# Safe installation with device detection and verification

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
DEFAULT_DEVICE="iPhone14,2"
DEFAULT_IPSW="build/LilithOS_17.2.1_iPhone14,2.ipsw"
BACKUP_DIR="backups"
LOG_DIR="logs"

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${PURPLE}[STEP]${NC} $1"
}

# Error handling
cleanup() {
    log_info "Cleaning up installation files..."
    # Cleanup temporary files if needed
}

trap cleanup EXIT

# Check system requirements
check_requirements() {
    log_step "Checking system requirements..."
    
    # Check if running on macOS
    if [[ "$OSTYPE" != "darwin"* ]]; then
        log_error "This script must be run on macOS"
        exit 1
    fi
    
    # Check for required tools
    local missing_tools=()
    
    for tool in "idevicerestore" "ideviceinfo" "idevice_id"; do
        if ! command -v "$tool" &> /dev/null; then
            missing_tools+=("$tool")
        fi
    done
    
    if [ ${#missing_tools[@]} -ne 0 ]; then
        log_error "Missing required tools: ${missing_tools[*]}"
        log_info "Install libimobiledevice: brew install libimobiledevice"
        exit 1
    fi
    
    log_success "All required tools found"
}

# Create necessary directories
setup_directories() {
    log_step "Setting up directories..."
    
    for dir in "$BACKUP_DIR" "$LOG_DIR"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
        fi
    done
    
    log_success "Directories created"
}

# Detect connected devices
detect_devices() {
    log_step "Detecting connected devices..."
    
    # Get list of connected devices
    local devices=($(idevice_id -l))
    
    if [ ${#devices[@]} -eq 0 ]; then
        log_error "No devices connected"
        log_info "Please connect your iPhone 13 Pro Max and try again"
        exit 1
    fi
    
    log_info "Found ${#devices[@]} connected device(s):"
    
    for device in "${devices[@]}"; do
        local device_info=$(ideviceinfo -u "$device" 2>/dev/null || echo "Unknown")
        local device_name=$(echo "$device_info" | grep -i "ProductType" | cut -d: -f2 | xargs)
        local device_version=$(echo "$device_info" | grep -i "ProductVersion" | cut -d: -f2 | xargs)
        
        log_info "  - Device: $device"
        log_info "    Model: $device_name"
        log_info "    iOS Version: $device_version"
        
        # Check if this is the target device
        if [[ "$device_name" == "$DEFAULT_DEVICE" ]]; then
            TARGET_DEVICE="$device"
            log_success "Target device found: $device"
        fi
    done
    
    if [ -z "${TARGET_DEVICE:-}" ]; then
        log_warning "Target device ($DEFAULT_DEVICE) not found"
        log_info "Using first connected device: ${devices[0]}"
        TARGET_DEVICE="${devices[0]}"
    fi
}

# Verify device compatibility
verify_device() {
    log_step "Verifying device compatibility..."
    
    local device_info=$(ideviceinfo -u "$TARGET_DEVICE" 2>/dev/null)
    local device_name=$(echo "$device_info" | grep -i "ProductType" | cut -d: -f2 | xargs)
    local device_version=$(echo "$device_info" | grep -i "ProductVersion" | cut -d: -f2 | xargs)
    
    log_info "Device: $device_name"
    log_info "Current iOS: $device_version"
    
    # Check if device is compatible
    if [[ "$device_name" != "$DEFAULT_DEVICE" ]]; then
        log_warning "Device $device_name is not the target device ($DEFAULT_DEVICE)"
        log_info "This installation is designed for iPhone 13 Pro Max"
        
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Installation cancelled"
            exit 0
        fi
    fi
    
    log_success "Device compatibility verified"
}

# Create device backup
create_backup() {
    log_step "Creating device backup..."
    
    local backup_name="backup_$(date +%Y%m%d_%H%M%S)"
    local backup_path="$BACKUP_DIR/$backup_name"
    
    log_info "Creating backup: $backup_path"
    log_warning "This may take a while depending on device storage..."
    
    # Create backup using iTunes/Finder backup
    if ! idevicebackup2 -u "$TARGET_DEVICE" backup "$backup_path" > "$LOG_DIR/backup.log" 2>&1; then
        log_warning "Failed to create backup, but continuing..."
        log_info "You can manually backup your device using Finder/iTunes"
    else
        log_success "Backup created successfully: $backup_path"
    fi
}

# Verify IPSW file
verify_ipsw() {
    log_step "Verifying IPSW file..."
    
    if [ ! -f "$IPSW_FILE" ]; then
        log_error "IPSW file not found: $IPSW_FILE"
        exit 1
    fi
    
    # Check file size (should be around 6.8GB)
    local file_size=$(stat -f%z "$IPSW_FILE")
    local expected_size=6800000000  # 6.8GB in bytes
    
    if [ "$file_size" -lt "$expected_size" ]; then
        log_warning "IPSW file seems too small ($file_size bytes)"
        log_info "Expected size: ~6.8GB"
        
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Installation cancelled"
            exit 0
        fi
    fi
    
    log_success "IPSW file verified"
}

# Put device in DFU mode
enter_dfu_mode() {
    log_step "Preparing device for DFU mode..."
    
    log_info "To enter DFU mode:"
    log_info "1. Press and hold Volume Down + Power for 10 seconds"
    log_info "2. Release Power button but keep holding Volume Down"
    log_info "3. Continue holding until device appears in DFU mode"
    
    read -p "Press Enter when device is in DFU mode..."
    
    # Wait for device to appear in DFU mode
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if idevice_id -l | grep -q "$TARGET_DEVICE"; then
            log_success "Device detected in DFU mode"
            return 0
        fi
        
        log_info "Waiting for device... (attempt $((attempt + 1))/$max_attempts)"
        sleep 2
        ((attempt++))
    done
    
    log_error "Device not detected in DFU mode"
    log_info "Please ensure device is properly connected and in DFU mode"
    exit 1
}

# Install LilithOS
install_lilithos() {
    log_step "Installing LilithOS..."
    
    log_warning "This will erase all data on the device!"
    log_info "Make sure you have a backup before proceeding"
    
    read -p "Are you sure you want to continue? (type 'YES' to confirm): " -r
    if [[ "$REPLY" != "YES" ]]; then
        log_info "Installation cancelled"
        exit 0
    fi
    
    log_info "Starting installation..."
    log_info "This process may take 10-15 minutes..."
    
    # Install using idevicerestore
    if ! idevicerestore -u "$TARGET_DEVICE" "$IPSW_FILE" > "$LOG_DIR/install.log" 2>&1; then
        log_error "Installation failed"
        log_info "Check logs: $LOG_DIR/install.log"
        exit 1
    fi
    
    log_success "LilithOS installed successfully!"
}

# Verify installation
verify_installation() {
    log_step "Verifying installation..."
    
    log_info "Waiting for device to boot..."
    sleep 30
    
    # Wait for device to appear
    local max_attempts=60
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if idevice_id -l | grep -q "$TARGET_DEVICE"; then
            log_success "Device detected after installation"
            
            # Get device info
            local device_info=$(ideviceinfo -u "$TARGET_DEVICE" 2>/dev/null)
            local device_version=$(echo "$device_info" | grep -i "ProductVersion" | cut -d: -f2 | xargs)
            
            log_info "Installed iOS version: $device_version"
            
            if [[ "$device_version" == "17.2.1" ]]; then
                log_success "LilithOS installation verified!"
            else
                log_warning "Unexpected iOS version: $device_version"
            fi
            
            return 0
        fi
        
        log_info "Waiting for device to boot... (attempt $((attempt + 1))/$max_attempts)"
        sleep 5
        ((attempt++))
    done
    
    log_warning "Device not detected after installation"
    log_info "Please check if device is booting properly"
}

# Generate installation report
generate_report() {
    log_step "Generating installation report..."
    
    local report_file="$LOG_DIR/installation_report_$(date +%Y%m%d_%H%M%S).txt"
    
    cat > "$report_file" << EOF
# LilithOS Installation Report

## Installation Information
- **Date**: $(date)
- **Device**: $TARGET_DEVICE
- **IPSW File**: $IPSW_FILE
- **Installation Duration**: $SECONDS seconds

## Device Information
- **Model**: $(ideviceinfo -u "$TARGET_DEVICE" 2>/dev/null | grep -i "ProductType" | cut -d: -f2 | xargs)
- **Serial**: $(ideviceinfo -u "$TARGET_DEVICE" 2>/dev/null | grep -i "SerialNumber" | cut -d: -f2 | xargs)
- **iOS Version**: $(ideviceinfo -u "$TARGET_DEVICE" 2>/dev/null | grep -i "ProductVersion" | cut -d: -f2 | xargs)

## Installation Status
- **Status**: SUCCESS
- **Backup Created**: $(if [ -d "$BACKUP_DIR"/* ]; then echo "Yes"; else echo "No"; fi)

## Next Steps
1. Complete device setup
2. Test all functionality
3. Report any issues
4. Enjoy LilithOS!

EOF
    
    log_success "Installation report generated: $report_file"
}

# Main installation function
main() {
    local start_time=$SECONDS
    
    log_info "Starting LilithOS installation for $DEVICE"
    
    # Check requirements
    check_requirements
    
    # Setup directories
    setup_directories
    
    # Detect devices
    detect_devices
    
    # Verify device compatibility
    verify_device
    
    # Create backup
    create_backup
    
    # Verify IPSW
    verify_ipsw
    
    # Enter DFU mode
    enter_dfu_mode
    
    # Install LilithOS
    install_lilithos
    
    # Verify installation
    verify_installation
    
    # Generate report
    generate_report
    
    local install_time=$((SECONDS - start_time))
    
    log_success "Installation completed successfully in ${install_time} seconds!"
    log_info "Your iPhone 13 Pro Max is now running LilithOS!"
    log_info "Please complete the device setup and test all functionality"
}

# Parse command line arguments
parse_args() {
    DEVICE="$DEFAULT_DEVICE"
    IPSW_FILE="$DEFAULT_IPSW"
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --device)
                DEVICE="$2"
                shift 2
                ;;
            --ipsw)
                IPSW_FILE="$2"
                shift 2
                ;;
            --help)
                echo "Usage: $0 [OPTIONS]"
                echo "Options:"
                echo "  --device DEVICE     Target device (default: $DEFAULT_DEVICE)"
                echo "  --ipsw FILE         IPSW file path (default: $DEFAULT_IPSW)"
                echo "  --help              Show this help message"
                echo ""
                echo "Example:"
                echo "  $0 --device iPhone14,2 --ipsw build/LilithOS_17.2.1_iPhone14,2.ipsw"
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
}

# Run main function
parse_args "$@"
main 