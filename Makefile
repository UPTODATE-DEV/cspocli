# Makefile for Cardano SPO CLI
# Usage: make install (local) or make install-global (global)

.PHONY: help install install-global uninstall test clean

# Default target
help:
	@echo "Cardano SPO CLI - Available targets:"
	@echo ""
	@echo "  make install        - Install CLI globally + Cardano tools (recommended)"
	@echo "  make install-global - Install CLI globally + Cardano tools (alternative)"
	@echo "  make install-tools  - Install only Cardano tools (cardano-cli, cardano-address, bech32)"
	@echo "  make uninstall      - Remove global installation"
	@echo "  make test           - Run tests"
	@echo "  make clean          - Clean up generated files"
	@echo "  make help           - Show this help"
	@echo ""
	@echo "Professional Installation:"
	@echo "  All install targets automatically install real Cardano tools"
	@echo "  (cardano-cli, cardano-address, bech32) for production use."
	@echo "  On ARM64 systems, tools will use simplified mode as fallback."
	@echo "  Global installation makes 'cspocli' available everywhere."
	@echo ""

# Global installation (recommended - no activation needed)
install:
	@echo "🌍 Installing Cardano SPO CLI globally..."
	@echo "=========================================="
	@echo ""
	@if [ ! -d "venv" ]; then \
		echo "Creating virtual environment..."; \
		python3 -m venv venv; \
	fi
	@echo "Installing dependencies in virtual environment..."
	@source venv/bin/activate && \
	pip install --upgrade pip && \
	pip install -r requirements.txt && \
	pip install -e .
	@echo ""
	@echo "Installing Cardano tools for professional use..."
	@chmod +x install-cardano-tools.sh && \
	./install-cardano-tools.sh
	@echo ""
	@echo "Creating global cspocli script..."
	@echo "⚠️  You will be prompted for your computer password (not sudo password)"
	@echo "   This is needed to write to /usr/local/bin/"
	@echo ""
	@CURRENT_DIR="$(shell pwd)" && \
	echo '#!/bin/bash' > /tmp/cspocli_script && \
	echo 'CARDANO_SPO_DIR="'$$CURRENT_DIR'"' >> /tmp/cspocli_script && \
	echo 'if [ -d "$$CARDANO_SPO_DIR" ] && [ -f "$$CARDANO_SPO_DIR/venv/bin/activate" ]; then' >> /tmp/cspocli_script && \
	echo '    source "$$CARDANO_SPO_DIR/venv/bin/activate"' >> /tmp/cspocli_script && \
	echo '    python -m cardano_spo_cli "$$@"' >> /tmp/cspocli_script && \
	echo 'else' >> /tmp/cspocli_script && \
	echo '    echo "❌ Cardano SPO CLI not found in $$CARDANO_SPO_DIR"' >> /tmp/cspocli_script && \
	echo '    echo "Please run '\''make install'\'' first."' >> /tmp/cspocli_script && \
	echo '    exit 1' >> /tmp/cspocli_script && \
	echo 'fi' >> /tmp/cspocli_script && \
	sudo cp /tmp/cspocli_script /usr/local/bin/cspocli && \
	sudo chmod +x /usr/local/bin/cspocli && \
	rm /tmp/cspocli_script
	@echo "✅ Global cspocli script created"
	@echo ""
	@echo "Testing global installation..."
	@cspocli --help || \
		(echo "❌ Global cspocli failed to run!"; exit 1)
	@echo "✅ Global cspocli works correctly!"
	@echo ""
	@echo "🎉 Global installation completed!"
	@echo "================================"
	@echo ""
	@echo "✅ cspocli is now available globally"
	@echo "✅ You can use 'cspocli' from any directory"
	@echo "✅ No need to activate virtual environment"
	@echo ""
	@echo "📖 Usage examples:"
	@echo "  cspocli generate --ticker MYPOOL --purpose pledge"
	@echo "  cspocli generate --ticker MYPOOL --purpose pledge --network testnet"
	@echo "  cspocli generate --ticker MYPOOL --purpose pledge --network preview"
	@echo ""

