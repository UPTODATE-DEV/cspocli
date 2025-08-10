# Usage Guide - Cardano SPO CLI

## 🚀 Quick Installation

### Recommended Installation

```bash
# Install globally (recommended)
make install
```

### Alternative Installation Methods

#### Linux/macOS

```bash
# Clone the repository
git clone https://github.com/your-repo/cardano-spo-cli.git
cd cardano-spo-cli

# Install
chmod +x install.sh
./install.sh
```

#### Windows

```bash
# Clone the repository
git clone https://github.com/your-repo/cardano-spo-cli.git
cd cardano-spo-cli

# Install
install.bat
```

#### Manual installation

```bash
python3 -m pip install --user requests click cryptography mnemonic bech32 colorama tqdm
python3 -m pip install --user -e .
```

## 📖 Usage

### Generate all wallets (recommended)

```bash
# Generate both pledge and rewards wallets with shared mnemonic
cspocli generate --ticker MYPOOL
```

### Generate complete stake pool files

```bash
# Generate all files needed for stake pool operations
cspocli generate --ticker MYPOOL --complete
```

### Generate specific wallet types

```bash
# Generate pledge wallet only
cspocli generate --ticker MYPOOL --purpose pledge

# Generate rewards wallet only
cspocli generate --ticker MYPOOL --purpose rewards
```

### Check version

```bash
cspocli version
```

### Available options

```bash
cspocli --help
```

**Main options:**

- `--ticker, -t` : Your pool ticker (ex: MYPOOL)
- `--purpose, -p` : Wallet purpose (pledge, rewards, or all - default: all)
- `--complete, -c` : Generate complete stake pool files (all keys, addresses, credentials, certificates)
- `--network, -n` : Cardano network (mainnet, testnet, preview, preprod - default: mainnet)
- `--force, -f` : Force regeneration of existing files
- `--simple, -s` : Use simplified version
- `--no-banner` : Do not display banner
- `--quiet, -q` : Quiet mode (JSON output)

### Usage examples

#### Basic generation (all wallets)

```bash
cspocli generate --ticker MYPOOL
```

#### Complete stake pool generation

```bash
cspocli generate --ticker MYPOOL --complete
```

#### Specific wallet with complete files

```bash
cspocli generate --ticker MYPOOL --purpose pledge --complete
```

#### Testnet generation

```bash
cspocli generate --ticker MYPOOL --network testnet --complete
```

#### Quiet mode (for scripts)

```bash
cspocli generate --ticker MYPOOL --complete --quiet --no-banner
```

#### Force regeneration

```bash
cspocli generate --ticker MYPOOL --complete --force
```

## 📁 Generated files

### Standard Mode

For each wallet, the CLI generates the following files:

#### Main files

- `TICKER-purpose.base_addr` - Base address for pledge
- `TICKER-purpose.reward_addr` - Staking address for rewards
- `TICKER-purpose.staking_skey` - Staking private key (SENSITIVE)
- `TICKER-purpose.staking_vkey` - Staking public key
- `TICKER-purpose.mnemonic.txt` - Recovery phrase (SENSITIVE)

#### Example structure

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

### Complete Mode (`--complete`)

Generates all files needed for complete stake pool operations:

#### Addresses

- `base.addr` - Base address (with staking)
- `payment.addr` - Payment-only address
- `reward.addr` - Reward address

#### Keys

- `payment.skey/vkey` - Payment keys
- `stake.skey/vkey` - Staking keys
- `cc-cold.skey/vkey` - Cold keys (stake pool)
- `cc-hot.skey/vkey` - Hot keys (stake pool)
- `drep.skey/vkey` - DRep keys
- `ms_payment.skey/vkey` - Multi-signature payment keys
- `ms_stake.skey/vkey` - Multi-signature staking keys
- `ms_drep.skey/vkey` - Multi-signature DRep keys

#### Credentials

- `payment.cred` - Payment credential
- `stake.cred` - Staking credential
- `ms_payment.cred` - Multi-signature payment credential
- `ms_stake.cred` - Multi-signature staking credential

