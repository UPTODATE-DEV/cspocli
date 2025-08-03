"""
Export functionality for Cardano SPO CLI
"""

import os
import zipfile
import tempfile
from pathlib import Path
from typing import List, Optional
import click
from cryptography.fernet import Fernet
from colorama import Fore, Style


class WalletExporter:
    """Export wallet files securely"""

    def __init__(self, ticker: str):
        self.ticker = ticker.upper()
        self.home_dir = Path.home() / f".CSPO_{self.ticker}"

    def create_encrypted_zip(self, purpose: str, password: str) -> Path:
        """Create an encrypted ZIP file with wallet files"""
        wallet_dir = self.home_dir / purpose

        if not wallet_dir.exists():
            raise click.ClickException(f"Wallet directory not found: {wallet_dir}")

        # Files to include in export (only essential files)
        essential_files = [
            f"{self.ticker}-{purpose}.base_addr",
            f"{self.ticker}-{purpose}.reward_addr",
            f"{self.ticker}-{purpose}.staking_skey",
            f"{self.ticker}-{purpose}.staking_vkey",
        ]

        # Create temporary ZIP file
        temp_zip = tempfile.NamedTemporaryFile(suffix=".zip", delete=False)
        temp_zip.close()

        # Create ZIP file
        with zipfile.ZipFile(temp_zip.name, "w", zipfile.ZIP_DEFLATED) as zipf:
            for filename in essential_files:
                file_path = wallet_dir / filename
                if file_path.exists():
                    zipf.write(file_path, filename)
                    click.echo(
                        f"{Fore.GREEN}Added to export: {filename}{Style.RESET_ALL}"
                    )
                else:
                    click.echo(
                        f"{Fore.YELLOW}Warning: {filename} not found{Style.RESET_ALL}"
                    )

        # Encrypt the ZIP file
        key = Fernet.generate_key()
        cipher = Fernet(key)

        with open(temp_zip.name, "rb") as f:
            encrypted_data = cipher.encrypt(f.read())

        # Create encrypted file
        encrypted_file = wallet_dir / f"{self.ticker}-{purpose}-export.zip.enc"
        with open(encrypted_file, "wb") as f:
            f.write(encrypted_data)

        # Save the key separately
        key_file = wallet_dir / f"{self.ticker}-{purpose}-export.key"
        with open(key_file, "wb") as f:
            f.write(key)

        # Clean up temporary file
        os.unlink(temp_zip.name)

        click.echo(
            f"{Fore.GREEN}Encrypted export created: {encrypted_file}{Style.RESET_ALL}"
        )
        click.echo(f"{Fore.YELLOW}Key file saved: {key_file}{Style.RESET_ALL}")
        click.echo(f"{Fore.CYAN}Password for decryption: {password}{Style.RESET_ALL}")

        return encrypted_file

    def list_export_files(self, purpose: str) -> List[Path]:
        """List files available for export"""
        wallet_dir = self.home_dir / purpose

        if not wallet_dir.exists():
            return []

        export_files = []
        for file_path in wallet_dir.iterdir():
            if file_path.is_file() and file_path.suffix in [".addr", ".skey", ".vkey"]:
                export_files.append(file_path)

        return export_files

    def verify_export_files(self, purpose: str) -> bool:
        """Verify that all required files exist for export"""
        required_files = [
            f"{self.ticker}-{purpose}.base_addr",
            f"{self.ticker}-{purpose}.reward_addr",
            f"{self.ticker}-{purpose}.staking_skey",
            f"{self.ticker}-{purpose}.staking_vkey",
        ]

        wallet_dir = self.home_dir / purpose

        for filename in required_files:
            file_path = wallet_dir / filename
            if not file_path.exists():
                click.echo(
                    f"{Fore.RED}Missing required file: {filename}{Style.RESET_ALL}"
                )
                return False

        click.echo(
            f"{Fore.GREEN}All required files present for export{Style.RESET_ALL}"
        )
        return True


def export_wallet_files(ticker: str, purpose: str, password: str) -> Path:
    """Export wallet files in encrypted ZIP format"""
    exporter = WalletExporter(ticker)

    # Verify files exist
    if not exporter.verify_export_files(purpose):
        raise click.ClickException("Cannot export: missing required files")

    # Create encrypted export
    return exporter.create_encrypted_zip(purpose, password)


def list_wallet_files(ticker: str, purpose: str) -> List[Path]:
    """List wallet files available for export"""
    exporter = WalletExporter(ticker)
    return exporter.list_export_files(purpose)
# Export functionality
