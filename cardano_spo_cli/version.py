"""
Version management for Cardano SPO CLI
"""

import subprocess
import re
from pathlib import Path
from typing import Optional


def get_git_version() -> str:
    """Get version from git tags"""
    try:
        # Get the latest tag
        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            # Remove 'v' prefix if present
            if version.startswith("v"):
                version = version[1:]
            return version
    except Exception:
        pass

    return "0.1.0"


def get_git_commit_hash() -> Optional[str]:
    """Get current git commit hash"""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass

    return None


def get_full_version() -> str:
    """Get full version string with commit hash"""
    version = get_git_version()
    commit_hash = get_git_commit_hash()

    if commit_hash:
        return f"{version}+{commit_hash}"
    return version


def is_dirty_working_tree() -> bool:
    """Check if working tree has uncommitted changes"""
    try:
        result = subprocess.run(
            ["git", "diff", "--quiet"],
            capture_output=True,
            cwd=Path(__file__).parent.parent,
        )
        return result.returncode != 0
    except Exception:
        return False


def get_version_info() -> dict:
    """Get complete version information"""
    version = get_git_version()
    commit_hash = get_git_commit_hash()
    is_dirty = is_dirty_working_tree()

    return {
        "version": version,
        "commit_hash": commit_hash,
        "is_dirty": is_dirty,
        "full_version": get_full_version(),
    }
# Version management
