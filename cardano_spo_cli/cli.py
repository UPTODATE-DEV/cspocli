#!/usr/bin/env python3
"""Cardano SPO CLI main module."""

import click
import sys
import json
from pathlib import Path
from colorama import Fore, Style, init

# Initialize colorama
init()


def print_banner():
    """Print welcome banner"""
    banner = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════╗
║                    Cardano SPO CLI v1.1.0                        ║
║              Professional Stake Pool Operator Tool                ║
╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
    click.echo(banner)


def print_security_warning():
    """Print security warning"""
    warning = f"""
{Fore.RED}SECURITY WARNING:{Style.RESET_ALL}
• This tool generates real cryptographic keys
• Store recovery phrases securely
• Never share private keys
• Create encrypted backups
"""
    click.echo(warning)


def print_next_steps(ticker: str, purpose: str, wallet_dir: Path):
    """Print next steps for the user"""
    steps = f"""
{Fore.GREEN}Next Steps:{Style.RESET_ALL}
1. Import the recovery phrase into a compatible Cardano wallet
2. Transfer funds to the base address for pledge
3. Keep the staking keys secure
4. Monitor your stake pool performance

{Fore.YELLOW}Files generated in: {wallet_dir}{Style.RESET_ALL}
"""
    click.echo(steps)


@click.group()
def cli():
    """
    Cardano SPO CLI - Professional Stake Pool Operator Tool

    Generate secure Cardano wallets for stake pool operations.
    Creates 24-word recovery phrases, addresses, and keys for pledge/rewards wallets.

    Files stored in: ~/.CSPO_{TICKER_NAME}/{purpose}/
    Security: Local storage with secure permissions.

    Examples:
        cspocli generate --ticker MYPOOL --purpose pledge
        cspocli generate -t MYPOOL -p rewards --simple
        cspocli generate --ticker MYPOOL --complete
        cspocli secure --ticker MYPOOL --purpose pledge --password mypass
        cspocli view --ticker MYPOOL --purpose pledge --password mypass
        cspocli version
    """
    pass


