import hashlib
from cryptography.fernet import Fernet  # serve per la possibile azione extra: encrypt_aes

def redact(_: str) -> str:
    return "[REDACTED]"

def hash_value(value: str) -> str:
    h = hashlib.sha256(value.encode()).hexdigest()
    return f"[HASH:{h[:4]}...]"

def mask_last_4(value: str) -> str:
    return "*" * (len(value) - 4) + value[-4:]

def keep(value: str) -> str:
    return value


# AES ENCRYPT SE SI VUOLE AGGIUNGERE

AES_KEY = Fernet.generate_key()  
cipher = Fernet(AES_KEY)

def encrypt_aes(value: str) -> str:
    return cipher.encrypt(value.encode()).decode()


# MAPPA AZIONI

ACTION_MAP = {
    "REDACT": redact,
    "HASH": hash_value,
    "MASK_LAST_4": mask_last_4,
    "KEEP": keep,
    "ENCRYPT_AES": encrypt_aes,  # azione extra
}