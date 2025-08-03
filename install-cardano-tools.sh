#!/bin/bash

# Cardano Tools Installation Script
# Automatically installs all necessary Cardano tools for professional use

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

print_status() {
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

print_header() {
    echo -e "${CYAN}================================${NC}"
    echo -e "${CYAN}  Cardano Tools Installation    ${NC}"
    echo -e "${CYAN}================================${NC}"
    echo ""
}

# Detect OS and architecture
detect_system() {
    OS=$(uname -s | tr '[:upper:]' '[:lower:]')
    ARCH=$(uname -m)
    
    case $OS in
        "darwin")
            OS_NAME="macos"
            ;;
        "linux")
            OS_NAME="linux"
            ;;
        "msys"*|"cygwin"*)
            OS_NAME="windows"
            ;;
        *)
            print_error "Unsupported OS: $OS"
            exit 1
            ;;
    esac
    
    case $ARCH in
        "x86_64")
            ARCH_NAME="x86_64"
            ;;
        "aarch64"|"arm64")
            ARCH_NAME="aarch64"
            ;;
        *)
            print_error "Unsupported architecture: $ARCH"
            exit 1
            ;;
    esac
    
    print_status "Detected: $OS_NAME ($ARCH_NAME)"
}

# Create tools directory
setup_directories() {
    TOOLS_DIR="$HOME/.cardano_spo_cli/tools"
    mkdir -p "$TOOLS_DIR"
    print_status "Tools directory: $TOOLS_DIR"
}

# Download and install tool
install_tool() {
    local tool_name=$1
    local url=$2
    local filename=$3
    local version_check=$4
    
    print_status "Installing $tool_name..."
    
    # Check if URL is a tar.gz file
    if [[ "$url" == *".tar.gz" ]]; then
        # Download and extract tar.gz
        local temp_file="$TOOLS_DIR/${tool_name}_temp.tar.gz"
        if curl -L -f -s -o "$temp_file" "$url"; then
            print_success "Downloaded $tool_name archive"
            
            # Extract the archive
            cd "$TOOLS_DIR"
            tar -xzf "$temp_file" 2>/dev/null || {
                print_error "Failed to extract $tool_name archive"
                rm -f "$temp_file"
                return 1
            }
            rm -f "$temp_file"
            
            # Find the extracted binary (check for various possible names)
            local extracted_binary=""
            for pattern in "$tool_name" "$tool_name-*" "*$tool_name*"; do
                extracted_binary=$(find . -name "$pattern" -type f 2>/dev/null | head -1)
                if [[ -n "$extracted_binary" ]]; then
                    break
                fi
            done
            
            if [[ -n "$extracted_binary" ]]; then
                mv "$extracted_binary" "$tool_name"
                print_success "Extracted $tool_name binary"
            else
                print_error "Could not find $tool_name binary in archive"
                return 1
            fi
        else
            print_error "Failed to download $tool_name from $url"
            return 1
        fi
    else
        # Direct download
        if curl -L -f -s -o "$TOOLS_DIR/$filename" "$url"; then
            print_success "Downloaded $tool_name"
        else
            print_error "Failed to download $tool_name from $url"
            return 1
        fi
    fi
    
    # Make executable (Unix only)
    if [[ "$OS_NAME" != "windows" ]]; then
        chmod +x "$TOOLS_DIR/$tool_name"
        print_success "Made $tool_name executable"
    fi
    
    # Test if tool works (skip version test for cardano-cli on ARM64 to avoid crashes)
    if [[ -n "$version_check" ]]; then
        if [[ "$tool_name" == "cardano-cli" && "$ARCH_NAME" == "aarch64" ]]; then
            print_success "$tool_name is installed (version test skipped on ARM64)"
        elif "$TOOLS_DIR/$tool_name" $version_check > /dev/null 2>&1; then
            print_success "$tool_name is working"
        else
            print_warning "$tool_name installed but version test failed"
        fi
    fi
}

