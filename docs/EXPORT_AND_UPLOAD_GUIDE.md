# 📦 Export and Upload Guide

## 🔒 **Export Process Overview**

The Cardano SPO CLI provides a secure export feature that creates password-protected ZIP archives containing all wallet files. This is essential for secure backup and transfer to other systems.

### **🎯 Export Features**

#### **✅ Security Features**

- **🔒 Password Protection**: AES-256 encryption with Fernet
- **📦 ZIP Archive**: Compressed archive with all wallet files
- **🔑 Key File**: Separate key file for decryption
- **🛡️ Secure Permissions**: Files protected with `0o600` permissions

#### **✅ Included Files**

- **Base Address**: `{TICKER}-{PURPOSE}.base_addr`
- **Reward Address**: `{TICKER}-{PURPOSE}.reward_addr`
- **Staking Private Key**: `{TICKER}-{PURPOSE}.staking_skey` (SENSITIVE)
- **Staking Public Key**: `{TICKER}-{PURPOSE}.staking_vkey`
- **Mnemonic Phrase**: `{TICKER}-{PURPOSE}.mnemonic.txt` (SENSITIVE)

## 📋 **Export Commands**

### **Basic Export**

```bash
# Export pledge wallet
cspocli export --ticker MYPOOL --purpose pledge --password mysecurepass123

# Export rewards wallet
cspocli export --ticker MYPOOL --purpose rewards --password mysecurepass123
```

### **Export Options**

```bash
cspocli export --help
```

**Options:**

- `--ticker, -t`: Pool ticker symbol (required)
- `--purpose, -p`: Wallet purpose: pledge or rewards (required)
- `--password`: Password for encrypted export (required)

## 🔧 **How Export Works**

### **Step 1: File Collection**

The export process collects all wallet files from the specified directory:

```
~/.CSPO_MYPOOL/pledge/
├── MYPOOL-pledge.base_addr
├── MYPOOL-pledge.reward_addr
├── MYPOOL-pledge.staking_skey
├── MYPOOL-pledge.staking_vkey
└── MYPOOL-pledge.mnemonic.txt
```

### **Step 2: ZIP Creation**

Creates a temporary ZIP archive containing all files:

```python
# Internal process
import zipfile
import tempfile

# Create temporary ZIP
with zipfile.ZipFile(temp_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for file_path in wallet_files:
        zipf.write(file_path, file_path.name)
```

### **Step 3: Encryption**

Encrypts the ZIP file using Fernet (AES-256):

```python
# Internal process
from cryptography.fernet import Fernet

# Generate encryption key
key = Fernet.generate_key()
cipher = Fernet(key)

# Encrypt ZIP file
with open(temp_zip, 'rb') as f:
    encrypted_data = cipher.encrypt(f.read())
```

### **Step 4: File Output**

Creates two files:

- **Encrypted Archive**: `{TICKER}-{PURPOSE}-export.zip.enc`
- **Key File**: `{TICKER}-{PURPOSE}-export.key`

## 📁 **Export Output Structure**

### **Generated Files**

```
~/.CSPO_MYPOOL/pledge/
├── MYPOOL-pledge.base_addr
├── MYPOOL-pledge.reward_addr
├── MYPOOL-pledge.staking_skey
├── MYPOOL-pledge.staking_vkey
├── MYPOOL-pledge.mnemonic.txt
├── MYPOOL-pledge-export.zip.enc    # 🔒 Encrypted archive
└── MYPOOL-pledge-export.key        # 🔑 Decryption key
```

### **Archive Contents**

The encrypted ZIP contains:

```
MYPOOL-pledge.base_addr
MYPOOL-pledge.reward_addr
MYPOOL-pledge.staking_skey
MYPOOL-pledge.staking_vkey
MYPOOL-pledge.mnemonic.txt
```

## 🔓 **Decryption Process**

### **Manual Decryption**

```bash
# Install cryptography if needed
pip install cryptography

# Python script to decrypt
python3 -c "
from cryptography.fernet import Fernet
import zipfile
import tempfile

# Load key and encrypted file
with open('MYPOOL-pledge-export.key', 'rb') as f:
    key = f.read()
with open('MYPOOL-pledge-export.zip.enc', 'rb') as f:
    encrypted_data = f.read()

# Decrypt
cipher = Fernet(key)
decrypted_data = cipher.decrypt(encrypted_data)

# Extract ZIP
with tempfile.NamedTemporaryFile(suffix='.zip') as tmp:
    tmp.write(decrypted_data)
    tmp.flush()

    with zipfile.ZipFile(tmp.name, 'r') as zipf:
        zipf.extractall('decrypted_wallet')
        print('Files extracted to: decrypted_wallet/')
"
```

### **Security Considerations**

- **🔑 Key File**: Store separately from encrypted archive
- **🔒 Password**: Use strong, unique passwords
- **📁 Backup**: Keep multiple copies in secure locations
- **🗑️ Cleanup**: Delete temporary files after decryption

## 📤 **Upload Process**

### **🎯 Upload Scenarios**

#### **1. Stake Pool Operator Setup**

Upload files to your stake pool operator for pool registration:

**Required Files:**

- `{TICKER}-pledge.base_addr`
- `{TICKER}-pledge.reward_addr`
- `{TICKER}-pledge.staking_skey`
- `{TICKER}-pledge.staking_vkey`

#### **2. Secure Backup**

Upload encrypted archives to secure cloud storage:

**Files to Upload:**

- `{TICKER}-{PURPOSE}-export.zip.enc`
- `{TICKER}-{PURPOSE}-export.key` (store separately)

#### **3. Wallet Import**

Upload mnemonic to wallet software for fund management:

**File to Upload:**

- `{TICKER}-shared.mnemonic.txt` (or individual mnemonic files)

