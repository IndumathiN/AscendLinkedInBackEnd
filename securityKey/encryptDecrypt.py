from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="./config/.env")

KEY_PATH=os.getenv("ENCRYPTION_KEY_PATH")

def load_key():
    with open(KEY_PATH, "rb") as f:
        return f.read()

def encrypt_text(plain_text: str) -> str:
    key = load_key()
    fernet = Fernet(key)
    return fernet.encrypt(plain_text.encode()).decode()

def decrypt_text(encrypted_text: str) -> str:
    key = load_key()
    fernet = Fernet(key)
    return fernet.decrypt(encrypted_text.encode()).decode()
