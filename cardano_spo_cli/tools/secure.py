#!/usr/bin/env python3
"""Secure wallet files module."""

import os
import base64
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import click


def derive_key_from_password(password: str, salt: bytes = None) -> tuple[bytes, bytes]:
    """Derive encryption key from password using PBKDF2"""
    if salt is None:
        salt = os.urandom(16)

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key, salt


def encrypt_file(file_path: Path, password: str) -> dict:
    """Encrypt a single file with password"""
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # Read original file
    with open(file_path, "rb") as f:
        original_data = f.read()

    # Derive key from password
    key, salt = derive_key_from_password(password)
    cipher = Fernet(key)

    # Encrypt data
    encrypted_data = cipher.encrypt(original_data)

    # Create encrypted file path
    encrypted_path = file_path.with_suffix(file_path.suffix + ".enc")

    # Write encrypted file
    with open(encrypted_path, "wb") as f:
        f.write(salt)
        f.write(encrypted_data)

    # Remove original file
    file_path.unlink()

    return {
        "original_path": str(file_path),
        "encrypted_path": str(encrypted_path),
        "size": len(encrypted_data),
    }


def decrypt_file(file_path: Path, password: str) -> bytes:
    """Decrypt a single file with password"""
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # Read encrypted file
    with open(file_path, "rb") as f:
        salt = f.read(16)  # First 16 bytes are salt
        encrypted_data = f.read()

    # Derive key from password
    key, _ = derive_key_from_password(password, salt)
    cipher = Fernet(key)

    # Decrypt data
    try:
        decrypted_data = cipher.decrypt(encrypted_data)
        return decrypted_data
    except Exception as e:
        raise ValueError(f"Decryption failed: {e}")


def get_sensitive_files(wallet_dir: Path) -> list[Path]:
    """Get list of sensitive files to secure"""
    sensitive_patterns = [
        "*.skey",  # Private keys
        "*.mnemonic.txt",  # Recovery phrases
    ]

    sensitive_files = []
    for pattern in sensitive_patterns:
        sensitive_files.extend(wallet_dir.glob(pattern))

    return sensitive_files


def secure_wallet_files(ticker: str, purpose: str, password: str) -> dict:
    """Secure all sensitive files in a wallet directory"""
    home_dir = Path.home() / f".CSPO_{ticker.upper()}"
    wallet_dir = home_dir / purpose

    if not wallet_dir.exists():
        raise FileNotFoundError(f"Wallet directory not found: {wallet_dir}")

    sensitive_files = get_sensitive_files(wallet_dir)

    if not sensitive_files:
        raise ValueError(f"No sensitive files found in {wallet_dir}")

    secured_files = []
    for file_path in sensitive_files:
        try:
            result = encrypt_file(file_path, password)
            secured_files.append(result)
        except Exception as e:
            raise click.ClickException(f"Failed to secure {file_path}: {e}")

    return {
        "wallet_dir": str(wallet_dir),
        "secured_count": len(secured_files),
        "secured_files": secured_files,
    }


def view_wallet_files(
    ticker: str, purpose: str, password: str, specific_file: str = None
) -> dict:
    """View secured files or specific file content"""
    home_dir = Path.home() / f".CSPO_{ticker.upper()}"
    wallet_dir = home_dir / purpose

    if not wallet_dir.exists():
        raise FileNotFoundError(f"Wallet directory not found: {wallet_dir}")

    # Find encrypted files
    encrypted_files = list(wallet_dir.glob("*.enc"))

    if not encrypted_files:
        raise ValueError(f"No secured files found in {wallet_dir}")

    if specific_file:
        # View specific file
        target_file = wallet_dir / f"{specific_file}.enc"
        if not target_file.exists():
            raise FileNotFoundError(f"Secured file not found: {specific_file}")

        try:
            decrypted_content = decrypt_file(target_file, password)
            return {"content": decrypted_content.decode("utf-8"), "file": specific_file}
        except Exception as e:
            raise click.ClickException(f"Failed to decrypt {specific_file}: {e}")
    else:
        # List all secured files
        secured_files = []
        for encrypted_file in encrypted_files:
            # Remove .enc extension to get original filename
            original_name = encrypted_file.stem
            secured_files.append(original_name)

        return {"files": secured_files, "wallet_dir": str(wallet_dir)}


def restore_wallet_files(ticker: str, purpose: str, password: str) -> dict:
    """Restore all secured files to their original state"""
    home_dir = Path.home() / f".CSPO_{ticker.upper()}"
    wallet_dir = home_dir / purpose

    if not wallet_dir.exists():
        raise FileNotFoundError(f"Wallet directory not found: {wallet_dir}")

    # Find encrypted files
    encrypted_files = list(wallet_dir.glob("*.enc"))

    if not encrypted_files:
        raise ValueError(f"No secured files found in {wallet_dir}")

    restored_files = []
    for encrypted_file in encrypted_files:
        try:
            # Decrypt file
            decrypted_content = decrypt_file(encrypted_file, password)

            # Write original file
            original_path = encrypted_file.with_suffix("")  # Remove .enc
            with open(original_path, "wb") as f:
                f.write(decrypted_content)

            # Remove encrypted file
            encrypted_file.unlink()

            restored_files.append(str(original_path))
        except Exception as e:
            raise click.ClickException(f"Failed to restore {encrypted_file.name}: {e}")

    return {
        "wallet_dir": str(wallet_dir),
        "restored_count": len(restored_files),
        "restored_files": restored_files,
    }
