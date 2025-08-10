from setuptools import setup, find_packages

setup(
    name="cardano-spo-cli",
    version="1.1.2",
    author="danbaruka",
    author_email="danbaruka@users.noreply.github.com",
    description="Professional Cardano Stake Pool Operator CLI",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
        "click>=8.0.0",
        "cryptography>=3.4.0",
        "mnemonic>=0.20.0",
        "bech32>=1.2.0",
        "colorama>=0.4.4",
        "tqdm>=4.62.0",
    ],
    entry_points={
        "console_scripts": [
            "cspocli=cardano_spo_cli.cli:main",
        ],
    },
    python_requires=">=3.7",
)
