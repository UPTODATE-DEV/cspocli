# 📦 Export Quick Reference

## 🚀 **Quick Export Commands**

### **Export Pledge Wallet**

```bash
cspocli export --ticker MYPOOL --purpose pledge --password mysecurepass123
```

### **Export Rewards Wallet**

```bash
cspocli export --ticker MYPOOL --purpose rewards --password mysecurepass123
```

### **Export Both Wallets**

```bash
# Export pledge wallet
cspocli export --ticker MYPOOL --purpose pledge --password mysecurepass123

# Export rewards wallet
cspocli export --ticker MYPOOL --purpose rewards --password mysecurepass123
```

## 📁 **Generated Files**

### **Export Output**

```
~/.CSPO_MYPOOL/pledge/
├── MYPOOL-pledge-export.zip.enc    # 🔒 Encrypted archive
└── MYPOOL-pledge-export.key        # 🔑 Decryption key
```

### **Archive Contents**

```
MYPOOL-pledge.base_addr
MYPOOL-pledge.reward_addr
MYPOOL-pledge.staking_skey
MYPOOL-pledge.staking_vkey
MYPOOL-pledge.mnemonic.txt
```

## 🔓 **Quick Decryption**

### **Python Script**

```bash
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

## 📤 **Quick Upload Methods**

### **SCP Transfer**

```bash
# Upload encrypted archive
scp MYPOOL-pledge-export.zip.enc user@server:/secure/location/

# Upload key separately
scp MYPOOL-pledge-export.key user@server:/secure-keys/
```

### **Cloud Storage**

```bash
# AWS S3
aws s3 cp MYPOOL-pledge-export.zip.enc s3://my-secure-bucket/

# Google Cloud
gcloud storage cp MYPOOL-pledge-export.zip.enc gs://my-backup-bucket/
```

### **Local Backup**

```bash
# Copy to encrypted USB
cp MYPOOL-*-export.zip.enc /Volumes/ENCRYPTED_USB/backups/
cp MYPOOL-*-export.key /Volumes/ENCRYPTED_USB/keys/
```

## 🔐 **Security Checklist**

### **✅ Export Security**

- [ ] Use strong password (16+ characters)
- [ ] Store key file separately from archive
- [ ] Verify export completed successfully
- [ ] Check file permissions (600)

### **✅ Upload Security**

- [ ] Use encrypted transfer (SCP, SFTP)
- [ ] Upload key file separately
- [ ] Verify upload completion
- [ ] Monitor access logs

### **✅ Backup Strategy**

- [ ] Multiple backup locations
- [ ] Different storage providers
- [ ] Physical backup (USB drive)
- [ ] Test decryption process

## 🚨 **Troubleshooting**

### **Export Issues**

```bash
# Check if wallet exists
ls ~/.CSPO_MYPOOL/pledge/

# Regenerate if needed
cspocli generate --ticker MYPOOL --purpose pledge --force
```

### **Decryption Issues**

```bash
# Verify files exist
ls -la MYPOOL-*-export.*

# Check file integrity
file MYPOOL-pledge-export.zip.enc
file MYPOOL-pledge-export.key
```

### **Upload Issues**

```bash
# Check file permissions
ls -la MYPOOL-*-export.*

# Test connectivity
ping upload-server.com

# Check storage space
df -h
```

## 📊 **Workflow Examples**

### **🎯 Pool Operator Setup**

```bash
# 1. Generate wallets
cspocli generate --ticker MYPOOL --purpose pledge
cspocli generate --ticker MYPOOL --purpose rewards

# 2. Export for pool operator
cspocli export --ticker MYPOOL --purpose pledge --password pool_pass
cspocli export --ticker MYPOOL --purpose rewards --password pool_pass

# 3. Upload to pool operator
scp MYPOOL-*-export.zip.enc pool-operator@server:/pool-files/
scp MYPOOL-*-export.key pool-operator@server:/secure-keys/
```

### **🎯 Secure Backup**

```bash
# 1. Export all wallets
cspocli export --ticker MYPOOL --purpose pledge --password backup_pass
cspocli export --ticker MYPOOL --purpose rewards --password backup_pass

# 2. Upload to multiple locations
aws s3 cp MYPOOL-*-export.zip.enc s3://my-secure-backup/
gcloud storage cp MYPOOL-*-export.zip.enc gs://my-backup-bucket/
cp MYPOOL-*-export.zip.enc /Volumes/ENCRYPTED_USB/backups/
```

## 🎉 **Success Indicators**

### **✅ Export Success**

- "✅ Export created" message
- Encrypted file smaller than original
- Key file is 44 characters (base64)
- No error messages

### **✅ Upload Success**

- Files appear in destination
- No network errors
- Correct file sizes
- Proper permissions maintained

**For detailed documentation, see [Export & Upload Guide](EXPORT_AND_UPLOAD_GUIDE.md)** 📚
