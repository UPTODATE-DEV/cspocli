#!/bin/bash
set -euo pipefail

# === CONFIGURATION ===
NETWORK="--testnet-magic 2"  # Use --mainnet for mainnet
INSTALL_DIR="${HOME}/.local/bin"
CURL_TIMEOUT=60
REPO_CARDANO_NODE="https://github.com/intersectmbo/cardano-node"
REPO_CARDANO_CLI="https://github.com/IntersectMBO/cardano-cli"
REPO_CARDANO_ADDRESS="https://github.com/intersectmbo/cardano-addresses"

# Detect OS and architecture
OS=$(uname -s)
ARCH=$(uname -m)
case $OS in
  Linux) OS_TYPE="linux" ;;
  Darwin) OS_TYPE="macos" ;;
  *) echo "ERROR: Unsupported OS: $OS. Use Linux or macOS (or WSL2 for Windows)." >&2; exit 1 ;;
esac
case $ARCH in
  x86_64) ARCH_TYPE="x64" ;;
  aarch64|arm64) ARCH_TYPE="arm64" ;;
  *) echo "ERROR: Unsupported architecture: $ARCH. Only x86_64 and aarch64/arm64 supported." >&2; exit 1 ;;
esac

# Ensure dependencies are available
check_dependencies() {
  for cmd in curl jq tar; do
    if ! command -v $cmd &> /dev/null; then
      echo "ERROR: $cmd is required. Install it using your package manager:" >&2
      case $OS in
        Linux)
          if command -v apt-get &> /dev/null; then
            echo "  sudo apt-get install $cmd" >&2
          elif command -v dnf &> /dev/null; then
            echo "  sudo dnf install $cmd" >&2
          else
            echo "  Use your package manager to install $cmd" >&2
          fi ;;
        Darwin) echo "  brew install $cmd" >&2 ;;
      esac
      exit 1
    fi
  done
}

# Ensure install directory exists
mkdir -p "$INSTALL_DIR"

# Update PATH in shell configuration
update_shell_path() {
  SHELL_CONFIG="${HOME}/.bashrc"
  if [[ "$OS" == "Darwin" && -n "${ZSH_VERSION:-}" ]]; then
    SHELL_CONFIG="${HOME}/.zshrc"
  fi
  if ! grep -q "${INSTALL_DIR}" "$SHELL_CONFIG"; then
    echo -e "\nexport PATH=\"${INSTALL_DIR}:\${PATH}\"" >> "$SHELL_CONFIG"
    export PATH="${INSTALL_DIR}:${PATH}"
    echo "Added ${INSTALL_DIR} to PATH in $SHELL_CONFIG. Run 'source $SHELL_CONFIG' or restart your shell."
  else
    echo "${INSTALL_DIR} already in PATH."
  fi
}

# Download and install a binary
download_binary() {
  local binary_name="$1"
  local repo_url="$2"
  local file_pattern="$3"
  local output_file="$4"
  local version
  version=$(curl -s -m $CURL_TIMEOUT https://api.github.com/repos${repo_url#https://github.com}/releases/latest | jq -r '.tag_name' || echo "unknown")
  if [[ "$version" == "unknown" ]]; then
    echo "ERROR: Failed to fetch latest version for $binary_name from GitHub." >&2
    exit 1
  fi
  echo "Downloading $binary_name version $version for $OS_TYPE-$ARCH_TYPE..."
  pushd "$(mktemp -d)" >/dev/null || { echo "ERROR: Failed to create temporary directory" >&2; exit 1; }
  local asset_url
  # Fix regex pattern for jq
  local jq_pattern
  case $file_pattern in
    *"macos"*) jq_pattern="macos.*tar.gz" ;;
    *"linux"*) jq_pattern="linux.*tar.gz" ;;
    *) jq_pattern="$file_pattern" ;;
  esac
  asset_url=$(curl -s -m $CURL_TIMEOUT https://api.github.com/repos${repo_url#https://github.com}/releases/latest | jq -r ".assets[].browser_download_url | select(test(\"$jq_pattern\"))")
  if [[ -z "$asset_url" ]]; then
    echo "ERROR: No matching $binary_name binary found for $OS_TYPE-$ARCH_TYPE. For ARM, you may need to build from source: $repo_url" >&2
    popd >/dev/null
    exit 1
  fi
  curl -m $CURL_TIMEOUT -sfL "$asset_url" -o "${binary_name}.tar.gz" || { echo "ERROR: Failed to download $binary_name from $asset_url" >&2; popd >/dev/null; exit 1; }
  tar zxf "${binary_name}.tar.gz" --strip-components 1 2>/dev/null || tar zxf "${binary_name}.tar.gz" 2>/dev/null || { echo "ERROR: Failed to extract $binary_name" >&2; popd >/dev/null; exit 1; }
  if [[ ! -f "$output_file" ]]; then
    echo "ERROR: $binary_name binary ($output_file) not found after extraction" >&2
    popd >/dev/null
    exit 1
  fi
  mv -f "$output_file" "$INSTALL_DIR/" || { echo "ERROR: Failed to move $output_file to $INSTALL_DIR" >&2; popd >/dev/null; exit 1; }
  chmod +x "${INSTALL_DIR}/$output_file"
  popd >/dev/null
  echo "$binary_name $version installed successfully."
}

# Verify installed binaries
verify_installation() {
  for binary in cardano-cli cardano-address cardano-node; do
    if command -v $binary &> /dev/null; then
      local version
      if [[ "$binary" == "cardano-address" ]]; then
        version=$($binary version 2>/dev/null | grep -oP '\d+\.\d+\.\d+' || echo "unknown")
      else
        version=$($binary version 2>/dev/null | head -n 1 | grep -oP '\d+\.\d+\.\d+\.\d+' || echo "unknown")
      fi
      echo "$binary installed, version: $version"
    else
      echo "ERROR: $binary not found in $INSTALL_DIR" >&2
      exit 1
    fi
  done
}

echo "Installing cardano-cli, cardano-address, and cardano-node for $OS_TYPE-$ARCH_TYPE..."

# Check dependencies
check_dependencies

# Update PATH
update_shell_path

# Download cardano-node
download_binary "cardano-node" "$REPO_CARDANO_NODE" "${OS_TYPE}.*\.tar\.gz" "cardano-node"

# Download cardano-cli
download_binary "cardano-cli" "$REPO_CARDANO_CLI" "${OS_TYPE}.*\.tar\.gz" "cardano-cli"

# Download cardano-address
download_binary "cardano-address" "$REPO_CARDANO_ADDRESS" "${OS_TYPE}.*\.tar\.gz" "cardano-address"

# Verify installations
verify_installation

echo "All binaries installed successfully in $INSTALL_DIR!"
echo "To use immediately, run: source \$HOME/.bashrc (or \$HOME/.zshrc on macOS with zsh)"
echo "Verify functionality with: cardano-cli --version, cardano-address version, cardano-node --version"
echo "WARNING: For sensitive operations (e.g., key generation), run on an air-gapped system."
echo "Clean up temporary files in /tmp if desired."

exit 0 