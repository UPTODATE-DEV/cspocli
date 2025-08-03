#!/bin/bash

# Cardano SPO CLI Installation Script
# This script will install and set up the Cardano SPO CLI

set -e  # Exit on any error

echo "🚀 Cardano SPO CLI Installation Script"
echo "======================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check if Python 3 is installed
print_status "Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1)
    print_success "Python found: $PYTHON_VERSION"
else
    print_error "Python 3 is not installed!"
    echo ""
    echo "Please install Python 3 first:"
    echo "  macOS: brew install python"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-venv python3-pip"
    echo "  Windows: Download from https://www.python.org/downloads/"
    exit 1
fi

# Check Python version
PYTHON_MAJOR=$(python3 -c "import sys; print(sys.version_info.major)")
PYTHON_MINOR=$(python3 -c "import sys; print(sys.version_info.minor)")

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 7 ]); then
    print_error "Python 3.7 or higher is required!"
    print_error "Current version: $PYTHON_VERSION"
    exit 1
fi

print_success "Python version is compatible (3.7+)"

# Check if pip is available
print_status "Checking pip installation..."
if python3 -m pip --version &> /dev/null; then
    print_success "pip is available"
else
    print_error "pip is not available!"
    echo ""
    echo "Please install pip:"
    echo "  macOS: brew install python"
    echo "  Ubuntu/Debian: sudo apt install python3-pip"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "setup.py" ] || [ ! -f "cardano_spo_cli/__init__.py" ]; then
    print_error "This script must be run from the cardano-spo-cli directory!"
    print_error "Please navigate to the project directory and run this script again."
    exit 1
fi

print_success "Running from correct directory"

# Check if virtual environment already exists
if [ -d "venv" ]; then
    print_warning "Virtual environment 'venv' already exists"
    read -p "Do you want to recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Removing existing virtual environment..."
        rm -rf venv
        print_success "Removed existing virtual environment"
    else
        print_status "Using existing virtual environment"
    fi
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate
print_success "Virtual environment activated"

# Upgrade pip
print_status "Upgrading pip..."
python -m pip install --upgrade pip
print_success "pip upgraded"

# Install dependencies
print_status "Installing dependencies..."
python -m pip install -r requirements.txt
print_success "Dependencies installed"

# Install the CLI in editable mode
print_status "Installing Cardano SPO CLI..."
python -m pip install -e .
print_success "Cardano SPO CLI installed"

# Test the installation
print_status "Testing installation..."
if command -v cspocli &> /dev/null; then
    print_success "cspocli command is available"
else
    print_warning "cspocli command not found in PATH"
    print_status "Trying to run with python -m..."
    if python -m cardano_spo_cli --help &> /dev/null; then
        print_success "CLI works with python -m cardano_spo_cli"
    else
        print_error "CLI installation failed!"
        exit 1
    fi
fi

# Ask if user wants global installation
echo ""
read -p "Do you want to install cspocli globally (available without activation)? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Installing cspocli globally..."
    
    # Create a global script
    GLOBAL_SCRIPT="/usr/local/bin/cspocli"
    if [ -w "/usr/local/bin" ]; then
        cat > "$GLOBAL_SCRIPT" << 'EOF'
#!/bin/bash
# Global cspocli wrapper
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CARDANO_SPO_DIR="$HOME/cardano-spo-cli"

if [ -d "$CARDANO_SPO_DIR" ] && [ -f "$CARDANO_SPO_DIR/venv/bin/activate" ]; then
    source "$CARDANO_SPO_DIR/venv/bin/activate"
    python -m cardano_spo_cli "$@"
else
    echo "❌ Cardano SPO CLI not found in $CARDANO_SPO_DIR"
    echo "Please run './install.sh' from the cardano-spo-cli directory first."
    exit 1
fi
EOF
        chmod +x "$GLOBAL_SCRIPT"
        print_success "Global cspocli installed at $GLOBAL_SCRIPT"
        print_success "You can now use 'cspocli' from anywhere!"
    else
        print_error "Cannot write to /usr/local/bin. Try running with sudo or use local installation."
        print_warning "You can still use 'source venv/bin/activate' to activate the environment."
    fi
else
    print_status "Skipping global installation. Use 'source venv/bin/activate' to activate."
fi

# Show version
echo ""
echo "🎉 Installation completed successfully!"
echo "======================================"
echo ""

if command -v cspocli &> /dev/null; then
    print_status "Showing cspocli version:"
    cspocli version
else
    print_status "Showing CLI version:"
    python -m cardano_spo_cli version
fi

echo ""
echo "📋 Next steps:"
echo "1. The virtual environment is now active in this script"
echo "2. To use 'cspocli' commands in a new terminal:"
echo "   source venv/bin/activate"
echo "3. To deactivate, run: deactivate"
echo ""
echo "📖 Quick start:"
echo "  source venv/bin/activate          # Activate environment"
echo "  cspocli --help                    # Show help"
echo "  cspocli version                   # Show version"
echo "  cspocli generate --ticker MYPOOL --purpose pledge  # Generate wallet"
echo ""

print_success "Installation completed! 🚀"
print_warning "Remember to activate the virtual environment in new terminals:"
print_warning "  source venv/bin/activate" # Install script
