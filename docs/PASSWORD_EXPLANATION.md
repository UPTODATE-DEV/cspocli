# Password Explanation for Global Installation

## Why is a password needed?

When you run `make install-global`, the system needs to write a file to `/usr/local/bin/`, which is a system directory that requires administrator privileges.

## What password do I need to enter?

**You need to enter your computer's user password** (the same password you use to log into your Mac), **NOT a sudo password**.

## Why is this necessary?

- `/usr/local/bin/` is a system directory that contains executable files available to all users
- Writing to this directory requires administrator privileges
- This is a standard security feature on macOS and Linux
- The password prompt is from the system's security mechanism, not from our CLI

## What happens if I don't want to enter a password?

If you prefer not to use global installation, you can:

1. **Use local installation instead:**

   ```bash
   make install
   source venv/bin/activate
   cspocli --help
   ```

2. **Use the virtual environment directly:**

   ```bash
   source venv/bin/activate
   cspocli --help
   ```

3. **Use pipx (alternative global installation):**
   ```bash
   pipx install .
   cspocli --help
   ```

## Is this safe?

Yes, this is completely safe:

- We only write to `/usr/local/bin/cspocli` (a single file)
- We don't modify any system files or settings
- The script only activates the virtual environment and runs the CLI
- You can always uninstall with `make uninstall`

## Troubleshooting

If you get a "permission denied" error:

1. Make sure you're entering your **computer password**, not a sudo password
2. Try running the command again
3. If it still doesn't work, use local installation instead

## Alternative: Use pipx

If you prefer not to use sudo, you can install with pipx:

```bash
# Install pipx
brew install pipx
pipx ensurepath

# Install the CLI
pipx install .

# Use the CLI
cspocli --help
```

This method doesn't require a password but achieves the same result (global availability).