# Install Cardano tools based on OS and architecture
install_cardano_tools() {
    print_status "Installing Cardano tools for $OS_NAME ($ARCH_NAME)..."
    
    # Latest versions (update these as needed)
    CARDANO_CLI_VERSION="10.11.1.0"
    CARDANO_ADDRESS_VERSION="4.0.0"
    BECH32_VERSION="v1.1.2"
    
    case $OS_NAME in
        "macos")
            if [[ "$ARCH_NAME" == "x86_64" ]]; then
                install_tool "cardano-cli" \
                    "https://github.com/IntersectMBO/cardano-cli/releases/download/cardano-cli-$CARDANO_CLI_VERSION/cardano-cli-$CARDANO_CLI_VERSION-x86_64-darwin.tar.gz" \
                    "cardano-cli" "--version" || print_warning "cardano-cli installation failed"
                    
                install_tool "cardano-address" \
                    "https://github.com/IntersectMBO/cardano-addresses/releases/download/$CARDANO_ADDRESS_VERSION/cardano-address-$CARDANO_ADDRESS_VERSION-macos.tar.gz" \
                    "cardano-address" "--version" || print_warning "cardano-address installation failed"
                    
                # Note: bech32 is not available for direct download
                # The CLI will use simplified mode for this tool
                print_warning "bech32 not available for direct download"
                print_warning "Using simplified mode for bech32 encoding"
            elif [[ "$ARCH_NAME" == "aarch64" ]]; then
                install_tool "cardano-cli" \
                    "https://github.com/IntersectMBO/cardano-cli/releases/download/cardano-cli-$CARDANO_CLI_VERSION/cardano-cli-$CARDANO_CLI_VERSION-aarch64-darwin.tar.gz" \
                    "cardano-cli" "--version" || print_warning "cardano-cli installation failed"
                    
                install_tool "cardano-address" \
                    "https://github.com/IntersectMBO/cardano-addresses/releases/download/$CARDANO_ADDRESS_VERSION/cardano-address-$CARDANO_ADDRESS_VERSION-macos.tar.gz" \
                    "cardano-address" "--version" || print_warning "cardano-address installation failed"
                    
                # Note: bech32 is not available for direct download
                # The CLI will use simplified mode for this tool
                print_warning "bech32 not available for direct download"
                print_warning "Using simplified mode for bech32 encoding"
                print_warning "Note: cardano-cli may crash on ARM64 due to missing dependencies"
                print_warning "The CLI will automatically detect and handle this"
            fi
            ;;
            
        "linux")
            if [[ "$ARCH_NAME" == "x86_64" ]]; then
                install_tool "cardano-cli" \
                    "https://github.com/IntersectMBO/cardano-cli/releases/download/cardano-cli-$CARDANO_CLI_VERSION/cardano-cli-$CARDANO_CLI_VERSION-x86_64-linux.tar.gz" \
                    "cardano-cli" "--version" || print_warning "cardano-cli installation failed"
                    
                install_tool "cardano-address" \
                    "https://github.com/IntersectMBO/cardano-addresses/releases/download/$CARDANO_ADDRESS_VERSION/cardano-address-$CARDANO_ADDRESS_VERSION-linux.tar.gz" \
                    "cardano-address" "--version" || print_warning "cardano-address installation failed"
                    
                # Note: bech32 is not available for direct download
                # The CLI will use simplified mode for this tool
                print_warning "bech32 not available for direct download"
                print_warning "Using simplified mode for bech32 encoding"
            elif [[ "$ARCH_NAME" == "aarch64" ]]; then
                install_tool "cardano-cli" \
                    "https://github.com/IntersectMBO/cardano-cli/releases/download/cardano-cli-$CARDANO_CLI_VERSION/cardano-cli-$CARDANO_CLI_VERSION-aarch64-linux.tar.gz" \
                    "cardano-cli" "--version" || print_warning "cardano-cli installation failed"
                    
                install_tool "cardano-address" \
                    "https://github.com/IntersectMBO/cardano-addresses/releases/download/$CARDANO_ADDRESS_VERSION/cardano-address-$CARDANO_ADDRESS_VERSION-linux.tar.gz" \
                    "cardano-address" "--version" || print_warning "cardano-address installation failed"
                    
                # Note: bech32 is not available for direct download
                # The CLI will use simplified mode for this tool
                print_warning "bech32 not available for direct download"
                print_warning "Using simplified mode for bech32 encoding"
            fi
            ;;
            
        "windows")
            install_tool "cardano-cli" \
                "https://github.com/IntersectMBO/cardano-node/releases/download/$CARDANO_NODE_VERSION/cardano-cli-win64.exe" \
                "cardano-cli.exe" "--version" || print_warning "cardano-cli installation failed"
                
            install_tool "cardano-address" \
                "https://github.com/IntersectMBO/cardano-addresses/releases/download/$CARDANO_ADDRESS_VERSION/cardano-address-win64.exe" \
                "cardano-address.exe" "--version" || print_warning "cardano-address installation failed"
                
            install_tool "bech32" \
                "https://github.com/IntersectMBO/bech32/releases/download/$BECH32_VERSION/bech32-win64.exe" \
                "bech32.exe" "--version" || print_warning "bech32 installation failed"
            ;;
    esac
}

