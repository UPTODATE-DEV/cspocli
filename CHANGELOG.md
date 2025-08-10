# Changelog

All notable changes to the Cardano SPO CLI project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2024-12-19

### Added

- **Complete Stake Pool Generation**: New `--complete` flag for generating all stake pool files
- **Enhanced Security Features**: Password protection for sensitive files with AES-256 encryption
- **Export Functionality**: Secure encrypted ZIP export of wallet files
- **View Command**: Secure viewing of encrypted files without writing to disk
- **Network Support**: Support for mainnet, testnet, preview, and preprod networks
- **Force Regeneration**: `--force` flag to overwrite existing wallets
- **Quiet Mode**: JSON output for scripting and automation
- **Simplified Mode**: Python-native fallback when external tools unavailable

### Changed

- **Version Update**: Bumped from v1.0.0 to v1.1.0
- **CLI Banner**: Updated version display in welcome banner
- **Documentation**: Comprehensive updates to all documentation files
- **File Structure**: Enhanced file organization for complete stake pool operations

### Fixed

- **Version Consistency**: Aligned CLI version with git tags
- **Documentation**: Updated all docs to reflect current functionality
- **Command Reference**: Complete command documentation with examples

## [1.0.0] - 2024-12-18

### Added

- **Core Wallet Generation**: Generate pledge and rewards wallets
- **Shared Mnemonic**: Same recovery phrase for all wallets of a ticker
- **CNTools Import**: Import existing CNTools keys and generate addresses
- **Cross-Platform Support**: macOS, Linux, and Windows compatibility
- **Real Tools Integration**: Use official Cardano tools when available
- **Basic Security**: Secure file permissions and local storage

### Features

- Wallet generation for stake pool operations
- Address and key file creation
- Mnemonic phrase generation (BIP39)
- Basic file management and organization

## [0.1.0.16] - 2024-12-17

### Added

- Initial project setup
- Basic CLI structure
- Core wallet generation functionality
- Documentation framework

---

## Version History

- **v1.1.0**: Current stable release with complete stake pool features
- **v1.0.0**: Major release with core functionality
- **v0.1.0.16**: Initial development version
- **v0.1.0.15**: Development milestone
- **v0.1.0.14**: Development milestone

## Contributing

When contributing to this project, please update this changelog with your changes following the established format.

## Links

- [GitHub Repository](https://github.com/your-username/cardano-spo-cli)
- [Documentation](docs/)
- [Issues](https://github.com/your-username/cardano-spo-cli/issues)
