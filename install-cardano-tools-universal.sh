#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Detect system
detect_system() {
    OS=$(uname -s | tr '[:upper:]' '[:lower:]')
    ARCH=$(uname -m)
    
    case $OS in
        "darwin")
            if [ "$ARCH" = "arm64" ] || [ "$ARCH" = "aarch64" ]; then
                SYSTEM="macos-aarch64"
            else
                SYSTEM="macos-x86_64"
            fi
            ;;
        "linux")
            if [ "$ARCH" = "aarch64" ] || [ "$ARCH" = "arm64" ]; then
                SYSTEM="linux-aarch64"
            else
                SYSTEM="linux-x86_64"
            fi
            ;;
        "msys"|"cygwin"|"mingw")
            SYSTEM="windows-x86_64"
            ;;
        *)
            print_error "Unsupported operating system: $OS"
            exit 1
            ;;
    esac
    
    print_info "Detected: $SYSTEM"
}

# Install system dependencies
install_system_deps() {
    print_info "Installing system dependencies..."
    
    case $SYSTEM in
        "macos-"*)
            if command -v brew >/dev/null 2>&1; then
                print_info "Using Homebrew to install dependencies..."
                brew install curl jq || print_warning "Some dependencies may not be available"
            else
                print_warning "Homebrew not found. Please install manually:"
                print_warning "  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
            fi
            ;;
        "linux-"*)
            if command -v apt-get >/dev/null 2>&1; then
                print_info "Using apt to install dependencies..."
                sudo apt-get update && sudo apt-get install -y curl jq || print_warning "Some dependencies may not be available"
            elif command -v yum >/dev/null 2>&1; then
                print_info "Using yum to install dependencies..."
                sudo yum install -y curl jq || print_warning "Some dependencies may not be available"
            else
                print_warning "Package manager not found. Please install curl and jq manually."
            fi
            ;;
        "windows-"*)
            print_info "Windows detected. Please install dependencies manually:"
            print_warning "  - Download curl from: https://curl.se/windows/"
            print_warning "  - Download jq from: https://stedolan.github.io/jq/download/"
            ;;
    esac
}

# Download and install tool
install_tool() {
    local tool_name=$1
    local url=$2
    local binary_name=$3
    local test_command=$4
    
    print_info "Installing $tool_name..."
    
    # Create temp directory
    TEMP_DIR=$(mktemp -d)
    
    # Download
    print_info "Downloading $tool_name..."
    if curl -L "$url" -o "$TEMP_DIR/$tool_name.tar.gz" --progress-bar; then
        print_success "Downloaded $tool_name archive"
    else
        print_error "Failed to download $tool_name"
        rm -rf "$TEMP_DIR"
        return 1
    fi
    
    # Extract
    if tar -xzf "$TEMP_DIR/$tool_name.tar.gz" -C "$TEMP_DIR" 2>/dev/null; then
        print_success "Extracted $tool_name binary"
    else
        print_error "Failed to extract $tool_name"
        rm -rf "$TEMP_DIR"
        return 1
    fi
    
    # Find and move binary
    BINARY_PATH=$(find "$TEMP_DIR" -name "$binary_name" -type f 2>/dev/null | head -1)
    if [ -n "$BINARY_PATH" ]; then
        mv "$BINARY_PATH" "$TOOLS_DIR/$binary_name"
        chmod +x "$TOOLS_DIR/$binary_name"
        print_success "Made $binary_name executable"
    else
        # Try to find any cardano-cli binary
        CARDANO_BINARY=$(find "$TEMP_DIR" -name "*cardano-cli*" -type f 2>/dev/null | head -1)
        if [ -n "$CARDANO_BINARY" ]; then
            mv "$CARDANO_BINARY" "$TOOLS_DIR/$binary_name"
            chmod +x "$TOOLS_DIR/$binary_name"
            print_success "Made $binary_name executable (renamed from $(basename "$CARDANO_BINARY")"
        else
            print_error "Could not find $binary_name binary in archive"
            rm -rf "$TEMP_DIR"
            return 1
        fi
    fi
    
    # Test the tool
    print_info "Testing $tool_name..."
    if [ "$SYSTEM" = "macos-aarch64" ] && [ "$tool_name" = "cardano-cli" ]; then
        # Skip version test for cardano-cli on ARM64 macOS (known to crash)
        print_warning "$tool_name version test skipped on ARM64 (known compatibility issue)"
        print_success "$tool_name is installed (version test skipped on ARM64)"
    else
        if "$TOOLS_DIR/$binary_name" $test_command >/dev/null 2>&1; then
            print_success "$tool_name is working"
        else
            print_warning "$tool_name installation may have issues"
        fi
    fi
    
    # Cleanup
    rm -rf "$TEMP_DIR"
}

