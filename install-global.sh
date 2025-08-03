#!/bin/bash

# Global Installation Script for Cardano SPO CLI
# This script installs cspocli globally so it's available without activation

set -e

echo "🌍 Installing Cardano SPO CLI globally..."
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "setup.py" ] || [ ! -f "cardano_spo_cli/__init__.py" ]; then
    print_error "This script must be run from the cardano-spo-cli directory!"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_error "Virtual environment not found!"
    print_error "Please run './install.sh' first to install the CLI."
    exit 1
fi

# Check if cspocli works in the virtual environment
print_status "Testing CLI in virtual environment..."
source venv/bin/activate
if python -m cardano_spo_cli --help &> /dev/null; then
    print_success "CLI works in virtual environment"
else
    print_error "CLI not working in virtual environment!"
    exit 1
fi

# Create global script
GLOBAL_SCRIPT="/usr/local/bin/cspocli"
CURRENT_DIR="$(pwd)"

print_status "Creating global cspocli script..."

# Check if we can write to /usr/local/bin
if [ ! -w "/usr/local/bin" ]; then
    print_error "Cannot write to /usr/local/bin"
    print_error "Try running with sudo: sudo ./install-global.sh"
    exit 1
fi

# Create the global script
cat > "$GLOBAL_SCRIPT" << EOF
#!/bin/bash
# Global cspocli wrapper
CARDANO_SPO_DIR="$CURRENT_DIR"

if [ -d "\$CARDANO_SPO_DIR" ] && [ -f "\$CARDANO_SPO_DIR/venv/bin/activate" ]; then
    source "\$CARDANO_SPO_DIR/venv/bin/activate"
    python -m cardano_spo_cli "\$@"
else
    echo "❌ Cardano SPO CLI not found in \$CARDANO_SPO_DIR"
    echo "Please run './install.sh' from the cardano-spo-cli directory first."
    exit 1
fi
EOF

chmod +x "$GLOBAL_SCRIPT"
print_success "Global cspocli script created at $GLOBAL_SCRIPT"

# Test the global installation
print_status "Testing global installation..."
if command -v cspocli &> /dev/null; then
    print_success "Global cspocli is available!"
    
    # Test the command
    if cspocli --help &> /dev/null; then
        print_success "Global cspocli works correctly!"
    else
        print_error "Global cspocli failed to run!"
        exit 1
    fi
else
    print_error "Global cspocli not found in PATH!"
    exit 1
fi

echo ""
echo "🎉 Global installation completed!"
echo "================================"
echo ""
echo "✅ cspocli is now available globally"
echo "✅ You can use 'cspocli' from any directory"
echo "✅ No need to activate virtual environment"
echo ""
echo "📖 Test it:"
echo "  cspocli --help"
echo "  cspocli version"
echo "  cspocli generate --ticker MYPOOL --purpose pledge --simple"
echo ""
echo "💡 To uninstall globally:"
echo "  sudo rm /usr/local/bin/cspocli"
echo ""

print_success "Global installation completed! 🚀" 