#### Certificates

- `stake.cert` - Staking certificate
- `delegation.cert` - Delegation certificate

#### Example complete structure

```
~/.CSPO_MYPOOL/
├── MYPOOL-shared.mnemonic.txt
└── pledge/
    ├── base.addr
    ├── payment.addr
    ├── reward.addr
    ├── payment.skey
    ├── payment.vkey
    ├── stake.skey
    ├── stake.vkey
    ├── cc-cold.skey
    ├── cc-cold.vkey
    ├── cc-hot.skey
    ├── cc-hot.vkey
    ├── drep.skey
    ├── drep.vkey
    ├── ms_payment.skey
    ├── ms_payment.vkey
    ├── ms_stake.skey
    ├── ms_stake.vkey
    ├── ms_drep.skey
    ├── ms_drep.vkey
    ├── payment.cred
    ├── stake.cred
    ├── ms_payment.cred
    ├── ms_stake.cred
    ├── stake.cert
    ├── delegation.cert
    └── MYPOOL-pledge.mnemonic.txt
```

## 🔐 Security

### Sensitive files

The following files contain sensitive information:

- `*.mnemonic.txt` - 24-word recovery phrase
- `*.skey` - Private keys (all types)
- `MYPOOL-shared.mnemonic.txt` - Shared recovery phrase

These files are automatically protected with `600` permissions (read/write for owner only).

### Shared mnemonic feature

- All wallets for the same ticker share the same recovery phrase
- Stored securely in `~/.CSPO_{TICKER}/{TICKER}-shared.mnemonic.txt`
- Makes wallet management easier and more secure

### Best practices

1. **Secure storage**: Store the recovery phrase on paper in a safe
2. **Encrypted backup**: Create an encrypted copy of sensitive files
3. **Secure environment**: Use a dedicated and secure computer
4. **Never share**: Never share your private keys
5. **Regular backups**: Backup your wallet files regularly

## 📋 Steps after generation

### 1. Import the wallet

```bash
# Read the shared recovery phrase
cat ~/.CSPO_MYPOOL/MYPOOL-shared.mnemonic.txt
```

Import this phrase into a compatible Cardano wallet.

### 2. Configure single-address mode

Make sure your wallet is configured in single-address mode to ensure funds remain on the registered address.

### 3. Transfer funds

```bash
# Read the base address
cat ~/.CSPO_MYPOOL/pledge/MYPOOL-pledge.base_addr
```

Transfer ADA to this address.

### 4. Send files to your stake pool operator

Send the following files via their secure portal:

#### Standard mode

- `MYPOOL-pledge.base_addr`
- `MYPOOL-pledge.reward_addr`
- `MYPOOL-pledge.staking_skey`
- `MYPOOL-pledge.staking_vkey`

#### Complete mode

- All `.addr` files
- All `.vkey` files
- All `.cred` files
- All `.cert` files

## 🔧 Troubleshooting

### Dependency errors

```bash
python3 -m pip install --user requests click cryptography mnemonic bech32 colorama tqdm
```

### Permission errors

```bash
chmod +x install.sh
```

### Cardano tools issues

Use the simplified version:

```bash
cspocli generate --ticker MYPOOL --purpose pledge --simple
```

### Complete mode requires real tools

The `--complete` option requires real Cardano tools. If they're not available:

```bash
# Use standard mode instead
cspocli generate --ticker MYPOOL --purpose pledge
```

### Debug mode

```bash
cspocli generate --ticker MYPOOL --purpose pledge --verbose
```

## 📞 Support

- **Email**: support@cardano-spo-cli.org
- **Issues**: GitHub Issues
- **Documentation**: Check docs/ folder for detailed guides

## ⚠️ Warnings

- This CLI generates sensitive private keys
- Always test with small amounts first
- Rewards are paid with a two-epoch delay
- Always maintain balance above declared pledge level
- Simplified version: Uses Python-native cryptography as fallback
- Complete mode requires real Cardano tools for full functionality
