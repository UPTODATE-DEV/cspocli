#!/bin/bash

# Make Cardano tools available globally
# This script creates symlinks to make cardano-cli available in PATH

set -e

# Colors
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

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

TOOLS_DIR="$HOME/.cardano_spo_cli/tools"
LOCAL_BIN="$HOME/.local/bin"

print_status "Making Cardano tools available globally..."

# Create ~/.local/bin if it doesn't exist
mkdir -p "$LOCAL_BIN"

# Create symlinks for available tools
if [[ -f "$TOOLS_DIR/cardano-cli" ]]; then
    ln -sf "$TOOLS_DIR/cardano-cli" "$LOCAL_BIN/cardano-cli"
    print_success "Created symlink for cardano-cli"
else
    print_warning "cardano-cli not found in $TOOLS_DIR"
fi

if [[ -f "$TOOLS_DIR/cardano-address" ]]; then
    ln -sf "$TOOLS_DIR/cardano-address" "$LOCAL_BIN/cardano-address"
    print_success "Created symlink for cardano-address"
else
    print_warning "cardano-address not found in $TOOLS_DIR"
fi

if [[ -f "$TOOLS_DIR/bech32" ]]; then
    ln -sf "$TOOLS_DIR/bech32" "$LOCAL_BIN/bech32"
    print_success "Created symlink for bech32"
else
    print_warning "bech32 not found in $TOOLS_DIR"
fi

# Add ~/.local/bin to PATH if not already there
if ! echo "$PATH" | grep -q "$LOCAL_BIN"; then
    print_status "Adding ~/.local/bin to PATH..."
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
    print_success "Added ~/.local/bin to PATH in ~/.zshrc"
    print_warning "Please restart your terminal or run: source ~/.zshrc"
else
    print_success "~/.local/bin is already in PATH"
fi

print_success "Cardano tools setup completed!"
print_status "You can now use:"
echo "  cardano-cli --version"
echo "  cspocli generate --ticker MYPOOL --purpose pledge" 