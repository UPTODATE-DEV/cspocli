# Usage Guide - Cardano SPO CLI

## 🚀 Quick Installation

### Linux/macOS

```bash
# Clone the repository
git clone https://github.com/your-repo/cardano-spo-cli.git
cd cardano-spo-cli

# Install
chmod +x install.sh
./install.sh
```

### Windows

```bash
# Clone the repository
git clone https://github.com/your-repo/cardano-spo-cli.git
cd cardano-spo-cli

# Install
install.bat
```

### Manual installation

```bash
python3 -m pip install --user requests click cryptography mnemonic bech32 colorama tqdm
python3 -m pip install --user -e .
```

## 📖 Usage

### Generate a pledge wallet

```bash
cspocli generate --ticker MYPOOL --purpose pledge
```

### Generate a rewards wallet

```bash
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
- `--purpose, -p` : Wallet purpose (pledge or rewards)
- `--force, -f` : Force regeneration of existing files
- `--simple, -s` : Use simplified version
- `--no-banner` : Do not display banner
- `--quiet, -q` : Quiet mode (JSON output)

### Usage examples

#### Basic generation

```bash
cspocli generate --ticker MYPOOL --purpose pledge
```

#### Generation with custom directory

```bash
cspocli generate --ticker MYPOOL --purpose rewards
```

#### Quiet mode (for scripts)

```bash
cspocli generate --ticker MYPOOL --purpose pledge --quiet --no-banner
```

#### Force regeneration

```bash
cspocli generate --ticker MYPOOL --purpose pledge --force
```

## 📁 Generated files

For each wallet, the CLI generates the following files:

### Main files

- `TICKER-purpose.base_addr` - Base address for pledge
- `TICKER-purpose.reward_addr` - Staking address for rewards
- `TICKER-purpose.staking_skey` - Staking private key (SENSITIVE)
- `TICKER-purpose.staking_vkey` - Staking public key
- `TICKER-purpose.mnemonic.txt` - Recovery phrase (SENSITIVE)

### Example structure

```
~/.CSPO_MYPOOL/
└── pledge/
    ├── MYPOOL-pledge.base_addr
    ├── MYPOOL-pledge.reward_addr
    ├── MYPOOL-pledge.staking_skey
    ├── MYPOOL-pledge.staking_vkey
    └── MYPOOL-pledge.mnemonic.txt
```

## 🔐 Security

### Sensitive files

The following files contain sensitive information:

- `*.mnemonic.txt` - 24-word recovery phrase
- `*.staking_skey` - Staking private key

These files are automatically protected with `600` permissions (read/write for owner only).

### Best practices

1. **Secure storage**: Store the recovery phrase on paper in a safe
2. **Encrypted backup**: Create an encrypted copy of sensitive files
3. **Secure environment**: Use a dedicated and secure computer
4. **Never share**: Never share your private keys

## 📋 Steps after generation

### 1. Import the wallet

```bash
# Read the recovery phrase
cat ~/.CSPO_MYPOOL/pledge/MYPOOL-pledge.mnemonic.txt
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

- `MYPOOL-pledge.base_addr`
- `MYPOOL-pledge.reward_addr`
- `MYPOOL-pledge.staking_skey`
- `MYPOOL-pledge.staking_vkey`

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

### Debug mode

```bash
cspocli generate --ticker MYPOOL --purpose pledge --verbose
```

## 📞 Support

- **Email**: support@cardano-spo-cli.org
- **Discord**: Join our Discord server
- **Documentation**: Check README.md

## ⚠️ Warnings

- This CLI generates sensitive private keys
- Always test with small amounts first
- Rewards are paid with a two-epoch delay
- Always maintain balance above declared pledge level
- Simplified version: Uses Python-native cryptography as fallback