# Global installation (no activation needed)
install-global:
	@echo "🌍 Installing Cardano SPO CLI globally..."
	@echo "=========================================="
	@echo ""
	@if [ ! -d "venv" ]; then \
		echo "❌ Virtual environment not found!"; \
		echo "Please run 'make install' first."; \
		exit 1; \
	fi
	@echo "Testing CLI in virtual environment..."
	@source venv/bin/activate && python -m cardano_spo_cli --help > /dev/null 2>&1 || \
		(echo "❌ CLI not working in virtual environment!"; exit 1)
	@echo "✅ CLI works in virtual environment"
	@echo ""
	@echo "Installing Cardano tools for professional use..."
	@chmod +x install-cardano-tools-universal.sh && \
	./install-cardano-tools-universal.sh
	@echo ""
	@echo "Creating global cspocli script..."
	@echo "⚠️  You will be prompted for your computer password (not sudo password)"
	@echo "   This is needed to write to /usr/local/bin/"
	@echo ""
	@CURRENT_DIR="$(shell pwd)" && \
	echo '#!/bin/bash' > /tmp/cspocli_script && \
	echo 'CARDANO_SPO_DIR="'$$CURRENT_DIR'"' >> /tmp/cspocli_script && \
	echo 'if [ -d "$$CARDANO_SPO_DIR" ] && [ -f "$$CARDANO_SPO_DIR/venv/bin/activate" ]; then' >> /tmp/cspocli_script && \
	echo '    source "$$CARDANO_SPO_DIR/venv/bin/activate"' >> /tmp/cspocli_script && \
	echo '    python -m cardano_spo_cli "$$@"' >> /tmp/cspocli_script && \
	echo 'else' >> /tmp/cspocli_script && \
	echo '    echo "❌ Cardano SPO CLI not found in $$CARDANO_SPO_DIR"' >> /tmp/cspocli_script && \
	echo '    echo "Please run '\''make install'\'' first."' >> /tmp/cspocli_script && \
	echo '    exit 1' >> /tmp/cspocli_script && \
	echo 'fi' >> /tmp/cspocli_script && \
	sudo cp /tmp/cspocli_script /usr/local/bin/cspocli && \
	sudo chmod +x /usr/local/bin/cspocli && \
	rm /tmp/cspocli_script
	@echo "✅ Global cspocli script created"
	@echo ""
	@echo "Testing global installation..."
	@cspocli --help || \
		(echo "❌ Global cspocli failed to run!"; exit 1)
	@echo "✅ Global cspocli works correctly!"
	@echo ""
	@echo "🎉 Global installation completed!"
	@echo "================================"
	@echo ""
	@echo "✅ cspocli is now available globally"
	@echo "✅ You can use 'cspocli' from any directory"
	@echo "✅ No need to activate virtual environment"
	@echo ""
	@echo "📖 Test it:"
	@echo "  cspocli --help"
	@echo "  cspocli version"
	@echo "  cspocli generate --ticker MYPOOL --purpose pledge --simple"
	@echo ""

# Install only Cardano tools
install-tools:
	@echo "🔧 Installing Cardano tools only..."
	@echo "===================================="
	@echo ""
	@chmod +x install-cardano-tools-universal.sh && \
	./install-cardano-tools-universal.sh
	@echo ""
	@echo "✅ Cardano tools installation completed!"
	@echo "📖 You can now use real tools mode:"
	@echo "  cspocli generate --ticker MYPOOL --purpose pledge"
	@echo ""

# Uninstall global installation
uninstall:
	@echo "🗑️  Uninstalling global cspocli..."
	@echo "⚠️  You will be prompted for your computer password"
	@echo ""
	@if [ -f "/usr/local/bin/cspocli" ]; then \
		sudo rm /usr/local/bin/cspocli; \
		echo "✅ Global cspocli removed"; \
	else \
		echo "ℹ️  Global cspocli not found"; \
	fi
	@echo ""

# Run tests
test:
	@echo "🧪 Running tests..."
	@source venv/bin/activate && python test_cli.py
	@echo "✅ Tests completed!"

# Clean up generated files
clean:
	@echo "🧹 Cleaning up..."
	@rm -rf ~/.CSPO_* 2>/dev/null || true
	@rm -rf .cardano_spo_cli 2>/dev/null || true
	@echo "✅ Cleanup completed!" # Makefile
