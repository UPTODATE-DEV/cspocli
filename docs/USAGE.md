# Cardano SPO CLI Usage Guide

## Prerequisites: Python & pip

### 1. Install Python 3 (if not already installed)

- **macOS:**
  ```bash
  brew install python
  ```
- **Ubuntu/Debian:**
  ```bash
  sudo apt update
  sudo apt install python3 python3-venv python3-pip
  ```
- **Windows:**
  - Download and install from [python.org](https://www.python.org/downloads/)

### 2. Check Python and pip

```bash
python3 --version
python3 -m pip --version
```

If `pip` is not found, use `python3 -m pip` instead of `pip` in all commands.

---

## Recommended: Install in a Virtual Environment

### Option 1: Use Makefile (Recommended - Global Installation)

```bash
# Install globally (no activation needed)
make install-global
# Note: You'll be prompted for your computer password (not sudo password)

# Or install locally (requires activation)
make install
source venv/bin/activate
```

### Option 2: Use the installation script

```bash
./install.sh
```

### Option 3: Manual installation

1. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   ```
2. **Activate the virtual environment:**
   - **macOS/Linux:**
     ```bash
     source venv/bin/activate
     ```
   - **Windows:**
     ```cmd
     venv\Scripts\activate
     ```
3. **Install the CLI in editable mode:**
   ```bash
   pip install -e .
   # or if pip is not found:
   python3 -m pip install -e .
   ```
4. **Use the CLI:**
   ```bash
   cspocli --help
   ```

---

## Alternative: Install with pipx (Recommended for CLI tools)

1. **Install pipx:**
   ```bash
   brew install pipx
   pipx ensurepath
   ```
2. **Install the CLI:**
   ```bash
   pipx install .
   ```
3. **Use the CLI globally:**
   ```bash
   cspocli --help
   ```

## Quick Activation

After installation, to activate the environment in a new terminal:

```bash
# If installed globally (make install-global)
cspocli --help  # No activation needed!

# If installed locally
# Option 1: Quick activation
source quick-activate.sh

# Option 2: Manual activation
source venv/bin/activate

# Option 3: Use the activation script
./activate.sh
```

---

## Basic Commands

### Show Help

```bash
cspocli --help
```

### Show Version

```bash
cspocli version
```

### Generate a Wallet (Real Cardano Tools)

```bash
cspocli generate --ticker MYPOOL --purpose pledge
```

### Generate a Rewards Wallet

```bash
cspocli generate --ticker MYPOOL --purpose rewards
```

### Use Simplified Mode (Python-native, for testing)

```bash
cspocli generate --ticker TEST --purpose pledge --simple
```

---

## Folder Structure

Wallets are stored in your home directory:

```
~/.CSPO_{TICKER}/
├── pledge/
│   ├── {TICKER}-pledge.base_addr
│   ├── {TICKER}-pledge.reward_addr
│   ├── {TICKER}-pledge.staking_skey
│   ├── {TICKER}-pledge.staking_vkey
│   └── {TICKER}-pledge.mnemonic.txt
└── rewards/
    ├── {TICKER}-rewards.base_addr
    ├── {TICKER}-rewards.reward_addr
    ├── {TICKER}-rewards.staking_skey
    ├── {TICKER}-rewards.staking_vkey
    └── {TICKER}-rewards.mnemonic.txt
```

---

## Handling Existing Folders

If you try to generate a wallet for a ticker that already exists, you will see:

```
⚠️  Wallet MYPOOL-pledge already exists
Do you want to regenerate it? [y/N]:
```

- Answer `n` (or press Enter) to cancel and use a different ticker.
- Answer `y` to overwrite the existing wallet files.

---

## Security Notes

- All sensitive files are stored with permissions `600` (read/write for owner only).
- Never share your mnemonic or private keys.
- Always test with small amounts before using on mainnet.

---

## More Information

- For advanced usage, see the main [README.md](../README.md) and [REAL_TOOLS.md](../REAL_TOOLS.md).
- For troubleshooting, see [USAGE.md](../USAGE.md) in the project root.

---

## Example Workflow

```bash
# Install Python and pip if needed (see above)

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install the CLI
pip install -e .

# Check version
cspocli version

# Generate a pledge wallet
cspocli generate --ticker MYPOOL --purpose pledge

# Generate a rewards wallet
cspocli generate --ticker MYPOOL --purpose rewards

# Use a different ticker if the folder exists
cspocli generate --ticker MYPOOL2 --purpose pledge
```