@cli.command()
@click.option(
    "--ticker",
    "-t",
    required=True,
    help="Pool ticker symbol (e.g., MYPOOL, ADA, CARDANO)",
)
@click.option(
    "--purpose",
    "-p",
    type=click.Choice(["pledge", "rewards", "all"]),
    help="Wallet purpose: pledge, rewards, or all (default: all)",
)
@click.option(
    "--network",
    "-n",
    default="mainnet",
    type=click.Choice(["mainnet", "testnet", "preview", "preprod"]),
    help="Cardano network (default: mainnet)",
)
@click.option(
    "--force",
    "-f",
    is_flag=True,
    help="Force regeneration of existing wallet",
)
@click.option("--no-banner", is_flag=True, help="Skip welcome banner")
@click.option(
    "--quiet",
    "-q",
    is_flag=True,
    help="Quiet mode - JSON output only",
)
@click.option(
    "--simple",
    "-s",
    is_flag=True,
    help="Use simplified mode (no external tools)",
)
@click.option(
    "--complete",
    "-c",
    is_flag=True,
    help="Generate complete stake pool files (all keys, addresses, credentials, certificates)",
)
def generate(
    ticker: str,
    purpose: str = "all",
    network: str = "mainnet",
    force: bool = False,
    no_banner: bool = False,
    quiet: bool = False,
    simple: bool = False,
    complete: bool = False,
):
    """
    Generate secure Cardano wallets for stake pool operations

    Creates wallet files for pledge and/or rewards purposes:
    • base_addr - Address for pledge funds
    • reward_addr - Address for staking rewards
    • staking_skey - Private staking key (SENSITIVE)
    • staking_vkey - Public staking key
    • mnemonic.txt - 24-word recovery phrase (SENSITIVE)

    With --complete flag, generates all stake pool files:
    • All addresses (base.addr, payment.addr, reward.addr)
    • All keys (payment, stake, cold, hot, DRep, multi-signature)
    • All credentials (payment.cred, stake.cred, ms_payment.cred, ms_stake.cred)
    • All certificates (stake.cert, delegation.cert)

    Storage: ~/.CSPO_{TICKER}/{PURPOSE}/
    Security: BIP39 recovery phrase, secure permissions (600)

    Examples:
        cspocli generate --ticker MYPOOL                    # Generate all wallets
        cspocli generate --ticker MYPOOL --purpose pledge   # Generate pledge only
        cspocli generate -t ADA -p rewards --simple         # Generate rewards only
        cspocli generate --ticker CARDANO --quiet           # Generate all quietly
        cspocli generate --ticker MYPOOL --complete         # Generate complete stake pool files
    """

    if not quiet and not no_banner:
        print_banner()

    if not quiet:
        print_security_warning()

        # Ask for confirmation
        if not click.confirm("Do you want to continue?", default=True):
            click.echo(f"{Fore.RED}Operation cancelled{Style.RESET_ALL}")
            sys.exit(0)

    try:
        # Determine which purposes to generate
        if purpose is None or purpose == "all":
            purposes = ["pledge", "rewards"]
        else:
            purposes = [purpose]

        home_dir = Path.home() / f".CSPO_{ticker.upper()}"
        all_wallet_data = {}

        # Check if any wallets already exist
        existing_wallets = []
        for purpose_item in purposes:
            wallet_dir = home_dir / purpose_item
            if wallet_dir.exists() and not force:
                existing_wallets.append(purpose_item)

        if existing_wallets and not force:
            if not quiet:
                click.echo(
                    f"{Fore.YELLOW}Wallets {ticker}-{', '.join(existing_wallets)} already exist{Style.RESET_ALL}"
                )
                if not click.confirm("Do you want to regenerate them?", default=False):
                    click.echo(f"{Fore.RED}Operation cancelled{Style.RESET_ALL}")
                    sys.exit(0)

        # Generate wallets for each purpose
        for purpose_item in purposes:
            wallet_dir = home_dir / purpose_item

            if not quiet:
                click.echo(
                    f"{Fore.CYAN}Generating {ticker}-{purpose_item} wallet...{Style.RESET_ALL}"
                )

            if complete:
                # Use complete stake pool generation
                try:
                    from cardano_spo_cli.tools.wallet import generate_stake_pool_real

                    wallet_data = generate_stake_pool_real(
                        ticker, purpose_item, network
                    )
                except click.ClickException as e:
                    if "Real Cardano tools not available" in str(e):
                        click.echo(
                            f"{Fore.YELLOW}Real tools not available. Complete mode requires real tools.{Style.RESET_ALL}"
                        )
                        raise e
                    else:
                        raise e
            elif simple:
                # Use simplified version
                from cardano_spo_cli.tools.wallet_simple import generate_wallet_simple

                wallet_data = generate_wallet_simple(ticker, purpose_item, network)
            else:
                # Use real Cardano tools by default
                try:
                    from cardano_spo_cli.tools.wallet import generate_wallet_real

                    wallet_data = generate_wallet_real(ticker, purpose_item, network)
                except click.ClickException as e:
                    if "Real Cardano tools not available" in str(e):
                        click.echo(
                            f"{Fore.YELLOW}Real tools not available. Switching to simplified mode...{Style.RESET_ALL}"
                        )
                        from cardano_spo_cli.tools.wallet_simple import (
                            generate_wallet_simple,
                        )

                        wallet_data = generate_wallet_simple(
                            ticker, purpose_item, network
                        )
                    else:
                        raise e

            all_wallet_data[purpose_item] = wallet_data

        # Display wallet information
        if not quiet:
            for purpose_item in purposes:
                wallet_dir = home_dir / purpose_item
                click.echo(
                    f"\n{Fore.GREEN}Files generated in: {wallet_dir}{Style.RESET_ALL}"
                )

                # List generated files
                files = list(wallet_dir.glob(f"{ticker}-{purpose_item}.*"))
                for file in files:
                    if file.name.endswith(".mnemonic.txt") or file.name.endswith(
                        ".staking_skey"
                    ):
                        click.echo(
                            f"  {Fore.RED}{file.name} (SENSITIVE){Style.RESET_ALL}"
                        )
                    else:
                        click.echo(f"  {Fore.CYAN}{file.name}{Style.RESET_ALL}")

                # Display addresses
                click.echo(
                    f"\n{Fore.CYAN}Generated addresses for {purpose_item}:{Style.RESET_ALL}"
                )
                click.echo(
                    f"  Base Address: {all_wallet_data[purpose_item]['base_addr']}"
                )
                click.echo(
                    f"  Reward Address: {all_wallet_data[purpose_item]['reward_addr']}"
                )

            # Display next steps
            if purpose is None or purpose == "all":
                # For "all" purpose, show the main directory
                print_next_steps(ticker, "all wallets", home_dir)
            else:
                print_next_steps(ticker, purpose, home_dir / purpose)

        # Return information in quiet mode
        if quiet:
            if purpose is None or purpose == "all":
                result = {"ticker": ticker, "purpose": "all", "wallets": {}}
                for purpose_item in purposes:
                    wallet_dir = home_dir / purpose_item
                    result["wallets"][purpose_item] = {
                        "wallet_dir": str(wallet_dir),
                        "base_addr": all_wallet_data[purpose_item]["base_addr"],
                        "reward_addr": all_wallet_data[purpose_item]["reward_addr"],
                        "files": [
                            str(f)
                            for f in wallet_dir.glob(f"{ticker}-{purpose_item}.*")
                        ],
                    }
            else:
                wallet_dir = home_dir / purpose
                result = {
                    "ticker": ticker,
                    "purpose": purpose,
                    "wallet_dir": str(wallet_dir),
                    "base_addr": all_wallet_data[purpose]["base_addr"],
                    "reward_addr": all_wallet_data[purpose]["reward_addr"],
                    "files": [str(f) for f in wallet_dir.glob(f"{ticker}-{purpose}.*")],
                }
            click.echo(json.dumps(result, indent=2))

    except click.ClickException as e:
        click.echo(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        click.echo(f"{Fore.RED}❌ Unexpected error: {e}{Style.RESET_ALL}")
        sys.exit(1)


@cli.command()
@click.option(
    "--ticker",
    "-t",
    required=True,
    help="Pool ticker symbol (e.g., MYPOOL, ADA, CARDANO)",
)
@click.option(
    "--purpose",
    "-p",
    required=True,
    type=click.Choice(["pledge", "rewards"]),
    help="Wallet purpose: pledge or rewards",
)
@click.option(
    "--payment-vkey",
    required=True,
    help="Path to payment verification key file (CNTools format)",
)
@click.option(
    "--payment-skey",
    required=True,
    help="Path to payment signing key file (CNTools format)",
)
@click.option(
    "--stake-vkey",
    required=True,
    help="Path to stake verification key file (CNTools format)",
)
@click.option(
    "--stake-skey",
    required=True,
    help="Path to stake signing key file (CNTools format)",
)
@click.option(
    "--network",
    "-n",
    default="mainnet",
    type=click.Choice(["mainnet", "testnet", "preview", "preprod"]),
    help="Cardano network (default: mainnet)",
)
@click.option("--no-banner", is_flag=True, help="Skip welcome banner")
@click.option(
    "-q",
    "--quiet",
    is_flag=True,
    help="Quiet mode - JSON output only",
)
def import_keys(
    ticker: str,
    purpose: str,
    payment_vkey: str,
    payment_skey: str,
    stake_vkey: str,
    stake_skey: str,
    network: str = "mainnet",
    no_banner: bool = False,
    quiet: bool = False,
):
    """
    Import existing CNTools keys into cspocli wallet.

    This command imports existing CNTools keys and generates compatible addresses
    and files for use with cspocli. Useful when you have existing CNTools wallets
    that you want to use with cspocli.

    Examples:
        cspocli import-keys --ticker MYPOOL --purpose pledge \\
            --payment-vkey /opt/apex/cnode/priv/wallet/wallet_hope/payment.vkey \\
            --payment-skey /opt/apex/cnode/priv/wallet/wallet_hope/payment.skey \\
            --stake-vkey /opt/apex/cnode/priv/wallet/wallet_hope/stake.vkey \\
            --stake-skey /opt/apex/cnode/priv/wallet/wallet_hope/stake.skey

        cspocli import-keys -t MYPOOL -p rewards \\
            --payment-vkey /path/to/payment.vkey \\
            --payment-skey /path/to/payment.skey \\
            --stake-vkey /path/to/stake.vkey \\
            --stake-skey /path/to/stake.skey \\
            --network testnet
    """
    if not no_banner:
        print_banner()

    if not quiet:
        print_security_warning()

    try:
        from cardano_spo_cli.tools.wallet import generate_wallet_real_with_import

        result = generate_wallet_real_with_import(
            ticker,
            purpose,
            network,
            payment_vkey,
            payment_skey,
            stake_vkey,
            stake_skey,
        )

        if quiet:
            # JSON output for scripts
            output = {
                "success": True,
                "ticker": ticker,
                "purpose": purpose,
                "network": network,
                "base_addr": result["base_addr"],
                "reward_addr": result["reward_addr"],
                "wallet_dir": str(Path.home() / f".CSPO_{ticker.upper()}" / purpose),
            }
            click.echo(json.dumps(output, indent=2))
        else:
            click.echo(f"{Fore.GREEN}✅ Keys imported successfully{Style.RESET_ALL}")
            click.echo(
                f"📁 Wallet directory: {Path.home() / f'.CSPO_{ticker.upper()}' / purpose}"
            )
            click.echo(f"🔑 Base address: {result['base_addr']}")
            click.echo(f"🔑 Reward address: {result['reward_addr']}")
            click.echo(f"💡 Use 'cspocli secure' to protect sensitive files")

    except Exception as e:
        if quiet:
            output = {"success": False, "error": str(e)}
            click.echo(json.dumps(output, indent=2))
        else:
            click.echo(f"{Fore.RED}❌ Import failed: {e}{Style.RESET_ALL}")
        sys.exit(1)


@cli.command()
@click.option(
    "--ticker",
    "-t",
    required=True,
    help="Pool ticker symbol (e.g., MYPOOL, ADA, CARDANO)",
)
@click.option(
    "--purpose",
    "-p",
    required=True,
    type=click.Choice(["pledge", "rewards"]),
    help="Wallet purpose: pledge or rewards",
)
@click.option(
    "--password",
    required=True,
    help="Password for encrypted export",
)
def export(ticker: str, purpose: str, password: str):
    """
    Export wallet files in encrypted ZIP format for secure backup and transfer.

    Creates a password-protected ZIP archive containing all wallet files.
    The archive is encrypted using AES-256 encryption.

    Examples:
        cspocli export --ticker MYPOOL --purpose pledge --password mypass
        cspocli export -t ADA -p rewards --password securepass123
    """
    from cardano_spo_cli.tools.export import export_wallet_files

    try:
        result = export_wallet_files(ticker, purpose, password)
        click.echo(f"{Fore.GREEN}✅ Export created successfully{Style.RESET_ALL}")
        click.echo(f"📦 Encrypted archive: {result['archive_path']}")
        click.echo(f"🔑 Key file: {result['key_path']}")
        click.echo(f"📊 Archive size: {result['size']} bytes")
    except Exception as e:
        click.echo(f"{Fore.RED}❌ Export failed: {e}{Style.RESET_ALL}")
        sys.exit(1)


@cli.command()
@click.option(
    "--ticker",
    "-t",
    required=True,
    help="Pool ticker symbol (e.g., MYPOOL, ADA, CARDANO)",
)
@click.option(
    "--purpose",
    "-p",
    required=True,
    type=click.Choice(["pledge", "rewards"]),
    help="Wallet purpose: pledge or rewards",
)
@click.option(
    "--password",
    required=True,
    help="Password to protect sensitive files",
)
def secure(ticker: str, purpose: str, password: str):
    """
    Secure sensitive wallet files with password protection.

    Encrypts all sensitive files (.skey, .mnemonic.txt) in the wallet directory
    using AES-256 encryption. Files can only be viewed with the correct password.

    Examples:
        cspocli secure --ticker MYPOOL --purpose pledge --password mypass
        cspocli secure -t ADA -p rewards --password securepass123
    """
    from cardano_spo_cli.tools.secure import secure_wallet_files

    try:
        result = secure_wallet_files(ticker, purpose, password)
        click.echo(f"{Fore.GREEN}✅ Wallet secured successfully{Style.RESET_ALL}")
        click.echo(f"🔒 Secured files: {result['secured_count']}")
        click.echo(f"📁 Wallet directory: {result['wallet_dir']}")
        click.echo(f"💡 Use 'cspocli view' to access secured files")
    except Exception as e:
        click.echo(f"{Fore.RED}❌ Security operation failed: {e}{Style.RESET_ALL}")
        sys.exit(1)


@cli.command()
@click.option(
    "--ticker",
    "-t",
    required=True,
    help="Pool ticker symbol (e.g., MYPOOL, ADA, CARDANO)",
)
@click.option(
    "--purpose",
    "-p",
    required=True,
    type=click.Choice(["pledge", "rewards"]),
    help="Wallet purpose: pledge or rewards",
)
@click.option(
    "--password",
    required=True,
    help="Password to decrypt sensitive files",
)
@click.option(
    "--file",
    "-f",
    help="Specific file to view (e.g., payment.skey, mnemonic.txt)",
)
def view(ticker: str, purpose: str, password: str, file: str = None):
    """
    View secured wallet files with password authentication.

    Decrypts and displays sensitive wallet files that were secured with 'cspocli secure'.
    Requires the correct password to access the files.

    Examples:
        cspocli view --ticker MYPOOL --purpose pledge --password mypass
        cspocli view -t ADA -p rewards --password securepass123 --file payment.skey
        cspocli view --ticker MYPOOL --purpose pledge --password mypass --file mnemonic.txt
    """
    from cardano_spo_cli.tools.secure import view_wallet_files

    try:
        result = view_wallet_files(ticker, purpose, password, file)
        if file:
            click.echo(f"{Fore.GREEN}📄 File: {file}{Style.RESET_ALL}")
            click.echo(result["content"])
        else:
            click.echo(f"{Fore.GREEN}📁 Available secured files:{Style.RESET_ALL}")
            for secured_file in result["files"]:
                click.echo(f"  • {secured_file}")
            click.echo(f"\n💡 Use --file option to view specific file content")
    except Exception as e:
        click.echo(f"{Fore.RED}❌ View operation failed: {e}{Style.RESET_ALL}")
        sys.exit(1)


@cli.command()
def version():
    """Display version and build information."""
    from cardano_spo_cli.version import (
        get_full_version,
        get_git_version,
        get_git_commit_hash,
    )

    version_info = get_full_version()
    git_version = get_git_version()
    commit_hash = get_git_commit_hash()

    click.echo(f"{Fore.CYAN}Cardano SPO CLI{Style.RESET_ALL}")
    click.echo(f"Version: {Fore.GREEN}{version_info}{Style.RESET_ALL}")
    click.echo(f"Git Tag: {Fore.YELLOW}{git_version}{Style.RESET_ALL}")
    click.echo(f"Commit: {Fore.BLUE}{commit_hash}{Style.RESET_ALL}")


def main():
    """Main entry point"""
    cli()


if __name__ == "__main__":
    main()
