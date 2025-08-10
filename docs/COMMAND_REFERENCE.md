# Cardano SPO CLI v1.1.0 - Command Reference

## Overview

The Cardano SPO CLI provides a professional interface for generating secure Cardano wallets for stake pool operations. All commands are designed to be clear, informative, and user-friendly.

## Main Commands

### `cspocli --help`

Display the main help menu with all available commands.

**Output:**

- List of all available commands
- Brief description of each command
- Usage examples

---

### `cspocli generate` - Generate Wallet

Generate secure Cardano wallets for stake pool operations.

#### Basic Usage

```bash
# Generate all wallets (pledge + rewards) with shared mnemonic
cspocli generate --ticker MYPOOL

# Generate complete stake pool files
cspocli generate --ticker MYPOOL --complete

# Generate specific wallet type
cspocli generate --ticker MYPOOL --purpose pledge
```

#### Required Options

| Option     | Short | Description             | Example           |
| ---------- | ----- | ----------------------- | ----------------- |
| `--ticker` | `-t`  | Your pool ticker symbol | `--ticker MYPOOL` |

#### Optional Options

| Option        | Short | Description                              | Default   |
| ------------- | ----- | ---------------------------------------- | --------- |
| `--purpose`   | `-p`  | Wallet purpose (pledge, rewards, all)    | `all`     |
| `--network`   | `-n`  | Cardano network (mainnet, testnet, etc.) | `mainnet` |
| `--complete`  | `-c`  | Generate complete stake pool files       | `false`   |
| `--force`     | `-f`  | Force regeneration even if wallet exists | `false`   |
| `--no-banner` |       | Skip welcome banner display              | `false`   |
| `--quiet`     | `-q`  | Quiet mode - JSON output only            | `false`   |
| `--simple`    | `-s`  | Use simplified mode (no external tools)  | `false`   |

#### Examples

**Generate all wallets (recommended):**

```bash
cspocli generate --ticker MYPOOL
```

**Generate complete stake pool files:**

```bash
cspocli generate --ticker MYPOOL --complete
```

**Generate specific wallet with complete files:**

```bash
cspocli generate --ticker MYPOOL --purpose pledge --complete
```

**Generate testnet wallets:**

```bash
cspocli generate --ticker MYPOOL --network testnet --complete
```

**Generate rewards wallet with simplified mode:**

```bash
cspocli generate -t ADA -p rewards --simple
```

**Force regeneration of existing wallet:**

```bash
cspocli generate --ticker CARDANO --purpose pledge --force
```

**Quiet mode for scripting:**

```bash
cspocli generate --ticker TEST --purpose pledge --quiet --no-banner
```

#### Generated Files

##### Standard Mode

For each wallet, the CLI creates these files in `~/.CSPO_{TICKER}/{PURPOSE}/`:

| File                              | Description                 | Security      |
| --------------------------------- | --------------------------- | ------------- |
| `{TICKER}-{PURPOSE}.base_addr`    | Address for pledge funds    | Public        |
| `{TICKER}-{PURPOSE}.reward_addr`  | Address for staking rewards | Public        |
| `{TICKER}-{PURPOSE}.staking_skey` | Private staking key         | **SENSITIVE** |
| `{TICKER}-{PURPOSE}.staking_vkey` | Public staking key          | Public        |
| `{TICKER}-{PURPOSE}.mnemonic.txt` | 24-word recovery phrase     | **SENSITIVE** |

##### Complete Mode (`--complete`)

Generates all files needed for complete stake pool operations:

**Addresses:**

- `base.addr` - Base address (with staking)
- `payment.addr` - Payment-only address
- `reward.addr` - Reward address

**Keys:**

- `payment.skey/vkey` - Payment keys
- `stake.skey/vkey` - Staking keys
- `cc-cold.skey/vkey` - Cold keys (stake pool)
- `cc-hot.skey/vkey` - Hot keys (stake pool)
- `drep.skey/vkey` - DRep keys
- `ms_payment.skey/vkey` - Multi-signature payment keys
- `ms_stake.skey/vkey` - Multi-signature staking keys
- `ms_drep.skey/vkey` - Multi-signature DRep keys

**Credentials:**

- `payment.cred` - Payment credential
- `stake.cred` - Staking credential
- `ms_payment.cred` - Multi-signature payment credential
- `ms_stake.cred` - Multi-signature staking credential

**Certificates:**

- `stake.cert` - Staking certificate
- `delegation.cert` - Delegation certificate

#### Shared Mnemonic Feature

