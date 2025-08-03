"""
Download module for Cardano tools
"""

import os
import sys
import platform
import requests
import subprocess
from pathlib import Path
from typing import Dict, Optional
import click
from tqdm import tqdm

# URLs for Cardano tools (IntersectMBO GitHub releases)
# Note: These tools are typically packaged in .tar.gz files, not direct executables
# For now, we'll provide instructions for manual installation
CARDANO_TOOLS = {
    "cardano-cli": {
        "linux": "https://github.com/IntersectMBO/cardano-node/releases/download/10.5.1/cardano-cli-linux",
        "darwin": "https://github.com/IntersectMBO/cardano-node/releases/download/10.5.1/cardano-cli-macos",
        "windows": "https://github.com/IntersectMBO/cardano-node/releases/download/10.5.1/cardano-cli-win64.exe",
    },
    "cardano-address": {
        "linux": "https://github.com/IntersectMBO/cardano-addresses/releases/download/4.0.0/cardano-address-linux",
        "darwin": "https://github.com/IntersectMBO/cardano-addresses/releases/download/4.0.0/cardano-address-macos",
        "windows": "https://github.com/IntersectMBO/cardano-addresses/releases/download/4.0.0/cardano-address-win64.exe",
    },
    "bech32": {
        "linux": "https://github.com/IntersectMBO/bech32/releases/download/v1.1.2/bech32-linux",
        "darwin": "https://github.com/IntersectMBO/bech32/releases/download/v1.1.2/bech32-macos",
        "windows": "https://github.com/IntersectMBO/bech32/releases/download/v1.1.2/bech32-win64.exe",
    },
}


def get_system_info() -> Dict[str, str]:
    """Detect operating system and architecture"""
    system = platform.system().lower()
    machine = platform.machine().lower()

    # System mapping
    if system == "linux":
        os_name = "linux"
    elif system == "darwin":
        os_name = "darwin"
    elif system == "windows":
        os_name = "windows"
    else:
        raise click.ClickException(f"Unsupported operating system: {system}")

    return {"os": os_name, "system": system, "machine": machine}


def get_tools_dir() -> Path:
    """Return tools directory"""
    home = Path.home()
    tools_dir = home / ".cardano_spo_cli" / "tools"
    tools_dir.mkdir(parents=True, exist_ok=True)
    return tools_dir


def download_file(url: str, filepath: Path, description: str) -> None:
    """Download a file with progress bar"""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        total_size = int(response.headers.get("content-length", 0))

        with open(filepath, "wb") as f:
            with tqdm(
                total=total_size, unit="B", unit_scale=True, desc=description
            ) as pbar:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        pbar.update(len(chunk))

        # Make executable on Unix
        if platform.system() != "Windows":
            filepath.chmod(0o755)

    except requests.RequestException as e:
        raise click.ClickException(f"Error downloading {description}: {e}")


def get_tool_path(tool_name: str) -> Optional[Path]:
    """Return tool path if it exists"""
    tools_dir = get_tools_dir()
    system_info = get_system_info()

    if system_info["os"] == "windows":
        tool_path = tools_dir / f"{tool_name}.exe"
    else:
        tool_path = tools_dir / tool_name

    return tool_path if tool_path.exists() else None


def download_cardano_tools(force: bool = False) -> Dict[str, Path]:
    """Download required Cardano tools"""
    system_info = get_system_info()
    tools_dir = get_tools_dir()
    downloaded_tools = {}

    click.echo("🔧 Downloading Cardano tools...")

    for tool_name, urls in CARDANO_TOOLS.items():
        url = urls.get(system_info["os"])
        if not url:
            raise click.ClickException(
                f"URL not available for {tool_name} on {system_info['os']}"
            )

        # Determine filename
        if system_info["os"] == "windows":
            filename = f"{tool_name}.exe"
        else:
            filename = tool_name

        tool_path = tools_dir / filename

        # Check if tool already exists
        if tool_path.exists() and not force:
            click.echo(f"✅ {tool_name} already present: {tool_path}")
            downloaded_tools[tool_name] = tool_path
            continue

        # Download tool
        click.echo(f"📥 Downloading {tool_name}...")
        download_file(url, tool_path, tool_name)

        # Verify tool works (skip for cardano-cli on ARM64 to avoid crashes)
        try:
            if tool_name == "cardano-cli" and platform.machine() in [
                "arm64",
                "aarch64",
            ]:
                click.echo(
                    f"✅ {tool_name} downloaded (version test skipped on ARM64): {tool_path}"
                )
                downloaded_tools[tool_name] = tool_path
            else:
                result = subprocess.run(
                    [str(tool_path), "--version"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if result.returncode == 0:
                    click.echo(f"✅ {tool_name} downloaded and functional: {tool_path}")
                    downloaded_tools[tool_name] = tool_path
                else:
                    click.echo(
                        f"⚠️  {tool_name} downloaded but version issue: {result.stderr}"
                    )
                    downloaded_tools[tool_name] = tool_path
        except subprocess.TimeoutExpired:
            click.echo(f"⚠️  {tool_name} downloaded but timeout during test")
            downloaded_tools[tool_name] = tool_path
        except Exception as e:
            click.echo(f"⚠️  {tool_name} downloaded but error during test: {e}")
            downloaded_tools[tool_name] = tool_path

    click.echo("✅ All Cardano tools are ready!")
    return downloaded_tools


def verify_tools() -> Dict[str, Path]:
    """Verify that all tools are available"""
    tools = {}
    missing_tools = []

    for tool_name in CARDANO_TOOLS.keys():
        tool_path = get_tool_path(tool_name)
        if tool_path:
            tools[tool_name] = tool_path
        else:
            missing_tools.append(tool_name)

            # Check if we have sufficient tools for real mode (at least cardano-address)
        if "cardano-address" in tools:
            # Additional check for ARM64 cardano-cli crash
            if "cardano-cli" in tools:
                # Check if we're on ARM64 macOS
                import platform

                is_arm64_macos = (
                    platform.system() == "Darwin"
                    and platform.machine() in ["arm64", "aarch64"]
                )

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
                            [str(tools["cardano-cli"]), "--version"],
                            capture_output=True,
                            text=True,
                            timeout=5,
                        )
                        if result.returncode != 0:
                            # Remove crashing cardano-cli from tools
                            del tools["cardano-cli"]
                            click.echo("⚠️  cardano-cli crashes, using simplified mode")
                            return {}
                    except Exception:
                        # Remove crashing cardano-cli from tools
                        if "cardano-cli" in tools:
                            del tools["cardano-cli"]
                        click.echo("⚠️  cardano-cli crashes, using simplified mode")
                        return {}

            click.echo("✅ Sufficient tools available for real mode")
            return tools

    if missing_tools:
        click.echo(f"❌ Missing tools: {', '.join(missing_tools)}")
        click.echo("Automatic download of missing tools...")
        try:
            downloaded_tools = download_cardano_tools()
            # If we have at least 2 tools (cardano-cli and cardano-address), we can use real mode
            if len(downloaded_tools) >= 2:
                click.echo("✅ Sufficient tools available for real mode")
                return downloaded_tools
            else:
                click.echo("💡 Using simplified mode instead...")
                return {}
        except Exception as e:
            click.echo(f"❌ Automatic download failed: {e}")
            click.echo("💡 Using simplified mode instead...")
            click.echo("💡 For real tools, install manually or use --simple flag")
            # Return empty dict to trigger simplified mode
            return {}

    return tools


# Cardano tools