### **📋 Upload Methods**

#### **Method 1: Direct File Upload**

```bash
# Extract files for direct upload
cspocli export --ticker MYPOOL --purpose pledge --password mypass
# Then upload the .enc and .key files separately
```

#### **Method 2: Secure Transfer**

```bash
# Use secure transfer methods
scp MYPOOL-pledge-export.zip.enc user@server:/secure/location/
scp MYPOOL-pledge-export.key user@server:/secure/location/
```

#### **Method 3: Cloud Storage**

```bash
# Upload to secure cloud storage
aws s3 cp MYPOOL-pledge-export.zip.enc s3://my-secure-bucket/
aws s3 cp MYPOOL-pledge-export.key s3://my-secure-bucket/
```

## 🔐 **Security Best Practices**

### **✅ Export Security**

- **Strong Passwords**: Use 16+ character passwords with mixed characters
- **Separate Storage**: Store encrypted archive and key file separately
- **Multiple Backups**: Keep backups in different secure locations
- **Access Control**: Limit access to exported files

### **✅ Upload Security**

- **Encrypted Transfer**: Use SFTP, SCP, or encrypted cloud storage
- **Access Logging**: Monitor access to uploaded files
- **Temporary Access**: Use temporary credentials when possible
- **Verification**: Verify file integrity after upload

### **✅ File Management**

- **Cleanup**: Remove temporary files after successful upload
- **Audit Trail**: Keep logs of export and upload activities
- **Version Control**: Use descriptive filenames with timestamps
- **Access Control**: Implement proper file permissions

## 📊 **Workflow Examples**

### **🎯 Professional Stake Pool Setup**

#### **Step 1: Generate Wallets**

```bash
# Create pledge wallet
cspocli generate --ticker MYPOOL --purpose pledge

# Create rewards wallet (uses same mnemonic)
cspocli generate --ticker MYPOOL --purpose rewards
```

#### **Step 2: Export for Pool Operator**

```bash
# Export pledge wallet for pool registration
cspocli export --ticker MYPOOL --purpose pledge --password pool_operator_pass

# Export rewards wallet for pool operator
cspocli export --ticker MYPOOL --purpose rewards --password pool_operator_pass
```

#### **Step 3: Upload to Pool Operator**

```bash
# Upload encrypted archives
scp MYPOOL-pledge-export.zip.enc pool-operator@server:/pool-files/
scp MYPOOL-rewards-export.zip.enc pool-operator@server:/pool-files/

# Upload keys separately
scp MYPOOL-pledge-export.key pool-operator@server:/secure-keys/
scp MYPOOL-rewards-export.key pool-operator@server:/secure-keys/
```

#### **Step 4: Pool Operator Decryption**

```bash
# Pool operator decrypts files
# (Using the decryption script provided above)
```

### **🎯 Secure Backup Workflow**

#### **Step 1: Export All Wallets**

```bash
# Export all wallets for backup
cspocli export --ticker MYPOOL --purpose pledge --password backup_pass_123
cspocli export --ticker MYPOOL --purpose rewards --password backup_pass_123
```

#### **Step 2: Upload to Multiple Locations**

```bash
# Primary backup (encrypted cloud storage)
aws s3 cp MYPOOL-*-export.zip.enc s3://my-secure-backup/

# Secondary backup (different provider)
gcloud storage cp MYPOOL-*-export.zip.enc gs://my-backup-bucket/

# Local backup (encrypted USB drive)
cp MYPOOL-*-export.zip.enc /Volumes/ENCRYPTED_USB/backups/
```

#### **Step 3: Key Management**

```bash
# Store keys separately from archives
# - Physical safe deposit box
# - Encrypted password manager
# - Secure cloud storage (separate from archives)
```

## 🚨 **Troubleshooting**

### **Common Issues**

#### **❌ Export Fails**

```bash
# Check if wallet exists
ls ~/.CSPO_MYPOOL/pledge/

# Regenerate wallet if needed
cspocli generate --ticker MYPOOL --purpose pledge --force
```

#### **❌ Decryption Fails**

```bash
# Verify key file exists
ls -la MYPOOL-pledge-export.key

# Check file integrity
file MYPOOL-pledge-export.zip.enc
file MYPOOL-pledge-export.key
```

#### **❌ Upload Fails**

```bash
# Check file permissions
ls -la MYPOOL-*-export.*

# Verify network connectivity
ping upload-server.com

# Check storage space
df -h
```

### **✅ Success Indicators**

- **Export**: "✅ Export created" message
- **File Size**: Encrypted file should be smaller than original
- **Key File**: Should be 44 characters (base64 encoded)
- **Upload**: No error messages, files appear in destination

## 📈 **Performance Tips**

### **✅ Export Optimization**

- **Compression**: ZIP files are automatically compressed
- **Selective Export**: Export only necessary files
- **Batch Processing**: Export multiple wallets in sequence
- **Cleanup**: Remove old exports to save space

### **✅ Upload Optimization**

- **Parallel Uploads**: Upload multiple files simultaneously
- **Resume Support**: Use tools that support resume on failure
- **Bandwidth**: Monitor upload speeds and adjust accordingly
- **Verification**: Verify uploads with checksums

## 🎉 **Summary**

The export and upload process provides:

- **🔒 Secure Encryption**: AES-256 with Fernet
- **📦 Complete Archives**: All wallet files included
- **🔑 Key Management**: Separate key files for security
- **📤 Multiple Upload Methods**: Direct, SCP, cloud storage
- **🛡️ Security Best Practices**: Comprehensive guidelines
- **📋 Professional Workflows**: Step-by-step examples

**This ensures your Cardano stake pool wallets are securely exported and uploaded for professional use!** 🚀
