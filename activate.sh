#!/bin/bash

# Cardano SPO CLI Activation Script
# This script activates the virtual environment and shows CLI status

echo "🔧 Activating Cardano SPO CLI environment..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment 'venv' not found!"
    echo "Please run './install.sh' first to install the CLI."
    exit 1
fi

# Activate virtual environment in current shell
source venv/bin/activate

echo "✅ Virtual environment activated"
echo ""

# Test if cspocli is available
if command -v cspocli &> /dev/null; then
    echo "✅ cspocli command is available"
    echo ""
    echo "📖 Available commands:"
    echo "  cspocli --help                    # Show help"
    echo "  cspocli version                   # Show version"
    echo "  cspocli generate --ticker MYPOOL --purpose pledge  # Generate wallet"
    echo ""
    echo "🎯 You can now use cspocli commands!"
    echo "💡 To deactivate later, run: deactivate"
else
    echo "❌ cspocli command not found"
    echo "Try running: python -m cardano_spo_cli --help"
fi

echo ""
echo "🔧 Environment is now ready for use!"

# Note: This script must be sourced, not executed
# Usage: source activate.sh 