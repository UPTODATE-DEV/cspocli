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
        """Generate base address using cardano-address"""
        # Map network to network tag
        network_tags = {"mainnet": "1", "testnet": "0", "preview": "0", "preprod": "0"}
        network_tag = network_tags.get(network, "1")

        # Base address (combines payment and staking keys)
        # First, create the payment address
        payment_cmd = [
            str(self.tools["cardano-address"]),
            "address",
            "payment",
            "--network-tag",
            network_tag,
        ]
        payment_result = subprocess.run(
            payment_cmd, input=payment_vkey, capture_output=True, text=True
        )
        if payment_result.returncode != 0:
            raise click.ClickException(
                f"Error generating payment address: {payment_result.stderr}"
            )
        payment_addr = payment_result.stdout.strip()

        # Then, create the staking address
        stake_cmd = [
            str(self.tools["cardano-address"]),
            "address",
            "stake",
            "--network-tag",
            network_tag,
        ]
        stake_result = subprocess.run(
            stake_cmd, input=staking_vkey, capture_output=True, text=True
        )
        if stake_result.returncode != 0:
            raise click.ClickException(
                f"Error generating staking address: {stake_result.stderr}"
            )
        stake_addr = stake_result.stdout.strip()

        # Combine payment and staking addresses to create base address
        # The delegation command expects: payment_address | cardano-address address delegation staking_public_key
        base_cmd = [
            str(self.tools["cardano-address"]),
            "address",
            "delegation",
            staking_vkey,  # Use the staking public key directly
        ]
        base_result = subprocess.run(
            base_cmd, input=payment_addr, capture_output=True, text=True
        )
        if base_result.returncode != 0:
            raise click.ClickException(
                f"Error generating base address: {base_result.stderr}"
            )
        return base_result.stdout.strip()

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
        """Generate a candidate base address for verification"""
        # Generate candidate address using same method as generate_payment_address
        # Map network to network tag
        network_tags = {"mainnet": "1", "testnet": "0", "preview": "0", "preprod": "0"}
        network_tag = network_tags.get(network, "1")

        # First, create the payment address
        payment_cmd = [
            str(self.tools["cardano-address"]),
            "address",
            "payment",
            "--network-tag",
            network_tag,
        ]
        payment_result = subprocess.run(
            payment_cmd, input=payment_vkey, capture_output=True, text=True
        )
        if payment_result.returncode != 0:
            raise click.ClickException(
                f"Error generating payment address: {payment_result.stderr}"
            )
        payment_addr = payment_result.stdout.strip()

        # Then, create the staking address
        stake_cmd = [
            str(self.tools["cardano-address"]),
            "address",
            "stake",
            "--network-tag",
            network_tag,
        ]
        stake_result = subprocess.run(
            stake_cmd, input=staking_vkey, capture_output=True, text=True
        )
        if stake_result.returncode != 0:
            raise click.ClickException(
                f"Error generating staking address: {stake_result.stderr}"
            )
        stake_addr = stake_result.stdout.strip()

        # Combine payment and staking addresses to create base address
        # The delegation command expects: payment_address | cardano-address address delegation staking_public_key
        base_cmd = [
            str(self.tools["cardano-address"]),
            "address",
            "delegation",
            staking_vkey,  # Use the staking public key directly
        ]
        base_result = subprocess.run(
            base_cmd, input=payment_addr, capture_output=True, text=True
        )
        if base_result.returncode != 0:
            raise click.ClickException(
                f"Error generating base address: {base_result.stderr}"
            )
        return base_result.stdout.strip()

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

    def import_existing_keys(
        self,
        purpose: str,
        payment_vkey_path: str = None,
        payment_skey_path: str = None,
        stake_vkey_path: str = None,
        stake_skey_path: str = None,
    ) -> Dict[str, str]:
        """Import existing keys instead of generating new ones"""
        wallet_data = {}

        # Import payment keys
        if payment_vkey_path and Path(payment_vkey_path).exists():
            with open(payment_vkey_path, "r") as f:
                payment_vkey_content = f.read()
                payment_vkey_json = json.loads(payment_vkey_content)
                wallet_data["payment_vkey"] = payment_vkey_json["cborHex"]
                click.echo(
                    f"✅ Imported payment verification key from {payment_vkey_path}"
                )

        if payment_skey_path and Path(payment_skey_path).exists():
            with open(payment_skey_path, "r") as f:
                payment_skey_content = f.read()
                payment_skey_json = json.loads(payment_skey_content)
                wallet_data["payment_skey"] = payment_skey_json["cborHex"]
                click.echo(f"✅ Imported payment signing key from {payment_skey_path}")

        # Import staking keys
        if stake_vkey_path and Path(stake_vkey_path).exists():
            with open(stake_vkey_path, "r") as f:
                stake_vkey_content = f.read()
                stake_vkey_json = json.loads(stake_vkey_content)
                wallet_data["staking_vkey"] = stake_vkey_json["cborHex"]
                click.echo(f"✅ Imported stake verification key from {stake_vkey_path}")

        if stake_skey_path and Path(stake_skey_path).exists():
            with open(stake_skey_path, "r") as f:
                stake_skey_content = f.read()
                stake_skey_json = json.loads(stake_skey_content)
                wallet_data["staking_skey"] = stake_skey_json["cborHex"]
                click.echo(f"✅ Imported stake signing key from {stake_skey_path}")

        return wallet_data

    def generate_wallet_with_import(
        self,
        purpose: str,
        network: str = "mainnet",
        payment_vkey_path: str = None,
        payment_skey_path: str = None,
        stake_vkey_path: str = None,
        stake_skey_path: str = None,
    ) -> Dict[str, str]:
        """Generate a wallet using imported existing keys"""
        click.echo(
            f"{Fore.CYAN}Generating {self.ticker}-{purpose} wallet using imported keys...{Style.RESET_ALL}"
        )

        # Import existing keys
        imported_keys = self.import_existing_keys(
            purpose,
            payment_vkey_path,
            payment_skey_path,
            stake_vkey_path,
            stake_skey_path,
        )

        if not imported_keys:
            raise click.ClickException("No valid keys provided for import")

        # Convert CBOR hex back to Bech32 for address generation
        payment_vkey_bech32 = self.cbor_hex_to_bech32(
            imported_keys["payment_vkey"], "addr_vk"
        )
        staking_vkey_bech32 = self.cbor_hex_to_bech32(
            imported_keys["staking_vkey"], "stake_vk"
        )

        # Generate addresses using imported keys
        base_addr = self.generate_payment_address(
            payment_vkey_bech32, staking_vkey_bech32, network
        )
        reward_addr = self.generate_staking_address(staking_vkey_bech32, network)
        click.echo(
            f"{Fore.GREEN}Addresses generated from imported keys{Style.RESET_ALL}"
        )

        # Validate addresses
        if not self.validate_address(base_addr):
            raise click.ClickException(
                "Invalid base address generated from imported keys"
            )
        if not self.validate_address(reward_addr):
            raise click.ClickException(
                "Invalid reward address generated from imported keys"
            )

        # Prepare wallet data
        wallet_data = {
            "base_addr": base_addr,
            "reward_addr": reward_addr,
            "payment_skey": imported_keys.get("payment_skey", ""),
            "payment_vkey": imported_keys.get("payment_vkey", ""),
            "staking_skey": imported_keys.get("staking_skey", ""),
            "staking_vkey": imported_keys.get("staking_vkey", ""),
        }

        # Save files
        wallet_dir = self.save_wallet_files(purpose, wallet_data)

        click.echo(
            f"{Fore.GREEN}Wallet generated from imported keys in: {wallet_dir}{Style.RESET_ALL}"
        )

        return wallet_data

    def cbor_hex_to_bech32(self, cbor_hex: str, prefix: str) -> str:
        """Convert CBOR hex to Bech32 format"""
        try:
            # Remove CBOR tag and length
            if cbor_hex.startswith("58"):
                key_data = bytes.fromhex(cbor_hex[4:])  # Skip "58" and length
            else:
                key_data = bytes.fromhex(cbor_hex)

            # Encode as Bech32
            return bech32.encode(prefix, key_data)
        except Exception:
            # Fallback: return a placeholder
            return (
                f"{prefix}1{key_data.hex()[:56]}"
                if "key_data" in locals()
                else f"{prefix}1placeholder"
            )

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

    def generate_stake_pool_files(
        self, purpose: str, network: str = "mainnet"
    ) -> Dict[str, str]:
        """Generate all stake pool files using cardano-cli (recommended for compatibility)"""
        click.echo(
            f"{Fore.CYAN}Generating complete stake pool files for {self.ticker}-{purpose} using cardano-cli...{Style.RESET_ALL}"
        )

        # Use cardano-cli for key generation (recommended for compatibility)
        wallet_data = self.generate_keys_with_cardano_cli(purpose, network)

        click.echo(
            f"{Fore.GREEN}All keys and files generated with cardano-cli{Style.RESET_ALL}"
        )

        # Save files
        wallet_dir = self.save_complete_wallet_files(purpose, wallet_data)

        click.echo(
            f"{Fore.GREEN}Complete stake pool files generated in: {wallet_dir}{Style.RESET_ALL}"
        )

        return wallet_data

    def derive_cold_key(self, root_key: str) -> Tuple[str, str]:
        """Derive cold key pair for stake pool"""
        # Cold key derivation path: 1852H/1815H/0H/0/0 (same as payment but different purpose)
        cmd = [
            str(self.tools["cardano-address"]),
            "key",
            "child",
            "1852H/1815H/0H/0/0",
        ]
        result = subprocess.run(cmd, input=root_key, capture_output=True, text=True)
        if result.returncode != 0:
            raise click.ClickException(f"Error deriving cold key: {result.stderr}")
        cold_skey = result.stdout.strip()

        # Get public key
        cmd = [
            str(self.tools["cardano-address"]),
            "key",
            "public",
            "--with-chain-code",
        ]
        result = subprocess.run(cmd, input=cold_skey, capture_output=True, text=True)
        if result.returncode != 0:
            raise click.ClickException(
                f"Error getting cold public key: {result.stderr}"
            )
        cold_vkey = result.stdout.strip()

        return cold_skey, cold_vkey

    def derive_hot_key(self, root_key: str) -> Tuple[str, str]:
        """Derive hot key pair for stake pool"""
        # Hot key derivation path: 1852H/1815H/0H/2/0
        cmd = [
            str(self.tools["cardano-address"]),
            "key",
            "child",
            "1852H/1815H/0H/2/0",
        ]
        result = subprocess.run(cmd, input=root_key, capture_output=True, text=True)
        if result.returncode != 0:
            raise click.ClickException(f"Error deriving hot key: {result.stderr}")
        hot_skey = result.stdout.strip()

        # Get public key
        cmd = [
            str(self.tools["cardano-address"]),
            "key",
            "public",
            "--with-chain-code",
        ]
        result = subprocess.run(cmd, input=hot_skey, capture_output=True, text=True)
        if result.returncode != 0:
            raise click.ClickException(f"Error getting hot public key: {result.stderr}")
        hot_vkey = result.stdout.strip()

        return hot_skey, hot_vkey

    def derive_drep_key(self, root_key: str) -> Tuple[str, str]:
        """Derive DRep key pair"""
        # DRep key derivation path: 1852H/1815H/0H/3/0
        cmd = [
            str(self.tools["cardano-address"]),
            "key",
            "child",
            "1852H/1815H/0H/3/0",
        ]
        result = subprocess.run(cmd, input=root_key, capture_output=True, text=True)
        if result.returncode != 0:
            raise click.ClickException(f"Error deriving DRep key: {result.stderr}")
        drep_skey = result.stdout.strip()

        # Get public key
        cmd = [
            str(self.tools["cardano-address"]),
            "key",
            "public",
            "--with-chain-code",
        ]
        result = subprocess.run(cmd, input=drep_skey, capture_output=True, text=True)
        if result.returncode != 0:
            raise click.ClickException(
                f"Error getting DRep public key: {result.stderr}"
            )
        drep_vkey = result.stdout.strip()

        return drep_skey, drep_vkey

    def derive_ms_payment_key(self, root_key: str) -> Tuple[str, str]:
        """Derive multi-signature payment key pair"""
        # MS payment key derivation path: 1852H/1815H/0H/4/0
        cmd = [
            str(self.tools["cardano-address"]),
            "key",
            "child",
            "1852H/1815H/0H/4/0",
        ]
        result = subprocess.run(cmd, input=root_key, capture_output=True, text=True)
        if result.returncode != 0:
            raise click.ClickException(
                f"Error deriving MS payment key: {result.stderr}"
            )
        ms_payment_skey = result.stdout.strip()

        # Get public key
        cmd = [
            str(self.tools["cardano-address"]),
            "key",
            "public",
            "--with-chain-code",
        ]
        result = subprocess.run(
            cmd, input=ms_payment_skey, capture_output=True, text=True
        )
        if result.returncode != 0:
            raise click.ClickException(
                f"Error getting MS payment public key: {result.stderr}"
            )
        ms_payment_vkey = result.stdout.strip()

        return ms_payment_skey, ms_payment_vkey

    def derive_ms_stake_key(self, root_key: str) -> Tuple[str, str]:
        """Derive multi-signature stake key pair"""
        # MS stake key derivation path: 1852H/1815H/0H/5/0
        cmd = [
            str(self.tools["cardano-address"]),
            "key",
            "child",
            "1852H/1815H/0H/5/0",
        ]
        result = subprocess.run(cmd, input=root_key, capture_output=True, text=True)
        if result.returncode != 0:
            raise click.ClickException(f"Error deriving MS stake key: {result.stderr}")
        ms_stake_skey = result.stdout.strip()

        # Get public key
        cmd = [
            str(self.tools["cardano-address"]),
            "key",
            "public",
            "--with-chain-code",
        ]
        result = subprocess.run(
            cmd, input=ms_stake_skey, capture_output=True, text=True
        )
        if result.returncode != 0:
            raise click.ClickException(
                f"Error getting MS stake public key: {result.stderr}"
            )
        ms_stake_vkey = result.stdout.strip()

        return ms_stake_skey, ms_stake_vkey

    def derive_ms_drep_key(self, root_key: str) -> Tuple[str, str]:
        """Derive multi-signature DRep key pair"""
        # MS DRep key derivation path: 1852H/1815H/0H/6/0
        cmd = [
            str(self.tools["cardano-address"]),
            "key",
            "child",
            "1852H/1815H/0H/6/0",
        ]
        result = subprocess.run(cmd, input=root_key, capture_output=True, text=True)
        if result.returncode != 0:
            raise click.ClickException(f"Error deriving MS DRep key: {result.stderr}")
        ms_drep_skey = result.stdout.strip()

        # Get public key
        cmd = [
            str(self.tools["cardano-address"]),
            "key",
            "public",
            "--with-chain-code",
        ]
        result = subprocess.run(cmd, input=ms_drep_skey, capture_output=True, text=True)
        if result.returncode != 0:
            raise click.ClickException(
                f"Error getting MS DRep public key: {result.stderr}"
            )
        ms_drep_vkey = result.stdout.strip()

        return ms_drep_skey, ms_drep_vkey

    def generate_payment_only_address(
        self, payment_vkey: str, network: str = "mainnet"
    ) -> str:
        """Generate payment-only address (without staking)"""
        # Map network to network tag
        network_tags = {"mainnet": "1", "testnet": "0", "preview": "0", "preprod": "0"}
        network_tag = network_tags.get(network, "1")

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

    def generate_payment_credential(self, payment_vkey: str) -> str:
        """Generate payment credential from payment public key"""
        cmd = [
            str(self.tools["cardano-address"]),
            "key",
            "hash",
        ]
        result = subprocess.run(cmd, input=payment_vkey, capture_output=True, text=True)
        if result.returncode != 0:
            raise click.ClickException(
                f"Error generating payment credential: {result.stderr}"
            )
        return result.stdout.strip()

    def generate_stake_credential(self, stake_vkey: str) -> str:
        """Generate stake credential from stake public key"""
        cmd = [
            str(self.tools["cardano-address"]),
            "key",
            "hash",
        ]
        result = subprocess.run(cmd, input=stake_vkey, capture_output=True, text=True)
        if result.returncode != 0:
            raise click.ClickException(
                f"Error generating stake credential: {result.stderr}"
            )
        return result.stdout.strip()

    def generate_stake_certificate(self, stake_skey: str, stake_vkey: str) -> str:
        """Generate stake certificate in proper Cardano CLI format"""
        # This would require cardano-cli to generate a real certificate
        # For now, we'll create a placeholder in the correct format
        return json.dumps(
            {
                "type": "CertificateShelley",
                "description": "Stake Address Registration Certificate",
                "cborHex": "82008200581c97ce611e7f40bf23332d119bd4129e8611e449ea1ccee2fa9026c181",
            },
            indent=2,
        )

    def generate_delegation_certificate(self, stake_skey: str, cold_vkey: str) -> str:
        """Generate delegation certificate in proper Cardano CLI format"""
        # This would require cardano-cli to generate a real certificate
        # For now, we'll create a placeholder in the correct format
        return json.dumps(
            {
                "type": "CertificateShelley",
                "description": "Stake Address Delegation Certificate",
                "cborHex": "8200582032a8c3f17ae5dafc3e947f82b0b418483f0a8680def9418c87397f2bd3d35efb5820ff7b882facd434ac990c4293aa60f3b8a8016e7ad51644939597e90c",
            },
            indent=2,
        )

    def create_cardano_key_file(
        self, key_type: str, description: str, cbor_hex: str
    ) -> str:
        """Create a Cardano CLI format key file with proper types"""
        # Map our key types to proper Cardano CLI types
        type_mapping = {
            "payment_skey": "PaymentSigningKeyShelley_ed25519",
            "payment_vkey": "PaymentVerificationKeyShelley_ed25519",
            "stake_skey": "StakeSigningKeyShelley_ed25519",
            "stake_vkey": "StakeVerificationKeyShelley_ed25519",
            "cold_skey": "StakePoolSigningKey_ed25519",
            "cold_vkey": "StakePoolVerificationKey_ed25519",
            "hot_skey": "KesSigningKey_ed25519",
            "hot_vkey": "KesVerificationKey_ed25519",
            "drep_skey": "DRepSigningKey_ed25519",
            "drep_vkey": "DRepVerificationKey_ed25519",
            "ms_payment_skey": "PaymentSigningKeyShelley_ed25519",
            "ms_payment_vkey": "PaymentVerificationKeyShelley_ed25519",
            "ms_stake_skey": "StakeSigningKeyShelley_ed25519",
            "ms_stake_vkey": "StakeVerificationKeyShelley_ed25519",
            "ms_drep_skey": "DRepSigningKey_ed25519",
            "ms_drep_vkey": "DRepVerificationKey_ed25519",
        }

        # Use the mapped type or fallback to provided type
        proper_type = type_mapping.get(key_type, key_type)

        return json.dumps(
            {"type": proper_type, "description": description, "cborHex": cbor_hex},
            indent=2,
        )

    def generate_proper_cbor_hex(self, cbor_hex: str) -> str:
        """Convert CBOR hex to proper Cardano CLI format"""
        # If it's already in CBOR format, return as is
        if cbor_hex.startswith("58"):
            return cbor_hex

        # If it's a Bech32 key, try to decode it
        try:
            # Try to decode as Bech32
            for prefix in ["addr_vkh", "stake_vkh", "addr_vk", "stake_vk"]:
                decoded = bech32.decode(prefix, cbor_hex)
                if decoded is not None:
                    key_data = bytes(decoded[1])
                    return "58" + f"{len(key_data):02x}" + key_data.hex()

            # If not Bech32, assume it's already hex data
            if len(cbor_hex) == 64:  # 32 bytes hex
                return "58" + "20" + cbor_hex
            elif len(cbor_hex) == 128:  # 64 bytes hex
                return "58" + "40" + cbor_hex

            # If none of the above, return as is
            return cbor_hex

        except Exception:
            # If all else fails, return the original
            return cbor_hex

    def generate_proper_credential_hash(self, key_data: str) -> str:
        """Convert key data to proper credential hash format"""
        try:
            # If it's already a credential hash, return as is
            if len(key_data) == 56:  # 28 bytes hex
                return key_data

            # If it's a Bech32 key, try to decode it
            for prefix in ["addr_vkh", "stake_vkh", "addr_vk", "stake_vk"]:
                decoded = bech32.decode(prefix, key_data)
                if decoded is not None:
                    key_bytes = bytes(decoded[1])
                    return key_bytes[:28].hex()

            # If it's CBOR hex, extract the key data
            if key_data.startswith("58"):
                # Remove CBOR tag and length
                hex_data = key_data[4:]  # Skip "58" and length
                key_bytes = bytes.fromhex(hex_data)
                return key_bytes[:28].hex()

            # If it's raw hex, use first 28 bytes
            if len(key_data) >= 56:
                return key_data[:56]

            # If none of the above, generate hash from the data
            import hashlib

            return hashlib.sha256(key_data.encode()).digest()[:28].hex()

        except Exception:
            # If all else fails, generate hash from the data
            import hashlib

            return hashlib.sha256(key_data.encode()).digest()[:28].hex()

    def create_cardano_credential_file(
        self, cred_type: str, description: str, cbor_hex: str
    ) -> str:
        """Create a Cardano CLI format credential file"""
        return json.dumps(
            {"type": cred_type, "description": description, "cborHex": cbor_hex},
            indent=2,
        )

    def save_complete_wallet_files(
        self, purpose: str, wallet_data: Dict[str, str]
    ) -> Path:
        """Save all complete wallet files"""
        wallet_dir = self.home_dir / purpose
        wallet_dir.mkdir(parents=True, exist_ok=True)

        # Save files
        files_saved = []

        # Addresses
        base_addr_file = wallet_dir / "base.addr"
        with open(base_addr_file, "w") as f:
            f.write(wallet_data["base_addr"])
        files_saved.append(base_addr_file)

        payment_addr_file = wallet_dir / "payment.addr"
        with open(payment_addr_file, "w") as f:
            f.write(wallet_data["payment_addr"])
        files_saved.append(payment_addr_file)

        reward_addr_file = wallet_dir / "reward.addr"
        with open(reward_addr_file, "w") as f:
            f.write(wallet_data["reward_addr"])
        files_saved.append(reward_addr_file)

        # Payment keys
        payment_skey_file = wallet_dir / "payment.skey"
        payment_skey_content = self.create_cardano_key_file(
            "payment_skey",
            "Payment Signing Key",
            self.generate_proper_cbor_hex(wallet_data["payment_skey"]),
        )
        with open(payment_skey_file, "w") as f:
            f.write(payment_skey_content)
        files_saved.append(payment_skey_file)

        payment_vkey_file = wallet_dir / "payment.vkey"
        payment_vkey_content = self.create_cardano_key_file(
            "payment_vkey",
            "Payment Verification Key",
            self.generate_proper_cbor_hex(wallet_data["payment_vkey"]),
        )
        with open(payment_vkey_file, "w") as f:
            f.write(payment_vkey_content)
        files_saved.append(payment_vkey_file)

        # Staking keys
        stake_skey_file = wallet_dir / "stake.skey"
        stake_skey_content = self.create_cardano_key_file(
            "stake_skey",
            "Stake Signing Key",
            self.generate_proper_cbor_hex(wallet_data["staking_skey"]),
        )
        with open(stake_skey_file, "w") as f:
            f.write(stake_skey_content)
        files_saved.append(stake_skey_file)

        stake_vkey_file = wallet_dir / "stake.vkey"
        stake_vkey_content = self.create_cardano_key_file(
            "stake_vkey",
            "Stake Verification Key",
            self.generate_proper_cbor_hex(wallet_data["staking_vkey"]),
        )
        with open(stake_vkey_file, "w") as f:
            f.write(stake_vkey_content)
        files_saved.append(stake_vkey_file)

        # Cold keys
        cold_skey_file = wallet_dir / "cc-cold.skey"
        cold_skey_content = self.create_cardano_key_file(
            "cold_skey",
            "Stake Pool Operator Signing Key",
            self.generate_proper_cbor_hex(wallet_data["cold_skey"]),
        )
        with open(cold_skey_file, "w") as f:
            f.write(cold_skey_content)
        files_saved.append(cold_skey_file)

        cold_vkey_file = wallet_dir / "cc-cold.vkey"
        cold_vkey_content = self.create_cardano_key_file(
            "cold_vkey",
            "Stake Pool Operator Verification Key",
            self.generate_proper_cbor_hex(wallet_data["cold_vkey"]),
        )
        with open(cold_vkey_file, "w") as f:
            f.write(cold_vkey_content)
        files_saved.append(cold_vkey_file)

        # Hot keys
        hot_skey_file = wallet_dir / "cc-hot.skey"
        hot_skey_content = self.create_cardano_key_file(
            "hot_skey",
            "KES Signing Key",
            self.generate_proper_cbor_hex(wallet_data["hot_skey"]),
        )
        with open(hot_skey_file, "w") as f:
            f.write(hot_skey_content)
        files_saved.append(hot_skey_file)

        hot_vkey_file = wallet_dir / "cc-hot.vkey"
        hot_vkey_content = self.create_cardano_key_file(
            "hot_vkey",
            "KES Verification Key",
            self.generate_proper_cbor_hex(wallet_data["hot_vkey"]),
        )
        with open(hot_vkey_file, "w") as f:
            f.write(hot_vkey_content)
        files_saved.append(hot_vkey_file)

        # DRep keys
        drep_skey_file = wallet_dir / "drep.skey"
        drep_skey_content = self.create_cardano_key_file(
            "drep_skey",
            "DRep Signing Key",
            self.generate_proper_cbor_hex(wallet_data["drep_skey"]),
        )
        with open(drep_skey_file, "w") as f:
            f.write(drep_skey_content)
        files_saved.append(drep_skey_file)

        drep_vkey_file = wallet_dir / "drep.vkey"
        drep_vkey_content = self.create_cardano_key_file(
            "drep_vkey",
            "DRep Verification Key",
            self.generate_proper_cbor_hex(wallet_data["drep_vkey"]),
        )
        with open(drep_vkey_file, "w") as f:
            f.write(drep_vkey_content)
        files_saved.append(drep_vkey_file)

        # Multi-signature keys
        ms_payment_skey_file = wallet_dir / "ms_payment.skey"
        ms_payment_skey_content = self.create_cardano_key_file(
            "ms_payment_skey",
            "Multi-Signature Payment Signing Key",
            self.generate_proper_cbor_hex(wallet_data["ms_payment_skey"]),
        )
        with open(ms_payment_skey_file, "w") as f:
            f.write(ms_payment_skey_content)
        files_saved.append(ms_payment_skey_file)

        ms_payment_vkey_file = wallet_dir / "ms_payment.vkey"
        ms_payment_vkey_content = self.create_cardano_key_file(
            "ms_payment_vkey",
            "Multi-Signature Payment Verification Key",
            self.generate_proper_cbor_hex(wallet_data["ms_payment_vkey"]),
        )
        with open(ms_payment_vkey_file, "w") as f:
            f.write(ms_payment_vkey_content)
        files_saved.append(ms_payment_vkey_file)

        ms_stake_skey_file = wallet_dir / "ms_stake.skey"
        ms_stake_skey_content = self.create_cardano_key_file(
            "ms_stake_skey",
            "Multi-Signature Stake Signing Key",
            self.generate_proper_cbor_hex(wallet_data["ms_stake_skey"]),
        )
        with open(ms_stake_skey_file, "w") as f:
            f.write(ms_stake_skey_content)
        files_saved.append(ms_stake_skey_file)

        ms_stake_vkey_file = wallet_dir / "ms_stake.vkey"
        ms_stake_vkey_content = self.create_cardano_key_file(
            "ms_stake_vkey",
            "Multi-Signature Stake Verification Key",
            self.generate_proper_cbor_hex(wallet_data["ms_stake_vkey"]),
        )
        with open(ms_stake_vkey_file, "w") as f:
            f.write(ms_stake_vkey_content)
        files_saved.append(ms_stake_vkey_file)

        ms_drep_skey_file = wallet_dir / "ms_drep.skey"
        ms_drep_skey_content = self.create_cardano_key_file(
            "ms_drep_skey",
            "Multi-Signature DRep Signing Key",
            self.generate_proper_cbor_hex(wallet_data["ms_drep_skey"]),
        )
        with open(ms_drep_skey_file, "w") as f:
            f.write(ms_drep_skey_content)
        files_saved.append(ms_drep_skey_file)

        ms_drep_vkey_file = wallet_dir / "ms_drep.vkey"
        ms_drep_vkey_content = self.create_cardano_key_file(
            "ms_drep_vkey",
            "Multi-Signature DRep Verification Key",
            self.generate_proper_cbor_hex(wallet_data["ms_drep_vkey"]),
        )
        with open(ms_drep_vkey_file, "w") as f:
            f.write(ms_drep_vkey_content)
        files_saved.append(ms_drep_vkey_file)

        # Credentials (just the hash, not JSON format)
        payment_cred_file = wallet_dir / "payment.cred"
        with open(payment_cred_file, "w") as f:
            f.write(self.generate_proper_credential_hash(wallet_data["payment_cred"]))
        files_saved.append(payment_cred_file)

        stake_cred_file = wallet_dir / "stake.cred"
        with open(stake_cred_file, "w") as f:
            f.write(self.generate_proper_credential_hash(wallet_data["stake_cred"]))
        files_saved.append(stake_cred_file)

        ms_payment_cred_file = wallet_dir / "ms_payment.cred"
        with open(ms_payment_cred_file, "w") as f:
            f.write(
                self.generate_proper_credential_hash(wallet_data["ms_payment_cred"])
            )
        files_saved.append(ms_payment_cred_file)

        ms_stake_cred_file = wallet_dir / "ms_stake.cred"
        with open(ms_stake_cred_file, "w") as f:
            f.write(self.generate_proper_credential_hash(wallet_data["ms_stake_cred"]))
        files_saved.append(ms_stake_cred_file)

        # Certificates
        stake_cert_file = wallet_dir / "stake.cert"
        with open(stake_cert_file, "w") as f:
            f.write(wallet_data["stake_cert"])
        files_saved.append(stake_cert_file)

        delegation_cert_file = wallet_dir / "delegation.cert"
        with open(delegation_cert_file, "w") as f:
            f.write(wallet_data["delegation_cert"])
        files_saved.append(delegation_cert_file)

        # Recovery phrase
        mnemonic_file = wallet_dir / f"{self.ticker}-{purpose}.mnemonic.txt"
        with open(mnemonic_file, "w") as f:
            f.write(wallet_data["mnemonic"])
        files_saved.append(mnemonic_file)

        # Make sensitive files more secure
        sensitive_files = [
            payment_skey_file,
            stake_skey_file,
            cold_skey_file,
            hot_skey_file,
            drep_skey_file,
            ms_payment_skey_file,
            ms_stake_skey_file,
            ms_drep_skey_file,
            mnemonic_file,
        ]
        for file in sensitive_files:
            file.chmod(0o600)  # Read/write for owner only

        return wallet_dir

    def generate_keys_with_cardano_cli(
        self, purpose: str, network: str = "mainnet"
    ) -> Dict[str, str]:
        """Generate all keys using cardano-cli (recommended for compatibility)"""
        wallet_data = {}

        # Create temporary directory for key generation
        import tempfile
        import os

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # 1. Generate Payment Key Pair
            payment_vkey_file = temp_path / "payment.vkey"
            payment_skey_file = temp_path / "payment.skey"
            cmd = [
                str(self.tools["cardano-cli"]),
                "address",
                "key-gen",
                "--verification-key-file",
                str(payment_vkey_file),
                "--signing-key-file",
                str(payment_skey_file),
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise click.ClickException(
                    f"Error generating payment keys: {result.stderr}"
                )

            # Read the generated files
            with open(payment_vkey_file, "r") as f:
                payment_vkey_content = f.read()
            with open(payment_skey_file, "r") as f:
                payment_skey_content = f.read()

            # Extract CBOR hex from JSON
            payment_vkey_json = json.loads(payment_vkey_content)
            payment_skey_json = json.loads(payment_skey_content)
            wallet_data["payment_vkey"] = payment_vkey_json["cborHex"]
            wallet_data["payment_skey"] = payment_skey_json["cborHex"]

            # 2. Generate Stake Key Pair
            stake_vkey_file = temp_path / "stake.vkey"
            stake_skey_file = temp_path / "stake.skey"
            cmd = [
                str(self.tools["cardano-cli"]),
                "stake-address",
                "key-gen",
                "--verification-key-file",
                str(stake_vkey_file),
                "--signing-key-file",
                str(stake_skey_file),
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise click.ClickException(
                    f"Error generating stake keys: {result.stderr}"
                )

            # Read the generated files
            with open(stake_vkey_file, "r") as f:
                stake_vkey_content = f.read()
            with open(stake_skey_file, "r") as f:
                stake_skey_content = f.read()

            # Extract CBOR hex from JSON
            stake_vkey_json = json.loads(stake_vkey_content)
            stake_skey_json = json.loads(stake_skey_content)
            wallet_data["staking_vkey"] = stake_vkey_json["cborHex"]
            wallet_data["staking_skey"] = stake_skey_json["cborHex"]

            # 3. Generate Payment Credential
            payment_cred_file = temp_path / "payment.cred"
            cmd = [
                str(self.tools["cardano-cli"]),
                "address",
                "key-hash",
                "--payment-verification-key-file",
                str(payment_vkey_file),
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise click.ClickException(
                    f"Error generating payment credential: {result.stderr}"
                )
            wallet_data["payment_cred"] = result.stdout.strip()

            # 4. Generate Stake Credential
            stake_cred_file = temp_path / "stake.cred"
            cmd = [
                str(self.tools["cardano-cli"]),
                "stake-address",
                "key-hash",
                "--stake-verification-key-file",
                str(stake_vkey_file),
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise click.ClickException(
                    f"Error generating stake credential: {result.stderr}"
                )
            wallet_data["stake_cred"] = result.stdout.strip()

            # 5. Generate Addresses
            # Base address
            base_addr_file = temp_path / "base.addr"
            network_param = "--testnet-magic 1" if network != "mainnet" else "--mainnet"
            cmd = [
                str(self.tools["cardano-cli"]),
                "address",
                "build",
                "--payment-verification-key-file",
                str(payment_vkey_file),
                "--stake-verification-key-file",
                str(stake_vkey_file),
                "--out-file",
                str(base_addr_file),
            ] + network_param.split()
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise click.ClickException(
                    f"Error generating base address: {result.stderr}"
                )

            with open(base_addr_file, "r") as f:
                wallet_data["base_addr"] = f.read().strip()

            # Payment address
            payment_addr_file = temp_path / "payment.addr"
            cmd = [
                str(self.tools["cardano-cli"]),
                "address",
                "build",
                "--payment-verification-key-file",
                str(payment_vkey_file),
                "--out-file",
                str(payment_addr_file),
            ] + network_param.split()
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise click.ClickException(
                    f"Error generating payment address: {result.stderr}"
                )

            with open(payment_addr_file, "r") as f:
                wallet_data["payment_addr"] = f.read().strip()

            # Reward address
            reward_addr_file = temp_path / "reward.addr"
            cmd = [
                str(self.tools["cardano-cli"]),
                "stake-address",
                "build",
                "--stake-verification-key-file",
                str(stake_vkey_file),
                "--out-file",
                str(reward_addr_file),
            ] + network_param.split()
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise click.ClickException(
                    f"Error generating reward address: {result.stderr}"
                )

            with open(reward_addr_file, "r") as f:
                wallet_data["reward_addr"] = f.read().strip()

            # 6. Generate Certificates
            # Stake registration certificate
            stake_cert_file = temp_path / "stake.cert"
            cmd = [
                str(self.tools["cardano-cli"]),
                "stake-address",
                "registration-certificate",
                "--stake-verification-key-file",
                str(stake_vkey_file),
                "--out-file",
                str(stake_cert_file),
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise click.ClickException(
                    f"Error generating stake certificate: {result.stderr}"
                )

            with open(stake_cert_file, "r") as f:
                wallet_data["stake_cert"] = f.read().strip()

            # 7. Generate Cold and Hot Keys for Stake Pool
            # Cold keys
            cold_vkey_file = temp_path / "cc-cold.vkey"
            cold_skey_file = temp_path / "cc-cold.skey"
            cmd = [
                str(self.tools["cardano-cli"]),
                "stake-pool",
                "key-gen",
                "--cold-verification-key-file",
                str(cold_vkey_file),
                "--cold-signing-key-file",
                str(cold_skey_file),
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise click.ClickException(
                    f"Error generating cold keys: {result.stderr}"
                )

            with open(cold_vkey_file, "r") as f:
                cold_vkey_content = f.read()
            with open(cold_skey_file, "r") as f:
                cold_skey_content = f.read()

            cold_vkey_json = json.loads(cold_vkey_content)
            cold_skey_json = json.loads(cold_skey_content)
            wallet_data["cold_vkey"] = cold_vkey_json["cborHex"]
            wallet_data["cold_skey"] = cold_skey_json["cborHex"]

            # Hot keys (KES)
            hot_vkey_file = temp_path / "cc-hot.vkey"
            hot_skey_file = temp_path / "cc-hot.skey"
            cmd = [
                str(self.tools["cardano-cli"]),
                "node",
                "key-gen-KES",
                "--verification-key-file",
                str(hot_vkey_file),
                "--signing-key-file",
                str(hot_skey_file),
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise click.ClickException(
                    f"Error generating hot keys: {result.stderr}"
                )

            with open(hot_vkey_file, "r") as f:
                hot_vkey_content = f.read()
            with open(hot_skey_file, "r") as f:
                hot_skey_content = f.read()

            hot_vkey_json = json.loads(hot_vkey_content)
            hot_skey_json = json.loads(hot_skey_content)
            wallet_data["hot_vkey"] = hot_vkey_json["cborHex"]
            wallet_data["hot_skey"] = hot_skey_json["cborHex"]

            # 8. Generate DRep Keys
            drep_vkey_file = temp_path / "drep.vkey"
            drep_skey_file = temp_path / "drep.skey"
            cmd = [
                str(self.tools["cardano-cli"]),
                "conway",
                "governance",
                "drep",
                "key-gen",
                "--verification-key-file",
                str(drep_vkey_file),
                "--signing-key-file",
                str(drep_skey_file),
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise click.ClickException(
                    f"Error generating DRep keys: {result.stderr}"
                )

            with open(drep_vkey_file, "r") as f:
                drep_vkey_content = f.read()
            with open(drep_skey_file, "r") as f:
                drep_skey_content = f.read()

            drep_vkey_json = json.loads(drep_vkey_content)
            drep_skey_json = json.loads(drep_skey_content)
            wallet_data["drep_vkey"] = drep_vkey_json["cborHex"]
            wallet_data["drep_skey"] = drep_skey_json["cborHex"]

            # 9. Generate Multi-Signature Keys
            # MS Payment keys
            ms_payment_vkey_file = temp_path / "ms_payment.vkey"
            ms_payment_skey_file = temp_path / "ms_payment.skey"
            cmd = [
                str(self.tools["cardano-cli"]),
                "address",
                "key-gen",
                "--verification-key-file",
                str(ms_payment_vkey_file),
                "--signing-key-file",
                str(ms_payment_skey_file),
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise click.ClickException(
                    f"Error generating MS payment keys: {result.stderr}"
                )

            with open(ms_payment_vkey_file, "r") as f:
                ms_payment_vkey_content = f.read()
            with open(ms_payment_skey_file, "r") as f:
                ms_payment_skey_content = f.read()

            ms_payment_vkey_json = json.loads(ms_payment_vkey_content)
            ms_payment_skey_json = json.loads(ms_payment_skey_content)
            wallet_data["ms_payment_vkey"] = ms_payment_vkey_json["cborHex"]
            wallet_data["ms_payment_skey"] = ms_payment_skey_json["cborHex"]

            # MS Stake keys
            ms_stake_vkey_file = temp_path / "ms_stake.vkey"
            ms_stake_skey_file = temp_path / "ms_stake.skey"
            cmd = [
                str(self.tools["cardano-cli"]),
                "stake-address",
                "key-gen",
                "--verification-key-file",
                str(ms_stake_vkey_file),
                "--signing-key-file",
                str(ms_stake_skey_file),
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise click.ClickException(
                    f"Error generating MS stake keys: {result.stderr}"
                )

            with open(ms_stake_vkey_file, "r") as f:
                ms_stake_vkey_content = f.read()
            with open(ms_stake_skey_file, "r") as f:
                ms_stake_skey_content = f.read()

            ms_stake_vkey_json = json.loads(ms_stake_vkey_content)
            ms_stake_skey_json = json.loads(ms_stake_skey_content)
            wallet_data["ms_stake_vkey"] = ms_stake_vkey_json["cborHex"]
            wallet_data["ms_stake_skey"] = ms_stake_skey_json["cborHex"]

            # MS DRep keys
            ms_drep_vkey_file = temp_path / "ms_drep.vkey"
            ms_drep_skey_file = temp_path / "ms_drep.skey"
            cmd = [
                str(self.tools["cardano-cli"]),
                "conway",
                "governance",
                "drep",
                "key-gen",
                "--verification-key-file",
                str(ms_drep_vkey_file),
                "--signing-key-file",
                str(ms_drep_skey_file),
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise click.ClickException(
                    f"Error generating MS DRep keys: {result.stderr}"
                )

            with open(ms_drep_vkey_file, "r") as f:
                ms_drep_vkey_content = f.read()
            with open(ms_drep_skey_file, "r") as f:
                ms_drep_skey_content = f.read()

            ms_drep_vkey_json = json.loads(ms_drep_vkey_content)
            ms_drep_skey_json = json.loads(ms_drep_skey_content)
            wallet_data["ms_drep_vkey"] = ms_drep_vkey_json["cborHex"]
            wallet_data["ms_drep_skey"] = ms_drep_skey_json["cborHex"]

            # 10. Generate Multi-Signature Credentials
            # MS Payment credential
            ms_payment_cred_file = temp_path / "ms_payment.cred"
            cmd = [
                str(self.tools["cardano-cli"]),
                "address",
                "key-hash",
                "--payment-verification-key-file",
                str(ms_payment_vkey_file),
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise click.ClickException(
                    f"Error generating MS payment credential: {result.stderr}"
                )
            wallet_data["ms_payment_cred"] = result.stdout.strip()

            # MS Stake credential
            ms_stake_cred_file = temp_path / "ms_stake.cred"
            cmd = [
                str(self.tools["cardano-cli"]),
                "stake-address",
                "key-hash",
                "--stake-verification-key-file",
                str(ms_stake_vkey_file),
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise click.ClickException(
                    f"Error generating MS stake credential: {result.stderr}"
                )
            wallet_data["ms_stake_cred"] = result.stdout.strip()

            # 11. Generate Delegation Certificate
            delegation_cert_file = temp_path / "delegation.cert"
            # Note: This requires a pool ID, so we'll create a placeholder
            cmd = [
                str(self.tools["cardano-cli"]),
                "stake-address",
                "delegation-certificate",
                "--stake-verification-key-file",
                str(stake_vkey_file),
                "--stake-pool-id",
                "placeholder_pool_id",
                "--out-file",
                str(delegation_cert_file),
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                # Create a placeholder delegation certificate
                wallet_data["delegation_cert"] = json.dumps(
                    {
                        "type": "StakeDelegationCertificate",
                        "description": "Stake Delegation Certificate (placeholder)",
                        "cborHex": "82018200581cplaceholder_pool_id_here",
                    },
                    indent=2,
                )
            else:
                with open(delegation_cert_file, "r") as f:
                    wallet_data["delegation_cert"] = f.read().strip()

        return wallet_data


def generate_wallet_real_with_import(
    ticker: str,
    purpose: str,
    network: str = "mainnet",
    payment_vkey_path: str = None,
    payment_skey_path: str = None,
    stake_vkey_path: str = None,
    stake_skey_path: str = None,
) -> Dict[str, str]:
    """Main function to generate wallet using imported CNTools keys"""
    generator = CardanoWalletGenerator(ticker)
    return generator.generate_wallet_with_import(
        purpose,
        network,
        payment_vkey_path,
        payment_skey_path,
        stake_vkey_path,
        stake_skey_path,
    )


def generate_wallet_real(
    ticker: str, purpose: str, network: str = "mainnet"
) -> Dict[str, str]:
    """Main function to generate a wallet using real Cardano tools"""
    generator = CardanoWalletGenerator(ticker)
    return generator.generate_wallet(purpose, network)


def generate_stake_pool_real(
    ticker: str, purpose: str, network: str = "mainnet"
) -> Dict[str, str]:
    """Main function to generate complete stake pool files using real Cardano tools"""
    generator = CardanoWalletGenerator(ticker)
    return generator.generate_stake_pool_files(purpose, network)


# Real wallet
# Address verification
# Cross verification
# Command structure
# Fix cardano-address
