#!/usr/bin/env python3
"""
Test script for Cardano SPO CLI
"""

import subprocess
import json
import os
from pathlib import Path


def test_cli_help():
    """Test help command"""
    print("🧪 Testing help command...")
    try:
        result = subprocess.run(
            ["python3", "-m", "cardano_spo_cli", "--help"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print("✅ Help command works")
            return True
        else:
            print(f"❌ Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False


def test_wallet_generation():
    """Test wallet generation"""
    print("🧪 Testing wallet generation...")
    try:
        result = subprocess.run(
            [
                "python3",
                "-m",
                "cardano_spo_cli",
                "generate",
                "--ticker",
                "TEST",
                "--purpose",
                "pledge",
                "--quiet",
                "--no-banner",
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            try:
                # Parse JSON output
                data = json.loads(result.stdout)
                print(f"✅ Wallet generated: {data['ticker']}-{data['purpose']}")
                print(f"   Base Address: {data['base_addr']}")
                print(f"   Reward Address: {data['reward_addr']}")
                print(f"   Files: {len(data['files'])}")
                return True
            except json.JSONDecodeError:
                print("⚠️  Non-JSON output (interactive mode)")
                return True
        else:
            print(f"❌ Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False


def test_wallet_files():
    """Test wallet file verification"""
    print("🧪 Testing wallet file verification...")
    wallet_dir = Path.home() / ".CSPO_TEST" / "pledge"

    if not wallet_dir.exists():
        print("❌ Wallet directory not found")
        return False

    required_files = [
        "TEST-pledge.base_addr",
        "TEST-pledge.reward_addr",
        "TEST-pledge.staking_skey",
        "TEST-pledge.staking_vkey",
        "TEST-pledge.mnemonic.txt",
    ]

    missing_files = []
    for file in required_files:
        if not (wallet_dir / file).exists():
            missing_files.append(file)

    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    else:
        print("✅ All required files are present")
        return True


def test_address_format():
    """Test address format"""
    print("🧪 Testing address format...")
    try:
        base_addr_file = Path.home() / ".CSPO_TEST" / "pledge" / "TEST-pledge.base_addr"
        reward_addr_file = (
            Path.home() / ".CSPO_TEST" / "pledge" / "TEST-pledge.reward_addr"
        )

        if not base_addr_file.exists() or not reward_addr_file.exists():
            print("❌ Address files not found")
            return False

        base_addr = base_addr_file.read_text().strip()
        reward_addr = reward_addr_file.read_text().strip()

        # Check address format
        if base_addr.startswith("addr") and reward_addr.startswith("stake"):
            print("✅ Address format correct")
            return True
        else:
            print(
                f"❌ Incorrect format: base={base_addr[:10]}..., reward={reward_addr[:10]}..."
            )
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False


def test_mnemonic():
    """Test recovery phrase"""
    print("🧪 Testing recovery phrase...")
    try:
        mnemonic_file = (
            Path.home() / ".CSPO_TEST" / "pledge" / "TEST-pledge.mnemonic.txt"
        )

        if not mnemonic_file.exists():
            print("❌ Mnemonic file not found")
            return False

        mnemonic = mnemonic_file.read_text().strip()
        words = mnemonic.split()

        if len(words) == 24:
            print("✅ Recovery phrase valid (24 words)")
            return True
        else:
            print(f"❌ Invalid phrase: {len(words)} words instead of 24")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False


def test_version():
    """Test version command"""
    print("🧪 Testing version command...")
    try:
        result = subprocess.run(
            ["python3", "-m", "cardano_spo_cli", "version"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print("✅ Version command works")
            return True
        else:
            print(f"❌ Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False


def main():
    """Main test function"""
    print("🚀 Starting Cardano SPO CLI tests...")
    print()

    tests = [
        test_cli_help,
        test_wallet_generation,
        test_wallet_files,
        test_address_format,
        test_mnemonic,
        test_version,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()

    print(f"📊 Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1


if __name__ == "__main__":
    exit(main())
