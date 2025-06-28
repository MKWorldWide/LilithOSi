# LilithOS Quick Start Guide

## 🚀 Getting Started with LilithOS for iPhone 13 Pro Max

This guide will help you quickly set up and build LilithOS for your iPhone 13 Pro Max.

## 📋 Prerequisites

### System Requirements
- **macOS**: 13.0 or later (Ventura+)
- **Xcode**: 15.0 or later
- **Python**: 3.9 or later
- **RAM**: 16GB minimum (32GB recommended)
- **Storage**: 50GB free space
- **Internet**: Stable connection for downloads

### Apple Developer Requirements
- **Apple Developer Account**: Active paid membership
- **Device Registration**: iPhone 13 Pro Max registered for development
- **Certificates**: Code signing and provisioning profiles

## ⚡ Quick Setup

### 1. Clone the Repository
```bash
git clone https://github.com/your-org/LilithOS.git
cd LilithOS
```

### 2. Install Dependencies
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install system tools (macOS)
brew install libimobiledevice
```

### 3. Download Base IPSW
```bash
# Download iOS 17.2.1 for iPhone 13 Pro Max
python tools/download_ipsw.py --device iPhone14,2 --version 17.2.1
```

### 4. Build LilithOS
```bash
# Build the custom firmware
./scripts/build.sh

# Or with custom options
./scripts/build.sh --device iPhone14,2 --version 17.2.1
```

### 5. Test the Build
```bash
# Run comprehensive tests
python tools/test_framework.py --device iPhone14,2 --test all
```

## 📱 Installation

### Prerequisites
- iPhone 13 Pro Max with backup
- USB-C or Lightning cable
- Valid Apple Developer account

### Installation Steps

#### 1. Prepare Your Device
```bash
# Connect your iPhone 13 Pro Max
# Ensure it's unlocked and trusted
```

#### 2. Create Backup
```bash
# The installation script will create a backup automatically
# Or manually backup using Finder/iTunes
```

#### 3. Install LilithOS
```bash
# Install the custom firmware
./scripts/install.sh --device iPhone14,2 --ipsw build/LilithOS_17.2.1_iPhone14,2.ipsw
```

#### 4. Follow DFU Instructions
The script will guide you through entering DFU mode:
1. Press and hold Volume Down + Power for 10 seconds
2. Release Power button but keep holding Volume Down
3. Continue holding until device appears in DFU mode

## 🛠️ Development Workflow

### Building Custom Modifications

#### 1. Kernel Modifications
```bash
# Edit kernel patches
nano src/kernel/patches.c

# Rebuild with kernel changes
./scripts/build.sh --no-tests
```

#### 2. System Modifications
```bash
# Edit system daemons
nano src/system/modifications.plist

# Rebuild with system changes
./scripts/build.sh
```

#### 3. Boot Animation
```bash
# Generate custom boot animation
python src/system/boot_animation.py --fps 120 --duration 3.2

# Rebuild with new animation
./scripts/build.sh
```

### Testing Your Changes

#### 1. Run Specific Tests
```bash
# Test boot process
python tools/test_framework.py --test boot --device iPhone14,2

# Test kernel modifications
python tools/test_framework.py --test kernel --device iPhone14,2

# Test system services
python tools/test_framework.py --test system --device iPhone14,2
```

#### 2. Performance Testing
```bash
# Test performance metrics
python tools/test_framework.py --test performance --device iPhone14,2

# Test security features
python tools/test_framework.py --test security --device iPhone14,2
```

## 🔧 Advanced Configuration

### Custom Build Options
```bash
# Build for specific device
./scripts/build.sh --device iPhone14,2

# Build with custom iOS version
./scripts/build.sh --version 17.2.1

# Build without signing (for testing)
./scripts/build.sh --no-sign

# Build without tests
./scripts/build.sh --no-tests
```

### Custom Installation Options
```bash
# Install with custom IPSW
./scripts/install.sh --ipsw custom.ipsw

# Install on specific device
./scripts/install.sh --device iPhone14,2

# Skip backup (not recommended)
./scripts/install.sh --no-backup
```

## 📊 Monitoring and Debugging

### View Build Logs
```bash
# View build logs
tail -f logs/build.log

# View installation logs
tail -f logs/install.log
```

### Check Device Status
```bash
# List connected devices
idevice_id -l

# Get device information
ideviceinfo -u <device_id>

# Check device logs
idevicesyslog -u <device_id>
```

### Performance Monitoring
```bash
# Monitor system performance
python tools/test_framework.py --test performance --verbose

# Generate performance report
python tools/test_framework.py --test all --output performance_report.json
```

## 🚨 Troubleshooting

### Common Issues

#### Build Failures
```bash
# Check system requirements
python -c "import sys; print(f'Python {sys.version}')"
xcode-select --print-path

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Clean build directory
rm -rf build/ work/
```

#### Installation Failures
```bash
# Check device connection
idevice_id -l

# Verify IPSW file
python tools/download_ipsw.py --verify-only --device iPhone14,2 --version 17.2.1

# Check device compatibility
ideviceinfo -u <device_id> | grep ProductType
```

#### Test Failures
```bash
# Run tests with verbose output
python tools/test_framework.py --test all --verbose

# Check test logs
cat test_report.json

# Run individual test categories
python tools/test_framework.py --test boot --verbose
```

### Getting Help

#### Documentation
- **README.md**: Main project documentation
- **@docs/ARCHITECTURE.md**: Technical architecture
- **@docs/memories.md**: Project progress tracking
- **CHANGELOG.md**: Version history and changes

#### Support Channels
- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and discussions
- **Security Reports**: Private security issues

## 🎯 Next Steps

### For Users
1. **Complete Setup**: Follow the installation guide
2. **Test Functionality**: Verify all features work correctly
3. **Report Issues**: Submit bug reports if needed
4. **Join Community**: Participate in discussions

### For Developers
1. **Fork Repository**: Create your own fork
2. **Make Changes**: Implement new features
3. **Add Tests**: Include tests for new functionality
4. **Submit PR**: Create pull requests for review

### For Contributors
1. **Read Documentation**: Understand the project structure
2. **Follow Guidelines**: Adhere to coding standards
3. **Test Thoroughly**: Ensure changes don't break existing functionality
4. **Update Documentation**: Keep docs in sync with changes

## 📈 Performance Tips

### Build Optimization
- Use SSD storage for faster builds
- Increase RAM allocation for Xcode
- Use multiple CPU cores for parallel builds
- Keep dependencies updated

### Installation Optimization
- Use USB 3.0+ connection
- Close unnecessary applications
- Ensure stable power supply
- Monitor system resources

### Development Workflow
- Use version control for all changes
- Test frequently on actual hardware
- Keep backups of working configurations
- Document all modifications

---

## 🎉 Congratulations!

You've successfully set up LilithOS for iPhone 13 Pro Max! 

### What's Next?
- Explore the custom features
- Test performance optimizations
- Customize the boot animation
- Contribute to the project

### Need Help?
- Check the documentation in `@docs/`
- Join the community discussions
- Report issues on GitHub
- Ask questions in Discussions

---

**💖 Enjoy your custom LilithOS experience!** 