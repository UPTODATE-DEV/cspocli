# Using Real Cardano Tools

## Overview

The Cardano SPO CLI can work with real Cardano tools (cardano-cli, cardano-address, bech32) for production use, or with demo tools for testing and development.

## Current Status

By default, the CLI uses **real Cardano tools** for production-ready addresses and keys. This requires the official Cardano tools to be installed.

For **development and testing**, you can use the simplified mode as a fallback.

## Installing Real Cardano Tools

### Option 1: Automatic Installation (Recommended)

```bash
# Install CLI and tools automatically
make install

# Or install tools only
make install-tools
```

### Option 2: Manual Installation

#### cardano-cli

```bash
# Download from IntersectMBO releases
# https://github.com/IntersectMBO/cardano-node/releases

# For macOS
curl -L -O https://github.com/IntersectMBO/cardano-node/releases/download/10.11.1.0/cardano-node-10.11.1.0-macos.tar.gz
tar -xzf cardano-node-10.11.1.0-macos.tar.gz
sudo cp cardano-cli /usr/local/bin/

# For Linux
curl -L -O https://github.com/IntersectMBO/cardano-node/releases/download/10.11.1.0/cardano-node-10.11.1.0-linux.tar.gz
tar -xzf cardano-node-10.11.1.0-linux.tar.gz
sudo cp cardano-cli /usr/local/bin/

# For Windows
# Download cardano-node-10.11.1.0-win64.zip and extract cardano-cli.exe
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
# Install via pip (recommended)
pip install bech32

# Or download from IntersectMBO releases
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

### Option 3: Using Package Managers

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

# Generate complete stake pool files (requires real tools)
cspocli generate --ticker MYPOOL --complete

# Or explicitly use real tools (if implemented)
cspocli generate --ticker MYPOOL --purpose pledge --real-tools
```

## Complete Stake Pool Generation

The `--complete` option requires real Cardano tools and generates all files needed for professional stake pool operations:

### Required Tools for Complete Mode

- **cardano-address**: For key derivation and address generation
- **cardano-cli**: For certificate generation (optional)
- **bech32**: For address encoding/decoding

### Generated Files (Complete Mode)

```
~/.CSPO_MYPOOL/pledge/
├── base.addr              # Base address (with staking)
├── payment.addr           # Payment-only address
├── reward.addr            # Reward address
├── payment.skey           # Private payment key
├── payment.vkey           # Public payment key
├── stake.skey             # Private staking key
├── stake.vkey             # Public staking key
├── cc-cold.skey           # Private cold key
├── cc-cold.vkey           # Public cold key
├── cc-hot.skey            # Private hot key
├── cc-hot.vkey            # Public hot key
├── drep.skey              # Private DRep key
├── drep.vkey              # Public DRep key
├── ms_payment.skey        # Private MS payment key
├── ms_payment.vkey        # Public MS payment key
├── ms_stake.skey          # Private MS staking key
├── ms_stake.vkey          # Public MS staking key
├── ms_drep.skey           # Private MS DRep key
├── ms_drep.vkey           # Public MS DRep key
├── payment.cred           # Payment credential
├── stake.cred             # Staking credential
├── ms_payment.cred        # MS payment credential
├── ms_stake.cred          # MS staking credential
├── stake.cert             # Staking certificate
├── delegation.cert        # Delegation certificate
└── MYPOOL-pledge.mnemonic.txt  # Recovery phrase
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

# Test complete generation
cspocli generate --ticker TEST --complete
```

## Differences Between Real Tools and Simplified Mode

### Real Tools Version (Default)

- ✅ Generates real Cardano addresses
- ✅ Creates cryptographically valid keys
- ✅ Compatible with Cardano blockchain
- ✅ Production-ready
- ✅ Supports complete stake pool generation
- ❌ Requires manual installation of tools
- ❌ More complex setup

### Simplified Version (Fallback)

- ✅ Safe for testing and development
- ✅ Generates realistic-looking addresses
- ✅ Creates valid file structure
- ✅ No external dependencies
- ❌ Addresses are not real Cardano addresses
- ❌ Keys are not cryptographically valid
- ❌ Cannot generate complete stake pool files

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
- **IMPORTANT**: Complete mode generates many sensitive files

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

### ARM64 macOS Issues

On ARM64 macOS, `cardano-cli` may crash due to Nix dependencies:

```bash
# The CLI will detect this and use cardano-address + bech32 only
# This is sufficient for most operations
cspocli generate --ticker MYPOOL --complete
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

# Use complete mode for full stake pool setup
cspocli generate --ticker MYPOOL --complete
```

## File Structure

### Standard Mode

Both demo and real tools create the same file structure:

```
~/.CSPO_MYPOOL/
├── MYPOOL-shared.mnemonic.txt
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

### Complete Mode

Real tools with `--complete` create comprehensive file structure:

```
~/.CSPO_MYPOOL/
├── MYPOOL-shared.mnemonic.txt
├── pledge/
│   ├── base.addr
│   ├── payment.addr
│   ├── reward.addr
│   ├── payment.skey
│   ├── payment.vkey
│   ├── stake.skey
│   ├── stake.vkey
│   ├── cc-cold.skey
│   ├── cc-cold.vkey
│   ├── cc-hot.skey
│   ├── cc-hot.vkey
│   ├── drep.skey
│   ├── drep.vkey
│   ├── ms_payment.skey
│   ├── ms_payment.vkey
│   ├── ms_stake.skey
│   ├── ms_stake.vkey
│   ├── ms_drep.skey
│   ├── ms_drep.vkey
│   ├── payment.cred
│   ├── stake.cred
│   ├── ms_payment.cred
│   ├── ms_stake.cred
│   ├── stake.cert
│   ├── delegation.cert
│   └── MYPOOL-pledge.mnemonic.txt
└── rewards/
    └── [same structure as pledge]
```

## Next Steps

1. **For Development**: Use the simplified version as fallback
2. **For Production**: Install real Cardano tools manually
3. **For Testing**: Use the simplified version with small amounts
4. **For Mainnet**: Use real tools with proper security measures
5. **For Complete Setup**: Use `--complete` with real tools

## Support

- **Documentation**: Check README.md and USAGE.md
- **Complete Guide**: See `docs/COMPLETE_STAKE_POOL_GUIDE.md`
- **Issues**: Report on GitHub
- **Community**: Join Cardano Discord channels
