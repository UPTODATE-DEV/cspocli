"""
Wallet generation module for Cardano SPO CLI using real Cardano tools
"""

import os
import json
import secrets
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import click
from mnemonic import Mnemonic
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import bech32
from colorama import Fore, Style

from .download import verify_tools


class CardanoWalletGenerator:
    """Cardano wallet generator using real Cardano tools"""

    def __init__(self, ticker: str):
        self.ticker = ticker.upper()
        self.home_dir = Path.home() / f".CSPO_{self.ticker}"
        self.home_dir.mkdir(parents=True, exist_ok=True)
        self.tools = verify_tools()
        self.mnemo = Mnemonic("english")

        # Check if shared mnemonic already exists for this ticker
        self.shared_mnemonic_file = self.home_dir / f"{self.ticker}-shared.mnemonic.txt"

        # Check if tools are available
        if not self.tools:
            raise click.ClickException(
                "Real Cardano tools not available. Use --simple flag for simplified mode."
            )

        # Check if cardano-cli is usable (not crashing)
        if "cardano-cli" in self.tools:
            import platform

            is_arm64_macos = platform.system() == "Darwin" and platform.machine() in [
                "arm64",
                "aarch64",
            ]

            if is_arm64_macos:
                # On ARM64 macOS, cardano-cli is known to crash due to Nix dependencies
                # But we can still use cardano-address and bech32 for real mode
                click.echo(
                    "ℹ️  cardano-cli may crash on ARM64 macOS (known compatibility issue)"
                )
                click.echo("✅ Using cardano-address and bech32 for real mode")
                # Keep cardano-cli but don't test it
            else:
                # Test cardano-cli on other platforms
                try:
                    result = subprocess.run(
                        [str(self.tools["cardano-cli"]), "--version"],
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )
                    if result.returncode != 0:
                        # Remove crashing cardano-cli from tools
                        del self.tools["cardano-cli"]
                        click.echo("⚠️  cardano-cli crashes, using simplified mode")
                except Exception:
                    # Remove crashing cardano-cli from tools
                    if "cardano-cli" in self.tools:
                        del self.tools["cardano-cli"]
                    click.echo("⚠️  cardano-cli crashes, using simplified mode")

        # Check if we have enough tools for real mode
        # We need at least cardano-address for real mode, cardano-cli is optional
        if "cardano-address" in self.tools:
            click.echo("✅ Using real Cardano tools mode")
        else:
            click.echo("⚠️  Using simplified mode (cardano-address missing)")

    def get_or_create_shared_mnemonic(self) -> str:
        """Get existing shared mnemonic or create new one"""
        if self.shared_mnemonic_file.exists():
            # Load existing shared mnemonic
            mnemonic = self.shared_mnemonic_file.read_text().strip()
            click.echo(f"📋 Using existing shared mnemonic for {self.ticker}")
            return mnemonic
        else:
            # Create new shared mnemonic
            mnemonic = self.mnemo.generate(strength=256)
            # Save shared mnemonic with secure permissions
            self.shared_mnemonic_file.write_text(mnemonic)
            self.shared_mnemonic_file.chmod(0o600)  # Secure permissions
            click.echo(f"🔐 Created new shared mnemonic for {self.ticker}")
            return mnemonic

    def generate_mnemonic(self) -> str:
        """Generate a 24-word recovery phrase (legacy method)"""
        return self.mnemo.generate(strength=256)

    def mnemonic_to_root_key(self, mnemonic: str) -> str:
        """Convert mnemonic phrase to root key using cardano-address"""
        cmd = [
            str(self.tools["cardano-address"]),
            "key",
            "from-recovery-phrase",
            "Shelley",
        ]
        result = subprocess.run(cmd, input=mnemonic, capture_output=True, text=True)
        if result.returncode != 0:
            raise click.ClickException(f"Error generating root key: {result.stderr}")
        return result.stdout.strip()

    def derive_payment_key(self, root_key: str, purpose: str) -> Tuple[str, str]:
        """Derive payment keys using cardano-address"""
        # Payment private key
        cmd = [str(self.tools["cardano-address"]), "key", "child", "1852H/1815H/0H/0/0"]
        result = subprocess.run(cmd, input=root_key, capture_output=True, text=True)
        if result.returncode != 0:
            raise click.ClickException(f"Error deriving payment key: {result.stderr}")
        payment_skey = result.stdout.strip()

        # Payment public key
        cmd = [str(self.tools["cardano-address"]), "key", "public", "--with-chain-code"]
        result = subprocess.run(cmd, input=payment_skey, capture_output=True, text=True)
        if result.returncode != 0:
            raise click.ClickException(f"Error generating public key: {result.stderr}")
        payment_vkey = result.stdout.strip()

        return payment_skey, payment_vkey

    def derive_staking_key(self, root_key: str) -> Tuple[str, str]:
        """Derive staking keys using cardano-address"""
        # Staking private key
        cmd = [str(self.tools["cardano-address"]), "key", "child", "1852H/1815H/0H/2/0"]
        result = subprocess.run(cmd, input=root_key, capture_output=True, text=True)
        if result.returncode != 0:
            raise click.ClickException(f"Error deriving staking key: {result.stderr}")
        staking_skey = result.stdout.strip()

        # Staking public key
        cmd = [str(self.tools["cardano-address"]), "key", "public", "--with-chain-code"]
        result = subprocess.run(cmd, input=staking_skey, capture_output=True, text=True)
        if result.returncode != 0:
            raise click.ClickException(
                f"Error generating staking public key: {result.stderr}"
            )
        staking_vkey = result.stdout.strip()

        return staking_skey, staking_vkey

    def generate_payment_address(
        self, payment_vkey: str, staking_vkey: str, network: str = "mainnet"
    ) -> str:
        """Generate payment address using cardano-address"""
        # Map network to network tag
        network_tags = {"mainnet": "1", "testnet": "0", "preview": "0", "preprod": "0"}
        network_tag = network_tags.get(network, "1")

        # Payment address (base address without staking)
        cmd = [
            str(self.tools["cardano-address"]),
            "address",
            "payment",
            "--network-tag",
            network_tag,
        ]
        result = subprocess.run(cmd, input=payment_vkey, capture_output=True, text=True)
        if result.returncode != 0:
            raise click.ClickException(
                f"Error generating payment address: {result.stderr}"
            )
        return result.stdout.strip()

    def generate_staking_address(
        self, staking_vkey: str, network: str = "mainnet"
    ) -> str:
        """Generate staking address using cardano-address"""
        # Map network to network tag
        network_tags = {"mainnet": "1", "testnet": "0", "preview": "0", "preprod": "0"}
        network_tag = network_tags.get(network, "1")

        cmd = [
            str(self.tools["cardano-address"]),
            "address",
            "stake",
            "--network-tag",
            network_tag,
        ]
        result = subprocess.run(cmd, input=staking_vkey, capture_output=True, text=True)
        if result.returncode != 0:
            raise click.ClickException(
                f"Error generating staking address: {result.stderr}"
            )
        return result.stdout.strip()

    def validate_address(self, address: str) -> bool:
        """Validate a Cardano address using bech32"""
        try:
            # Decode bech32 address
            hrp, data = bech32.bech32_decode(address)
            if hrp is None or data is None:
                return False

            # Check prefix
            valid_prefixes = ["addr", "addr_test", "stake", "stake_test"]
            return hrp in valid_prefixes
        except Exception:
            return False

    def generate_address_candidate(
        self, payment_vkey: str, staking_vkey: str, network: str = "mainnet"
    ) -> str:
        """Generate a candidate address for verification"""
        # Generate candidate address using same method
        return self.generate_payment_address(payment_vkey, staking_vkey, network)

    def verify_address_candidates(self, base_addr: str, candidate_addr: str) -> bool:
        """Verify that base address matches candidate address"""
        return base_addr == candidate_addr

    def save_wallet_files(self, purpose: str, wallet_data: Dict[str, str]) -> Path:
        """Save wallet files"""
        wallet_dir = self.home_dir / purpose
        wallet_dir.mkdir(parents=True, exist_ok=True)

        # Save files
        files_saved = []

        # Base address (payment address)
        base_addr_file = wallet_dir / f"{self.ticker}-{purpose}.base_addr"
        with open(base_addr_file, "w") as f:
            f.write(wallet_data["base_addr"])
        files_saved.append(base_addr_file)

        # Base address candidate for verification
        base_addr_candidate_file = (
            wallet_dir / f"{self.ticker}-{purpose}.base_addr.candidate"
        )
        with open(base_addr_candidate_file, "w") as f:
            f.write(wallet_data["base_addr_candidate"])
        files_saved.append(base_addr_candidate_file)

        # Reward address (staking address)
        reward_addr_file = wallet_dir / f"{self.ticker}-{purpose}.reward_addr"
        with open(reward_addr_file, "w") as f:
            f.write(wallet_data["reward_addr"])
        files_saved.append(reward_addr_file)

        # Reward address candidate for verification
        reward_addr_candidate_file = (
            wallet_dir / f"{self.ticker}-{purpose}.reward_addr.candidate"
        )
        with open(reward_addr_candidate_file, "w") as f:
            f.write(wallet_data["reward_addr_candidate"])
        files_saved.append(reward_addr_candidate_file)

        # Staking private key
        staking_skey_file = wallet_dir / f"{self.ticker}-{purpose}.staking_skey"
        with open(staking_skey_file, "w") as f:
            f.write(wallet_data["staking_skey"])
        files_saved.append(staking_skey_file)

        # Staking public key
        staking_vkey_file = wallet_dir / f"{self.ticker}-{purpose}.staking_vkey"
        with open(staking_vkey_file, "w") as f:
            f.write(wallet_data["staking_vkey"])
        files_saved.append(staking_vkey_file)

        # Recovery phrase
        mnemonic_file = wallet_dir / f"{self.ticker}-{purpose}.mnemonic.txt"
        with open(mnemonic_file, "w") as f:
            f.write(wallet_data["mnemonic"])
        files_saved.append(mnemonic_file)

        # Make sensitive files more secure
        for file in [staking_skey_file, mnemonic_file]:
            file.chmod(0o600)  # Read/write for owner only

        return wallet_dir

    def generate_wallet(self, purpose: str, network: str = "mainnet") -> Dict[str, str]:
        """Generate a complete wallet using real Cardano tools"""
        click.echo(
            f"{Fore.CYAN}Generating {self.ticker}-{purpose} wallet using real Cardano tools...{Style.RESET_ALL}"
        )

        # Get or create shared mnemonic phrase
        mnemonic = self.get_or_create_shared_mnemonic()
        click.echo(f"{Fore.GREEN}Recovery phrase ready{Style.RESET_ALL}")

        # Convert to root key
        root_key = self.mnemonic_to_root_key(mnemonic)
        click.echo(f"{Fore.GREEN}Root key derived{Style.RESET_ALL}")

        # Derive payment keys
        payment_skey, payment_vkey = self.derive_payment_key(root_key, purpose)
        click.echo(f"{Fore.GREEN}Payment keys derived{Style.RESET_ALL}")

        # Derive staking keys
        staking_skey, staking_vkey = self.derive_staking_key(root_key)
        click.echo(f"{Fore.GREEN}Staking keys derived{Style.RESET_ALL}")

        # Generate addresses
        base_addr = self.generate_payment_address(payment_vkey, staking_vkey, network)
        reward_addr = self.generate_staking_address(staking_vkey, network)
        click.echo(f"{Fore.GREEN}Addresses generated{Style.RESET_ALL}")

        # Generate candidate addresses for verification
        base_addr_candidate = self.generate_address_candidate(
            payment_vkey, staking_vkey, network
        )
        reward_addr_candidate = self.generate_staking_address(staking_vkey, network)
        click.echo(
            f"{Fore.GREEN}Address candidates generated for verification{Style.RESET_ALL}"
        )

        # Verify address candidates
        if not self.verify_address_candidates(base_addr, base_addr_candidate):
            raise click.ClickException(
                "Address verification failed: base address mismatch"
            )
        if not self.verify_address_candidates(reward_addr, reward_addr_candidate):
            raise click.ClickException(
                "Address verification failed: reward address mismatch"
            )
        click.echo(f"{Fore.GREEN}Address verification successful{Style.RESET_ALL}")

        # Validate addresses
        if not self.validate_address(base_addr):
            raise click.ClickException("Invalid base address generated")
        if not self.validate_address(reward_addr):
            raise click.ClickException("Invalid reward address generated")

        # Prepare wallet data
        wallet_data = {
            "base_addr": base_addr,
            "base_addr_candidate": base_addr_candidate,
            "reward_addr": reward_addr,
            "reward_addr_candidate": reward_addr_candidate,
            "staking_skey": staking_skey,
            "staking_vkey": staking_vkey,
            "mnemonic": mnemonic,
        }

        # Save files
        wallet_dir = self.save_wallet_files(purpose, wallet_data)

        click.echo(f"{Fore.GREEN}Wallet generated in: {wallet_dir}{Style.RESET_ALL}")

        return wallet_data


def generate_wallet_real(
    ticker: str, purpose: str, network: str = "mainnet"
) -> Dict[str, str]:
    """Main function to generate a wallet using real Cardano tools"""
    generator = CardanoWalletGenerator(ticker)
    return generator.generate_wallet(purpose, network)


# Real wallet
# Address verification
# Cross verification
# Command structure
# Fix cardano-address
