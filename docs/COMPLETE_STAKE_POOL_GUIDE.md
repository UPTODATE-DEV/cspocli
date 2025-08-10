# Complete Stake Pool Generation Guide - Cardano SPO CLI v1.1.0

## Overview

The `--complete` option generates all files necessary for professional stake pool operations. This includes addresses, keys, credentials, and certificates needed for complete stake pool setup and management.

## Quick Start

```bash
# Generate complete stake pool files for all wallets
cspocli generate --ticker MYPOOL --complete

# Generate complete files for specific wallet
cspocli generate --ticker MYPOOL --purpose pledge --complete

# Generate for testnet
cspocli generate --ticker MYPOOL --network testnet --complete
```

## Generated Files

### Addresses

| File           | Type            | Description                     | Example     |
| -------------- | --------------- | ------------------------------- | ----------- |
| `base.addr`    | Base Address    | Address with staking capability | `addr1q...` |
| `payment.addr` | Payment Address | Payment-only address            | `addr1v...` |
| `reward.addr`  | Reward Address  | Staking reward address          | `stake1...` |

### Keys

#### Payment Keys

- `payment.skey` - Private payment key
- `payment.vkey` - Public payment key

#### Staking Keys

- `stake.skey` - Private staking key
- `stake.vkey` - Public staking key

#### Cold Keys (Stake Pool)

- `cc-cold.skey` - Private cold key
- `cc-cold.vkey` - Public cold key

#### Hot Keys (Stake Pool)

- `cc-hot.skey` - Private hot key
- `cc-hot.vkey` - Public hot key

#### DRep Keys (Delegation Representative)

- `drep.skey` - Private DRep key
- `drep.vkey` - Public DRep key

#### Multi-Signature Keys

- `ms_payment.skey` - Private multi-signature payment key
- `ms_payment.vkey` - Public multi-signature payment key
- `ms_stake.skey` - Private multi-signature staking key
- `ms_stake.vkey` - Public multi-signature staking key
- `ms_drep.skey` - Private multi-signature DRep key
- `ms_drep.vkey` - Public multi-signature DRep key

### Credentials

| File              | Type                  | Description                         |
| ----------------- | --------------------- | ----------------------------------- |
| `payment.cred`    | Payment Credential    | Hash of payment public key          |
| `stake.cred`      | Staking Credential    | Hash of staking public key          |
| `ms_payment.cred` | MS Payment Credential | Hash of multi-signature payment key |
| `ms_stake.cred`   | MS Staking Credential | Hash of multi-signature staking key |

### Certificates

| File              | Type                   | Description                            |
| ----------------- | ---------------------- | -------------------------------------- |
| `stake.cert`      | Staking Certificate    | Stake address registration certificate |
| `delegation.cert` | Delegation Certificate | Stake delegation certificate           |

## File Structure

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

## Key Derivation Paths

All keys are derived from the same root key using BIP44 paths:

| Key Type   | Derivation Path      | Purpose                   |
| ---------- | -------------------- | ------------------------- |
| Payment    | `1852H/1815H/0H/0/0` | Payment transactions      |
| Staking    | `1852H/1815H/0H/2/0` | Staking operations        |
| Cold       | `1852H/1815H/0H/0/0` | Stake pool cold key       |
| Hot        | `1852H/1815H/0H/2/0` | Stake pool hot key        |
| DRep       | `1852H/1815H/0H/3/0` | Delegation representative |
| MS Payment | `1852H/1815H/0H/4/0` | Multi-signature payment   |
| MS Stake   | `1852H/1815H/0H/5/0` | Multi-signature staking   |
| MS DRep    | `1852H/1815H/0H/6/0` | Multi-signature DRep      |

## Security Features

### File Permissions

- Private keys (`.skey` files): `600` (owner read/write only)
- Public keys (`.vkey` files): `644` (owner read/write, others read)
- Addresses (`.addr` files): `644` (owner read/write, others read)
- Credentials (`.cred` files): `644` (owner read/write, others read)
- Certificates (`.cert` files): `644` (owner read/write, others read)

### Shared Mnemonic

- All wallets for the same ticker share the same recovery phrase
- Stored securely in `{TICKER}-shared.mnemonic.txt`
- Makes wallet management easier and more secure

## Usage Examples

### Basic Complete Generation

```bash
# Generate all files for both pledge and rewards wallets
cspocli generate --ticker MYPOOL --complete
```

### Specific Wallet Complete Generation

```bash
# Generate complete files for pledge wallet only
cspocli generate --ticker MYPOOL --purpose pledge --complete
```

### Network-Specific Generation

```bash
# Generate complete files for testnet
cspocli generate --ticker MYPOOL --network testnet --complete

# Generate complete files for preview
cspocli generate --ticker MYPOOL --network preview --complete
```

### Quiet Mode for Scripting

```bash
# Generate complete files with JSON output
cspocli generate --ticker MYPOOL --complete --quiet
```

## Requirements

### Real Cardano Tools

The `--complete` option requires real Cardano tools to be available:

- `cardano-address` - For key derivation and address generation
- `cardano-cli` - For certificate generation (optional)

### Fallback Behavior

If real tools are not available:

1. The CLI will show an error message
2. Use standard mode instead: `cspocli generate --ticker MYPOOL`
3. Or use simplified mode: `cspocli generate --ticker MYPOOL --simple`

## Next Steps

### 1. Import Recovery Phrase

```bash
# Read the shared recovery phrase
cat ~/.CSPO_MYPOOL/MYPOOL-shared.mnemonic.txt
```

Import this phrase into a compatible Cardano wallet.

### 2. Transfer Funds

```bash
# Read the base address for pledge
cat ~/.CSPO_MYPOOL/pledge/base.addr
```

Transfer ADA to this address for your pledge.

### 3. Configure Stake Pool

Use the generated files to configure your stake pool:

- Cold keys for offline operations
- Hot keys for online operations
- Certificates for registration and delegation

### 4. Backup Securely

Create encrypted backups of all sensitive files:

```bash
cspocli export --ticker MYPOOL --purpose pledge --password mypassword
```

## Troubleshooting

### Common Issues

1. **"Real tools not available"**

   - Install Cardano tools: `make install`
   - Or use standard mode instead

2. **"Complete mode requires real tools"**

   - The complete mode needs real Cardano tools
   - Use standard mode: `cspocli generate --ticker MYPOOL`

3. **Permission errors**

   - Ensure you have write permissions to `~/.CSPO_{TICKER}/`
   - Check file permissions: `ls -la ~/.CSPO_MYPOOL/`

4. **Network-specific issues**
   - Verify network parameter: `--network mainnet/testnet/preview/preprod`
   - Check address prefixes match expected network

### Verification

Verify your generated files:

```bash
# Check file count
ls -la ~/.CSPO_MYPOOL/pledge/ | wc -l

# Verify addresses are valid
cat ~/.CSPO_MYPOOL/pledge/base.addr
cat ~/.CSPO_MYPOOL/pledge/payment.addr
cat ~/.CSPO_MYPOOL/pledge/reward.addr

# Check key formats
head -1 ~/.CSPO_MYPOOL/pledge/payment.vkey
head -1 ~/.CSPO_MYPOOL/pledge/stake.vkey
```

## Support

For technical support:

- Email: support@cardano-spo-cli.org
- Documentation: See other guides in `docs/` folder
- Examples: See `README.md` and `USAGE.md`
