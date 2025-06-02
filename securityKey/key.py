from cryptography.fernet import Fernet

key = Fernet.generate_key()

with open("encryption.key", "wb") as f:
    f.write(key)

print("🔐 Encryption key saved to 'encryption.key'")