# Main installation function
main() {
    print_info "Universal Cardano Tools Installation"
    print_info "===================================="
    
    # Detect system
    detect_system
    
    # Create tools directory
    TOOLS_DIR="$HOME/.cardano_spo_cli/tools"
    mkdir -p "$TOOLS_DIR"
    print_info "Tools directory: $TOOLS_DIR"
    
    # Install system dependencies
    install_system_deps
    
    # Install tools based on system
    case $SYSTEM in
        "macos-aarch64")
            print_info "Installing Cardano tools for macOS ARM64..."
            
            # cardano-cli (may crash on ARM64, but CLI handles it gracefully)
            install_tool "cardano-cli" \
                "https://github.com/IntersectMBO/cardano-cli/releases/download/cardano-cli-10.11.1.0/cardano-cli-10.11.1.0-aarch64-darwin.tar.gz" \
                "cardano-cli" "--version" || print_warning "cardano-cli installation failed"
            
            # cardano-address
            install_tool "cardano-address" \
                "https://github.com/IntersectMBO/cardano-addresses/releases/download/4.0.0/cardano-address-4.0.0-macos.tar.gz" \
                "cardano-address" "--version" || print_warning "cardano-address installation failed"
            
            # bech32 (use Python package instead of binary)
            print_info "Installing bech32 via Python..."
            if command -v pip3 >/dev/null 2>&1; then
                pip3 install bech32 && print_success "bech32 installed via pip"
            elif command -v pip >/dev/null 2>&1; then
                pip install bech32 && print_success "bech32 installed via pip"
            else
                print_warning "pip not found, bech32 will use Python library"
            fi
            
            print_warning "Note: cardano-cli may crash on ARM64 due to missing dependencies"
            print_warning "The CLI will automatically detect and handle this"
            ;;
            
        "macos-x86_64")
            print_info "Installing Cardano tools for macOS x86_64..."
            
            install_tool "cardano-cli" \
                "https://github.com/IntersectMBO/cardano-cli/releases/download/cardano-cli-10.11.1.0/cardano-cli-10.11.1.0-x86_64-darwin.tar.gz" \
                "cardano-cli" "--version" || print_warning "cardano-cli installation failed"
            
            install_tool "cardano-address" \
                "https://github.com/IntersectMBO/cardano-addresses/releases/download/4.0.0/cardano-address-4.0.0-macos.tar.gz" \
                "cardano-address" "--version" || print_warning "cardano-address installation failed"
            
            print_info "Installing bech32 via Python..."
            if command -v pip3 >/dev/null 2>&1; then
                pip3 install bech32 && print_success "bech32 installed via pip"
            elif command -v pip >/dev/null 2>&1; then
                pip install bech32 && print_success "bech32 installed via pip"
            else
                print_warning "pip not found, bech32 will use Python library"
            fi
            ;;
            
        "linux-x86_64")
            print_info "Installing Cardano tools for Linux x86_64..."
            
            install_tool "cardano-cli" \
                "https://github.com/IntersectMBO/cardano-cli/releases/download/cardano-cli-10.11.1.0/cardano-cli-10.11.1.0-x86_64-linux.tar.gz" \
                "cardano-cli" "--version" || print_warning "cardano-cli installation failed"
            
            install_tool "cardano-address" \
                "https://github.com/IntersectMBO/cardano-addresses/releases/download/4.0.0/cardano-address-4.0.0-linux.tar.gz" \
                "cardano-address" "--version" || print_warning "cardano-address installation failed"
            
            print_info "Installing bech32 via Python..."
            if command -v pip3 >/dev/null 2>&1; then
                pip3 install bech32 && print_success "bech32 installed via pip"
            elif command -v pip >/dev/null 2>&1; then
                pip install bech32 && print_success "bech32 installed via pip"
            else
                print_warning "pip not found, bech32 will use Python library"
            fi
            ;;
            
        "linux-aarch64")
            print_info "Installing Cardano tools for Linux ARM64..."
            
            install_tool "cardano-cli" \
                "https://github.com/IntersectMBO/cardano-cli/releases/download/cardano-cli-10.11.1.0/cardano-cli-10.11.1.0-aarch64-linux.tar.gz" \
                "cardano-cli" "--version" || print_warning "cardano-cli installation failed"
            
            install_tool "cardano-address" \
                "https://github.com/IntersectMBO/cardano-addresses/releases/download/4.0.0/cardano-address-4.0.0-linux.tar.gz" \
                "cardano-address" "--version" || print_warning "cardano-address installation failed"
            
            print_info "Installing bech32 via Python..."
            if command -v pip3 >/dev/null 2>&1; then
                pip3 install bech32 && print_success "bech32 installed via pip"
            elif command -v pip >/dev/null 2>&1; then
                pip install bech32 && print_success "bech32 installed via pip"
            else
                print_warning "pip not found, bech32 will use Python library"
            fi
            ;;
            
        "windows-"*)
            print_warning "Windows installation requires manual steps:"
            print_warning "1. Download cardano-cli from: https://github.com/IntersectMBO/cardano-cli/releases"
            print_warning "2. Download cardano-address from: https://github.com/IntersectMBO/cardano-addresses/releases"
            print_warning "3. Install bech32: pip install bech32"
            print_warning "4. Place binaries in: $TOOLS_DIR"
            return 1
            ;;
    esac
    
    # Verify installation
    print_info "Verifying installation..."
    TOOLS_INSTALLED=0
    
    if [ -f "$TOOLS_DIR/cardano-cli" ] && [ -x "$TOOLS_DIR/cardano-cli" ]; then
        print_success "cardano-cli is installed and executable"
        TOOLS_INSTALLED=$((TOOLS_INSTALLED + 1))
    else
        print_warning "cardano-cli is not properly installed"
    fi
    
    if [ -f "$TOOLS_DIR/cardano-address" ] && [ -x "$TOOLS_DIR/cardano-address" ]; then
        print_success "cardano-address is installed and executable"
        TOOLS_INSTALLED=$((TOOLS_INSTALLED + 1))
    else
        print_warning "cardano-address is not properly installed"
    fi
    
    if python3 -c "import bech32" 2>/dev/null || python -c "import bech32" 2>/dev/null; then
        print_success "bech32 is properly installed"
        TOOLS_INSTALLED=$((TOOLS_INSTALLED + 1))
    else
        print_warning "bech32 is not properly installed"
    fi
    
    print_info "Tools installed: $TOOLS_INSTALLED/3"
    
    if [ $TOOLS_INSTALLED -ge 2 ]; then
        print_success "Cardano tools installation completed!"
        print_info "You can now use real tools mode:"
        print_info "  cspocli generate --ticker MYPOOL --purpose pledge"
        print_info ""
        print_info "Or continue using simplified mode:"
        print_info "  cspocli generate --ticker MYPOOL --purpose pledge --simple"
        print_info ""
        print_warning "Note: If some tools failed to install, the CLI will automatically"
        print_warning "fall back to simplified mode when needed."
    else
        print_warning "Some tools failed to install. The CLI will use simplified mode."
        print_info "You can still use the CLI with simplified mode:"
        print_info "  cspocli generate --ticker MYPOOL --purpose pledge --simple"
    fi
}

# Run main function
main "$@" 