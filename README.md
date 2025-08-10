# Cardano SPO CLI v1.1.0

Professional Cardano Stake Pool Operator CLI tool with complete stake pool file generation and management.

## Features

- **Complete Stake Pool Generation**: Generate all necessary files for stake pool operations
- **CNTools Import**: Import existing CNTools keys and generate compatible addresses
- **Shared Mnemonic**: Same recovery phrase for all wallets of a ticker
- **Cross-Platform**: Works on macOS, Linux, and Windows
- **Real Tools Integration**: Uses official Cardano tools when available
- **Simplified Mode**: Fallback to Python-native implementation
- **Secure Export**: Encrypted ZIP archives for safe backup
- **Password Protection**: AES-256 encryption for sensitive files
- **Professional Output**: Colorized, concise, and user-friendly interface

## Installation

```bash
make install
```

## Quick Start

```bash
# Generate all wallets (pledge + rewards) with shared mnemonic
cspocli generate --ticker MYPOOL

# Generate complete stake pool files (all keys, addresses, credentials, certificates)
cspocli generate --ticker MYPOOL --complete

# Import existing CNTools keys
cspocli import-keys --ticker MYPOOL --purpose pledge \
  --payment-vkey /path/to/payment.vkey \
  --payment-skey /path/to/payment.skey \
  --stake-vkey /path/to/stake.vkey \
  --stake-skey /path/to/stake.skey

# Generate specific wallet type
cspocli generate --ticker MYPOOL --purpose pledge

# Secure sensitive files with password protection
cspocli secure --ticker MYPOOL --purpose pledge --password mysecurepass

# View secured files (requires password)
cspocli view --ticker MYPOOL --purpose pledge --password mysecurepass --file payment.skey

# Export wallet files securely
cspocli export --ticker MYPOOL --purpose pledge --password mypassword
```

## Generated Files

### Standard Mode

- `base_addr` - Address for pledge funds
- `reward_addr` - Address for staking rewards
- `staking_skey` - Private staking key (SENSITIVE)
- `staking_vkey` - Public staking key
- `mnemonic.txt` - 24-word recovery phrase (SENSITIVE)

### Complete Mode (`--complete`)

- **Addresses**: `base.addr`, `payment.addr`, `reward.addr`
- **Keys**: `payment.skey/vkey`, `stake.skey/vkey`, `cc-cold.skey/vkey`, `cc-hot.skey/vkey`, `drep.skey/vkey`, `ms_payment.skey/vkey`, `ms_stake.skey/vkey`, `ms_drep.skey/vkey`
- **Credentials**: `payment.cred`, `stake.cred`, `ms_payment.cred`, `ms_stake.cred`
- **Certificates**: `stake.cert`, `delegation.cert`

## Documentation

- [Documentation Index](docs/README.md) - Complete documentation overview
- [Usage Guide](USAGE.md) - Detailed usage instructions
- [Security Guide](docs/SECURITY_GUIDE.md) - Password protection and security features
- [Export & Upload Guide](docs/EXPORT_AND_UPLOAD_GUIDE.md) - Secure export and upload process
- [Command Reference](docs/COMMAND_REFERENCE.md) - Complete command documentation
- [Complete Stake Pool Guide](docs/COMPLETE_STAKE_POOL_GUIDE.md) - Complete stake pool generation
- [Password Explanation](docs/PASSWORD_EXPLANATION.md) - Why password is needed for installation
- [Export Quick Reference](docs/EXPORT_QUICK_REFERENCE.md) - Quick export commands
- [Code Examples](docs/CODE_EXAMPLES.md) - Complete code examples with expected outputs
- [Real Tools Guide](REAL_TOOLS.md) - Manual Cardano tools installation
- [Changelog](CHANGELOG.md) - Version history and changes

## Support

- **Email**: support@cardano-spo-cli.org
- **Issues**: GitHub Issues
- **Documentation**: See docs/ folder for detailed guides
