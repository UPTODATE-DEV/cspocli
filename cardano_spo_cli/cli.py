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
║                    Cardano SPO CLI v1.0.0                        ║
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
    required=True,
    type=click.Choice(["pledge", "rewards"]),
    help="Wallet purpose: pledge or rewards",
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
def generate(
    ticker: str,
    purpose: str,
    network: str,
    force: bool,
    no_banner: bool,
    quiet: bool,
    simple: bool,
):
    """
    Generate a secure Cardano wallet for stake pool operations

    Creates wallet files for pledge or rewards purposes:
    • base_addr - Address for pledge funds
    • reward_addr - Address for staking rewards
    • staking_skey - Private staking key (SENSITIVE)
    • staking_vkey - Public staking key
    • mnemonic.txt - 24-word recovery phrase (SENSITIVE)

    Storage: ~/.CSPO_{TICKER}/{PURPOSE}/
    Security: BIP39 recovery phrase, secure permissions (600)

    Examples:
        cspocli generate --ticker MYPOOL --purpose pledge
        cspocli generate -t ADA -p rewards --simple
        cspocli generate --ticker CARDANO --purpose pledge --quiet
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
        # Check if wallet already exists
        home_dir = Path.home() / f".CSPO_{ticker.upper()}"
        wallet_dir = home_dir / purpose

        if wallet_dir.exists() and not force:
            if not quiet:
                click.echo(
                    f"{Fore.YELLOW}Wallet {ticker}-{purpose} already exists{Style.RESET_ALL}"
                )
                if not click.confirm("Do you want to regenerate it?", default=False):
                    click.echo(f"{Fore.RED}Operation cancelled{Style.RESET_ALL}")
                    sys.exit(0)

        # Generate wallet
        if not quiet:
            click.echo(
                f"{Fore.CYAN}Generating {ticker}-{purpose} wallet...{Style.RESET_ALL}"
            )

        if simple:
            # Use simplified version
            from cardano_spo_cli.tools.wallet_simple import generate_wallet_simple

            wallet_data = generate_wallet_simple(ticker, purpose, network)
        else:
            # Use real Cardano tools by default
            try:
                from cardano_spo_cli.tools.wallet import generate_wallet_real

                wallet_data = generate_wallet_real(ticker, purpose, network)
            except click.ClickException as e:
                if "Real Cardano tools not available" in str(e):
                    click.echo(
                        f"{Fore.YELLOW}Real tools not available. Switching to simplified mode...{Style.RESET_ALL}"
                    )
                    from cardano_spo_cli.tools.wallet_simple import (
                        generate_wallet_simple,
                    )

                    wallet_data = generate_wallet_simple(ticker, purpose, network)
                else:
                    raise e

        # Display wallet information
        if not quiet:
            click.echo(
                f"\n{Fore.GREEN}Files generated in: {wallet_dir}{Style.RESET_ALL}"
            )

            # List generated files
            files = list(wallet_dir.glob(f"{ticker}-{purpose}.*"))
            for file in files:
                if file.name.endswith(".mnemonic.txt") or file.name.endswith(
                    ".staking_skey"
                ):
                    click.echo(f"  {Fore.RED}{file.name} (SENSITIVE){Style.RESET_ALL}")
                else:
                    click.echo(f"  {Fore.CYAN}{file.name}{Style.RESET_ALL}")

            # Display addresses
            click.echo(f"\n{Fore.CYAN}Generated addresses:{Style.RESET_ALL}")
            click.echo(f"  Base Address: {wallet_data['base_addr']}")
            click.echo(f"  Reward Address: {wallet_data['reward_addr']}")

            # Display next steps
            print_next_steps(ticker, purpose, wallet_dir)

        # Return information in quiet mode
        if quiet:
            result = {
                "ticker": ticker,
                "purpose": purpose,
                "wallet_dir": str(wallet_dir),
                "base_addr": wallet_data["base_addr"],
                "reward_addr": wallet_data["reward_addr"],
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
    "--password",
    required=True,
    help="Password for encrypted export",
)
def export(ticker: str, purpose: str, password: str):
    """
    Export wallet files in encrypted ZIP format

    Creates a password-protected ZIP archive containing all wallet files.
    Use this for secure backup and transfer to other systems.

    Examples:
        cspocli export --ticker MYPOOL --purpose pledge --password mypassword
    """
    try:
        from cardano_spo_cli.tools.export import WalletExporter

        exporter = WalletExporter(ticker)
        zip_path = exporter.create_encrypted_zip(purpose, password)

        click.echo(f"{Fore.GREEN}✅ Export created: {zip_path}{Style.RESET_ALL}")
        click.echo(
            f"{Fore.YELLOW}📦 Archive contains all wallet files{Style.RESET_ALL}"
        )
        click.echo(
            f"{Fore.CYAN}🔒 Protected with password: {password}{Style.RESET_ALL}"
        )

    except Exception as e:
        click.echo(f"{Fore.RED}❌ Export failed: {e}{Style.RESET_ALL}")
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
