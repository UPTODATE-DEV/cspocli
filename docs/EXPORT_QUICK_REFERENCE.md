# 📦 Export Quick Reference - Cardano SPO CLI v1.1.0

## 🚀 **Quick Export Commands**

### **Standard Wallet Export**

```bash
# Export pledge wallet
cspocli export --ticker MYPOOL --purpose pledge --password mypassword

# Export rewards wallet
cspocli export --ticker MYPOOL --purpose rewards --password mypassword
```

### **Complete Stake Pool Export**

```bash
# Export complete pledge wallet (all files)
cspocli export --ticker MYPOOL --purpose pledge --password mypassword

# Export complete rewards wallet (all files)
cspocli export --ticker MYPOOL --purpose rewards --password mypassword
```

## 📁 **Generated Files**

### **Standard Export**

- `MYPOOL-pledge-export.zip.enc` - Encrypted archive
- `MYPOOL-pledge-export.key` - Decryption key

### **Complete Export**

- `MYPOOL-pledge-export.zip.enc` - Encrypted archive (all files)
- `MYPOOL-pledge-export.key` - Decryption key

## 🔓 **Decryption Script**

```bash
#!/bin/bash
# decrypt_export.sh

TICKER=$1
PURPOSE=$2
PASSWORD=$3

if [ -z "$TICKER" ] || [ -z "$PURPOSE" ] || [ -z "$PASSWORD" ]; then
    echo "Usage: ./decrypt_export.sh TICKER PURPOSE PASSWORD"
    echo "Example: ./decrypt_export.sh MYPOOL pledge mypassword"
    exit 1
fi

# Decrypt the export
python3 -c "
import base64
from cryptography.fernet import Fernet
import zipfile
import tempfile
import os

# Read the key file
with open('${TICKER}-${PURPOSE}-export.key', 'rb') as f:
    key = f.read()

# Read the encrypted file
with open('${TICKER}-${PURPOSE}-export.zip.enc', 'rb') as f:
    encrypted_data = f.read()

# Decrypt
cipher = Fernet(key)
decrypted_data = cipher.decrypt(encrypted_data)

# Extract ZIP
with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
    tmp.write(decrypted_data)
    tmp_path = tmp.name

# Extract files
with zipfile.ZipFile(tmp_path, 'r') as zipf:
    zipf.extractall('${TICKER}-${PURPOSE}-decrypted')

# Clean up
os.unlink(tmp_path)

print(f'Files extracted to: ${TICKER}-${PURPOSE}-decrypted/')
"
```

## 📤 **Upload Methods**

### **Secure Portal Upload**

1. **Prepare Files**

   ```bash
   # For standard export
   ls -la MYPOOL-pledge-export.zip.enc
   ls -la MYPOOL-pledge-export.key

   # For complete export
   ls -la MYPOOL-pledge-export.zip.enc
   ls -la MYPOOL-pledge-export.key
   ```

2. **Upload to Portal**
   - Upload both `.enc` and `.key` files
   - Provide password separately via secure channel
   - Include ticker and purpose information

### **Manual File Transfer**

```bash
# Copy files to secure location
cp MYPOOL-pledge-export.zip.enc /secure/location/
cp MYPOOL-pledge-export.key /secure/location/

# Verify transfer
ls -la /secure/location/MYPOOL-pledge-export.*
```

## 🔒 **Security Checklist**

### **Before Export**

- [ ] Verify wallet files exist
- [ ] Use strong password (12+ characters)
- [ ] Check file permissions (600 for sensitive files)
- [ ] Backup original files

### **After Export**

- [ ] Verify encrypted file size
- [ ] Test decryption on separate system
- [ ] Store key file separately from archive
- [ ] Use secure transfer method

### **For Upload**

- [ ] Verify file integrity
- [ ] Use secure portal or encrypted transfer
- [ ] Provide password via separate channel
- [ ] Confirm receipt with operator

## ⚠️ **Important Notes**

### **File Sizes**

- **Standard Export**: ~2-5 KB
- **Complete Export**: ~15-25 KB

### **Password Requirements**

- Minimum 8 characters
- Include uppercase, lowercase, numbers
- Avoid common words or patterns

### **Storage Recommendations**

- Store encrypted file and key separately
- Use different storage locations
- Regular backup of both files
- Secure deletion of original files after verification

## 🆘 **Troubleshooting**

### **Common Issues**

1. **"File not found"**

   ```bash
   # Check if wallet exists
   ls -la ~/.CSPO_MYPOOL/pledge/
   ```

2. **"Permission denied"**

   ```bash
   # Fix permissions
   chmod 600 ~/.CSPO_MYPOOL/pledge/*.skey
   chmod 600 ~/.CSPO_MYPOOL/pledge/*.mnemonic.txt
   ```

3. **"Decryption failed"**
   ```bash
   # Verify key file
   ls -la MYPOOL-pledge-export.key
   # Check file size (should be 44 bytes)
   ```

### **Verification Commands**

```bash
# Check export files
ls -la MYPOOL-pledge-export.*

# Verify file sizes
wc -c MYPOOL-pledge-export.zip.enc
wc -c MYPOOL-pledge-export.key

# Test decryption
./decrypt_export.sh MYPOOL pledge mypassword
```

## 📞 **Support**

- **Email**: support@cardano-spo-cli.org
- **Documentation**: See `docs/EXPORT_AND_UPLOAD_GUIDE.md`
- **Examples**: See `USAGE.md`