- All wallets for the same ticker share the same recovery phrase
- Stored in `~/.CSPO_{TICKER}/{TICKER}-shared.mnemonic.txt`
- Makes wallet management easier and more secure

---

### `cspocli export` - Export Wallet

Export wallet files in encrypted ZIP format for secure backup and transfer.

#### Usage

```bash
cspocli export --ticker MYPOOL --purpose pledge --password mypassword
```

#### Options

| Option       | Description                     | Required |
| ------------ | ------------------------------- | -------- |
| `--ticker`   | Pool ticker symbol              | Yes      |
| `--purpose`  | Wallet purpose (pledge/rewards) | Yes      |
| `--password` | Password for encrypted ZIP      | Yes      |

#### Output

- Creates encrypted ZIP archive
- Contains all wallet files
- Protected with provided password
- Suitable for secure backup and transfer

---

### `cspocli version` - Version Information

Display version and build information.

#### Usage

```bash
cspocli version
```

#### Output

- Current version number
- Git commit hash
- Build status (clean/dirty)

**Example:**

```
Cardano SPO CLI v1.0.0+fe1e288
Commit: fe1e288
⚠️  Working tree has uncommitted changes
```

---

## Command Help

### Get help for any command:

```bash
cspocli --help              # Main help
cspocli generate --help     # Generate command help
cspocli export --help       # Export command help
cspocli version --help      # Version command help
```

---

## Usage Patterns

### 1. Interactive Mode (Default)

```bash
cspocli generate --ticker MYPOOL
```

- Shows welcome banner
- Displays security warnings
- Asks for confirmation
- Shows detailed output
- Provides next steps

### 2. Complete Stake Pool Generation

```bash
cspocli generate --ticker MYPOOL --complete
```

- Generates all stake pool files
- Creates keys, addresses, credentials, certificates
- Requires real Cardano tools
- Professional stake pool setup

### 3. Scripting Mode

```bash
cspocli generate --ticker TEST --purpose pledge --quiet --no-banner
```

- No interactive prompts
- JSON output for parsing
- No banners or warnings
- Suitable for automation

### 4. Simplified Mode

```bash
cspocli generate --ticker ADA --purpose rewards --simple
```

- Uses Python-native cryptography
- No external Cardano tools required
- Good for testing and development
- Faster execution

### 5. Force Mode

```bash
cspocli generate --ticker MYPOOL --purpose pledge --force
```

- Overwrites existing wallets
- No confirmation prompts
- Useful for regeneration

### 6. Network-Specific Generation

```bash
cspocli generate --ticker MYPOOL --network testnet --complete
```

- Generates for specific network
- Supports mainnet, testnet, preview, preprod
- Network-specific addresses and keys

---

## Security Considerations

### File Permissions

All generated files have secure permissions:

- Private keys: `600` (owner read/write only)
- Public files: `644` (owner read/write, others read)

### Storage Location

All wallets are stored in the user's home directory:

```
~/.CSPO_{TICKER}/
├── {TICKER}-shared.mnemonic.txt
├── pledge/
│   └── [wallet files]
└── rewards/
    └── [wallet files]
```

### Sensitive Files

These files contain sensitive information and should be handled carefully:

- `*.skey` - All private keys
- `*.mnemonic.txt` - 24-word recovery phrase
- `{TICKER}-shared.mnemonic.txt` - Shared recovery phrase

---

## Error Handling

### Common Errors

| Error                               | Cause                              | Solution                         |
| ----------------------------------- | ---------------------------------- | -------------------------------- |
| `Missing command`                   | No command specified               | Use `cspocli --help`             |
| `Missing option`                    | Required option not provided       | Check `cspocli generate --help`  |
| `Wallet already exists`             | Wallet directory exists            | Use `--force` flag               |
| `Invalid ticker`                    | Ticker contains invalid characters | Use alphanumeric characters only |
| `Real tools not available`          | Cardano tools missing              | Use `--simple` flag              |
| `Complete mode requires real tools` | Complete mode needs tools          | Use standard mode instead        |

### Troubleshooting

1. **Check version:** `cspocli version`
2. **Get help:** `cspocli --help`
3. **Check command help:** `cspocli generate --help`
4. **Use quiet mode:** Add `--quiet` flag for JSON output
5. **Use simplified mode:** Add `--simple` flag if tools unavailable
6. **Check network:** Ensure correct `--network` option

---

## Support

For technical support:

- Email: support@cardano-spo-cli.org
- Documentation: See `docs/` folder
- Examples: See `README.md`
