# Using Real Cardano Tools

## Overview

The Cardano SPO CLI can work with real Cardano tools (cardano-cli, cardano-address, bech32) for production use, or with demo tools for testing and development.

## Current Status

By default, the CLI uses **real Cardano tools** for production-ready addresses and keys. This requires the official Cardano tools to be installed.

For **development and testing**, you can use the simplified mode as a fallback.

## Installing Real Cardano Tools

### Option 1: Manual Installation

#### cardano-cli

```bash
# Download from IntersectMBO releases
# https://github.com/IntersectMBO/cardano-node/releases

# For macOS
curl -L -O https://github.com/IntersectMBO/cardano-node/releases/download/10.5.1/cardano-node-10.5.1-macos.tar.gz
tar -xzf cardano-node-10.5.1-macos.tar.gz
sudo cp cardano-cli /usr/local/bin/

# For Linux
curl -L -O https://github.com/IntersectMBO/cardano-node/releases/download/10.5.1/cardano-node-10.5.1-linux.tar.gz
tar -xzf cardano-node-10.5.1-linux.tar.gz
sudo cp cardano-cli /usr/local/bin/

# For Windows
# Download cardano-node-10.5.1-win64.zip and extract cardano-cli.exe
```

#### cardano-address

```bash
# Download from IntersectMBO releases
# https://github.com/IntersectMBO/cardano-addresses/releases

# For macOS
curl -L -O https://github.com/IntersectMBO/cardano-addresses/releases/download/4.0.0/cardano-address-4.0.0-macos.tar.gz
tar -xzf cardano-address-4.0.0-macos.tar.gz
sudo cp cardano-address /usr/local/bin/

# For Linux
curl -L -O https://github.com/IntersectMBO/cardano-addresses/releases/download/4.0.0/cardano-address-4.0.0-linux.tar.gz
tar -xzf cardano-address-4.0.0-linux.tar.gz
sudo cp cardano-address /usr/local/bin/

# For Windows
# Download cardano-address-4.0.0-win64.zip and extract cardano-address.exe
```

#### bech32

```bash
# Download from IntersectMBO releases
# https://github.com/IntersectMBO/bech32/releases

# For macOS
curl -L -O https://github.com/IntersectMBO/bech32/releases/download/v1.1.2/bech32-v1.1.2-macos.tar.gz
tar -xzf bech32-v1.1.2-macos.tar.gz
sudo cp bech32 /usr/local/bin/

# For Linux
curl -L -O https://github.com/IntersectMBO/bech32/releases/download/v1.1.2/bech32-v1.1.2-linux.tar.gz
tar -xzf bech32-v1.1.2-linux.tar.gz
sudo cp bech32 /usr/local/bin/

# For Windows
# Download bech32-v1.1.2-win64.zip and extract bech32.exe
```

### Option 2: Using Package Managers

#### macOS (Homebrew)

```bash
# Install cardano-node (includes cardano-cli)
brew install cardano-node

# Install cardano-address
brew install cardano-address

# Install bech32
brew install bech32
```

#### Ubuntu/Debian

```bash
# Add Cardano repository
curl -fsSL https://downloads.cardano.org/cardano-node-repo/cardano-node-repo-1.0.0-all.deb -o cardano-node-repo-1.0.0-all.deb
sudo dpkg -i cardano-node-repo-1.0.0-all.deb
sudo apt update

# Install cardano-node (includes cardano-cli)
sudo apt install cardano-node

# Install cardano-address and bech32
sudo apt install cardano-address bech32
```

## Using Real Tools with the CLI

Once you have installed the real Cardano tools, you can use them with the CLI:

```bash
# The CLI will automatically detect and use real tools if available
cspocli generate --ticker MYPOOL --purpose pledge

# Or explicitly use real tools (if implemented)
cspocli generate --ticker MYPOOL --purpose pledge --real-tools
```

## Verification

To verify that real tools are being used:

```bash
# Check if tools are available
which cardano-cli
which cardano-address
which bech32

# Test tool versions
cardano-cli --version
cardano-address --version
bech32 --help
```

## Differences Between Real Tools and Simplified Mode

### Real Tools Version (Default)

- ✅ Generates real Cardano addresses
- ✅ Creates cryptographically valid keys
- ✅ Compatible with Cardano blockchain
- ✅ Production-ready
- ❌ Requires manual installation of tools
- ❌ More complex setup

### Simplified Version (Fallback)

- ✅ Safe for testing and development
- ✅ Generates realistic-looking addresses
- ✅ Creates valid file structure
- ✅ No external dependencies
- ❌ Addresses are not real Cardano addresses
- ❌ Keys are not cryptographically valid

## Security Considerations

### Simplified Version

- Safe for testing and development
- Generated addresses and keys are not real
- Cannot be used on mainnet

### Real Tools Version

- Generates real cryptographic keys
- Addresses can be used on mainnet
- **IMPORTANT**: Keep private keys secure
- **IMPORTANT**: Test with small amounts first

## Troubleshooting

### Tool Not Found

```bash
# Check if tools are in PATH
echo $PATH
which cardano-cli

# Add to PATH if needed
export PATH="/usr/local/bin:$PATH"
```

### Permission Denied

```bash
# Make tools executable
chmod +x /usr/local/bin/cardano-cli
chmod +x /usr/local/bin/cardano-address
chmod +x /usr/local/bin/bech32
```

### Version Issues

```bash
# Check tool versions
cardano-cli --version
cardano-address --version

# Update to latest versions if needed
```

## Development vs Production

### Development/Testing

```bash
# Use simplified version as fallback
cspocli generate --ticker TEST --purpose pledge --simple
```

### Production

```bash
# Use real tools (default)
cspocli generate --ticker MYPOOL --purpose pledge
```

## File Structure

Both demo and real tools create the same file structure:

```
~/.CSPO_MYPOOL/
├── pledge/
│   ├── MYPOOL-pledge.base_addr
│   ├── MYPOOL-pledge.reward_addr
│   ├── MYPOOL-pledge.staking_skey
│   ├── MYPOOL-pledge.staking_vkey
│   └── MYPOOL-pledge.mnemonic.txt
└── rewards/
    ├── MYPOOL-rewards.base_addr
    ├── MYPOOL-rewards.reward_addr
    ├── MYPOOL-rewards.staking_skey
    ├── MYPOOL-rewards.staking_vkey
    └── MYPOOL-rewards.mnemonic.txt
```

## Next Steps

1. **For Development**: Use the simplified version as fallback
2. **For Production**: Install real Cardano tools manually
3. **For Testing**: Use the simplified version with small amounts
4. **For Mainnet**: Use real tools with proper security measures

## Support

- **Documentation**: Check README.md and USAGE.md
- **Issues**: Report on GitHub
- **Community**: Join Cardano Discord channels
