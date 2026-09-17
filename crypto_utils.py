import os
import base64

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

SALT_SIZE = 16
KDF_ITERATIONS = 390_000


def generate_salt() -> bytes:
    return os.urandom(SALT_SIZE)


def derive_key(master_password: str, salt: bytes) -> bytes:
    """Turn a master password + salt into a Fernet-compatible key.
    Same password + same salt always produces the same key,
    but the raw password itself is never stored anywhere."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=KDF_ITERATIONS,
    )
    key_bytes = kdf.derive(master_password.encode())
    return base64.urlsafe_b64encode(key_bytes)


def encrypt_password(plain_password: str, key: bytes) -> str:
    return Fernet(key).encrypt(plain_password.encode()).decode()


def decrypt_password(token: str, key: bytes) -> str:
    return Fernet(key).decrypt(token.encode()).decode()


def key_is_correct(key: bytes, check_token: str) -> bool:
    """Try decrypting a known check-value with this key; tells us if the
    master password the user typed in was the right one."""
    try:
        decrypt_password(check_token, key)
        return True
    except InvalidToken:
        return False
