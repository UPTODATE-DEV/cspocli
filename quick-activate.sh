#!/bin/bash

# Quick activation script - must be sourced
# Usage: source quick-activate.sh

if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Run './install.sh' first."
    return 1
fi

source venv/bin/activate
echo "✅ Virtual environment activated. Use 'cspocli' commands now."
echo "💡 To deactivate: deactivate" 