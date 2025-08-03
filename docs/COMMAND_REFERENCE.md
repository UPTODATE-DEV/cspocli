# Cardano SPO CLI - Command Reference

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

Generate a secure Cardano wallet for stake pool operations.

#### Basic Usage

```bash
cspocli generate --ticker MYPOOL --purpose pledge
cspocli generate -t ADA -p rewards
```

#### Required Options

| Option      | Short | Description             | Example            |
| ----------- | ----- | ----------------------- | ------------------ |
| `--ticker`  | `-t`  | Your pool ticker symbol | `--ticker MYPOOL`  |
| `--purpose` | `-p`  | Wallet purpose          | `--purpose pledge` |

#### Optional Options

| Option        | Short | Description                              | Default |
| ------------- | ----- | ---------------------------------------- | ------- |
| `--force`     | `-f`  | Force regeneration even if wallet exists | `false` |
| `--no-banner` |       | Skip welcome banner display              | `false` |
| `--quiet`     | `-q`  | Quiet mode - JSON output only            | `false` |
| `--simple`    | `-s`  | Use simplified mode (no external tools)  | `false` |

#### Examples

**Basic wallet generation:**

```bash
cspocli generate --ticker MYPOOL --purpose pledge
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

For each wallet, the CLI creates these files in `~/.CSPO_{TICKER}/{PURPOSE}/`:

| File                              | Description                 | Security      |
| --------------------------------- | --------------------------- | ------------- |
| `{TICKER}-{PURPOSE}.base_addr`    | Address for pledge funds    | Public        |
| `{TICKER}-{PURPOSE}.reward_addr`  | Address for staking rewards | Public        |
| `{TICKER}-{PURPOSE}.staking_skey` | Private staking key         | **SENSITIVE** |
| `{TICKER}-{PURPOSE}.staking_vkey` | Public staking key          | Public        |
| `{TICKER}-{PURPOSE}.mnemonic.txt` | 24-word recovery phrase     | **SENSITIVE** |

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
Cardano SPO CLI v0.1.0+fe1e288
Commit: fe1e288
⚠️  Working tree has uncommitted changes
```

---

## Command Help

### Get help for any command:

```bash
cspocli --help              # Main help
cspocli generate --help     # Generate command help
cspocli version --help      # Version command help
```

---

## Usage Patterns

### 1. Interactive Mode (Default)

```bash
cspocli generate --ticker MYPOOL --purpose pledge
```

- Shows welcome banner
- Displays security warnings
- Asks for confirmation
- Shows detailed output
- Provides next steps

### 2. Scripting Mode

```bash
cspocli generate --ticker TEST --purpose pledge --quiet --no-banner
```

- No interactive prompts
- JSON output for parsing
- No banners or warnings
- Suitable for automation

### 3. Simplified Mode

```bash
cspocli generate --ticker ADA --purpose rewards --simple
```

- Uses Python-native cryptography
- No external Cardano tools required
- Good for testing and development
- Faster execution

### 4. Force Mode

```bash
cspocli generate --ticker MYPOOL --purpose pledge --force
```

- Overwrites existing wallets
- No confirmation prompts
- Useful for regeneration

---

## Security Considerations

### File Permissions

All generated files have secure permissions:

- Private keys: `600` (owner read/write only)
- Public files: `644` (owner read/write, others read)

### Storage Location

All wallets are stored in the user's home directory:

```
~/.CSPO_{TICKER}/{PURPOSE}/
```

### Sensitive Files

These files contain sensitive information and should be handled carefully:

- `*.staking_skey` - Private staking key
- `*.mnemonic.txt` - 24-word recovery phrase

---

## Error Handling

### Common Errors

| Error                   | Cause                              | Solution                         |
| ----------------------- | ---------------------------------- | -------------------------------- |
| `Missing command`       | No command specified               | Use `cspocli --help`             |
| `Missing option`        | Required option not provided       | Check `cspocli generate --help`  |
| `Wallet already exists` | Wallet directory exists            | Use `--force` flag               |
| `Invalid ticker`        | Ticker contains invalid characters | Use alphanumeric characters only |

### Troubleshooting

1. **Check version:** `cspocli version`
2. **Get help:** `cspocli --help`
3. **Check command help:** `cspocli generate --help`
4. **Use quiet mode:** Add `--quiet` flag for JSON output

---

## Support

For technical support:

- Email: support@cardano-spo-cli.org
- Documentation: See `docs/` folder
- Examples: See `README.md`
