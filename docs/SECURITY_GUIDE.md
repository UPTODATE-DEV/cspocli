# 🔒 Security Guide - Cardano SPO CLI v1.1.0

## Overview

The Cardano SPO CLI provides advanced security features to protect sensitive wallet files. This guide explains how to use password protection for your wallet files and best practices for secure wallet management.

## 🔐 Security Features

### **Password Protection**

- **AES-256 Encryption**: All sensitive files are encrypted using industry-standard AES-256
- **PBKDF2 Key Derivation**: Passwords are securely derived using PBKDF2 with 100,000 iterations
- **Salt-based Encryption**: Each file uses a unique salt for enhanced security
- **File-level Protection**: Individual files can be secured and accessed independently

### **Sensitive Files**

The following files are considered sensitive and can be password-protected:

- **`.skey` files**: All private keys (payment, stake, cold, hot, DRep, multi-signature)
- **`.mnemonic.txt` files**: 24-word recovery phrases

## 📋 Security Commands

### **Secure Files**

```bash
# Secure all sensitive files in a wallet
cspocli secure --ticker MYPOOL --purpose pledge --password mysecurepass

# Secure rewards wallet
cspocli secure --ticker MYPOOL --purpose rewards --password mysecurepass
```

**What happens:**

1. All `.skey` and `.mnemonic.txt` files are encrypted
2. Original files are replaced with `.enc` versions
3. Files can only be accessed with the correct password

### **View Secured Files**

```bash
# List all secured files
cspocli view --ticker MYPOOL --purpose pledge --password mysecurepass

# View specific file content
cspocli view --ticker MYPOOL --purpose pledge --password mysecurepass --file payment.skey

# View recovery phrase
cspocli view --ticker MYPOOL --purpose pledge --password mysecurepass --file mnemonic.txt
```

**What happens:**

1. Files are temporarily decrypted in memory
2. Content is displayed securely
3. No decrypted files are written to disk

## 🔧 How It Works

### **Encryption Process**

1. **Password Derivation**

   ```python
   # Generate unique salt
   salt = os.urandom(16)

   # Derive key using PBKDF2
   kdf = PBKDF2HMAC(
       algorithm=hashes.SHA256(),
       length=32,
       salt=salt,
       iterations=100000,
   )
   key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
   ```

2. **File Encryption**

   ```python
   # Encrypt file content
   cipher = Fernet(key)
   encrypted_data = cipher.encrypt(original_data)

   # Write encrypted file with salt
   with open(encrypted_path, 'wb') as f:
       f.write(salt)  # 16 bytes
       f.write(encrypted_data)
   ```

3. **File Decryption**

   ```python
   # Read salt and encrypted data
   salt = f.read(16)
   encrypted_data = f.read()

   # Derive key and decrypt
   key, _ = derive_key_from_password(password, salt)
   cipher = Fernet(key)
   decrypted_data = cipher.decrypt(encrypted_data)
   ```

### **File Structure**

#### **Before Securing**

```
~/.CSPO_MYPOOL/pledge/
├── base.addr
├── payment.addr
├── reward.addr
├── payment.skey          # SENSITIVE
├── payment.vkey
├── stake.skey            # SENSITIVE
├── stake.vkey
├── cc-cold.skey          # SENSITIVE
├── cc-cold.vkey
├── cc-hot.skey           # SENSITIVE
├── cc-hot.vkey
├── drep.skey             # SENSITIVE
├── drep.vkey
├── ms_payment.skey       # SENSITIVE
├── ms_payment.vkey
├── ms_stake.skey         # SENSITIVE
├── ms_stake.vkey
├── ms_drep.skey          # SENSITIVE
├── ms_drep.vkey
├── payment.cred
├── stake.cred
├── ms_payment.cred
├── ms_stake.cred
├── stake.cert
├── delegation.cert
└── MYPOOL-pledge.mnemonic.txt  # SENSITIVE
```

#### **After Securing**

```
~/.CSPO_MYPOOL/pledge/
├── base.addr
├── payment.addr
├── reward.addr
├── payment.skey.enc      # ENCRYPTED
├── payment.vkey
├── stake.skey.enc        # ENCRYPTED
├── stake.vkey
├── cc-cold.skey.enc      # ENCRYPTED
├── cc-cold.vkey
├── cc-hot.skey.enc       # ENCRYPTED
├── cc-hot.vkey
├── drep.skey.enc         # ENCRYPTED
├── drep.vkey
├── ms_payment.skey.enc   # ENCRYPTED
├── ms_payment.vkey
├── ms_stake.skey.enc     # ENCRYPTED
├── ms_stake.vkey
├── ms_drep.skey.enc      # ENCRYPTED
├── ms_drep.vkey
├── payment.cred
├── stake.cred
├── ms_payment.cred
├── ms_stake.cred
├── stake.cert
├── delegation.cert
└── MYPOOL-pledge.mnemonic.txt.enc  # ENCRYPTED
```