# Install system dependencies
install_system_deps() {
    print_status "Installing system dependencies..."
    
    case $OS_NAME in
        "macos")
            if command -v brew >/dev/null 2>&1; then
                print_status "Using Homebrew to install dependencies..."
                brew install curl jq || print_warning "Some dependencies may not be available"
            else
                print_warning "Homebrew not found. Please install manually:"
                print_warning "  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
            fi
            ;;
            
        "linux")
            if command -v apt-get >/dev/null 2>&1; then
                print_status "Using apt to install dependencies..."
                sudo apt-get update -qq
                sudo apt-get install -y curl jq || print_warning "Some dependencies may not be available"
            elif command -v yum >/dev/null 2>&1; then
                print_status "Using yum to install dependencies..."
                sudo yum install -y curl jq || print_warning "Some dependencies may not be available"
            elif command -v dnf >/dev/null 2>&1; then
                print_status "Using dnf to install dependencies..."
                sudo dnf install -y curl jq || print_warning "Some dependencies may not be available"
            else
                print_warning "No supported package manager found"
            fi
            ;;
    esac
}

# Verify installation
verify_installation() {
    print_status "Verifying installation..."
    
    local tools_installed=0
    local total_tools=3
    
    for tool in cardano-cli cardano-address bech32; do
        if [[ "$OS_NAME" == "windows" ]]; then
            tool_file="$TOOLS_DIR/${tool}.exe"
        else
            tool_file="$TOOLS_DIR/$tool"
        fi
        
        if [[ -f "$tool_file" && -x "$tool_file" ]]; then
            print_success "$tool is installed and executable"
            ((tools_installed++))
        else
            print_warning "$tool is not properly installed"
        fi
    done
    
    if [[ $tools_installed -eq $total_tools ]]; then
        print_success "All Cardano tools installed successfully!"
        return 0
    elif [[ $tools_installed -gt 0 ]]; then
        print_warning "Some tools installed ($tools_installed/$total_tools)"
        print_warning "CLI will use simplified mode for missing tools"
        return 0
    else
        print_warning "No tools installed successfully"
        print_warning "CLI will use simplified mode"
        return 0
    fi
}

# Main installation flow
main() {
    print_header
    detect_system
    setup_directories
    install_system_deps
    install_cardano_tools
    verify_installation
    
    echo ""
    print_success "Cardano tools installation completed!"
    echo ""
    print_status "You can now use real tools mode:"
    echo "  cspocli generate --ticker MYPOOL --purpose pledge"
    echo ""
    print_status "Or continue using simplified mode:"
    echo "  cspocli generate --ticker MYPOOL --purpose pledge --simple"
    echo ""
    print_warning "Note: If some tools failed to install, the CLI will automatically"
    print_warning "fall back to simplified mode when needed."
}

# Run main function
main "$@" 