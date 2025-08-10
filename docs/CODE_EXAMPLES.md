# Code Examples & Expected Outputs - Cardano SPO CLI v1.1.0

This document provides comprehensive code examples for all Cardano SPO CLI commands, including their expected outputs, file structures, and usage patterns.

## 📋 Table of Contents

1. [CLI Overview](#cli-overview)
2. [Core Commands](#core-commands)
3. [Wallet Generation](#wallet-generation)
4. [Security Features](#security-features)
5. [Export Functionality](#export-functionality)
6. [Import Operations](#import-operations)
7. [File Structures](#file-structures)
8. [Error Handling](#error-handling)
9. [Advanced Usage](#advanced-usage)

---

## 🚀 CLI Overview

### Main Help Command

```bash
cspocli --help
```

**Expected Output:**

```
╔══════════════════════════════════════════════════════════════╗
║                    Cardano SPO CLI v1.1.0                    ║
║              Professional Stake Pool Operator Tool           ║
╚══════════════════════════════════════════════════════════════╝

Usage: cspocli [OPTIONS] COMMAND [ARGS]...

  Cardano SPO CLI - Professional Stake Pool Operator Tool

  Generate secure Cardano wallets for stake pool operations.
  Creates 24-word recovery phrases, addresses, and keys for pledge/rewards wallets.

  Files stored in: ~/.CSPO_{TICKER_NAME}/{purpose}/
  Security: Local storage with secure permissions.

Options:
  --help  Show this message and exit.

Commands:
  export       Export wallet files securely
  generate     Generate secure Cardano wallets for stake pool operations
  import-keys  Import existing CNTools keys and generate addresses
  secure       Secure sensitive files with password protection
  version      Show version information
  view         View secured files (requires password)
```

---

## 🔧 Core Commands

### Version Command

```bash
cspocli version
```

**Expected Output:**

```json
{
  "version": "1.1.0",
  "commit_hash": "a1b2c3d",
  "is_dirty": false,
  "full_version": "1.1.0+a1b2c3d"
}
```

---

## 💰 Wallet Generation

### Basic Wallet Generation

```bash
cspocli generate --ticker MYPOOL
```

**Expected Output:**

```
╔══════════════════════════════════════════════════════════════╗
║                    Cardano SPO CLI v1.1.0                    ║
║              Professional Stake Pool Operator Tool           ║
╚══════════════════════════════════════════════════════════════╝

SECURITY WARNING:
• This tool generates real cryptographic keys
• Store recovery phrases securely
• Never share private keys
• Create encrypted backups

Do you want to continue? [Y/n]: y

✅ Using real Cardano tools mode
📋 Using existing shared mnemonic for MYPOOL
🔐 Generating pledge wallet...
🔐 Generating rewards wallet...

✅ Pledge wallet generated successfully
✅ Rewards wallet generated successfully

Next Steps:
1. Import the recovery phrase into a compatible Cardano wallet
2. Transfer funds to the base address for pledge
3. Keep the staking keys secure
4. Monitor your stake pool performance

Files generated in: ~/.CSPO_MYPOOL/pledge/
```

### Complete Stake Pool Generation

```bash
cspocli generate --ticker MYPOOL --complete
```

**Expected Output:**

```
╔══════════════════════════════════════════════════════════════╗
║                    Cardano SPO CLI v1.1.0                    ║
║              Professional Stake Pool Operator Tool           ║
╚══════════════════════════════════════════════════════════════╝

SECURITY WARNING:
• This tool generates real cryptographic keys
• Store recovery phrases securely
• Never share private keys
• Create encrypted backups

Do you want to continue? [Y/n]: y

✅ Using real Cardano tools mode
📋 Using existing shared mnemonic for MYPOOL
🔐 Generating complete pledge wallet...
🔐 Generating complete rewards wallet...

✅ Complete pledge wallet generated successfully
✅ Complete rewards wallet generated successfully

Next Steps:
1. Import the recovery phrase into a compatible Cardano wallet
2. Transfer funds to the base address for pledge
3. Keep the staking keys secure
4. Monitor your stake pool performance

Files generated in: ~/.CSPO_MYPOOL/pledge/
```

### Specific Wallet Generation

```bash
cspocli generate --ticker MYPOOL --purpose pledge
```

**Expected Output:**

```
╔══════════════════════════════════════════════════════════════╗
║                    Cardano SPO CLI v1.1.0                    ║
║              Professional Stake Pool Operator Tool           ║
╚══════════════════════════════════════════════════════════════╝

SECURITY WARNING:
• This tool generates real cryptographic keys
• Store recovery phrases securely
• Never share private keys
• Create encrypted backups

Do you want to continue? [Y/n]: y

✅ Using real Cardano tools mode
📋 Using existing shared mnemonic for MYPOOL
🔐 Generating pledge wallet...

✅ Pledge wallet generated successfully

Next Steps:
1. Import the recovery phrase into a compatible Cardano wallet
2. Transfer funds to the base address for pledge
3. Keep the staking keys secure
4. Monitor your stake pool performance

Files generated in: ~/.CSPO_MYPOOL/pledge/
```

### Testnet Wallet Generation

```bash
cspocli generate --ticker MYPOOL --network testnet
```

**Expected Output:**

```
╔══════════════════════════════════════════════════════════════╗
║                    Cardano SPO CLI v1.1.0                    ║
║              Professional Stake Pool Operator Tool           ║
╚══════════════════════════════════════════════════════════════╝

SECURITY WARNING:
• This tool generates real cryptographic keys
• Store recovery phrases securely
• Never share private keys
• Create encrypted backups

Do you want to continue? [Y/n]: y

✅ Using real Cardano tools mode
📋 Using existing shared mnemonic for MYPOOL
🔐 Generating pledge wallet (testnet)...
🔐 Generating rewards wallet (testnet)...

✅ Pledge wallet generated successfully
✅ Rewards wallet generated successfully

Next Steps:
1. Import the recovery phrase into a compatible Cardano wallet
2. Transfer funds to the base address for pledge
3. Keep the staking keys secure
4. Monitor your stake pool performance

Files generated in: ~/.CSPO_MYPOOL/pledge/
```

### Simplified Mode Generation

```bash
cspocli generate --ticker TEST --purpose pledge --simple
```

**Expected Output:**

```
╔══════════════════════════════════════════════════════════════╗
║                    Cardano SPO CLI v1.1.0                    ║
║              Professional Stake Pool Operator Tool           ║
╚══════════════════════════════════════════════════════════════╝

SECURITY WARNING:
• This tool generates real cryptographic keys
• Store recovery phrases securely
• Never share private keys
• Create encrypted backups

Do you want to continue? [Y/n]: y

⚠️  Using simplified mode (no external tools)
🔐 Generating pledge wallet...

✅ Pledge wallet generated successfully

Next Steps:
1. Import the recovery phrase into a compatible Cardano wallet
2. Transfer funds to the base address for pledge
3. Keep the staking keys secure
4. Monitor your stake pool performance

Files generated in: ~/.CSPO_TEST/pledge/
```

### Force Regeneration

```bash
cspocli generate --ticker MYPOOL --purpose pledge --force
```

**Expected Output:**

```
╔══════════════════════════════════════════════════════════════╗
║                    Cardano SPO CLI v1.1.0                    ║
║              Professional Stake Pool Operator Tool           ║
╚══════════════════════════════════════════════════════════════╝

SECURITY WARNING:
• This tool generates real cryptographic keys
• Store recovery phrases securely
• Never share private keys
• Create encrypted backups

⚠️  Wallet MYPOOL-pledge already exists
Do you want to regenerate it? [y/N]: y

✅ Using real Cardano tools mode
📋 Using existing shared mnemonic for MYPOOL
🔐 Generating pledge wallet...

✅ Pledge wallet generated successfully

Next Steps:
1. Import the recovery phrase into a compatible Cardano wallet
2. Transfer funds to the base address for pledge
3. Keep the staking keys secure
4. Monitor your stake pool performance

Files generated in: ~/.CSPO_MYPOOL/pledge/
```

### Quiet Mode Generation

```bash
cspocli generate --ticker MYPOOL --purpose pledge --quiet --no-banner
```

**Expected Output:**

```json
{
  "status": "success",
  "ticker": "MYPOOL",
  "purpose": "pledge",
  "network": "mainnet",
  "wallet_dir": "~/.CSPO_MYPOOL/pledge",
  "files_generated": [
    "MYPOOL-pledge.base_addr",
    "MYPOOL-pledge.reward_addr",
    "MYPOOL-pledge.staking_skey",
    "MYPOOL-pledge.staking_vkey",
    "MYPOOL-pledge.mnemonic.txt"
  ],
  "message": "Pledge wallet generated successfully"
}
```

---

## 🔒 Security Features

### Secure Files Command

```bash
cspocli secure --ticker MYPOOL --purpose pledge --password mysecurepass
```

**Expected Output:**

```
╔══════════════════════════════════════════════════════════════╗
║                    Cardano SPO CLI v1.1.0                    ║
║              Professional Stake Pool Operator Tool           ║
╚══════════════════════════════════════════════════════════════╝

🔒 Securing sensitive files for MYPOOL-pledge...

✅ Secured: MYPOOL-pledge.staking_skey → MYPOOL-pledge.staking_skey.enc
✅ Secured: MYPOOL-pledge.mnemonic.txt → MYPOOL-pledge.mnemonic.txt.enc

🎉 All sensitive files secured successfully!
📁 Original files replaced with encrypted versions
🔑 Use the same password to view or restore files
```

### View Secured Files Command

```bash
cspocli view --ticker MYPOOL --purpose pledge --password mysecurepass
```

**Expected Output:**

```
╔══════════════════════════════════════════════════════════════╗
║                    Cardano SPO CLI v1.1.0                    ║
║              Professional Stake Pool Operator Tool           ║
╚══════════════════════════════════════════════════════════════╝

🔓 Decrypting files for MYPOOL-pledge...

📁 Available secured files:
1. MYPOOL-pledge.staking_skey.enc
2. MYPOOL-pledge.mnemonic.txt.enc

💡 Use --file option to view specific file content
   Example: cspocli view --ticker MYPOOL --purpose pledge --password mypass --file mnemonic.txt
```

### View Specific File Command

```bash
cspocli view --ticker MYPOOL --purpose pledge --password mysecurepass --file mnemonic.txt
```

**Expected Output:**

```
╔══════════════════════════════════════════════════════════════╗
║                    Cardano SPO CLI v1.1.0                    ║
║              Professional Stake Pool Operator Tool           ║
╚══════════════════════════════════════════════════════════════╝

🔓 Decrypting file: MYPOOL-pledge.mnemonic.txt.enc

📝 Recovery Phrase (24 words):
abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon art

⚠️  Keep this phrase secure and never share it!
```

---

## 📦 Export Functionality

### Export Wallet Command

```bash
cspocli export --ticker MYPOOL --purpose pledge --password mypassword
```

**Expected Output:**

```
╔══════════════════════════════════════════════════════════════╗
║                    Cardano SPO CLI v1.1.0                    ║
║              Professional Stake Pool Operator Tool           ║
╚══════════════════════════════════════════════════════════════╝

📦 Exporting wallet files for MYPOOL-pledge...

✅ Added to export: MYPOOL-pledge.base_addr
✅ Added to export: MYPOOL-pledge.reward_addr
✅ Added to export: MYPOOL-pledge.staking_skey
✅ Added to export: MYPOOL-pledge.staking_vkey

🔐 Encrypted export created: ~/.CSPO_MYPOOL/pledge/MYPOOL-pledge-export.zip.enc
🔑 Key file saved: ~/.CSPO_MYPOOL/pledge/MYPOOL-pledge-export.key
🔒 Password for decryption: mypassword

🎉 Export completed successfully!
📁 Files are encrypted and ready for secure transfer
```

---

## 🔄 Import Operations

### Import Keys Command

```bash
cspocli import-keys --ticker MYPOOL --purpose pledge \
  --payment-vkey /path/to/payment.vkey \
  --payment-skey /path/to/payment.skey \
  --stake-vkey /path/to/stake.vkey \
  --stake-skey /path/to/stake.skey
```

**Expected Output:**

```
╔══════════════════════════════════════════════════════════════╗
║                    Cardano SPO CLI v1.1.0                    ║
║              Professional Stake Pool Operator Tool           ║
╚══════════════════════════════════════════════════════════════╝

📥 Importing existing CNTools keys for MYPOOL-pledge...

✅ Payment verification key imported: /path/to/payment.vkey
✅ Payment signing key imported: /path/to/payment.skey
✅ Stake verification key imported: /path/to/stake.vkey
✅ Stake signing key imported: /path/to/stake.skey

🔐 Generating addresses from imported keys...
✅ Base address generated: addr1q9...
✅ Reward address generated: stake1...

🎉 Import completed successfully!
📁 Wallet files generated in: ~/.CSPO_MYPOOL/pledge/
```

---

## 📁 File Structures

### Standard Wallet Structure

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

### Complete Wallet Structure

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
│   └── delegation.cert
└── rewards/
    └── [same structure as pledge]
```

### Secured Wallet Structure

```
~/.CSPO_MYPOOL/
├── MYPOOL-shared.mnemonic.txt
├── pledge/
│   ├── MYPOOL-pledge.base_addr
│   ├── MYPOOL-pledge.reward_addr
│   ├── MYPOOL-pledge.staking_vkey
│   ├── MYPOOL-pledge.staking_skey.enc
│   └── MYPOOL-pledge.mnemonic.txt.enc
└── rewards/
    └── [same structure as pledge]
```

### Export Structure

```
~/.CSPO_MYPOOL/
├── pledge/
│   ├── MYPOOL-pledge-export.zip.enc
│   └── MYPOOL-pledge-export.key
└── rewards/
    ├── MYPOOL-rewards-export.zip.enc
    └── MYPOOL-rewards-export.key
```

---

## ❌ Error Handling

### Missing Tools Error

```bash
cspocli generate --ticker MYPOOL
```

**Expected Error Output:**

```
╔══════════════════════════════════════════════════════════════╗
║                    Cardano SPO CLI v1.1.0                    ║
║              Professional Stake Pool Operator Tool           ║
╚══════════════════════════════════════════════════════════════╝

SECURITY WARNING:
• This tool generates real cryptographic keys
• Store recovery phrases securely
• Never share private keys
• Create encrypted backups

Do you want to continue? [Y/n]: y

❌ Error: Real Cardano tools not available. Use --simple flag for simplified mode.
```

### Invalid Ticker Error

```bash
cspocli generate --ticker ""
```

**Expected Error Output:**

```
Error: Invalid value for '--ticker': '' is not a valid string.
```

### Missing Password Error

```bash
cspocli secure --ticker MYPOOL --purpose pledge
```

**Expected Error Output:**

```
Error: Missing option '--password'.
```

### File Not Found Error

```bash
cspocli export --ticker INVALID --purpose pledge --password mypass
```

**Expected Error Output:**

```
╔══════════════════════════════════════════════════════════════╗
║                    Cardano SPO CLI v1.1.0                    ║
║              Professional Stake Pool Operator Tool           ║
╚══════════════════════════════════════════════════════════════╝

❌ Error: Cannot export: missing required files
```

---

## 🚀 Advanced Usage

### Batch Processing with Quiet Mode

```bash
# Generate multiple wallets in sequence
for ticker in POOL1 POOL2 POOL3; do
  cspocli generate --ticker $ticker --purpose pledge --quiet --no-banner
done
```

**Expected Output:**

```json
{"status": "success", "ticker": "POOL1", "purpose": "pledge", "message": "Pledge wallet generated successfully"}
{"status": "success", "ticker": "POOL2", "purpose": "pledge", "message": "Pledge wallet generated successfully"}
{"status": "success", "ticker": "POOL3", "purpose": "pledge", "message": "Pledge wallet generated successfully"}
```

### Network-Specific Generation

```bash
# Generate wallets for different networks
cspocli generate --ticker TESTNET --network testnet --complete
cspocli generate --ticker PREVIEW --network preview --complete
cspocli generate --ticker PREPROD --network preprod --complete
cspocli generate --ticker MAINNET --network mainnet --complete
```

### Security Workflow

```bash
# Complete security workflow
cspocli generate --ticker SECURE --purpose pledge --complete
cspocli secure --ticker SECURE --purpose pledge --password mysecurepass
cspocli export --ticker SECURE --purpose pledge --password myexportpass
```

### Import and Export Workflow

```bash
# Import existing keys and export securely
cspocli import-keys --ticker IMPORT --purpose pledge \
  --payment-vkey /path/to/payment.vkey \
  --payment-skey /path/to/payment.skey \
  --stake-vkey /path/to/stake.vkey \
  --stake-skey /path/to/stake.skey

cspocli export --ticker IMPORT --purpose pledge --password mypass
```

---

## 📊 Output Formats

### Standard Output Format

All commands provide human-readable output with:

- Color-coded status messages
- Clear success/error indicators
- File paths and locations
- Next steps guidance

### JSON Output Format (Quiet Mode)

When using `--quiet` flag, commands return structured JSON:

```json
{
  "status": "success|error",
  "ticker": "string",
  "purpose": "string",
  "network": "string",
  "wallet_dir": "string",
  "files_generated": ["array"],
  "message": "string",
  "error": "string (if applicable)"
}
```

### Error Output Format

Errors include:

- Clear error description
- Suggested solutions
- Command usage hints
- File path information

---

## 🔧 Troubleshooting

### Common Issues and Solutions

1. **Tools Not Available**

   - Use `--simple` flag for Python-native mode
   - Install Cardano tools manually (see REAL_TOOLS.md)

2. **Permission Denied**

   - Check file permissions
   - Ensure proper ownership
   - Use appropriate user account

3. **Wallet Already Exists**

   - Use `--force` flag to regenerate
   - Choose different ticker name
   - Remove existing wallet directory

4. **Encryption/Decryption Failures**
   - Verify password correctness
   - Check file integrity
   - Ensure proper file extensions

---

## 📝 Code Examples Summary

This documentation covers all major Cardano SPO CLI commands with:

- **Command syntax** and options
- **Expected outputs** and formats
- **File structures** and organization
- **Error handling** and troubleshooting
- **Advanced usage** patterns
- **Security workflows** and best practices

For additional information, refer to:

- [Command Reference](COMMAND_REFERENCE.md)
- [Security Guide](SECURITY_GUIDE.md)
- [Complete Stake Pool Guide](COMPLETE_STAKE_POOL_GUIDE.md)
- [Export & Upload Guide](EXPORT_AND_UPLOAD_GUIDE.md)

---

_Last updated: December 2024 - Cardano SPO CLI v1.1.0_