## 🛡️ Security Best Practices

### **Password Requirements**

- **Minimum 8 characters**
- **Include uppercase and lowercase letters**
- **Include numbers**
- **Include special characters**
- **Avoid common words or patterns**
- **Use unique passwords for different wallets**

### **Password Management**

1. **Strong Passwords**

   ```bash
   # Good examples
   cspocli secure --ticker MYPOOL --purpose pledge --password "K9#mP2$vL8@nQ4!"
   cspocli secure --ticker MYPOOL --purpose pledge --password "MyP00l2024!Secure"

   # Avoid weak passwords
   cspocli secure --ticker MYPOOL --purpose pledge --password "password123"
   cspocli secure --ticker MYPOOL --purpose pledge --password "123456"
   ```

2. **Password Storage**
   - Store passwords in a secure password manager
   - Never write passwords in plain text files
   - Use different passwords for different wallets
   - Consider using passphrases for better security

### **File Access Patterns**

1. **Secure Immediately After Generation**

   ```bash
   # Generate wallet
   cspocli generate --ticker MYPOOL --complete

   # Secure immediately
   cspocli secure --ticker MYPOOL --purpose pledge --password mysecurepass
   ```

2. **Access Only When Needed**

   ```bash
   # View only when necessary
   cspocli view --ticker MYPOOL --purpose pledge --password mysecurepass --file payment.skey

   # Don't leave files unsecured
   ```

3. **Secure Environment**
   - Use dedicated, secure computer
   - Ensure no keyloggers or malware
   - Use encrypted disk if possible
   - Lock screen when not in use

## 🔍 Verification and Testing

### **Test Security**

```bash
# 1. Generate test wallet
cspocli generate --ticker TEST --purpose pledge --complete

# 2. Secure files
cspocli secure --ticker TEST --purpose pledge --password testpass

# 3. Verify files are encrypted
ls -la ~/.CSPO_TEST/pledge/*.enc

# 4. Test access with correct password
cspocli view --ticker TEST --purpose pledge --password testpass

# 5. Test access with wrong password (should fail)
cspocli view --ticker TEST --purpose pledge --password wrongpass
```

### **Verify File Integrity**

```bash
# Check that sensitive files are encrypted
ls -la ~/.CSPO_MYPOOL/pledge/ | grep "\.enc"

# Verify original files are gone
ls -la ~/.CSPO_MYPOOL/pledge/ | grep -E "\.(skey|mnemonic\.txt)$"

# Test decryption
cspocli view --ticker MYPOOL --purpose pledge --password mypass --file payment.skey
```

## 🚨 Security Warnings

### **Important Considerations**

1. **Password Loss**

   - If you lose the password, files cannot be recovered
   - Always backup passwords securely
   - Consider using password managers

2. **File Backup**

   - Encrypted files can be backed up safely
   - Original files are deleted after encryption
   - Keep encrypted backups in multiple locations

3. **Access Control**

   - Only access files when necessary
   - Use strong, unique passwords
   - Don't share passwords or files

4. **System Security**
   - Ensure your system is secure
   - Use antivirus and firewall
   - Keep system updated

## 🔧 Troubleshooting

### **Common Issues**

1. **"File not found"**

   ```bash
   # Check if wallet exists
   ls -la ~/.CSPO_MYPOOL/pledge/

   # Check if files are secured
   ls -la ~/.CSPO_MYPOOL/pledge/*.enc
   ```

2. **"Decryption failed"**

   ```bash
   # Verify password is correct
   # Check for typos
   # Ensure password matches exactly
   ```

3. **"No secured files found"**
   ```bash
   # Files may not be secured yet
   cspocli secure --ticker MYPOOL --purpose pledge --password mypass
   ```

### **Recovery Options**

1. **If Password is Lost**

   - Files cannot be recovered without password
   - Regenerate wallet if necessary
   - Use backup if available

2. **If Files are Corrupted**
   - Check file permissions
   - Verify file integrity
   - Restore from backup

## 📞 Support

For security-related issues:

- **Email**: support@cardano-spo-cli.org
- **Documentation**: See other guides in `docs/` folder
- **Security**: Report vulnerabilities responsibly

## ⚠️ Disclaimer

This security feature provides file-level encryption but does not guarantee absolute security. Always follow security best practices and use additional security measures as appropriate for your use case.
